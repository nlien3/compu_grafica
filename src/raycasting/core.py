# src/raycasting/core.py
import numpy as np
import pyglet
from pyglet.window import key
from math import cos, sin, tan, pi

from src.renderer_base import RendererBase

class RaycastingRenderer(RendererBase):
    def __init__(self, window):
        """
        window: referencia a la ventana Pyglet para blitear la imagen.
        """
        self.window = window
        self.W, self.H = window.width, window.height

        # Mapa simple (1 = pared, 0 = vacío)
        self.map = np.array([
            [1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,2,1],
            [1,0,0,0,0,0,0,0,0,0,2,1],
            [1,0,0,0,0,0,0,0,0,0,2,1],
            [1,0,0,0,0,0,0,0,0,0,2,1],
            [1,0,0,0,0,0,0,0,0,0,2,1],
            [1,0,0,0,0,0,0,0,0,0,2,1],
            [1,0,0,0,0,0,0,0,0,0,2,1],
            [1,0,0,0,0,0,0,0,0,0,2,1],
            [1,3,3,3,3,0,0,0,0,0,2,1],
            [1,0,0,0,0,0,0,0,0,0,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1],
        ], dtype=np.int32)
        self.map_h, self.map_w = self.map.shape

        # Cámara (x, y) en coordenadas de celda (y + altura “ojos” implícita)
        self.cam_x = 2.5
        self.cam_y = 2.5
        self.cam_a = 0.0         # ángulo en radianes
        self.fov   = pi/3        # ~60°

        # Movement flags
        self.keys = set()
        self.move_speed = 3.0    # unidades/seg
        self.rot_speed  = 1.8    # rad/seg

        # Framebuffer de imagen (RGB)
        self.fb = np.zeros((self.H, self.W, 3), dtype=np.uint8)
        self._img = None

    # ---------- API RendererBase ----------
    def on_resize(self, w: int, h: int):
        self.W, self.H = int(w), int(h)
        self.fb = np.zeros((self.H, self.W, 3), dtype=np.uint8)
        self._img = None

    def update(self, dt: float):
        # Movimiento básico
        dx = cos(self.cam_a) * self.move_speed * dt
        dy = sin(self.cam_a) * self.move_speed * dt

        if key.W in self.keys:
            self._try_move(self.cam_x + dx, self.cam_y + dy)
        if key.S in self.keys:
            self._try_move(self.cam_x - dx, self.cam_y - dy)
        if key.A in self.keys:
            # strafe izquierda
            sx = cos(self.cam_a - pi/2) * self.move_speed * dt
            sy = sin(self.cam_a - pi/2) * self.move_speed * dt
            self._try_move(self.cam_x + sx, self.cam_y + sy)
        if key.D in self.keys:
            # strafe derecha
            sx = cos(self.cam_a + pi/2) * self.move_speed * dt
            sy = sin(self.cam_a + pi/2) * self.move_speed * dt
            self._try_move(self.cam_x + sx, self.cam_y + sy)

        if key.LEFT  in self.keys:
            self.cam_a -= self.rot_speed * dt
        if key.RIGHT in self.keys:
            self.cam_a += self.rot_speed * dt

    def render(self):
        # Cielo / piso
        self.fb[: self.H//2, :, :] = (22, 24, 31)      # “cielo”
        self.fb[self.H//2 :, :, :] = (32, 34, 42)      # “piso”

        # Raycasting por columnas
        for x in range(self.W):
            # Desde -fov/2 a +fov/2
            cam_ray = (x / max(1, (self.W - 1)) - 0.5) * self.fov
            ray_a = self.cam_a + cam_ray
            dist, tile = self._cast_ray(self.cam_x, self.cam_y, ray_a)

            # Altura de columna con corrección por “fisheye”
            dist = max(1e-4, dist * cos(cam_ray))
            col_h = int(self.H / dist)

            # Color por tipo de pared + atenuación con distancia
            base = {
                1: np.array([220, 220, 220], dtype=np.uint8),  # gris
                2: np.array([180, 80,  80 ], dtype=np.uint8),  # rojo
                3: np.array([80,  180, 80 ], dtype=np.uint8),  # verde
            }.get(tile, np.array([160, 160, 220], dtype=np.uint8))

            shade = 1.0 / (1.0 + 0.1 * dist * dist)
            color = np.clip(base * shade, 0, 255).astype(np.uint8)

            y0 = max(0, self.H//2 - col_h//2)
            y1 = min(self.H, self.H//2 + col_h//2)
            if y1 > y0:
                self.fb[y0:y1, x, :] = color

        # Blit a la ventana (creamos o actualizamos ImageData)
        # OJO: pyglet usa formato 'RGB' y la imagen se crea desde un buffer alto->bajo
        data = self.fb[::-1].tobytes()  # flip vertical
        if self._img is None or self._img.width != self.W or self._img.height != self.H:
            self._img = pyglet.image.ImageData(self.W, self.H, 'RGB', data)
        else:
            self._img.set_data('RGB', self.W * 3, data)

        self._img.blit(0, 0)

    # ---------- Eventos de teclado ----------
    def on_key_press(self, symbol, modifiers):
        self.keys.add(symbol)

    def on_key_release(self, symbol, modifiers):
        self.keys.discard(symbol)

    # ---------- Helpers ----------
    def _try_move(self, nx, ny):
        """Colisión simple contra celdas sólidas."""
        if not self._is_solid(nx, self.cam_y):
            self.cam_x = nx
        if not self._is_solid(self.cam_x, ny):
            self.cam_y = ny

    def _is_solid(self, x, y):
        i = int(y)
        j = int(x)
        if i < 0 or j < 0 or i >= self.map_h or j >= self.map_w:
            return True
        return self.map[i, j] != 0

    def _cast_ray(self, ox, oy, ang):
        """
        DDA sobre grid: avanzamos celda por celda hasta chocar pared.
        Devuelve (distancia, tile_id).
        """
        # Dirección del rayo
        dx = cos(ang)
        dy = sin(ang)

        # celda actual
        map_x = int(ox)
        map_y = int(oy)

        # longitudes a las próximas paredes en X e Y
        delta_dist_x = abs(1.0 / (dx if abs(dx) > 1e-8 else 1e-8))
        delta_dist_y = abs(1.0 / (dy if abs(dy) > 1e-8 else 1e-8))

        # paso y dist inicial a la primera intersección
        if dx < 0:
            step_x = -1
            side_dist_x = (ox - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - ox) * delta_dist_x

        if dy < 0:
            step_y = -1
            side_dist_y = (oy - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - oy) * delta_dist_y

        hit = False
        side = 0  # 0 = vertical, 1 = horizontal
        tile = 0
        max_steps = 4096

        for _ in range(max_steps):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if map_y < 0 or map_y >= self.map_h or map_x < 0 or map_x >= self.map_w:
                break

            tile = int(self.map[map_y, map_x])
            if tile != 0:
                hit = True
                break

        if not hit:
            return 1e6, 0  # “muy lejos”

        # Distancia al impacto
        if side == 0:
            # impacto en una pared vertical
            dist = (map_x - ox + (1 - step_x) / 2.0) / (dx if abs(dx) > 1e-8 else 1e-8)
        else:
            # impacto en pared horizontal
            dist = (map_y - oy + (1 - step_y) / 2.0) / (dy if abs(dy) > 1e-8 else 1e-8)

        return abs(dist), tile
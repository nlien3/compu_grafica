from pathlib import Path
import numpy as np
import moderngl
import glm
import pyglet
import pyglet.shapes  # <- necesario para el rectángulo del HUD
from pyglet.window import key


class RaytracingRenderer:
    """
    Quad a pantalla; el fragment shader hace el raytracing
    (esfera + plano, Lambert/Phong, sombra dura).
    Controles:
      T          : alternar TP4 ↔ Raytracing (lo maneja main/window)
      ESPACIO    : pausar/seguir animación orbital de la luz
      W/S/A/D    : mover luz en XZ (continuo al mantener)
      R/F        : mover luz en Y
      H          : mostrar/ocultar ayuda (HUD)
      P          : imprimir posición de la luz (debug)
    """
    def __init__(self, win, shaders_dir: Path):
        self.win = win
        self.ctx: moderngl.Context = win.ctx
        self.W, self.H = win.width, win.height

        # ---------- Shaders ----------
        vs_src = (shaders_dir / "raytrace.vert").read_text(encoding="utf-8")
        fs_src = (shaders_dir / "raytrace.frag").read_text(encoding="utf-8")
        self.prog = self.ctx.program(vertex_shader=vs_src, fragment_shader=fs_src)

        # ---------- Fullscreen quad ----------
        quad = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
            -1.0,  1.0,
             1.0, -1.0,
             1.0,  1.0,
        ], dtype="f4")
        self.vbo = self.ctx.buffer(quad.tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [(self.vbo, "2f", "in_pos")])

        # ---------- Uniforms escena ----------
        self.prog["uSphereCenter"].value = (0.0, 0.5, 0.0)
        self.prog["uSphereRadius"].value = 0.75
        self.prog["uPlaneY"].value = -1.0

        # cámara
        self.set_aspect(self.W / max(1, self.H))
        self.set_fov(glm.radians(60.0))
        eye    = glm.vec3(3.0, 2.5, 3.0)
        target = glm.vec3(0.0, 0.5, 0.0)
        up     = glm.vec3(0.0, 1.0, 0.0)
        self.view = glm.lookAt(eye, target, up)

        # luz (inicial)
        self.light_pos = glm.vec3(4.0, 2.5, 0.0)
        self.prog["uLightPos"].value = tuple(self.light_pos)

        # animación / input
        self.time = 0.0
        self.animate = True
        self._keys = set()
        self.light_speed = 6.0     # más rápido al mantener teclas
        self.orbit_radius = 4.0    # órbita más grande

        # ---------- HUD ----------
        self.show_hud = True
        self._batch = pyglet.graphics.Batch()
        self._hud_bg = pyglet.shapes.Rectangle(
            x=8, y=self.H - 8 - 110, width=460, height=110,
            color=(0, 0, 0), batch=self._batch
        )
        self._hud_bg.opacity = 140
        self._hud_label = pyglet.text.Label(
            self._hud_text(),
            font_name="Menlo", font_size=12,
            x=16, y=self.H - 16,
            anchor_x='left', anchor_y='top',
            color=(255, 255, 255, 230),
            batch=self._batch,
        )

    # ---------------- HUD text ----------------
    def _hud_text(self):
        return (
            "Controles (Raytracing):\n"
            "  T        : alternar TP4 ↔ Raytracing\n"
            "  ESPACIO  : pausar/seguir animación de la luz\n"
            "  W/S/A/D  : mover luz en XZ\n"
            "  R/F      : mover luz en Y\n"
            "  H        : mostrar/ocultar esta ayuda\n"
            "  P        : imprimir posición de la luz (consola)\n"
        )

    # --------------- API pública ---------------
    def set_aspect(self, aspect: float):
        self.aspect = max(1e-5, float(aspect))
        self.prog["uAspect"].value = self.aspect

    def set_fov(self, fov_rad: float):
        self.fov = float(fov_rad)
        self.prog["uFov"].value = self.fov

    def on_resize(self, w: int, h: int):
        self.W, self.H = int(w), int(h)
        self.ctx.viewport = (0, 0, self.W, self.H)
        self.set_aspect(self.W / max(1, self.H))
        # mover HUD
        self._hud_bg.y = self.H - 8 - 110
        self._hud_label.y = self.H - 16

    def update(self, dt: float):
        # órbita visible y oscilación vertical
        if self.animate:
            self.time += dt
            ang = 1.0 * self.time
            y   = 2.5 + 0.8 * glm.sin(0.9 * self.time)
            self.light_pos = glm.vec3(
                self.orbit_radius * glm.cos(ang),
                y,
                self.orbit_radius * glm.sin(ang)
            )

        # movimiento continuo con teclas
        move = glm.vec3(0)
        if key.W in self._keys: move += glm.vec3( 0, 0, -1)
        if key.S in self._keys: move += glm.vec3( 0, 0,  1)
        if key.A in self._keys: move += glm.vec3(-1, 0,  0)
        if key.D in self._keys: move += glm.vec3( 1, 0,  0)
        if key.R in self._keys: move += glm.vec3( 0, 1,  0)
        if key.F in self._keys: move += glm.vec3( 0,-1,  0)
        if glm.length(move) > 0:
            move = glm.normalize(move) * (self.light_speed * dt)
            self.light_pos += move

    def render(self):
        self.ctx.clear(0.08, 0.09, 0.12, 1.0)

        # uniforms
        invV = glm.inverse(self.view)
        self.prog["uInvView"].write(np.array(invV.to_list(), dtype="f4").tobytes())
        self.prog["uLightPos"].value = tuple(self.light_pos)

        self.vao.render()

        # HUD encima
        if self.show_hud:
            self.ctx.finish()
            self._batch.draw()

    # --------------- eventos teclado ---------------
    def on_key_press(self, symbol, modifiers):
        self._keys.add(symbol)
        if symbol == key.SPACE:
            self.animate = not self.animate
        elif symbol == key.H:
            self.show_hud = not self.show_hud
        elif symbol == key.P:
            print(f"Light = ({self.light_pos.x:.2f}, {self.light_pos.y:.2f}, {self.light_pos.z:.2f})")

    def on_key_release(self, symbol, modifiers):
        self._keys.discard(symbol)
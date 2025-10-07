# src/scene.py
import moderngl
import glm
from src.ray import Ray

class Scene:
    def __init__(self, ctx: moderngl.Context, camera, shader_program):
        self.ctx = ctx
        self.camera = camera
        self.shader = shader_program
        self.items = []      # lista de tuplas: (obj, graphics)

    def add(self, obj, graphics):
        self.items.append((obj, graphics))

    # ---- ciclo ----
    def update(self, dt: float):
        # Animación simple: si el objeto tiene rotate_y, lo hacemos rotar
        for obj, _ in self.items:
            if hasattr(obj, "rotate_y"):
                obj.rotate_y(dt * 0.6)

    def render(self):
        # Fondo y z-buffer
        self.ctx.clear(0.08, 0.09, 0.12, 1.0)
        self.ctx.enable(moderngl.DEPTH_TEST)

        V = self.camera.view
        P = self.camera.projection

        for obj, gfx in self.items:
            M = obj.get_model_matrix()

            # (opcional) feedback visual si el objeto está "seleccionado"
            if getattr(obj, "selected", False):
                M = M * glm.scale(glm.mat4(1.0), glm.vec3(1.05))

            Mvp = P * V * M
            self.shader.set_mat4("Mvp", Mvp)
            gfx.render()

    # ---- tamaño de ventana ----
    def on_resize(self, width: int, height: int):
        # Lo llama Window.on_resize; actualizamos aspect de la cámara
        aspect = max(1e-5, width / max(1, height))
        self.camera.set_aspect(aspect)

    # ---- picking por click ----
    def on_mouse_click(self, u: float, v: float):
        # u,v ∈ [0,1], ya con v invertida desde window.py
        origin, direction = self.camera.generate_ray(u, v)
        ray = Ray(origin, direction)

        # Elegir SIEMPRE el impacto más cercano (t mínimo)
        best_obj = None
        best_t = float("inf")

        for obj, _ in self.items:
            if hasattr(obj, "check_hit"):
                t = obj.check_hit(ray.origin, ray.direction)  # float o None
                if t is not None and 0.0 <= t < best_t:
                    best_t = t
                    best_obj = obj

        if best_obj is not None:
            # alternar "seleccionado" como feedback visual
            best_obj.selected = not getattr(best_obj, "selected", False)
            print(f"[HIT] → {getattr(best_obj, 'name', best_obj.__class__.__name__)}  t={best_t:.3f}")
        else:
            print("[HIT] ninguno")
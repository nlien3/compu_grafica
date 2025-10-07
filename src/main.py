from pathlib import Path
import pyglet
import glm

from src.window import Window
from src.shader_program import ShaderProgram
from src.graphics import Graphics
from src.camera import Camera
from src.scene import Scene
from src.cube import Cube

from src.raytracing.core import RaytracingRenderer   # <--- nuevo

def build_tp4_scene(win, shaders_dir: Path):
    shader = ShaderProgram(win.ctx, shaders_dir / "basic.vert", shaders_dir / "basic.frag")
    cam = Camera(fov_deg=60.0, aspect=win.width / win.height, near=0.1, far=100.0)
    scene = Scene(win.ctx, cam, shader)

    cube1 = Cube("CuboA")
    cube1.set_position(-1.2, 0.0, 0.0)
    cube1.scale_uniform(0.9)

    cube2 = Cube("CuboB")
    cube2.set_position( 1.2, 0.0, 0.0)
    cube2.scale_uniform(0.9)

    g1 = Graphics(win.ctx, shader, cube1.vertices, cube1.indices)
    g2 = Graphics(win.ctx, shader, cube2.vertices, cube2.indices)

    scene.add(cube1, g1)
    scene.add(cube2, g2)
    return scene

def main():
    base = Path(__file__).resolve().parent.parent
    shaders_dir = base / "shaders"

    win = Window(1280, 720, "Parcial CG 2025 – TP4 + Raytracing (T para alternar)")

    # ---- Modo A: Escena TP4 (picking) ----
    scene = build_tp4_scene(win, shaders_dir)

    # ---- Modo B: Raytracing (quad + shader) ----
    rt = RaytracingRenderer(win, shaders_dir)

    # estado: arrancamos en modo TP4
    mode = {"rt": False}

    def use_tp4():
        win.set_scene(scene)
        mode["rt"] = False
        print("[Modo] TP4 + Picking")

    def use_rt():
        win.set_scene(None)          # desconectamos la escena
        win.set_renderer(rt)         # (opcional) si usás set_renderer, sino llama rt.render() desde on_draw
        mode["rt"] = True
        print("[Modo] Raytracing")

    use_tp4()  # start
    print("""
================= CONTROLES =================
T : Alternar TP4 <-> Raytracing
H : Mostrar/ocultar HUD (solo en Raytracing)
Espacio : Pausar/reanudar animación (Raytracing)
W / S : Mover luz adelante / atrás
A / D : Mover luz izquierda / derecha
R / F : Mover luz arriba / abajo
P : Mostrar posición de la luz en consola
=============================================
""")
    # update loop
    def _update(dt):
        if mode["rt"]:
            rt.update(dt)
        else:
            scene.update(dt)
    pyglet.clock.schedule_interval(_update, 1/60)

    # tecla T para alternar
    @win.event
    def on_key_press(symbol, modifiers):
        from pyglet.window import key
        if symbol == key.T:
            if mode["rt"]:
                use_tp4()
            else:
                use_rt()

    try:
        win.switch_to(); win.set_visible(True); win.activate()
    except Exception:
        pass

    win.run()

if __name__ == "__main__":
    main()
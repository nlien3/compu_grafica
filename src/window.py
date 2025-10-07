import pyglet
import moderngl


class Window(pyglet.window.Window):
    def __init__(self, width=1280, height=720, title="Parcial CG 2025"):
        super().__init__(width=width, height=height, caption=title, resizable=True)
        self.ctx = moderngl.create_context()
        self.ctx.viewport = (0, 0, width, height)
        self.scene = None
        self.renderer = None

    def set_scene(self, scene):
        self.scene = scene
        if self.scene:
            self.scene.on_resize(self.width, self.height)

    def set_renderer(self, renderer):
        self.renderer = renderer
        if self.renderer:
            self.renderer.on_resize(self.width, self.height)

    def on_draw(self):
        self.clear()
        if self.scene:
            self.scene.render()
        elif self.renderer:
            self.renderer.render()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.ctx.viewport = (0, 0, width, height)
        if self.scene:
            self.scene.on_resize(width, height)
        elif self.renderer:
            self.renderer.on_resize(width, height)

    def on_mouse_press(self, x, y, button, modifiers):
        u = x / max(1, self.width)
        v = 1.0 - (y / max(1, self.height))
        if self.scene and hasattr(self.scene, "on_mouse_click"):
            self.scene.on_mouse_click(u, v)
        elif self.renderer and hasattr(self.renderer, "on_mouse_press"):
            self.renderer.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol, modifiers):
        if self.scene and hasattr(self.scene, "on_key_press"):
            self.scene.on_key_press(symbol, modifiers)
        if self.renderer and hasattr(self.renderer, "on_key_press"):
            self.renderer.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        if self.scene and hasattr(self.scene, "on_key_release"):
            self.scene.on_key_release(symbol, modifiers)
        if self.renderer and hasattr(self.renderer, "on_key_release"):
            self.renderer.on_key_release(symbol, modifiers)

    def run(self):
        pyglet.app.run()
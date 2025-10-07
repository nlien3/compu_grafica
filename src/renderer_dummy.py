import moderngl
from src.renderer_base import RendererBase

class DummyRenderer(RendererBase):
    """Renderer placeholder para el INICIO: limpia con color constante."""
    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx

    def on_resize(self, w: int, h: int):
        self.ctx.viewport = (0, 0, w, h)

    def update(self, dt: float):
        pass

    def render(self):
        # Fondo gris azulado, como en TP4
        self.ctx.clear(0.08, 0.09, 0.12, 1.0)
import numpy as np
import moderngl

class Graphics:
    """
    Crea VBO/IBO/VAO para un objeto con atributos:
      - in_pos   : vec3
      - in_color : vec3
    El formato es intercalado: [x,y,z,r,g,b] por vértice.
    """
    def __init__(self, ctx: moderngl.Context, shader, vertices: np.ndarray, indices: np.ndarray):
        self.ctx = ctx
        self.shader = shader  # instancia de ShaderProgram (tiene .program)

        # Buffers
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.ibo = self.ctx.buffer(indices.tobytes())

        # VAO describiendo layout "3f 3f"
        self.vao = self.ctx.vertex_array(
            self.shader.program,
            [
                (self.vbo, "3f 3f", "in_pos", "in_color"),
            ],
            self.ibo,
            index_element_size=4,  # int32
        )

    def render(self):
        self.vao.render(mode=moderngl.TRIANGLES)
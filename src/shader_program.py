from pathlib import Path
from ctypes import c_float, POINTER, cast
import numpy as np
import moderngl
import glm

class ShaderProgram:
    """
    Wrapper mínimo para compilar shaders y subir uniforms.
    """
    def __init__(self, ctx: moderngl.Context, vert_path: Path, frag_path: Path):
        self.ctx = ctx
        vert_src = Path(vert_path).read_text(encoding="utf-8")
        frag_src = Path(frag_path).read_text(encoding="utf-8")
        self.program = self.ctx.program(
            vertex_shader=vert_src,
            fragment_shader=frag_src,
        )

    def set_mat4(self, name: str, mat4_value) -> None:
        """
        Envía un glm.mat4 o np.ndarray(4x4) al uniform `name` en column-major.
        """
        if isinstance(mat4_value, glm.mat4):
            ptr = glm.value_ptr(mat4_value)
            data = cast(ptr, POINTER(c_float * 16)).contents  # 16 floats column-major
            self.program[name].write(bytes(data))
        else:
            arr = np.array(mat4_value, dtype="f4").reshape(4, 4)
            self.program[name].write(arr.flatten(order="F").tobytes())
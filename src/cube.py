# src/cube.py
import numpy as np
import glm
from src.hit import HitBoxOBB

class Cube:
    def __init__(self, name="Cube"):
        self.name = name
        self.vertices = np.array([
            -1,-1,-1, 1,0,0,  1,-1,-1, 0,1,0,  1, 1,-1, 0,0,1, -1, 1,-1, 1,1,0,
            -1,-1, 1, 1,0,1,  1,-1, 1, 0,1,1,  1, 1, 1, 1,1,1, -1, 1, 1, 0,0,0,
        ], dtype='f4')
        self.indices = np.array([
            0,1,2, 2,3,0,  4,5,6, 6,7,4,
            0,4,7, 7,3,0,  1,5,6, 6,2,1,
            3,2,6, 6,7,3,  0,1,5, 5,4,0
        ], dtype='i4')

        self.model = glm.mat4(1.0)
        self.selected = False
        self.collision = HitBoxOBB(get_model_matrix=self.get_model_matrix)

    def get_model_matrix(self) -> glm.mat4:
        return glm.mat4(self.model)

    def set_position(self, x: float, y: float, z: float):
        T = glm.translate(glm.mat4(1.0), glm.vec3(x, y, z))
        self.model = T * self.model

    def rotate_y(self, radians: float):
        self.model = self.model * glm.rotate(glm.mat4(1.0), radians, glm.vec3(0.0, 1.0, 0.0))

    def scale_uniform(self, s: float):
        self.model = self.model * glm.scale(glm.mat4(1.0), glm.vec3(s))

    def check_hit(self, ray_origin, ray_dir):
        """Devuelve t (distancia) o None."""
        return self.collision.check_hit(ray_origin, ray_dir)
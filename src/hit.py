# src/hit.py
from abc import ABC, abstractmethod
import glm
import numpy as np

_EPS = 1e-8

def _safe_div(x):
    return x if abs(x) > _EPS else (_EPS if x >= 0 else -_EPS)

class Hit(ABC):
    def __init__(self, get_model_matrix=None):
        self._get_M = get_model_matrix

    @property
    def model_matrix(self) -> glm.mat4:
        return glm.mat4(self._get_M()) if self._get_M else glm.mat4(1.0)

    @property
    def position(self) -> glm.vec3:
        M = self.model_matrix
        return glm.vec3(M[3].x, M[3].y, M[3].z)

    @property
    def scale(self) -> glm.vec3:
        M = self.model_matrix
        sx = glm.length(glm.vec3(M[0].x, M[0].y, M[0].z))
        sy = glm.length(glm.vec3(M[1].x, M[1].y, M[1].z))
        sz = glm.length(glm.vec3(M[2].x, M[2].y, M[2].z))
        return glm.vec3(sx, sy, sz)

    @abstractmethod
    def check_hit(self, ray_origin, ray_dir):
        """Devuelve t_near (float) si hay impacto, o None si no."""
        ...


class HitBox(Hit):  # AABB en mundo
    def __init__(self, position, scale):
        super().__init__(None)
        self._pos = glm.vec3(position)
        self._scale = glm.vec3(scale)

    def check_hit(self, ray_origin, ray_dir):
        o = glm.vec3(ray_origin)
        d = glm.normalize(glm.vec3(ray_dir))

        half = self._scale * 0.5
        # epsilon para evitar “huecos” por precisión numérica
        half += glm.vec3(1e-4)

        bmin = self._pos - half
        bmax = self._pos + half

        t1 = (bmin - o) / glm.vec3(_safe_div(d.x), _safe_div(d.y), _safe_div(d.z))
        t2 = (bmax - o) / glm.vec3(_safe_div(d.x), _safe_div(d.y), _safe_div(d.z))

        tmin = glm.min(t1, t2)
        tmax = glm.max(t1, t2)

        t_near = max(tmin.x, tmin.y, tmin.z)
        t_far  = min(tmax.x, tmax.y, tmax.z)

        if (t_near <= t_far) and (t_far >= 0.0):
            return max(0.0, float(t_near))
        return None


class HitBoxOBB(Hit):  # OBB: transforma el rayo al espacio local del objeto
    def __init__(self, get_model_matrix):
        super().__init__(get_model_matrix)

    def check_hit(self, ray_origin, ray_dir):
        M = self.model_matrix
        invM = glm.inverse(M)

        o4 = invM * glm.vec4(ray_origin, 1.0)  # punto
        d4 = invM * glm.vec4(ray_dir,    0.0)  # vector
        o = glm.vec3(o4.x, o4.y, o4.z)
        d = glm.normalize(glm.vec3(d4.x, d4.y, d4.z))

        # el cubo local es [-1,1] -> half local = (1,1,1)
        base_half = glm.vec3(1.0)
        half = base_half * self.scale   # NO 0.5
        half += glm.vec3(3e-4)  # o 5e-4 si tu GPU/driver es muy quisquilloso
        bmin = -half
        bmax =  half

        t1 = (bmin - o) / glm.vec3(_safe_div(d.x), _safe_div(d.y), _safe_div(d.z))
        t2 = (bmax - o) / glm.vec3(_safe_div(d.x), _safe_div(d.y), _safe_div(d.z))

        tmin = glm.min(t1, t2)
        tmax = glm.max(t1, t2)

        t_near = max(tmin.x, tmin.y, tmin.z)
        t_far  = min(tmax.x, tmax.y, tmax.z)

        if (t_near <= t_far) and (t_far >= 0.0):
            return max(0.0, float(t_near))
        return None
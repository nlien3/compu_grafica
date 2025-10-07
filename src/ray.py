import glm

class Ray:
    def __init__(self, origin, direction):
        self._o = glm.vec3(origin)
        d = glm.vec3(direction)
        self._d = glm.normalize(d) if glm.length(d) > 0 else glm.vec3(0,0,-1)

    @property
    def origin(self):     return glm.vec3(self._o)
    @property
    def direction(self):  return glm.vec3(self._d)
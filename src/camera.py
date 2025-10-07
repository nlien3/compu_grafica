import glm

class Camera:
    def __init__(self, fov_deg: float = 60.0, aspect: float = 16/9, near: float = 0.1, far: float = 100.0):
        self.fov_deg = fov_deg
        self.aspect = aspect
        self.near = near
        self.far = far
        self.eye = glm.vec3(3.0, 3.0, 3.0)
        self.target = glm.vec3(0.0, 0.0, 0.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)

    @property
    def projection(self) -> glm.mat4:
        return glm.perspective(glm.radians(self.fov_deg), self.aspect, self.near, self.far)

    @property
    def view(self) -> glm.mat4:
        return glm.lookAt(self.eye, self.target, self.up)

    def set_aspect(self, aspect: float):
        self.aspect = max(1e-5, float(aspect))

    # -------- Picking: ray (u,v) -> mundo --------
    def generate_ray(self, u: float, v: float):
        # NDC [-1,1]
        ndc_x = 2.0 * u - 1.0
        ndc_y = 1.0 - 2.0 * v  # pantalla to NDC

        half_tan = glm.tan(glm.radians(self.fov_deg) * 0.5)
        x = ndc_x * half_tan * self.aspect
        y = ndc_y * half_tan
        z = -1.0
        dir_cam = glm.normalize(glm.vec3(x, y, z))

        inv_view = glm.inverse(self.view)
        d4 = inv_view * glm.vec4(dir_cam, 0.0)   # vector → w=0
        dir_world = glm.normalize(glm.vec3(d4.x, d4.y, d4.z))
        origin_world = glm.vec3(self.eye)

        return origin_world, dir_world
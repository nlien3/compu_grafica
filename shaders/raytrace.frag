#version 330

in vec2 v_ndc;
out vec4 f_color;

// ---- Uniforms de cámara ----
uniform mat4 uInvView;    // inversa de la view (para pasar de cam a mundo)
uniform float uFov;       // fov en radianes
uniform float uAspect;    // ancho/alto

// ---- Luz ----
uniform vec3 uLightPos;   // posición de luz en mundo

// ---- Escena simple ----
// esfera
uniform vec3 uSphereCenter; 
uniform float uSphereRadius;
// plano y= y0
uniform float uPlaneY;

// helpers
const float EPS = 1e-4;

struct Hit {
    float t;
    vec3  p;
    vec3  n;
    int   id; // 1 = esfera, 2 = plano
};

bool ray_sphere(vec3 ro, vec3 rd, vec3 c, float r, out float t) {
    vec3 oc = ro - c;
    float b = dot(oc, rd);
    float c2 = dot(oc, oc) - r*r;
    float disc = b*b - c2;
    if (disc < 0.0) return false;
    float s = sqrt(disc);
    float t0 = -b - s;
    float t1 = -b + s;
    t = (t0 > EPS) ? t0 : ((t1 > EPS) ? t1 : -1.0);
    return t > EPS;
}

bool ray_plane_y(vec3 ro, vec3 rd, float y0, out float t) {
    // plano horizontal (0,1,0)·(p - (0,y0,0)) = 0 => rd.y != 0
    if (abs(rd.y) < 1e-6) return false;
    t = (y0 - ro.y) / rd.y;
    return t > EPS;
}

// sombreado lambert + phong
vec3 shade(vec3 p, vec3 n, vec3 albedo, vec3 lightPos, vec3 eye) {
    vec3 L = normalize(lightPos - p);
    vec3 V = normalize(eye - p);
    vec3 H = normalize(L + V);

    float diff = max(dot(n, L), 0.0);
    float spec = pow(max(dot(n, H), 0.0), 50.0);

    vec3 kd = albedo * diff;
    vec3 ks = vec3(0.3) * spec;

    // atenuación por distancia (simple)
    float dist = length(lightPos - p);
    float att = 1.0 / (1.0 + 0.05 * dist * dist);

    return (kd + ks) * att;
}

// (opcional) sombra dura: rayo hacia la luz
bool in_shadow(vec3 p, vec3 lightPos) {
    vec3 ro = p + normalize(lightPos - p) * EPS*4.0;
    vec3 rd = normalize(lightPos - p);

    // esfera
    float t;
    if (ray_sphere(ro, rd, uSphereCenter, uSphereRadius, t)) {
        if (t > 0.0 && t < length(lightPos - p)) return true;
    }
    // plano (como obstáculo): opcional, desactivado por defecto
    // float tp; if (ray_plane_y(ro, rd, uPlaneY, tp)) { ... }

    return false;
}

void main() {
    // 1) construir rayo en espacio de cámara desde NDC
    // v_ndc llega en [-1,1]. Para cámara pinhole:
    float halfTan = tan(uFov * 0.5);
    vec3 dir_cam = normalize(vec3(v_ndc.x * halfTan * uAspect,
                                  v_ndc.y * halfTan,
                                  -1.0));
    // 2) pasar a mundo con invView (vector = w=0)
    vec3 ro = vec3(uInvView[3]);  // origen = eye (col 3 de invView)
    vec3 rd = normalize((uInvView * vec4(dir_cam, 0.0)).xyz);

    // 3) intersectar escena
    Hit best; best.t = 1e20; best.id = 0;

    float t;
    if (ray_sphere(ro, rd, uSphereCenter, uSphereRadius, t) && t < best.t) {
        best.t = t;
        best.p = ro + rd * t;
        best.n = normalize(best.p - uSphereCenter);
        best.id = 1;
    }
    if (ray_plane_y(ro, rd, uPlaneY, t) && t < best.t) {
        best.t = t;
        best.p = ro + rd * t;
        best.n = vec3(0.0, 1.0, 0.0);
        best.id = 2;
    }

    if (best.id == 0) {
        // fondo
        f_color = vec4(0.08, 0.09, 0.12, 1.0);
        return;
    }

    // 4) color por material simple
    vec3 albedo = (best.id == 1) ? vec3(0.9, 0.3, 0.3) : vec3(0.7, 0.7, 0.7);

    // 5) sombra dura (opcional): comentar si no querés sombra
    bool shadow = in_shadow(best.p, uLightPos);

    vec3 c = shade(best.p, best.n, albedo, uLightPos, ro);
    if (shadow) c *= 0.35;

    f_color = vec4(c, 1.0);
}
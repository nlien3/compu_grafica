#version 330

// Quad a pantalla con NDC en [-1,1]
in vec2 in_pos;
out vec2 v_ndc;

void main() {
    v_ndc = in_pos;             // pasamos NDC al fragment
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
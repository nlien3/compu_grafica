#version 330
in vec3 in_pos;
in vec3 in_color;
uniform mat4 Mvp;
out vec3 v_color;
void main(){
    gl_Position = Mvp * vec4(in_pos, 1.0);
    v_color = in_color;
}
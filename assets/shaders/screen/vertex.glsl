#version 330 core

in vec3 in_vertex;
in vec2 in_uv;

out vec2 uv;

void main() {
    gl_Position = vec4(in_vertex, 1);

    uv = in_uv;
}

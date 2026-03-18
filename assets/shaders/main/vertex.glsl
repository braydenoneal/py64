#version 330 core

uniform mat4 camera;

in vec3 in_vertex;
in vec3 in_normal;
in vec2 in_uv;
in vec4 in_color;

out vec3 normal;
out vec2 uv;
out vec4 color;

void main() {
    gl_Position = camera * vec4(in_vertex, 1);

    normal = in_normal;
    uv = in_uv;
    color = in_color;
}

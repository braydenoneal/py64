#version 330 core

uniform mat4 camera;

in vec4 in_vertex;
in vec4 in_color;

out vec4 color;

void main() {
    gl_Position = camera * in_vertex;

    color = in_color;
}

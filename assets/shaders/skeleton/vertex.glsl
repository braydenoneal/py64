#version 330 core

const int MAX_BONES = 100;

uniform mat4 camera;
uniform mat4 bones[MAX_BONES];

in vec4 in_vertex;

void main() {
    vec4 position = bones[int(in_vertex.w)] * vec4(in_vertex.xyz, 1);
    gl_Position = camera * vec4(position.xyz, 1);
}

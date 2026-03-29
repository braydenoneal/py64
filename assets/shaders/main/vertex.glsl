#version 330 core

uniform mat4 camera;
uniform mat4 bones[];

in vec3 in_vertex;
in vec3 in_normal;
in vec2 in_uv;
in vec4 in_color;
in ivec4 in_bone_indices;
in vec4 in_weights;

out vec3 normal;
out vec2 uv;
out vec4 color;

void main() {
    gl_Position = camera * vec4(in_vertex, 1);

    normal = in_normal;
    uv = in_uv;
    color = in_color;

    float stub = in_bone_indices[0] + in_weights[0];
    color.a *= clamp(stub + 1000, 0, 1);
}

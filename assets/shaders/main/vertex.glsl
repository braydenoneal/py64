#version 330 core

const int MAX_BONES = 100;

uniform mat4 camera;
uniform bool animate;
uniform mat4 bones[MAX_BONES];

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
    if (animate) {
        vec4 position = vec4(0);
        vec3 new_normal = vec3(0);

        for (int i = 0; i < 4; i++) {
            int index = in_bone_indices[i];

            if (index == -1) {
                continue;
            }

            position += (bones[index] * vec4(in_vertex, 1)) * in_weights[i];
            new_normal += (mat3(bones[index]) * in_normal) * in_weights[i];
        }

        gl_Position = camera * vec4(position.xyz, 1);
        normal = new_normal;
    } else {
        gl_Position = camera * vec4(in_vertex, 1);
        normal = in_normal;
    }

    uv = in_uv;
    color = in_color;
}

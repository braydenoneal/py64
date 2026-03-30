#version 330 core

const int MAX_BONES = 2;

uniform mat4 camera;
uniform mat4 bones[MAX_BONES];

in vec3 in_vertex;
in vec3 in_normal;
in ivec4 in_bone_indices;
in vec4 in_weights;

out vec3 normal;

void main() {
    vec4 position = vec4(0);

    for (int i = 0; i < 4; i++) {
        int index = in_bone_indices[i];

        if (index == -1) {
            continue;
        }

        position += (bones[index] * vec4(in_vertex, 1)) * in_weights[i];
    }

    gl_Position = camera * vec4(position.xyz, 1);

    normal = in_normal;
}

#version 330 core

uniform vec3 light;

in vec3 normal;

out vec4 out_color;

void main() {
    out_color = vec4(0.75, 0.75, 0.75, 1);

    float luminance = dot(normalize(normal), normalize(light));
    out_color.rgb *= max(luminance, 0.0) * 0.5 + 0.5;
}

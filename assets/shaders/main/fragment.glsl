#version 330 core

uniform vec3 light;
uniform sampler2D Texture;
uniform ivec2 bounds;

in vec3 normal;
in vec2 uv;
in vec4 color;

out vec4 out_color;

void main() {
    float u = uv.x;

    if (bounds.x == 1) {
        u = clamp(u, 0, 1);
    } else if (bounds.x == 3) {
        u = mod(u, 2);

        if (u > 1) {
            u = 2 - u;
        }
    }

    float v = uv.y;

    if (bounds.y == 1) {
        v = clamp(v, 0, 1);
    } else if (bounds.y == 3) {
        v = mod(v, 2);

        if (v > 1) {
            v = 2 - v;
        }
    }

    out_color = texture(Texture, vec2(u, v));

    if (bounds.x == 2 && (u < 0 || u > 1 || v < 0 || v > 1)) {
        out_color.rgb *= 0;
    }

    float lum = dot(normalize(normal), normalize(light));
    out_color.rgb *= max(lum, 0.0) * 0.5 + 0.5;

    out_color.rgb *= color;
}

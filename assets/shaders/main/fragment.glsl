#version 330 core

uniform vec3 light;
uniform sampler2D Texture;
uniform ivec2 bounds;
uniform vec3 overlay_color;

in vec3 normal;
in vec2 uv;
in vec4 color;

out vec4 out_color;

float wrap(float value, int bound) {
    float out_value = value;

    if (bound == 1) {
        out_value = clamp(out_value, 0, 1);
    } else if (bound == 3) {
        out_value = mod(out_value, 2);

        if (out_value > 1) {
            out_value = 2 - out_value;
        }
    }

    return out_value;
}

vec2 wrap_uv(vec2 uv) {
    return vec2(wrap(uv.x, bounds.x), wrap(uv.y, bounds.y));
}

vec4 filter_texture(sampler2D sampler, vec2 uv) {
    // From https://www.shadertoy.com/view/w3tcWM by Offline
    vec2 texture_size = vec2(textureSize(sampler, 0));
    vec2 pixel_size = 1.0 / texture_size;
    vec2 pixel_position = fract(uv * texture_size);

    float side = step(0.0, pixel_position.x - pixel_position.y);
    vec2 offset = vec2(side, 1.0 - side) * pixel_size;

    return
    texture(sampler, wrap_uv(uv)) * (1.0 - max(pixel_position.x, pixel_position.y)) +
    texture(sampler, wrap_uv(uv + pixel_size)) * min(pixel_position.x, pixel_position.y) +
    texture(sampler, wrap_uv(uv + offset)) * abs(pixel_position.x - pixel_position.y);
}

void main() {
    out_color = filter_texture(Texture, uv);

    float luminance = dot(normalize(normal), normalize(light));
    out_color.rgb *= max(luminance, 0.0) * 0.5 + 0.5;

    out_color.rgba *= color;
    out_color.rgb *= overlay_color;
}

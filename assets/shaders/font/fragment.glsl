#version 330 core

uniform sampler2D font_texture;

in vec2 uv;

out vec4 out_color;

vec4 filter_texture(sampler2D sampler, vec2 uv) {
    // From https://www.shadertoy.com/view/w3tcWM by Offline
    vec2 texture_size = vec2(textureSize(sampler, 0));
    vec2 pixel_size = 1.0 / texture_size;
    vec2 pixel_position = fract(uv * texture_size);

    float side = step(0.0, pixel_position.x - pixel_position.y);
    vec2 offset = vec2(side, 1.0 - side) * pixel_size;

    vec4 color_a = texture(sampler, uv);
    vec4 color_b = texture(sampler, uv + pixel_size);
    vec4 color_c = texture(sampler, uv + offset);

    return color_a * (1.0 - max(pixel_position.x, pixel_position.y)) +
    color_b * min(pixel_position.x, pixel_position.y) +
    color_c * abs(pixel_position.x - pixel_position.y);
}

void main() {
    out_color = filter_texture(font_texture, uv);
}

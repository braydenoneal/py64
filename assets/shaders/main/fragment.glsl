#version 330 core

uniform vec3 light;
uniform vec2 screen_size;
uniform int pass;

uniform vec3 solid_color;

uniform sampler2D texture_a;
uniform bool use_texture_a;
uniform ivec2 bounds_a;
uniform vec2 texture_a_scale;

uniform sampler2D texture_b;
uniform bool use_texture_b;
uniform ivec2 bounds_b;
uniform vec2 texture_b_scale;
uniform float texture_b_mix;

uniform vec3 overlay_color;

uniform float translucency;
uniform int transparency_mode;

uniform sampler2D depth_texture0;
uniform sampler2D depth_texture1;

in vec3 normal;
in vec2 uv;
in vec4 color;

out vec4 out_color;
out float out_depth;

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

vec2 wrap_uv(vec2 uv, ivec2 bounds) {
    return vec2(wrap(uv.x, bounds.x), wrap(uv.y, bounds.y));
}

vec4 clip_color(float value, int bound, vec4 color) {
    if (bound == 2 && (value < 0 || value > 1)) {
        return vec4(0);
    }

    return color;
}

vec4 clip_color(vec2 uv, ivec2 bounds, vec4 color) {
    return clip_color(uv.x, bounds.x, clip_color(uv.y, bounds.y, color));
}

vec4 filter_texture(sampler2D sampler, vec2 uv, ivec2 bounds) {
    // From https://www.shadertoy.com/view/w3tcWM by Offline
    vec2 texture_size = vec2(textureSize(sampler, 0));
    vec2 pixel_size = 1.0 / texture_size;
    vec2 pixel_position = fract(uv * texture_size);

    float side = step(0.0, 1.0 - pixel_position.x - pixel_position.y);
    vec2 offset = vec2(-side, 1.0 - side) * pixel_size;

    vec2 uv_a = wrap_uv(uv, bounds);
    vec2 uv_b = wrap_uv(uv + vec2(-pixel_size.x, pixel_size.y), bounds);
    vec2 uv_c = wrap_uv(uv + offset, bounds);

    vec4 color_a = clip_color(uv_a, bounds, texture(sampler, uv_a));
    vec4 color_b = clip_color(uv_b, bounds, texture(sampler, uv_b));
    vec4 color_c = clip_color(uv_c, bounds, texture(sampler, uv_c));

    return
    color_a * (1.0 - max(1.0 - pixel_position.x, pixel_position.y)) +
    color_b * min(1.0 - pixel_position.x, pixel_position.y) +
    color_c * abs(1.0 - pixel_position.x - pixel_position.y);
}

void main() {
    if (use_texture_a) {
        out_color = filter_texture(texture_a, uv / texture_a_scale, bounds_a);
    } else {
        out_color = vec4(solid_color, 1);
    }

    if (use_texture_b) {
        out_color = mix(out_color, filter_texture(texture_b, uv / texture_b_scale, bounds_b), texture_b_mix);
    }

    float luminance = dot(normalize(normal), normalize(light));
    out_color.rgb *= max(luminance, 0.0) * 0.5 + 0.5;

    out_color.rgba *= color;
    out_color.rgb *= overlay_color;
    out_color.a *= 1.0 - translucency;

    if (transparency_mode == 1) {
        out_color.a = round(out_color.a);
    }

    float d = 1.0 - (gl_FragCoord.z / gl_FragCoord.w / 1000.0);

    if (pass == 0) {
        out_depth = d;
    } else if (pass == 1) {
        out_depth = d;

        if (d < texture(depth_texture0, gl_FragCoord.xy / screen_size).r) {
            discard;
        }
    } else if (pass == 2) {
        out_depth = d;

        if (d < texture(depth_texture0, gl_FragCoord.xy / screen_size).r ||
        d > texture(depth_texture1, gl_FragCoord.xy / screen_size).r
        ) {
            discard;
        }
    }
}

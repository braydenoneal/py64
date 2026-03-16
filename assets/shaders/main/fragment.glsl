#version 330 core

uniform vec3 light;
uniform sampler2D Texture;
uniform ivec2 bounds;

in vec3 normal;
in vec2 uv;
in vec4 color;

out vec4 out_color;

vec4 textureN64(sampler2D tex, vec2 uv2)
{
    vec2 texSize = vec2(textureSize(tex, 0));
    vec2 texelSize = 1. / texSize;
    vec2 texelUV = fract(uv2 * texSize);

    // Round texture UV coordinate to the center of a pixel. (It can lead to cracks/mipping errors)
    // This can be omitted if nearest texture filtering is used.
    // uv2 = floor(uv2 * texSize) / texSize + texelSize * .5;

    // Masks for the three samples that we'll blend together.
    vec3 mask = vec3(
    1. - max(texelUV.x, texelUV.y),
    min(texelUV.x, texelUV.y),
    abs(texelUV.x - texelUV.y)
    );

    // Offset sample depending on which side of the triangle we're shading.
    float side = step(.0, texelUV.x - texelUV.y);
    vec2 offset = vec2(side, 1. - side) * texelSize;

    float u = uv2.x;

    //    if (bounds.x == 1) {
    //        u = clamp(u, 0, 1);
    //    } else if (bounds.x == 3) {
    //        u = mod(u, 2);

    //        if (u > 1) {
    //            u = 2 - u;
    //        }
    //    }

    float v = uv2.y;

    //    if (bounds.y == 1) {
    //        v = clamp(v, 0, 1);
    //    } else if (bounds.y == 3) {
    //        v = mod(v, 2);
    //
    //        if (v > 1) {
    //            v = 2 - v;
    //        }
    //    }

    vec2 uv21 = vec2(u, v);

    u = uv2.x + texelSize.x;

    //    if (bounds.x == 1) {
    //        u = clamp(u, 0, 1);
    //    } else if (bounds.x == 3) {
    //        u = mod(u, 2);

    //        if (u > 1) {
    //            u = 2 - u;
    //        }
    //    }

    v = uv2.y + texelSize.y;

    //    if (bounds.y == 1) {
    //        v = clamp(v, 0, 1);
    //    } else if (bounds.y == 3) {
    //        v = mod(v, 2);

    //        if (v > 1) {
    //            v = 2 - v;
    //        }
    //    }

    vec2 uv22 = vec2(u, v);

    uv2 = vec2(u, v);

    u = uv2.x + offset.x;

    //    if (bounds.x == 1) {
    //        u = clamp(u, 0, 1);
    //    } else if (bounds.x == 3) {
    //        u = mod(u, 2);

    //        if (u > 1) {
    //            u = 2 - u;
    //        }
    //    }

    v = uv2.y + offset.y;

    //    if (bounds.y == 1) {
    //        v = clamp(v, 0, 1);
    //    } else if (bounds.y == 3) {
    //        v = mod(v, 2);
    //
    //        if (v > 1) {
    //            v = 2 - v;
    //        }
    //    }

    vec2 uv23 = vec2(u, v);

    vec4 col = texture(tex, uv2) * mask.x +
    texture(tex, uv22) * mask.y +
    texture(tex, uv23) * mask.z;

    if (bounds.x == 2 && (u < 0 || u > 1 || v < 0 || v > 1)) {
        col.rgb *= 0;
    }

    return col;
}

void main() {
    //    out_color = texture(Texture, vec2(u, v));
    out_color = textureN64(Texture, uv);

    float lum = dot(normalize(normal), normalize(light));
    out_color.rgb *= max(lum, 0.0) * 0.5 + 0.5;

    out_color.rgba *= color;
}

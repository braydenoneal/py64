#version 330 core

uniform sampler2D in_texture_0;
uniform sampler2D in_texture_1;
uniform sampler2D in_texture_2;
uniform sampler2D in_texture_3;
uniform sampler2D in_texture_4;

in vec2 uv;

out vec4 out_color;

void main() {
    vec4 c0 = texture(in_texture_0, uv);
    vec4 c1 = texture(in_texture_1, uv);
    vec4 c2 = texture(in_texture_2, uv);
    vec4 c3 = texture(in_texture_3, uv);
    vec4 c4 = texture(in_texture_4, uv);

    vec3 color = c1.rgb * c1.a + (1.0 - c1.a) * (c2.rgb * c2.a + (1.0 - c2.a) * (c3.rgb * c3.a + (1.0-c3.a) * (c4.rgb * c4.a + (1.0 - c4.a) * c0.rgb)));
    out_color = vec4(color, 1);
}

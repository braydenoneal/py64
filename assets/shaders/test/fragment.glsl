#version 330 core

uniform sampler2D in_texture;

in vec2 uv;

out vec4 out_color;

void main() {
    out_color = texture(in_texture, uv);
}

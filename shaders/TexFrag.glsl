#version 330 core
out vec4 FragColour;

in vec3 ourColour;
in vec2 TexCoord;

uniform sampler2D texture1;
uniform sampler2D texture2;

void main() {
    FragColour = mix(texture(texture1, TexCoord), texture(texture2, vec2(1.0-TexCoord.x, TexCoord.y)), 0.2) * vec4(ourColour, 1.0);
}
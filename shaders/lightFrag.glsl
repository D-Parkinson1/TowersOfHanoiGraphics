#version 330 core
out vec4 FragColour;

uniform vec3 objectColour;
uniform vec3 lightColour;

void main() {
    FragColour = vec4(objectColour * lightColour, 1.0);
}
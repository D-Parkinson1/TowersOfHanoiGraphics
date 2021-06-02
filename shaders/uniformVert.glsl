#version 330 core
layout (location = 0) in vec3 aPos;   // the position variable has attribute position 0
layout (location = 1) in vec3 aColour; // the colour variable has attribute position 1
  
out vec3 ourColour; // output a colour to the fragment shader

void main() {
    gl_Position = vec4(aPos, 1.0);
    ourColour = aColour; // set ourColor to the input colour we got from the vertex data
}   
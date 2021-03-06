#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texCoord;
layout (location = 3) in vec3 tangent;
layout (location = 4) in vec3 bitangent;

out VertexData {
	vec3 v2f_viewSpaceNormal;
	vec2 v2f_texCoord;
};

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat3 normalMat;

//uniform mat3 modelToViewNormalTransform;

void main() 
{
	gl_Position = projection * view * model * vec4(position, 1.0);

	v2f_viewSpaceNormal = normalize(normalMat * normal);

	v2f_texCoord = texCoord;
}
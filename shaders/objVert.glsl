#version 330 core
layout (location = 0) in vec3 aPosition;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;
layout (location = 3) in vec3 aTangent;
layout (location = 4) in vec3 aBitangent;

uniform mat4 modelToClipTransform;
uniform mat4 modelToViewTransform;
uniform mat3 modelToViewNormalTransform;

// For a pixel shader the variable is interpolated (the type of interpolation can be modified, try placing 'flat' in front, and also in the fragment shader!).
out VertexData
{
	vec3 v2f_viewSpaceNormal;
	vec2 v2f_texCoord;
};

void main() 
{
	gl_Position = modelToClipTransform * vec4(positionAttribute, 1.0);
    
	// We transform the normal to view space using the normal transform (which is the inverse-transpose of the rotation part of the modelToViewTransform)
    // Just using the rotation is only valid if the matrix contains only rotation and uniform scaling.
	v2f_viewSpaceNormal = normalize(modelToViewNormalTransform * normalAttribute);

	v2f_texCoord = texCoordAttribute;
}
#version 330 core

in VertexData
{
	vec3 v2f_viewSpaceNormal;
	vec2 v2f_texCoord;
};

// Material properties uniform buffer, required by OBJModel.
// 'MaterialProperties' must be bound to a uniform buffer, OBJModel::setDefaultUniformBindings is of help!

struct Material {
    vec3 diffuse_color;
    float alpha;
    vec3 specular_color;
    vec3 emissive_color;
    float specular_exponent;
};

uniform Material material;


// Textures set by OBJModel (names must be bound to the right texture unit, OBJModel::setDefaultUniformBindings helps with that.
uniform sampler2D diffuse_texture;
uniform sampler2D opacity_texture;
uniform sampler2D specular_texture;
uniform sampler2D normal_texture;

// Other uniforms used by the shader
uniform vec3 viewSpaceLightDirection;

out vec4 fragmentColor;

// If we do not convert the colour to srgb before writing it out it looks terrible! All our lighting is done in linear space
// (which it should be!), and the frame buffer is srgb by default. So we must convert, or somehow create a linear frame buffer...
vec3 toSrgb(vec3 color) {
  return pow(color, vec3(1.0 / 2.2));
}

void main() {
	// Manual alpha test (note: alpha test is no longer part of Opengl 3.3).
	if (texture(opacity_texture, v2f_texCoord).r < 0.5)
	{
		discard;
	}

	vec3 materialDiffuse = texture(diffuse_texture, v2f_texCoord).xyz * material.diffuse_color;
	vec3 color = materialDiffuse * (0.1 + 0.9 * max(0.0, dot(v2f_viewSpaceNormal, -viewSpaceLightDirection))) + material.emissive_color;
	fragmentColor = vec4(1.0);//vec4(toSrgb(color), material.alpha);
}
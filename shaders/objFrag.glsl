#version 330 core

in VertexData
{
	vec3 v2f_viewSpaceNormal;
	vec2 v2f_texCoord;
};

// Material properties uniform buffer, required by OBJModel.
struct Material {
    vec3 diffuse_colour;
    float alpha;
    vec3 specular_colour;
    vec3 emissive_colour;
    float specular_exponent;
};

// Textures set by OBJModel (names must be bound to the right texture unit, OBJModel::setDefaultUniformBindings helps with that.
uniform sampler2D diffuse_texture;
uniform sampler2D opacity_texture;
uniform sampler2D specular_texture;
uniform sampler2D normal_texture;

// Other uniforms used by the shader
uniform vec3 viewSpaceLightDirection;
uniform Material material;

out vec4 fragmentcolour;

// If we do not convert the colour to srgb before writing it out it looks terrible! All our lighting is done in linear space
// (which it should be!), and the frame buffer is srgb by default. So we must convert, or somehow create a linear frame buffer...
vec3 toSrgb(vec3 colour) {
  return pow(colour, vec3(1.0 / 2.2));
}

void main() {
	// Manual alpha test (note: alpha test is no longer part of Opengl 3.3).
	if (texture(opacity_texture, v2f_texCoord).r < 0.5)
	{
		discard;
	}

	vec3 materialDiffuse = texture(diffuse_texture, v2f_texCoord).xyz * material.diffuse_colour;
	vec3 colour = materialDiffuse * (0.1 + 0.9 * max(0.0, dot(v2f_viewSpaceNormal, -viewSpaceLightDirection))) + material.emissive_colour;
	fragmentcolour = vec4(toSrgb(colour), material.alpha);
}
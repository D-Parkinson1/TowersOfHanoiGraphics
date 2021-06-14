#version 330 core

struct Material {
    vec3 diffuse_colour;
    vec3 specular_colour;
    vec3 emissive_colour;
    float specular_exponent;
    sampler2D diffuse_texture;
    sampler2D opacity_texture;
    sampler2D specular_texture;
    sampler2D normal_texture;
    float alpha;
};

struct DirLight {
    vec3 direction;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct PointLight {
    vec3 position;

    float constant;
    float linear;
    float quadratic;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};


struct SpotLight {
    vec3 position;
    vec3 direction;
    float cutOff;
    float outerCutOff;
    
    int on;
    
    float constant;
    float linear;
    float quadratic;
  
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;       
};


vec3 calcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir); 
vec3 calcSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir);
vec3 calcDirLight(DirLight light, vec3 normal, vec3 viewDir);
vec3 toSrgb(vec3 colour);

out vec4 FragColour;

in vec3 Normal;
in vec3 FragPos;
in vec2 TexCoords;


#define NR_POINT_LIGHTS 4
uniform PointLight pointLights[NR_POINT_LIGHTS];
uniform SpotLight spotLight;
uniform DirLight dirLight;

uniform vec3 viewPos;
uniform Material material;



void main() {
    //if (texture(material.opacity_texture, TexCoords).r < 0.5)	{
	//	discard;
	//}

    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    // Directional lighting
    vec3 result = calcDirLight(dirLight, norm, viewDir);

    // Point Lights
    for(int i = 0; i < NR_POINT_LIGHTS; i++) {
        result += calcPointLight(pointLights[i], norm, FragPos, viewDir);
    }
    result += calcSpotLight(spotLight, norm, FragPos, viewDir);

    // Depth display FragColour = vec4(vec3(gl_FragCoord.z), 1.0);//vec4(result, 1.0);
    FragColour = vec4(toSrgb(result), 1.0);
}

// If we do not convert the colour to srgb before writing it out it looks terrible! All our lighting is done in linear space
// (which it should be!), and the frame buffer is srgb by default. So we must convert, or somehow create a linear frame buffer...
vec3 toSrgb(vec3 colour) {
  return pow(colour, vec3(1.0 / 2.2));
}

vec3 calcDirLight(DirLight light, vec3 normal, vec3 viewDir) {
    vec3 lightDir = normalize(-light.direction);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.specular_exponent);
    vec3 ambient = light.ambient * vec3(texture(material.diffuse_texture, TexCoords))  * material.diffuse_colour;
    vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse_texture, TexCoords)) * material.diffuse_colour;
    vec3 specular = light.specular * spec * vec3(texture(material.specular_texture, TexCoords))  * material.diffuse_colour;
    return ambient + diffuse + specular;
}

vec3 calcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);
    // diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);
    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.specular_exponent);
    // attenuation
    float distance    = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + 
  			     light.quadratic * (distance * distance));    
    // combine results
    vec3 ambient  = light.ambient  * vec3(texture(material.diffuse_texture, TexCoords));
    vec3 diffuse  = light.diffuse  * diff * vec3(texture(material.diffuse_texture, TexCoords));
    vec3 specular = light.specular * spec * vec3(texture(material.specular_texture, TexCoords));
    ambient  *= attenuation;
    diffuse  *= attenuation;
    specular *= attenuation;
    return (ambient + diffuse + specular);
} 

// calculates the color when using a spot light.
vec3 calcSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);
    // diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);
    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.specular_exponent);
    // attenuation
    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));   
    // spotlight intensity
    float theta = dot(lightDir, normalize(-light.direction)); 
    float epsilon = light.cutOff - light.outerCutOff;
    float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);
    // combine results
    vec3 ambient = light.ambient * vec3(texture(material.diffuse_texture, TexCoords));
    vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse_texture, TexCoords));
    vec3 specular = light.specular * spec * vec3(texture(material.specular_texture, TexCoords));
    ambient *= attenuation * intensity;
    diffuse *= attenuation * intensity;
    specular *= attenuation * intensity;
    return (ambient + diffuse + specular) * light.on;
}
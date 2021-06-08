from Texture import Texture
from Shader import Shader
from OpenGL.GL import *
import os
from PIL import Image
from ctypes import sizeof, c_float
import magic
from lab_utils import Mat3, Mat4, inverse, make_scale, make_translation, transpose, vec3
import numpy as np


def flatten(*lll):
    return [u for ll in lll for l in ll for u in l]


def bindTexture(texUnit, texture, defaultTexture):
    glActiveTexture(GL_TEXTURE0 + texUnit)
    glBindTexture(GL_TEXTURE_2D, texture.id if texture != -1 else defaultTexture.id)


class ObjModel:
    RF_Transparent = 1
    RF_AlphaTested = 2
    RF_Opaque = 4
    RF_All = RF_Opaque | RF_AlphaTested | RF_Transparent

    AA_Position = 0
    AA_Normal = 1
    AA_TexCoord = 2
    AA_Tangent = 3
    AA_Bitangent = 4

    TU_Diffuse = 0
    TU_Opacity = 1
    TU_Specular = 2
    TU_Normal = 3
    TU_Max = 4

    texturesByName = {}
    texturesById = {}

    def __init__(self, fileName, shader=None, scale: vec3 = None):
        # Create default textures
        self.defaultTextureOne = Texture()
        self.defaultNormalTexture = Texture(mapType="normal")

        self.overrideDiffuseTextureWithDefault = False
        self.children = []
        self.load(fileName)

        if shader:
            self.shader = shader
        else:
            self.shader = Shader(vertFile="shaders/vertex.glsl", fragFile='shaders/fragment.glsl')

        self.position = vec3(0.0)
        if scale:
            if (isinstance(scale, int) or isinstance(scale, float)):
                self.scale = make_scale(scale)
            else:
                self.scale = make_scale(*scale)
        else:
            self.scale = make_scale(1.0)

    def addChild(self, object):
        object.position += self.position
        self.children.append(object)

    def load(self, fileName):
        basePath, _ = os.path.split(fileName)
        with open(fileName, "r") as inFile:
            self.loadObj(inFile.readlines(), basePath)

    def loadObj(self, objLines, basePath):
        positions = []
        normals = []
        uvs = []
        materialChunks = []
        materials = {}

        for l in objLines:
            # 1 standardize line
            if len(l) > 0 and l[:1] != "#":
                tokens = l.split()
                if len(tokens):
                    if tokens[0] == "mtllib":
                        assert len(tokens) >= 2
                        materialName = " ".join(tokens[1:])
                        materials = self.loadMaterials(os.path.join(basePath, materialName), basePath)
                    if tokens[0] == "usemtl":
                        assert len(tokens) >= 2
                        materialName = " ".join(tokens[1:])
                        if len(materialChunks) == 0 or materialChunks[-1][0] != materialName:
                            materialChunks.append([materialName, []])
                    elif tokens[0] == "v":
                        assert len(tokens[1:]) >= 3
                        positions.append([float(v) for v in tokens[1:4]])
                    elif tokens[0] == "vn":
                        assert len(tokens[1:]) >= 3
                        normals.append([float(v) for v in tokens[1:4]])
                    elif tokens[0] == "vt":
                        assert len(tokens[1:]) >= 2
                        uvs.append([float(v) for v in tokens[1:3]])
                    elif tokens[0] == "f":
                        materialChunks[-1][1] += self.parseFace(tokens[1:])
        self.numVerts = 0
        for mc in materialChunks:
            self.numVerts += len(mc[1])

        self.positions = [None]*self.numVerts
        self.normals = [None]*self.numVerts
        self.uvs = [[0.0, 0.0]]*self.numVerts
        self.tangents = [[0.0, 1.0, 0.0]]*self.numVerts
        self.bitangents = [[1.0, 0.0, 0.0]]*self.numVerts
        self.chunks = []

        start = 0
        end = 0
        self.materials = materials
        for matId, tris in materialChunks:
            material = materials[matId]
            renderFlags = 0
            if material["alpha"] != 1.0:
                renderFlags |= self.RF_Transparent
            elif material["texture"]["opacity"] != -1:
                renderFlags |= self.RF_AlphaTested
            else:
                renderFlags |= self.RF_Opaque
            start = end
            end = start + int(len(tris)/3)

            chunkOffset = start * 3
            chunkCount = len(tris)

            # De-index mesh and (TODO) compute tangent frame
            for k in range(0, len(tris), 3):
                for j in [0, 1, 2]:
                    p = positions[tris[k + j][0]]
                    oo = chunkOffset + k + j
                    self.positions[oo] = p
                    if tris[k + j][1] != -1:
                        self.uvs[oo] = uvs[tris[k + j][1]]
                    self.normals[oo] = normals[tris[k + j][2]]
            self.chunks.append((material, chunkOffset, chunkCount, renderFlags))

        self.vertexArrayObject = glGenVertexArrays(1)
        glBindVertexArray(self.vertexArrayObject)

        def createBindVertexAttribArrayFloat(data, attribLoc):
            bufId = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, bufId)
            flatData = flatten(data)
            data_buffer = (c_float * len(flatData))(*flatData)
            glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)
            glVertexAttribPointer(attribLoc, int(len(flatData) / len(data)), GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(attribLoc)
            return bufId

        # 3 pos, 3 norm, 2 tex, 3 tangent, 3 bitangent
        self.positionBuffer = createBindVertexAttribArrayFloat(self.positions, self.AA_Position)
        self.normalBuffer = createBindVertexAttribArrayFloat(self.normals, self.AA_Normal)
        self.uvBuffer = createBindVertexAttribArrayFloat(self.uvs, self.AA_TexCoord)
        self.tangentBuffer = createBindVertexAttribArrayFloat(self.tangents, self.AA_Tangent)
        self.biTangentBuffer = createBindVertexAttribArrayFloat(self.bitangents, self.AA_Bitangent)

        npPos = np.array(positions)
        self.aabbMin = npPos.min(0)
        self.aabbMax = npPos.max(0)
        self.centre = (self.aabbMin + self.aabbMax) * 0.5
        self.height = round(self.aabbMax[1], 1)
        self.position = vec3(*self.centre)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def parseFloats(self, tokens, minNum):
        assert len(tokens) >= minNum
        return [float(v) for v in tokens[0:minNum]]

    def parseFaceIndexSet(self, s):
        inds = s.split('/')
        assert len(inds) == 3
        return [int(ind) - 1 if ind != '' else -1 for ind in inds]

    def parseFace(self, tokens):
        assert len(tokens) >= 3
        result = []
        v0 = self.parseFaceIndexSet(tokens[0])
        v1 = self.parseFaceIndexSet(tokens[1])
        for t in tokens[2:]:
            v2 = self.parseFaceIndexSet(t)
            result += [v0, v1, v2]
            v1 = v2
        return result

    def loadMaterials(self, materialFileName, basePath):
        materials = {}
        with open(materialFileName, "r") as inFile:
            currentMaterial = ""
            for l in inFile.readlines():
                tokens = l.split()
                if len(tokens):
                    if tokens[0] == "newmtl":
                        assert len(tokens) >= 2
                        currentMaterial = " ".join(tokens[1:])
                        materials[currentMaterial] = {
                            "color": {
                                "diffuse": [0.5, 0.5, 0.5],
                                "ambient": [0.5, 0.5, 0.5],
                                "specular": [0.5, 0.5, 0.5],
                                "emissive": [0.0, 0.0, 0.0]
                            },
                            "texture": {
                                "diffuse": -1,
                                "opacity": -1,
                                "specular": -1,
                                "normal": -1,
                            },
                            "alpha": 1.0,
                            "specularExponent": 22.0,
                            "offset": 0,
                        }
                    elif tokens[0] == "Ka":
                        materials[currentMaterial]["color"]["ambient"] = self.parseFloats(tokens[1:], 3)
                    elif tokens[0] == "Ns":
                        materials[currentMaterial]["specularExponent"] = float(tokens[1])
                    # elif tokens[0] == "Ni":
                    #     #Optical density - NOT USED ATM
                    #     materials[currentMaterial]["specularExponent"] = float(tokens[1])
                    elif tokens[0] == "Kd":
                        materials[currentMaterial]["color"]["diffuse"] = self.parseFloats(tokens[1:], 3)
                    elif tokens[0] == "Ks":
                        materials[currentMaterial]["color"]["specular"] = self.parseFloats(tokens[1:], 3)
                    elif tokens[0] == "Ke":
                        materials[currentMaterial]["color"]["emissive"] = self.parseFloats(tokens[1:], 3)
                    elif tokens[0] == "map_Kd":
                        materials[currentMaterial]["texture"]["diffuse"] = self.loadTexture(
                            " ".join(tokens[1:]), basePath, True)
                    elif tokens[0] == "map_Ks":
                        materials[currentMaterial]["texture"]["specular"] = self.loadTexture(
                            " ".join(tokens[1:]), basePath, True)
                    elif tokens[0] == "map_bump" or tokens[0] == "bump":
                        materials[currentMaterial]["texture"]["normal"] = self.loadTexture(
                            " ".join(tokens[1:]), basePath, False)
                    elif tokens[0] == "map_d":
                        materials[currentMaterial]["texture"]["opacity"] = self.loadTexture(
                            " ".join(tokens[1:]), basePath, False)
                    elif tokens[0] == "d":
                        materials[currentMaterial]["alpha"] = float(tokens[1])

        # check of there is a colour texture but the coour is zero and then change it to 1, Maya exporter does this to us...
        for id, m in materials.items():
            for ch in ["diffuse", "specular"]:
                if m["texture"][ch] != -1 and sum(m["color"][ch]) == 0.0:
                    m["color"][ch] = [1, 1, 1]
                if m["texture"][ch] != -1 and sum(m["color"][ch]) == 0.0:
                    m["color"][ch] = [1, 1, 1]
        return materials

    def loadTexture(self, fileName, basePath, srgb):
        fullFileName = os.path.join(basePath, fileName)
        try:
            texture = Texture(fullFileName, srgb=srgb)
            texId = texture.id

            self.texturesByName[fileName.lower()] = texture
            self.texturesById[texId] = fileName.lower()
            return texture
        except Exception as e:
            print("WARNING: FAILED to load texture '%s'" % fileName)
            print(e)

        return -1

    def updateMaterials(self):
        newChunks = []
        for material, chunkOffset, chunkCount, renderFlags in self.chunks:
            renderFlags = 0
            if material["alpha"] != 1.0:
                renderFlags |= self.RF_Transparent
            elif material["texture"]["opacity"] != -1:
                renderFlags |= self.RF_AlphaTested
            else:
                renderFlags |= self.RF_Opaque
            newChunks.append((material, chunkOffset, chunkCount, renderFlags))
        self.chunks = newChunks

    def render(self, renderFlags=None, transforms={}):
        if not renderFlags:
            renderFlags = self.RF_All

        # Filter chunks based of render flags
        chunks = [ch for ch in self.chunks if ch[3] & renderFlags]

        # if transforms.get("parentPos") is None:
        #     model = Mat4()
        # else:
        #     model = transforms.get("parentPos")

        #     print(model.getData())
        parentModel = transforms.get("parentModel", Mat4())
        model = parentModel * make_translation(*self.position) * self.scale

        # define defaults (identity)
        defaultTfms = {
            "model": model,
            "view": Mat4(),
            "normalMat": Mat3(transpose(inverse(model))),
            "projection": Mat4()
        }

        # overwrite defaults
        defaultTfms.update(transforms)

        for child in self.children:
            transforms.update({"parentModel": model})
            child.render(transforms=transforms)

        # Bind after children rendered
        glBindVertexArray(self.vertexArrayObject)
        self.shader.use()

        # upload map of transforms
        for tfmName, tfm in defaultTfms.items():
            self.shader.setUniform(tfmName, tfm)
            # assert magic.getUniformLocationDebug(self.shader.program, tfmName) != -1

        previousMaterial = None
        for material, chunkOffset, chunkCount, renderFlags in chunks:

            # as an optimization we only do this if the material has changed between chunks.
            # for more efficiency still consider sorting chunks based on material (or fusing them?)
            if material != previousMaterial:
                previousMaterial = material
                if self.overrideDiffuseTextureWithDefault:
                    bindTexture(self.TU_Diffuse, self.defaultTextureOne, self.defaultTextureOne)
                else:
                    bindTexture(self.TU_Diffuse, material["texture"]["diffuse"], self.defaultTextureOne)
                bindTexture(self.TU_Opacity, material["texture"]["opacity"], self.defaultTextureOne)
                bindTexture(self.TU_Specular, material["texture"]["specular"], self.defaultTextureOne)
                bindTexture(self.TU_Normal, material["texture"]["normal"], self.defaultNormalTexture)
                # TODO: can I do uniform buffers from python (yes, I need to use that struct thingo!)
                # uint32_t matUniformSize = sizeof(MaterialProperties_Std140);
                # glBindBufferRange(GL_UNIFORM_BUFFER, UBS_MaterialProperties, m_materialPropertiesBuffer, (uint32_t)chunk.material->offset * matUniformSize, matUniformSize);
                # TODO: this is very slow, it should be packed into an uniform buffer as per above!
                for k, v in material["color"].items():
                    # setting value so slightly different to set Uniform use
                    glUniform3fv(magic.getUniformLocationDebug(self.shader.program, "material_%s_color" % k), 1, v)
                # glUniform1f(magic.getUniformLocationDebug(shaderProgram,
                #                                           "material_specular_exponent"), material["specularExponent"])
                self.shader.setUniform("material.shininess", material["specularExponent"])
                # glUniform1f(magic.getUniformLocationDebug(shaderProgram, "material_alpha"), material["alpha"])
                self.shader.setUniform("material.alpha", material["alpha"])
            glDrawArrays(GL_TRIANGLES, chunkOffset, chunkCount)

        glUseProgram(0)
        # deactivate texture units...
        # for (int i = TU_Max - 1; i >= 0; --i)
        # {
        # glActiveTexture(GL_TEXTURE0 + i);
        # glBindTexture(GL_TEXTURE_2D, 0);
        # }

    # useful to get the default bindings that the ObjModel will use when rendering, use to set up own shaders
    # for example an optimized shadow shader perhaps?
    def getDefaultAttributeBindings():
        return {
            "position": ObjModel.AA_Position,
            "normal": ObjModel.AA_Normal,
            "texCoord": ObjModel.AA_TexCoord,
            "tangent": ObjModel.AA_Tangent,
            "bitangent": ObjModel.AA_Bitangent,
        }

        #
        # Helper to set the default uniforms provided by ObjModel. This only needs to be done once after creating the shader
        # NOTE: the shader must be bound when calling this function.

    def setDefaultUniformBindings(shaderProgram):
        assert glGetIntegerv(GL_CURRENT_PROGRAM) == shaderProgram

        glUniform1i(magic.getUniformLocationDebug(shaderProgram, "diffuse_texture"), ObjModel.TU_Diffuse)
        glUniform1i(magic.getUniformLocationDebug(shaderProgram, "opacity_texture"), ObjModel.TU_Opacity)
        glUniform1i(magic.getUniformLocationDebug(shaderProgram, "specular_texture"), ObjModel.TU_Specular)
        glUniform1i(magic.getUniformLocationDebug(shaderProgram, "normal_texture"), ObjModel.TU_Normal)
        # glUniformBlockBinding(shaderProgram, glGetUniformBlockIndex(shaderProgram, "MaterialProperties"), UBS_MaterialProperties);

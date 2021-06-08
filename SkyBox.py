from ctypes import c_float, c_void_p
from lab_utils import make_scale
from Shader import Shader
from OpenGL.GL import *
from PIL import Image

cubeVerts = [
    -1.0,  1.0, -1.0,
    -1.0, -1.0, -1.0,
    1.0, -1.0, -1.0,
    1.0, -1.0, -1.0,
    1.0,  1.0, -1.0,
    -1.0,  1.0, -1.0,

    -1.0, -1.0,  1.0,
    -1.0, -1.0, -1.0,
    -1.0,  1.0, -1.0,
    -1.0,  1.0, -1.0,
    -1.0,  1.0,  1.0,
    -1.0, -1.0,  1.0,

    1.0, -1.0, -1.0,
    1.0, -1.0,  1.0,
    1.0,  1.0,  1.0,
    1.0,  1.0,  1.0,
    1.0,  1.0, -1.0,
    1.0, -1.0, -1.0,

    -1.0, -1.0,  1.0,
    -1.0,  1.0,  1.0,
    1.0,  1.0,  1.0,
    1.0,  1.0,  1.0,
    1.0, -1.0,  1.0,
    -1.0, -1.0,  1.0,

    -1.0,  1.0, -1.0,
    1.0,  1.0, -1.0,
    1.0,  1.0,  1.0,
    1.0,  1.0,  1.0,
    -1.0,  1.0,  1.0,
    -1.0,  1.0, -1.0,

    -1.0, -1.0, -1.0,
    -1.0, -1.0,  1.0,
    1.0, -1.0, -1.0,
    1.0, -1.0, -1.0,
    -1.0, -1.0,  1.0,
    1.0, -1.0,  1.0
]


class SkyBox:
    def __init__(self, directory, scale=50, srgb=True):
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.id)

        texSuffixFaceMap = {
            "right": GL_TEXTURE_CUBE_MAP_POSITIVE_X,
            "left": GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
            "top": GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            "bottom": GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            "front": GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            "back": GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
        }

        self.shader = Shader(vertFile='shaders/cubemapVert.glsl', fragFile='shaders/cubemapFrag.glsl')
        self.scale = scale
        try:
            for name, faceId in texSuffixFaceMap.items():
                with Image.open(directory + name+".jpg").transpose(Image.FLIP_TOP_BOTTOM) as im:
                    data = im.tobytes("raw", "RGBX" if im.mode == 'RGB' else "RGBA", 0, -1)
                    glTexImage2D(faceId, 0, GL_SRGB_ALPHA if srgb else GL_RGBA,
                                 im.size[0], im.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        except:
            print("WARNING: FAILED to load cubemap texture '%s'" % directory)
            raise RuntimeWarning

        data = None
        glGenerateMipmap(GL_TEXTURE_CUBE_MAP)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # Use tri-linear mip map filtering
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        #	glTexParameterf(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAX_ANISOTROPY_EXT, 16)			  // or replace trilinear mipmap filtering with nicest anisotropic filtering
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)
        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)
        cube_buffer = (c_float * len(cubeVerts))(*cubeVerts)
        glBufferData(GL_ARRAY_BUFFER, len(cubeVerts) * sizeof(GLfloat), cube_buffer, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), c_void_p(0))
        glEnableVertexAttribArray(0)

    def draw(self, view, projection):
        glDepthMask(GL_FALSE)
        glDepthFunc(GL_LEQUAL)
        self.shader.use()
        self.shader.setUniform("view", view)
        self.shader.setUniform("projection", projection)
        self.shader.setUniform("model", make_scale(self.scale))
        glBindVertexArray(self._vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.id)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glBindVertexArray(0)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LEQUAL)

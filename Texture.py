from OpenGL.GL import *
from PIL import Image


class Texture:

    def __init__(self, filePath=None, textureGLType=GL_TEXTURE_2D, mapType=None, srgb=False):

        if (not filePath):
            # Make a daefault texture
            print("Using default texture")
            self.id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.id)
            if mapType == "normal":
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_FLOAT, [1.0, 1.0, 1.0, 1.0])
            else:
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 1, 1, 0, GL_RGBA, GL_FLOAT, [0.5, 0.5, 0.5, 1.0])

            glBindTexture(GL_TEXTURE_2D, 0)
            return
        with Image.open(filePath) as image:
            self.mode = "RGBX" if image.mode == 'RGB' else "RGBA"
            data = image.tobytes("raw", self.mode, 0, -1)
            self.width = image.size[0]
            self.height = image.size[1]

        if mapType in ("diffuse", "specular", "emmision"):
            self.mapType = mapType
        else:
            self.mapType = None

        self.id = glGenTextures(1)
        glBindTexture(textureGLType, self.id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        if (data):
            glTexImage2D(textureGLType, 0, GL_RGBA, self.width, self.height, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, data)
            glGenerateMipmap(textureGLType)
        else:
            print("TEXTURE.WARNING: FAILED to load texture '%s'" % filePath)
            raise RuntimeWarning

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(textureGLType, 0)
        data = None

    def delete(self):
        glDeleteTextures(self.id)

    def bind(self, texUnit=0, type=GL_TEXTURE_2D):
        glActiveTexture(GL_TEXTURE0 + texUnit)
        glBindTexture(type, self.id)

    def unbind(self, type=GL_TEXTURE_2D):
        glActiveTexture(0)
        glBindTexture(type, 0)

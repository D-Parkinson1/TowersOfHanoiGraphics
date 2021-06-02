from OpenGL.GL import *
from PIL import Image


class Texture:

    def __init__(self, filePath, textureType=GL_TEXTURE_2D):
        with Image.open(filePath) as image:
            self.mode = "RGBX" if image.mode == 'RGB' else "RGBA"
            data = image.tobytes("raw", self.mode, 0, -1)
            self.width = image.size[0]
            self.height = image.size[1]

        self.texture = glGenTextures(1)
        glBindTexture(textureType, self.texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        if (data):
            glTexImage2D(textureType, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
            glGenerateMipmap(textureType)
        else:
            print("WARNING: FAILED to load texture '%s'" % filePath)
            raise RuntimeWarning

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(textureType, 0)
        data = None

    def delete(self):
        glDeleteTextures(self.texture)

    def bind(self, texUnit=0, type=GL_TEXTURE_2D):
        glActiveTexture(GL_TEXTURE0 + texUnit)
        glBindTexture(type, self.texture)

    def unbind(self, type=GL_TEXTURE_2D):
        glActiveTexture(0)
        glBindTexture(type, 0)

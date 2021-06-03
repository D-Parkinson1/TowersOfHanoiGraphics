from ctypes import c_float
from OpenGL.GL import *
import lab_utils as lu
from Shader import Shader


class LightSource:

    # Positions and texture coords. Texture not needed
    cubeVerts = [
        -0.5, -0.5, -0.5,  # 0.0, 0.0,
        0.5, -0.5, -0.5,  # 1.0, 0.0,
        0.5,  0.5, -0.5,  # 1.0, 1.0,
        0.5,  0.5, -0.5,  # 1.0, 1.0,
        -0.5,  0.5, -0.5,  # 0.0, 1.0,
        -0.5, -0.5, -0.5,  # 0.0, 0.0,

        -0.5, -0.5,  0.5,  # 0.0, 0.0,
        0.5, -0.5,  0.5,  # 1.0, 0.0,
        0.5,  0.5,  0.5,  # 1.0, 1.0,
        0.5,  0.5,  0.5,  # 1.0, 1.0,
        -0.5,  0.5,  0.5,  # 0.0, 1.0,
        -0.5, -0.5,  0.5,  # 0.0, 0.0,

        -0.5,  0.5,  0.5,  # 1.0, 0.0,
        -0.5,  0.5, -0.5,  # 1.0, 1.0,
        -0.5, -0.5, -0.5,  # 0.0, 1.0,
        -0.5, -0.5, -0.5,  # .0, 1.0,
        -0.5, -0.5,  0.5,  # .0, 0.0,
        -0.5,  0.5,  0.5,  # 1.0, 0.0,

        0.5,  0.5,  0.5,  # 1.0, 0.0,
        0.5,  0.5, -0.5,  # 1.0, 1.0,
        0.5, -0.5, -0.5,  # 0.0, 1.0,
        0.5, -0.5, -0.5,  # 0.0, 1.0,
        0.5, -0.5,  0.5,  # 0.0, 0.0,
        0.5,  0.5,  0.5,  # 1.0, 0.0,

        -0.5, -0.5, -0.5,  # 0.0, 1.0,
        0.5, -0.5, -0.5,  # 1.0, 1.0,
        0.5, -0.5,  0.5,  # 1.0, 0.0,
        0.5, -0.5,  0.5,  # 1.0, 0.0,
        -0.5, -0.5,  0.5,  # 0.0, 0.0,
        -0.5, -0.5, -0.5,  # 0.0, 1.0,

        -0.5,  0.5, -0.5,  # 0.0, 1.0,
        0.5,  0.5, -0.5,  # 1.0, 1.0,
        0.5,  0.5,  0.5,  # 1.0, 0.0,
        0.5,  0.5,  0.5,  # 1.0, 0.0,
        -0.5,  0.5,  0.5,  # 0.0, 0.0,
        -0.5,  0.5, -0.5,  # 0.0, 1.0
    ]

    def __init__(self, pos: lu.vec3, shader: Shader = None, colour: lu.vec3 = lu.vec3(1.0, 1.0, 1.0)):
        self.position = lu.vec3(*pos)
        if shader:
            self.shader = shader
        else:
            self.shader = Shader(vertFile='shaders/lightSourceVert.glsl', fragFile='shaders/lightSourceFrag.glsl')
        self.colour = colour
        self.__vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        glBindVertexArray(self.__vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        cube_buffer = (c_float * len(self.cubeVerts))(*self.cubeVerts)
        glBufferData(GL_ARRAY_BUFFER, len(self.cubeVerts) * ctypes.sizeof(GLfloat), cube_buffer, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * ctypes.sizeof(GLfloat), None)
        glEnableVertexAttribArray(0)

        self.shader.use()
        self.shader.setUniform("objectColour", lu.vec3(1.0, 0.5, 0.3))
        self.shader.setUniform("lightColour", colour)

    def draw(self, projection, view):
        self.shader.use()
        self.shader.setUniform("projection", projection)
        self.shader.setUniform("view", view)
        model = lu.make_translation(*self.position) * lu.make_scale(0.2)
        self.shader.setUniform("model", model)
        glBindVertexArray(self.__vao)
        glDrawArrays(GL_TRIANGLES, 0, 36)

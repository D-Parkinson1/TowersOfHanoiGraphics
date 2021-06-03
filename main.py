
from LightSource import LightSource
from Texture import Texture
from ctypes import c_float, c_uint, c_void_p
from OpenGL.GL import *
from PIL import Image
import glfw

import ObjModel as Obj

from lab_utils import make_perspective, make_rotation_x, make_rotation_y, make_rotation_z, vec3, Mat4, make_lookAt, make_scale, make_translation

import Shader as sha

from Window import Window
# import imgui
# from imgui.integrations.glfw import GlfwRenderer

import numpy as np
from math import radians, sin, cos, pi


def drawCircle(numSegments: int, radius: int = 1):
    g_triangleVerts = []
    for i in range(numSegments):
        theta = 2 * pi * i / (numSegments)
        theta_next = 2 * pi * (i+1) / (numSegments)
        x = radius * cos(theta)
        y = radius * sin(theta)
        x2 = radius * cos(theta_next)
        y2 = radius * sin(theta_next)

        g_triangleVerts.append([0, 0, 0])
        g_triangleVerts.append([x, y, 0])
        g_triangleVerts.append([x2, y2, 0])
    return g_triangleVerts


    # magic.drawVertexDataAsTriangles(g_triangleVerts)
torus = None


# def drawObjModel(viewToClipTfm, worldToViewTfm, modelToWorldTfm, model):
#     # Lighting/Shading is very often done in view space, which is why a transformation that lands positions in this space is needed
#     modelToViewTransform = worldToViewTfm * modelToWorldTfm

#     # this is a special transform that ensures that normal vectors remain orthogonal to the
#     # surface they are supposed to be even in the prescence of non-uniform scaling.
#     # It is a 3x3 matrix as vectors don't need translation anyway and this transform is only for vectors,
#     # not points. If there is no non-uniform scaling this is just the same as Mat3(modelToViewTransform)
#     modelToViewNormalTransform = inverse(
#         transpose(Mat3(modelToViewTransform)))

#     # Bind the shader program such that we can set the uniforms (model.render sets it again)
#     glUseProgram(model.defaultShader)

#     # transform (rotate) light direction into view space (as this is what the ObjModel shader wants)
#     viewSpaceLightDirection = normalize(
#         Mat3(worldToViewTfm) * [-1, -1, -1])
#     glUniform3fv(glGetUniformLocation(model.defaultShader,
#                                       "viewSpaceLightDirection"), 1, viewSpaceLightDirection)

#     # This dictionary contains a few transforms that are needed to render the ObjModel using the default shader.
#     # it would be possible to just set the modelToWorld transform, as this is the only thing that changes between
#     # the objects, and compute the other matrices in the vertex shader.
#     # However, this would push a lot of redundant computation to the vertex shader and makes the code less self contained,
#     # in this way we set all the required parameters explicitly.
#     transforms = {
#         "modelToClipTransform": viewToClipTfm * worldToViewTfm * modelToWorldTfm,
#         "modelToViewTransform": modelToViewTransform,
#         "modelToViewNormalTransform": modelToViewNormalTransform,
#     }

#     model.render(None, None, transforms)


# def createAndAddVertexArrayData(vertexArrayObject, data, attributeIndex):
#     glBindVertexArray(vertexArrayObject)
#     buffer = glGenBuffers(1)
#     uploadFloatData(buffer, data)

#     glBindBuffer(GL_ARRAY_BUFFER, buffer)
#     glVertexAttribPointer(attributeIndex, len(
#         data[0]), GL_FLOAT, GL_FALSE, 0, None)
#     glEnableVertexAttribArray(attributeIndex)

#     # Unbind the buffers again to avoid unintentianal GL state corruption (this is something that can be rather inconventient to debug)
#     glBindBuffer(GL_ARRAY_BUFFER, 0)
#     glBindVertexArray(0)

#     return buffer


class Hanoi:
    vao = None
    ebo = None
    shader = None
    texture1 = None
    texture2 = None
    light = None
    # coords, colours, texcoords
    vertices = [
        0.5,  0.5, 0.0,  1.0, 0.0, 0.0,  1.0, 1.0,
        0.5, -0.5, 0.0,  0.0, 1.0, 0.0,  1.0, 0.0,
        -0.5, -0.5, 0.0,  0.0, 0.0, 1.0,  0.0, 0.0,
        -0.5,  0.5, 0.0,  1.0, 1.0, 0.0,  0.0, 1.0
    ]
    indices = [
        0, 1, 3,
        1, 2, 3
    ]

    cubeVerts = [
        -0.5, -0.5, -0.5,  0.0, 0.0,
        0.5, -0.5, -0.5,  1.0, 0.0,
        0.5,  0.5, -0.5,  1.0, 1.0,
        0.5,  0.5, -0.5,  1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0, 1.0,
        -0.5, -0.5, -0.5,  0.0, 0.0,

        -0.5, -0.5,  0.5,  0.0, 0.0,
        0.5, -0.5,  0.5,  1.0, 0.0,
        0.5,  0.5,  0.5,  1.0, 1.0,
        0.5,  0.5,  0.5,  1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0, 1.0,
        -0.5, -0.5,  0.5,  0.0, 0.0,

        -0.5,  0.5,  0.5,  1.0, 0.0,
        -0.5,  0.5, -0.5,  1.0, 1.0,
        -0.5, -0.5, -0.5,  0.0, 1.0,
        -0.5, -0.5, -0.5,  0.0, 1.0,
        -0.5, -0.5,  0.5,  0.0, 0.0,
        -0.5,  0.5,  0.5,  1.0, 0.0,

        0.5,  0.5,  0.5,  1.0, 0.0,
        0.5,  0.5, -0.5,  1.0, 1.0,
        0.5, -0.5, -0.5,  0.0, 1.0,
        0.5, -0.5, -0.5,  0.0, 1.0,
        0.5, -0.5,  0.5,  0.0, 0.0,
        0.5,  0.5,  0.5,  1.0, 0.0,

        -0.5, -0.5, -0.5,  0.0, 1.0,
        0.5, -0.5, -0.5,  1.0, 1.0,
        0.5, -0.5,  0.5,  1.0, 0.0,
        0.5, -0.5,  0.5,  1.0, 0.0,
        -0.5, -0.5,  0.5,  0.0, 0.0,
        -0.5, -0.5, -0.5,  0.0, 1.0,

        -0.5,  0.5, -0.5,  0.0, 1.0,
        0.5,  0.5, -0.5,  1.0, 1.0,
        0.5,  0.5,  0.5,  1.0, 0.0,
        0.5,  0.5,  0.5,  1.0, 0.0,
        -0.5,  0.5,  0.5,  0.0, 0.0,
        -0.5,  0.5, -0.5,  0.0, 1.0
    ]

    cubePositions = [
        vec3(0.0,  0.0,  0.0),
        vec3(2.0,  5.0, -15.0),
        vec3(-1.5, -2.2, -2.5),
        vec3(-3.8, -2.0, -12.3),
        vec3(2.4, -0.4, -3.5),
        vec3(-1.7,  3.0, -7.5),
        vec3(1.3, -2.0, -2.5),
        vec3(1.5,  2.0, -2.5),
        vec3(1.5,  0.2, -1.5),
        vec3(-1.3,  1.0, -1.5)
    ]

    def __init__(self):
        self.window = Window(800, 600, "Towers of Hanoi", render=self.render, initResources=self.initResources)
        self.light = LightSource(vec3(1.2, 1.0, 2.0))

    def start(self):
        self.window.main()

    def render(self, width, height):
        # global g_torus

        self.texture1.bind()
        self.texture2.bind(texUnit=1)

        # shader.use()
        # scale = make_scale(0.5)
        # translate = make_translation(0, 0, 0)
        # rotate = make_rotation_z(glfw.get_time())
        # tfm = rotate * translate * scale
        # shader.setUniform("transform", scale)
        angle = glfw.get_time() * 25
        model = make_rotation_x(radians(angle)) * make_rotation_y(radians(2*angle))
        # view = make_translation(0, 0, -5)

        radius = 10
        camX = sin(glfw.get_time()) * radius
        camZ = cos(glfw.get_time()) * radius
        view = make_lookAt(vec3(camX, 0, camZ), vec3(0), vec3(0, 1, 0))
        projection = make_perspective(45, width/height, 0.1, 100)
        self.shader.use()
        self.shader.setUniform("model", model)
        self.shader.setUniform("view", view)
        self.shader.setUniform("projection", projection)
        glBindVertexArray(self.vao)

        for i in range(10):
            model = make_translation(*self.cubePositions[i])
            angle = 20.0 * i
            model *= make_rotation_x(radians(angle)) * make_rotation_y(radians(0.3*angle))
            if i % 3 == 0:
                model *= make_rotation_z(radians(angle*glfw.get_time()))
            self.shader.setUniform("model", model)

            glDrawArrays(GL_TRIANGLES, 0, 36)

        glDrawArrays(GL_TRIANGLES, 0, 36)
        self.light.draw(projection, view)
        # glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # shader.use()
        # scale = make_scale(sin(glfw.get_time()))
        # translate = make_translation(-0.75, 0.75, 0)
        # rotate = make_rotation_z(0)
        # tfm = translate * rotate * scale
        # shader.setUniform("transform", tfm)
        # glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # verts = drawCircle(28)
        # numVerts = len(verts)
        # vertsArrayObj = gl.glGenVertexArrays(1)
        # createAndAddVertexArrayData(vertsArrayObj, verts, 0)
        # shader = sha.Shader(vertexShader, fragmentShader, {
        #     "positionIn": 0, "normalIn": 1})
        # gl.glUseProgram(shader.program)
        # gl.glBindVertexArray(vertsArrayObj)
        # gl.glDrawArrays(gl.GL_TRIANGLES, 0, numVerts)

        # drawObjModel(Mat4(), Mat4(), Mat4(), torus)

    def initResources(self):
        # global torus
        # torus = Obj.ObjModel("objects/torus.obj")
        # vertexShader = """
        # #version 330
        # in vec3 positionIn;

        # void main()
        # {
        #     gl_Position = vec4(positionIn, 1.0);
        # }
        # """

        # fragmentShader = """
        # #version 330
        # out vec4 fragmentColor;

        # void main()
        # {
        #     fragmentColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
        # }
        # """
        # Set the colour we want the frame buffer cleared to,
        glClearColor(0.2, 0.3, 0.1, 1.0)
        # Tell OpenGL to clear the render target to the clear values for both depth and colour buffers (depth uses the default)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        # shader = sha.Shader(vertFile='shaders/uniformVert.glsl', fragFile='shaders/uniformFrag.glsl')
        self.shader = sha.Shader(vertFile='shaders/lightVert.glsl',
                                 fragFile='shaders/lightFrag.glsl')

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        # ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        ##############################CUBE START ##################################
        #######################################################################
        cube_buffer = (c_float * len(self.cubeVerts))(*self.cubeVerts)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(self.cubeVerts) * ctypes.sizeof(GLfloat), cube_buffer, GL_STATIC_DRAW)

        # position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * ctypes.sizeof(GLfloat), c_void_p(0))
        glEnableVertexAttribArray(0)

        # texture attribute
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * ctypes.sizeof(GLfloat),
                              c_void_p(3 * ctypes.sizeof(GLfloat)))
        glEnableVertexAttribArray(1)

        ###################################
        ### END CUBE###########
        ##########################

        # data_buffer = (c_float * len(vertices))(*vertices)
        # glBindBuffer(GL_ARRAY_BUFFER, vbo)
        # glBufferData(GL_ARRAY_BUFFER, len(vertices) * ctypes.sizeof(GLfloat), data_buffer, GL_STATIC_DRAW)

        # index_buffer = (c_uint * len(indices))(*indices)
        # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        # glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * ctypes.sizeof(GLuint), index_buffer, GL_STATIC_DRAW)

        # # position attribute
        # glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * ctypes.sizeof(GLfloat), c_void_p(0))
        # glEnableVertexAttribArray(0)

        # # colour attribute
        # glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * ctypes.sizeof(GLfloat), c_void_p(3 * ctypes.sizeof(GLfloat)))
        # glEnableVertexAttribArray(1)

        # # texture attribute
        # glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * ctypes.sizeof(GLfloat), c_void_p(6 * ctypes.sizeof(GLfloat)))
        # glEnableVertexAttribArray(2)

        self.texture1 = Texture('textures/container.jpg')
        self.texture2 = Texture('textures/awesomeface.png')

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.shader.use()
        self.shader.setUniform("texture2", 1)
        self.shader.setUniform("texture1", 0)
        self.shader.setUniform("objectColour", vec3(1.0, 0.5, 0.3))
        self.shader.setUniform("lightColour", vec3(1.0, 1.0, 1.0))

        # For wireframe
        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


if __name__ == "__main__":
    project = Hanoi()
    project.start()


import glfw
from Camera import Camera, CameraMovement
from LightSource import LightSource
from Texture import Texture
from ctypes import c_float, c_uint, c_void_p
from OpenGL.GL import *
from PIL import Image

import ObjModel as Obj

from lab_utils import make_perspective, make_rotation_x, make_rotation_y, make_rotation_z, vec3, Mat4, make_lookAt, make_scale, make_translation

from Shader import Shader

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
    texture3 = None
    light = None
    pointLights = []
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
    cubeVertsTextureNormal = [
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,
        0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0,
        0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
        0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0,
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,

        -0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 0.0,
        0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 0.0,
        0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 1.0,
        0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 1.0,
        -0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 0.0,

        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0,
        -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  1.0, 1.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0,
        -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  0.0, 0.0,
        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0,

        0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0,
        0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 1.0,
        0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
        0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
        0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 0.0,
        0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0,

        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,
        0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0,
        0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
        0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
        -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0, 0.0,
        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,

        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0,
        0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0, 1.0,
        0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
        0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
        -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 0.0,
        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0
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

    def __init__(self, width=800, height=800):
        self.window = Window(width, height, "Towers of Hanoi", render=self.render,
                             initResources=self.initResources, processInput=self.processInput)
        # Capture the mosuse
        glfw.set_input_mode(self.window._win, glfw.CURSOR, glfw.CURSOR_DISABLED)

        # Callabcks for mouse input
        glfw.set_cursor_pos_callback(self.window._win, self.mouseCallback)
        glfw.set_scroll_callback(self.window._win, self.scrollCallback)

        # Last camera position
        self.lastX = width / 2
        self.lastY = height / 2
        # First mouse move

        self.firstMouse = True
        self.deltaTime = 0
        self.lastFrame = 0

        # self.light = LightSource(vec3(1.2, 1.0, 2.0))
        self.pointLights.append(LightSource(vec3(1.0, 0.5, 3.0), None, vec3(0.83, 0.98, 1.0)))
        self.pointLights.append(LightSource(vec3(0.0, 1.0, 0.0), None, vec3(0.25, 0.25, 1.0)))
        self.pointLights.append(LightSource(vec3(-3.0, -2, 3.0), None, vec3(1.0, 0.3, 0.11)))
        self.pointLights.append(LightSource(vec3(2.0, 3, -3.0), None, vec3(0.25, 1.0, 0.11)))
        self.camera = Camera(vec3(0, 0, 3))

    def mouseCallback(self, window, xPos, yPos):
        if (self.firstMouse):
            self.lastX = xPos
            self.lastY = yPos
            self.firstMouse = False

        xOffset = xPos - self.lastX
        yOffset = self.lastY - yPos
        self.lastX = xPos
        self.lastY = yPos

        self.camera.processMouse(xOffset, yOffset)

    def scrollCallback(self, window, xOffset, yOffset):
        self.camera.processMouseScroll(yOffset)

    def start(self):
        self.window.main()

    def render(self, width, height):
        currentFrame = glfw.get_time()
        self.deltaTime = currentFrame - self.lastFrame
        self.lastFrame = currentFrame
        # global g_torus
        glClearColor(0.2, 0.3, 0.1, 1.0)
        # Tell OpenGL to clear the render target to the clear values for both depth and colour buffers (depth uses the default)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        # Bind textures
        self.texture1.bind()
        self.texture2.bind(texUnit=1)
        self.texture3.bind(texUnit=2)

        # shader.use()
        # scale = make_scale(0.5)
        # translate = make_translation(0, 0, 0)
        # rotate = make_rotation_z(glfw.get_time())
        # tfm = rotate * translate * scale
        # shader.setUniform("transform", scale)

        # view = make_translation(0, 0, -5)

        # radius = 10
        # camX = radius  # sin(glfw.get_time()) * radius
        # camZ = radius  # cos(glfw.get_time()) * radius
        # camPos = vec3(camX, 0, camZ)

        # angle = glfw.get_time() * 25

        # self.light.shader.use()
        # lightColour = vec3(sin(glfw.get_time() * 2.0), sin(glfw.get_time() * 0.7), sin(glfw.get_time() * 1.3))
        # self.light.colour = lightColour
        # self.light.shader.setUniform("lightColour", lightColour)

        # Calculate transformation matrices
        model = Mat4()  # make_rotation_x(radians(angle)) * make_rotation_y(radians(2*angle))
        view = self.camera.getViewMatrix()  # make_lookAt(self.camera.position, vec3(0), vec3(0, 1, 0))
        projection = make_perspective(self.camera.zoom, width/height, 0.1, 100)

        self.shader.use()
        self.shader.setUniform("model", model)
        self.shader.setUniform("view", view)
        self.shader.setUniform("projection", projection)
        self.shader.setUniform("viewPos", self.camera.position)
        self.shader.setUniform("material.shininess", 32.0)

        # Directional light
        self.shader.setUniform("dirLight.direction", vec3(-0.2, -1.0, -0.3))
        self.shader.setUniform("dirLight.ambient", vec3(0.05))
        self.shader.setUniform("dirLight.diffuse", vec3(0.4))
        self.shader.setUniform("dirLight.specular", vec3(0.5))
        # Point lights
        for i in range(len(self.pointLights)):
            light = self.pointLights[i]
            # light.shader.setUniform("lightColour", vec3(0.0, 1.0, 0.5))
            self.shader.setUniform("pointLights[%s].position" % i, light.position)
            self.shader.setUniform("pointLights[%s].ambient" % i, vec3(0.05)*light.colour)
            self.shader.setUniform("pointLights[%s].diffuse" % i, vec3(0.8)*light.colour)
            self.shader.setUniform("pointLights[%s].specular" % i, vec3(1.0)*light.colour)
            self.shader.setUniform("pointLights[%s].constant" % i, 1.0)
            self.shader.setUniform("pointLights[%s].linear" % i, 0.09)
            self.shader.setUniform("pointLights[%s].quadratic" % i, 0.032)

            light.draw(projection, view)

        # Spotlight
        self.shader.setUniform("spotLight.position", self.camera.position)
        self.shader.setUniform("spotLight.direction", self.camera.front)
        self.shader.setUniform("spotLight.ambient", vec3(0.0))
        self.shader.setUniform("spotLight.diffuse", vec3(1.0))
        self.shader.setUniform("spotLight.specular", vec3(1.0))
        self.shader.setUniform("spotLight.constant", 1.0)
        self.shader.setUniform("spotLight.linear", 0.09)
        self.shader.setUniform("spotLight.quadratic", 0.032)
        self.shader.setUniform("spotLight.cutOff", cos(radians(12.5)))
        self.shader.setUniform("spotLight.outerCutOff", cos(radians(15.0)))

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

        # self.light.draw(projection, view)
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
        # shader = Shader(vertexShader, fragmentShader, {
        #     "positionIn": 0, "normalIn": 1})
        # gl.glUseProgram(shader.program)
        # gl.glBindVertexArray(vertsArrayObj)
        # gl.glDrawArrays(gl.GL_TRIANGLES, 0, numVerts)

        # drawObjModel(Mat4(), Mat4(), Mat4(), torus)

    def initResources(self):
        # global torus
        # torus = Obj.ObjModel("objects/torus.obj")

        # Set the colour we want the frame buffer cleared to,
        glClearColor(0.2, 0.3, 0.1, 1.0)
        # Tell OpenGL to clear the render target to the clear values for both depth and colour buffers (depth uses the default)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        # shader = Shader(vertFile='shaders/uniformVert.glsl', fragFile='shaders/uniformFrag.glsl')
        self.shader = Shader(vertFile='shaders/lightVert.glsl',
                             fragFile='shaders/lightFrag.glsl')

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        # ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        ##############################CUBE START ##################################
        #######################################################################
        cube_buffer = (c_float * len(self.cubeVertsTextureNormal))(*self.cubeVertsTextureNormal)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(self.cubeVertsTextureNormal) *
                     ctypes.sizeof(GLfloat), cube_buffer, GL_STATIC_DRAW)

        # position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * ctypes.sizeof(GLfloat), c_void_p(0))
        glEnableVertexAttribArray(0)

        # normal attribute
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * ctypes.sizeof(GLfloat),
                              c_void_p(3 * ctypes.sizeof(GLfloat)))
        glEnableVertexAttribArray(1)

        # texture attribute
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * ctypes.sizeof(GLfloat),
                              c_void_p(6 * ctypes.sizeof(GLfloat)))
        glEnableVertexAttribArray(2)

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

        self.texture1 = Texture('textures/container2.png')
        self.texture2 = Texture('textures/container2_specular.png')
        self.texture3 = Texture('textures/matrix.jpg')

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.shader.use()
        # self.shader.setUniform("lightColour", self.light.colour)
        # self.shader.setUniform("light.position", self.light.position)
        # self.shader.setUniform("material.ambient", vec3(1.0, 0.5, 0.31))
        self.shader.setUniform("material.diffuse", 0)
        self.shader.setUniform("material.specular", 1)
        # self.shader.setUniform("material.emission", 2)
        # self.shader.setUniform("material.shininess", 32.0)
        # self.shader.setUniform("light.ambient", vec3(0.2))
        # self.shader.setUniform("light.diffuse", vec3(0.5))
        # self.shader.setUniform("light.specular", vec3(1.0))
        # For wireframe
        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    def processInput(self):
        if (glfw.get_key(self.window._win, glfw.KEY_ESCAPE) == glfw.PRESS):
            glfw.set_window_should_close(self.window._win, True)

        if(glfw.get_key(self.window._win, glfw.KEY_W) == glfw.PRESS):
            self.camera.processKeyboard(CameraMovement.FORWARD, self.deltaTime)
        if(glfw.get_key(self.window._win, glfw.KEY_S) == glfw.PRESS):
            self.camera.processKeyboard(CameraMovement.BACKWARD, self.deltaTime)
        if(glfw.get_key(self.window._win, glfw.KEY_A) == glfw.PRESS):
            self.camera.processKeyboard(CameraMovement.LEFT, self.deltaTime)
        if(glfw.get_key(self.window._win, glfw.KEY_D) == glfw.PRESS):
            self.camera.processKeyboard(CameraMovement.RIGHT, self.deltaTime)


if __name__ == "__main__":
    project = Hanoi()
    project.start()

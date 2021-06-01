
from ctypes import c_float
from OpenGL.GL import *

import ObjModel as Obj

import lab_utils as lu

import Shader as sha

from Window import Window
# import imgui
# from imgui.integrations.glfw import GlfwRenderer

import numpy as np
from math import sin, cos, pi


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

vao = None


def initResources():
    global vao
    # global torus
    # torus = Obj.ObjModel("objects/torus.obj")
    vertexShader = """
    #version 330
    in vec3 positionIn;

    void main() 
    {
	    gl_Position = vec4(positionIn, 1.0);
    }
    """

    fragmentShader = """
    #version 330
    out vec4 fragmentColor;

    void main() 
    {
	    fragmentColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
    }
    """
    # Set the colour we want the frame buffer cleared to,
    glClearColor(0.2, 0.3, 0.1, 1.0)
    # Tell OpenGL to clear the render target to the clear values for both depth and colour buffers (depth uses the default)
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
    shader = sha.Shader(vertexShader, fragmentShader)
    vertices = [
        -0.5, -0.5, 0,
        0.5, -0.5, 0,
        0, 0.5, 0
    ]
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    data_buffer = (c_float * len(vertices))(*vertices)
    # Upload data to the currently bound GL_ARRAY_BUFFER, note that this is
    # completely anonymous binary data, no type information is retained (we'll
    # supply that later in glVertexAttribPointer)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                          3*ctypes.sizeof(GLfloat), None)
    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    glUseProgram(shader.program)


def createAndAddVertexArrayData(vertexArrayObject, data, attributeIndex):
    glBindVertexArray(vertexArrayObject)
    buffer = glGenBuffers(1)
    lu.uploadFloatData(buffer, data)

    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    glVertexAttribPointer(attributeIndex, len(
        data[0]), GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(attributeIndex)

    # Unbind the buffers again to avoid unintentianal GL state corruption (this is something that can be rather inconventient to debug)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return buffer


def render(width, height):
    # global g_torus
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    # verts = drawCircle(28)
    # numVerts = len(verts)
    # vertsArrayObj = gl.glGenVertexArrays(1)
    # createAndAddVertexArrayData(vertsArrayObj, verts, 0)
    # shader = sha.Shader(vertexShader, fragmentShader, {
    #     "positionIn": 0, "normalIn": 1})
    # gl.glUseProgram(shader.program)
    # gl.glBindVertexArray(vertsArrayObj)
    # gl.glDrawArrays(gl.GL_TRIANGLES, 0, numVerts)

    # drawObjModel(lu.Mat4(), lu.Mat4(), lu.Mat4(), torus)


def drawObjModel(viewToClipTfm, worldToViewTfm, modelToWorldTfm, model):
    # Lighting/Shading is very often done in view space, which is why a transformation that lands positions in this space is needed
    modelToViewTransform = worldToViewTfm * modelToWorldTfm

    # this is a special transform that ensures that normal vectors remain orthogonal to the
    # surface they are supposed to be even in the prescence of non-uniform scaling.
    # It is a 3x3 matrix as vectors don't need translation anyway and this transform is only for vectors,
    # not points. If there is no non-uniform scaling this is just the same as Mat3(modelToViewTransform)
    modelToViewNormalTransform = lu.inverse(
        lu.transpose(lu.Mat3(modelToViewTransform)))

    # Bind the shader program such that we can set the uniforms (model.render sets it again)
    glUseProgram(model.defaultShader)

    # transform (rotate) light direction into view space (as this is what the ObjModel shader wants)
    viewSpaceLightDirection = lu.normalize(
        lu.Mat3(worldToViewTfm) * [-1, -1, -1])
    glUniform3fv(glGetUniformLocation(model.defaultShader,
                                      "viewSpaceLightDirection"), 1, viewSpaceLightDirection)

    # This dictionary contains a few transforms that are needed to render the ObjModel using the default shader.
    # it would be possible to just set the modelToWorld transform, as this is the only thing that changes between
    # the objects, and compute the other matrices in the vertex shader.
    # However, this would push a lot of redundant computation to the vertex shader and makes the code less self contained,
    # in this way we set all the required parameters explicitly.
    transforms = {
        "modelToClipTransform": viewToClipTfm * worldToViewTfm * modelToWorldTfm,
        "modelToViewTransform": modelToViewTransform,
        "modelToViewNormalTransform": modelToViewNormalTransform,
    }

    model.render(None, None, transforms)


if __name__ == "__main__":
    window = Window(1280, 720, "Towers of Hanoi",
                    render=render, initResources=initResources)
    window.main()

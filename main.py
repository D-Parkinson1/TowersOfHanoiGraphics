import glfw
import OpenGL.GL as gl

import ObjModel

import lab_utils as lu

import Shader as sha
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


class Window:

    def __init__(self, width: int = 1280, height: int = 720, title: str = "Window", render=None):
        # imgui.create_context()

        # Initialise glfw library
        if not glfw.init():
            print("Could not initialise OpenGL context")
            exit(1)

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.SRGB_CAPABLE, 1)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        # Create a windowed mode window and its OpenGL context
        self._win = glfw.create_window(width, height, title, None, None)

        if not self._win:
            glfw.terminate()
            print("Could nto initialise window")
            exit(1)

        glfw.set_window_pos(self._win, 400, 200)
        # Make the window's context current
        glfw.make_context_current(self._win)

        # self._renderer = GlfwRenderer(self._win)

        # Set background colour, or colour when nothing rendered
        gl.glClearColor(0.5, 0.5, 1., 1)
        if render:
            self.render = render
        else:
            self.render = self.defaultRender
        # Handle key presses with a callback MUST be run after renderer initialisation for some reason
        # glfw.set_key_callback(self._win, self.key_callback)

    def defaultRender(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glClearColor(0.5, 0.5, 1., 1)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)

    def key_callback(window, key, scancode, action, mode, extra):
        if (key == glfw.KEY_ESCAPE and action == glfw.PRESS):
            glfw.set_window_should_close(window, True)

    def main(self):
        #  How often to swap the frame buffers
        glfw.swap_interval(1)

        gl.glDisable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)

        # Loop until window close flag is set.
        while not glfw.window_should_close(self._win):
            width, height = glfw.get_framebuffer_size(self._win)
            # Render here
            # imgui.new_frame()
            # imgui.begin("Debug window", True)
            # imgui.text("Test text")
            # imgui.end()

            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            self.render(width, height)
            # imgui.render()
            # self._renderer.render(imgui.get_draw_data())

            # Poll for process events - MUST HAVE, or window hangs
            glfw.poll_events()

            # swap front and back buffers
            glfw.swap_buffers(self._win)

            # self._renderer.process_inputs()

        # self._renderer.shutdown()

        # Must terminate glfw before exiting.
        # This will destroy any remaining windows, and released allocated resources.
        glfw.terminate()


def createAndAddVertexArrayData(vertexArrayObject, data, attributeIndex):
    gl.glBindVertexArray(vertexArrayObject)
    buffer = gl.glGenBuffers(1)
    lu.uploadFloatData(buffer, data)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
    gl.glVertexAttribPointer(attributeIndex, len(
        data[0]), gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    gl.glEnableVertexAttribArray(attributeIndex)

    # Unbind the buffers again to avoid unintentianal GL state corruption (this is something that can be rather inconventient to debug)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

    return buffer


def render(width, height):
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
	    fragmentColor = vec4(1.0);
    }
    """
    gl.glViewport(0, 0, width, height)
    # Set the colour we want the frame buffer cleared to,
    gl.glClearColor(0.2, 0.3, 0.1, 1.0)
    # Tell OpenGL to clear the render target to the clear values for both depth and colour buffers (depth uses the default)
    gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
    verts = drawCircle(28)
    numVerts = len(verts)
    vertsArrayObj = gl.glGenVertexArrays(1)
    createAndAddVertexArrayData(vertsArrayObj, verts, 0)
    shader = sha.Shader(vertexShader, fragmentShader, {
        "positionIn": 0, "normalIn": 1})
    gl.glUseProgram(shader.program)
    gl.glBindVertexArray(vertsArrayObj)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, numVerts)


if __name__ == "__main__":
    window = Window(1280, 720, "Towers of Hanoi", render=render)
    window.main()

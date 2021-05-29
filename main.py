import glfw
import OpenGL.GL as gl

import ObjModel

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

    # magic.drawVertexDataAsTriangles(g_triangleVerts)


class Window:

    def __init__(self, width: int = 1280, height: int = 720, title: str = "Window"):
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

        # Handle key presses with a callback MUST be run after renderer initialisation for some reason
        glfw.set_key_callback(self._win, self.key_callback)

    def key_callback(window, key, scancode, action, mode):
        if (key == glfw.KEY_ESCAPE and action == glfw.PRESS):
            glfw.set_window_should_close(window, True)

    def main(self):
        #  How often to swap the frame buffers
        glfw.swap_interval(1)

        # Loop until window close flag is set.
        while not glfw.window_should_close(self._win):

            # Render here
            # imgui.new_frame()
            # imgui.begin("Debug window", True)
            # imgui.text("Test text")
            # imgui.end()

            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

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


if __name__ == "__main__":
    window = Window(1280, 720, "Towers of Hanoi")
    window.main()

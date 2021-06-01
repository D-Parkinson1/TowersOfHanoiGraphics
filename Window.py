import glfw
from OpenGL.GL import *


class Window:

    def __init__(self, width: int = 1280, height: int = 720, title: str = "Window", render=None, initResources=None):
        # imgui.create_context()

        # Initialise glfw library
        if not glfw.init():
            print("Could not initialise OpenGL context")
            exit(1)

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.SRGB_CAPABLE, 1)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

        # Create a windowed mode window and its OpenGL context
        self._win = glfw.create_window(width, height, title, None, None)
        glfw.set_framebuffer_size_callback(self._win, self.resize)
        if not self._win:
            glfw.terminate()
            print("Could nto initialise window")
            exit(1)

        glfw.set_window_pos(self._win, 400, 200)
        # Make the window's context current
        glfw.make_context_current(self._win)

        # self._renderer = GlfwRenderer(self._win)

        # Set background colour, or colour when nothing rendered

        if render:
            self.render = render
        else:
            self.render = self.defaultRender

        self.initResources = initResources
        # Handle key presses with a callback MUST be run after renderer initialisation for some reason
        # glfw.set_key_callback(self._win, self.key_callback)

    def defaultRender(self, width, height):
        glViewport(0, 0, width, height)
        glClearColor(0.529, 0.808, .922, 1)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    def key_callback(window, key, scancode, action, mode, extra):
        if (key == glfw.KEY_ESCAPE and action == glfw.PRESS):
            glfw.set_window_should_close(window, True)

    def resize(self, window, width, height):
        glViewport(0, 0, width, height)

    def processInput(self):
        if (glfw.get_key(self._win, glfw.KEY_ESCAPE) == glfw.PRESS):
            glfw.set_window_should_close(self._win, True)

    def main(self):
        #  How often to swap the frame buffers
        glfw.swap_interval(1)

        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        if self.initResources:
            self.initResources()

        # Loop until window close flag is set.
        while not glfw.window_should_close(self._win):
            self.processInput()
            width, height = glfw.get_framebuffer_size(self._win)
            # Render here
            # imgui.new_frame()
            # imgui.begin("Debug window", True)
            # imgui.text("Test text")
            # imgui.end()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.render(width, height)
            # imgui.render()
            # self._renderer.render(imgui.get_draw_data())

            # swap front and back buffers
            glfw.swap_buffers(self._win)
            # Poll for process events - MUST HAVE, or window hangs
            glfw.poll_events()

            # self._renderer.process_inputs()

        # self._renderer.shutdown()

        # Must terminate glfw before exiting.
        # This will destroy any remaining windows, and released allocated resources.
        glfw.terminate()

import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer


class Window:

    def __init__(self, width: int = 1280, height: int = 720, title: str = "Window"):
        imgui.create_context()

        # Initialise glfw library
        if not glfw.init():
            print("Could not initialise OpenGL context")
            exit(1)

        # Create a windowed mode window and its OpenGL context
        self._win = glfw.create_window(
            width, height, title, None, None)

        if not self._win:
            glfw.terminate()
            print("Could nto initialise window")
            exit(1)

        glfw.set_window_pos(self._win, 400, 200)
        # Make the window's context current
        glfw.make_context_current(self._win)

        self._renderer = GlfwRenderer(self._win)

        # Handle key presses with a callback MUST be run after renderer initialisation for some reason
        glfw.set_key_callback(self._win, self.key_callback)

    def key_callback(window, key, scancode, action, mode):
        if (key == glfw.KEY_ESCAPE and action == glfw.PRESS):
            glfw.set_window_should_close(window, True)

    def main(self):
        # Loop until window close flag is set.
        while not glfw.window_should_close(self._win):

            # Render here
            imgui.new_frame()
            imgui.begin("Debug window", True)
            imgui.text("Test text")
            imgui.end()

            gl.glClearColor(1., 1., 1., 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            imgui.render()
            self._renderer.render(imgui.get_draw_data())
            # swap front and back buffers
            glfw.swap_buffers(self._win)
            # Poll for process events - MUST HAVE, or window hangs
            glfw.poll_events()

            self._renderer.process_inputs()

        self._renderer.shutdown()
        # Must terminate glfw before exiting.
        # This will destroy any remaining windows, and released allocated resources.
        glfw.terminate()


if __name__ == "__main__":
    window = Window(1280, 720, "Towers of Hanoi")
    window.main()

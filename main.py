
from SkyBox import SkyBox
import glfw
from Camera import Camera, CameraMovement
from LightSource import LightSource
from Texture import Texture
from ctypes import c_float, c_void_p
from OpenGL.GL import *
import ObjModel as Obj

from lab_utils import Mat3, inverse, make_perspective, make_rotation_x, make_rotation_y, make_rotation_z, transpose, vec3, Mat4, make_lookAt, make_scale, make_translation

from Shader import Shader
from Window import Window
# import imgui
# from imgui.integrations.glfw import GlfwRenderer
from math import radians, sin, cos, pi


class Hanoi:
    # coords, colours, texcoords
    # vertices = [
    #     0.5,  0.5, 0.0,  1.0, 0.0, 0.0,  1.0, 1.0,
    #     0.5, -0.5, 0.0,  0.0, 1.0, 0.0,  1.0, 0.0,
    #     -0.5, -0.5, 0.0,  0.0, 0.0, 1.0,  0.0, 0.0,
    #     -0.5,  0.5, 0.0,  1.0, 1.0, 0.0,  0.0, 1.0
    # ]
    # indices = [
    #     0, 1, 3,
    #     1, 2, 3
    # ]
    # cubeVertsTextureNormal = [
    #     -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,
    #     0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0,
    #     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
    #     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
    #     -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0,
    #     -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,

    #     -0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 0.0,
    #     0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 0.0,
    #     0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 1.0,
    #     0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 1.0,
    #     -0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 1.0,
    #     -0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 0.0,

    #     -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0,
    #     -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  1.0, 1.0,
    #     -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0,
    #     -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0,
    #     -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  0.0, 0.0,
    #     -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0,

    #     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0,
    #     0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 1.0,
    #     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
    #     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
    #     0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 0.0,
    #     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0,

    #     -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,
    #     0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0,
    #     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
    #     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
    #     -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0, 0.0,
    #     -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,

    #     -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0,
    #     0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0, 1.0,
    #     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
    #     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
    #     -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 0.0,
    #     -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0
    # ]

    # cubePositions = [
    #     vec3(0.0,  0.0,  0.0),
    #     vec3(2.0,  5.0, -15.0),
    #     vec3(-1.5, -2.2, -2.5),
    #     vec3(-3.8, -2.0, -12.3),
    #     vec3(2.4, -0.4, -3.5),
    #     vec3(-1.7,  3.0, -7.5),
    #     vec3(1.3, -2.0, -2.5),
    #     vec3(1.5,  2.0, -2.5),
    #     vec3(1.5,  0.2, -1.5),
    #     vec3(-1.3,  1.0, -1.5)
    # ]

    def __init__(self, width=800, height=800, numRings=5):
        self.window = Window(width, height, "Towers of Hanoi", render=self.render,
                             initResources=self.initResources, processInput=self.processInput)
        # Capture the mosuse
        glfw.set_input_mode(self.window._win, glfw.CURSOR, glfw.CURSOR_DISABLED)

        # Callbacks for mouse input
        glfw.set_cursor_pos_callback(self.window._win, self.mouseCallback)
        glfw.set_scroll_callback(self.window._win, self.scrollCallback)

        # Last camera position
        self.lastX = width / 2
        self.lastY = height / 2
        # First mouse move
        self.firstMouse = True
        self.deltaTime = 0
        self.lastFrame = 0

        # Should the spotlight be on
        self.spotLight = True
        # Did we just change spotlight state
        self.justChanged = False

        self.pointLights = []
        self.camera = Camera(vec3(-5, 2.5, 0), yawDeg=0)

        self.numRings = numRings

        self.skybox = SkyBox('textures/skybox/')

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
        if(glfw.get_key(self.window._win, glfw.KEY_SPACE) == glfw.PRESS):
            if not self.justChanged:
                self.spotLight = not self.spotLight
                self.justChanged = True
        if(glfw.get_key(self.window._win, glfw.KEY_SPACE) == glfw.RELEASE):
            self.justChanged = False

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

    def initResources(self):
        # Set the colour we want the frame buffer cleared to,
        glClearColor(0.529, 0.808, .922, 1)
        # Tell OpenGL to clear the render target to the clear values for both depth and colour buffers (depth uses the default)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        self.shader = Shader(vertFile='shaders/lightVert.glsl',
                             fragFile='shaders/lightFrag.glsl')

        # Constant Unifroms are set here
        # If a uniform can change, it's set in render
        self.shader.setUniform("spotLight.ambient", vec3(0.0))
        self.shader.setUniform("spotLight.diffuse", vec3(1.0))
        self.shader.setUniform("spotLight.specular", vec3(1.0))
        self.shader.setUniform("spotLight.constant", 1.0)
        self.shader.setUniform("spotLight.linear", 0.09)
        self.shader.setUniform("spotLight.quadratic", 0.032)
        self.shader.setUniform("spotLight.cutOff", cos(radians(12.5)))
        self.shader.setUniform("spotLight.outerCutOff", cos(radians(15.0)))
        self.shader.setUniform("spotLight.on", self.spotLight)  # Will change, but needs initialisation
        # self.shader.setUniform("material.shininess", 32.0)

        # Directional light
        self.shader.setUniform("dirLight.direction", vec3(-0.2, -1.0, -0.3))
        self.shader.setUniform("dirLight.ambient", vec3(0.25))
        self.shader.setUniform("dirLight.diffuse", vec3(0.4))
        self.shader.setUniform("dirLight.specular", vec3(0.5))

        self.pointLights.append(LightSource(vec3(1.0, 0.5, 3.0), None, vec3(0.83, 0.98, 1.0)))
        self.pointLights.append(LightSource(vec3(0.0, 3.0, 0.0), None, vec3(0.25, 0.25, 1.0)))
        self.pointLights.append(LightSource(vec3(-0.2, -2, -1.5), None, vec3(1.0, 0.3, 0.11)))
        self.pointLights.append(LightSource(vec3(2.0, 3, -3.0), None, vec3(0.25, 1.0, 0.11)))

        self.objects = []

        self.table = Obj.ObjModel('objects/table.obj', self.shader)

        rods = []
        for i in range(3):
            rod = Obj.ObjModel('objects/rod.obj', self.shader)
            rod.position = vec3(0.0, self.table.height, -1.0 + i)
            rods.append(rod)
            self.table.addChild(rod)

        prevPos = rods[0].position
        for i in range(self.numRings):
            if i % 2:
                torus = Obj.ObjModel('objects/torus.obj', self.shader, scale=(1-i/10))
            else:
                torus = Obj.ObjModel('objects/metal_torus.obj', self.shader, scale=(1-i/10))

            if i == 0:
                torus.position = prevPos
            else:
                torus.position = prevPos + vec3(0.0, torus.height, 0.0)
            prevPos = torus.position
            self.objects.append(torus)

        self.objects.append(self.table)

        # For wireframe
        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    def render(self, width, height):
        currentFrame = glfw.get_time()
        self.deltaTime = currentFrame - self.lastFrame
        self.lastFrame = currentFrame

        glClearColor(0.529, 0.808, .922, 1)
        # Tell OpenGL to clear the render target to the clear values for both depth and colour buffers (depth uses the default)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        # Calculate transformation matrices
        model = Mat4()
        view = self.camera.getViewMatrix()
        projection = make_perspective(self.camera.zoom, width/height, 0.1, 100)

        self.shader.use()
        self.shader.setUniform("model", model)
        self.shader.setUniform("normalMat", Mat3(transpose(inverse(model))))
        self.shader.setUniform("view", view)
        self.shader.setUniform("projection", projection)
        self.shader.setUniform("viewPos", self.camera.position)

        # Point lights
        for i in range(len(self.pointLights)):
            light = self.pointLights[i]
            self.shader.setUniform("pointLights[%s].position" % i, light.position)
            self.shader.setUniform("pointLights[%s].ambient" % i, vec3(0.05)*light.colour)
            self.shader.setUniform("pointLights[%s].diffuse" % i, vec3(0.8)*light.colour)
            self.shader.setUniform("pointLights[%s].specular" % i, vec3(1.0)*light.colour)
            self.shader.setUniform("pointLights[%s].constant" % i, 1.0)
            self.shader.setUniform("pointLights[%s].linear" % i, 0.09)
            self.shader.setUniform("pointLights[%s].quadratic" % i, 0.032)

            light.draw(projection, view)

        # Spotlight
        if (self.spotLight):
            self.shader.setUniform("spotLight.position", self.camera.position)
            self.shader.setUniform("spotLight.direction", self.camera.front)

        # Only update uniform when needed
        if self.justChanged:
            self.shader.setUniform("spotLight.on", self.spotLight)

        for obj in self.objects:
            obj.render(transforms={"view": view, "projection": projection})

        # Render cubemap/skybox last
        self.skybox.draw(view, projection)


if __name__ == "__main__":
    project = Hanoi()
    project.start()

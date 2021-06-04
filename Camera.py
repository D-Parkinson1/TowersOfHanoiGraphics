from enum import Enum
from lab_utils import cross, make_lookAt, normalize, vec3
from math import sin, cos, radians


class CameraMovement(Enum):
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4


class Camera:
    def __init__(self, pos: vec3, up=vec3(0, 1, 0), yawDeg=-90, pitchDeg=0.0):
        self.front = vec3(0, 0, -1)
        self.moveSpeed = 2.5
        self.mouseSensitivity = 0.1
        self.zoom = 45
        self.position = pos
        self.worldUp = up
        self.yaw = yawDeg
        self.pitch = pitchDeg
        self.calcPosVectors()

    def calcPosVectors(self):
        x = cos(radians(self.yaw)) * cos(radians(self.pitch))
        y = sin(radians(self.pitch))
        z = sin(radians(self.yaw)) * cos(radians(self.pitch))
        self.front = normalize(vec3(x, y, z))
        self.right = normalize(cross(self.front, self.worldUp))
        self.up = normalize(cross(self.right, self.front))

    def getViewMatrix(self):
        return make_lookAt(self.position, self.position + self.front, self.up)

    def processKeyboard(self, direction, dt):
        velocity = self.moveSpeed * dt
        if (direction == CameraMovement.FORWARD):
            self.position += self.front * velocity
        if (direction == CameraMovement.BACKWARD):
            self.position -= self.front * velocity
        if (direction == CameraMovement.LEFT):
            self.position -= self.right * velocity
        if (direction == CameraMovement.RIGHT):
            self.position += self.right * velocity

    def processMouse(self, x, y, constrainPitch=True):
        x *= self.mouseSensitivity
        y *= self.mouseSensitivity

        self.yaw += x
        self.pitch += y

        if (constrainPitch):
            if (self.pitch > 89):
                self.pitch = 89
            if (self.pitch < -89):
                self.pitch = -89
        self.calcPosVectors()

    def processMouseScroll(self, yOffset):
        self.zoom -= yOffset

        if (self.zoom < 1):
            self.zoom = 1
        if (self.zoom > 45):
            self.zoom = 45

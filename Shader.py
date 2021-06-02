from OpenGL.GL import *


class Shader:

    def __init__(self, vertFile='shaders/vertex.glsl', fragFile='shaders/fragment.glsl'):
        # , attribLocs=None, fragDataLocs={}):

        self.vertexFile = vertFile
        self.fragmentFile = fragFile
        vertexShader = ""
        with open(vertFile) as f:
            vertexShader = f.read()
        fragmentShader = ""
        with open(fragFile) as f:
            fragmentShader = f.read()
        vertexShader = self.compileShader(vertexShader, GL_VERTEX_SHADER)
        fragmentShader = self.compileShader(fragmentShader, GL_FRAGMENT_SHADER)

        self.program = glCreateProgram()

        glAttachShader(self.program, vertexShader)
        glAttachShader(self.program, fragmentShader)

        # if attribLocs:
        #     self.bindLocations(attribLocs, fragDataLocs)

        glLinkProgram(self.program)

        if glGetProgramiv(self.program, GL_LINK_STATUS) != GL_TRUE:
            err = glGetProgramInfoLog(self.program).decode()
            print("SHADER PROGRAM LINKER ERROR: '%s'" % err)
            # Automatically detaches shaders, but won't delete
            glDeleteProgram(self.program)
            glDeleteShader(vertexShader)
            glDeleteShader(fragmentShader)
            return None

        glDeleteShader(vertexShader)
        glDeleteShader(fragmentShader)

    def compileShader(self, source, shaderType):
        try:
            shader = glCreateShader(shaderType)
            glShaderSource(shader, source)
            glCompileShader(shader)

            if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
                shaderTypeStr = {GL_VERTEX_SHADER: "VERTEX",
                                 GL_FRAGMENT_SHADER: "FRAGMENT", GL_COMPUTE_SHADER: "COMPUTE"}
                err = self.getShaderInfoLog(shader)
                print("%s SHADER COMPILE ERROR: '%s'" %
                      (shaderTypeStr.get(shaderType, "??"), err))
                raise RuntimeError('Shader compilation failed: %s' % (err))
            return shader
        except Exception:
            glDeleteShader(shader)
            raise

    def use(self):
        glUseProgram(self.program)

    def setInt(self, name, value: int):
        glUniform1i(glGetUniformLocation(self.program, name), value)

    def setBool(self, name, value: bool):
        glUniform1i(glGetUniformLocation(self.program, name), value)

    def setFloat(self, name, value: float):
        glUniform1f(glGetUniformLocation(self.program, name), value)

    def getShaderInfoLog(self, obj):
        logLength = glGetShaderiv(obj, GL_INFO_LOG_LENGTH)

        if logLength > 0:
            return glGetShaderInfoLog(obj).decode()

        return ""

    def attributeLocation(self, name):
        return glGetAttribLocation(self.program, name)

    # def bindLocations(self, attribLocs, fragDataLocs):
    #     # Link the attribute names we used in the vertex shader to the integer index
    # for name, loc in attribLocs.items():
    #     glBindAttribLocation(self.program, loc, name)

    #     # If we have multiple images bound as render targets, we need to specify which
    #     # 'out' variable in the fragment shader goes where in this case it is totally redundant
    # # as we only have one (the default render target, or frame buffer) and the default binding is always zero.
    # for name, loc in fragDataLocs.items():
    #     glBindFragDataLocation(self.program, loc, name)

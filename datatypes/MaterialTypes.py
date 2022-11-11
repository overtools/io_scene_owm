from .CommonTypes import OWMFile

class OWMATHeader:
    def __init__(self, major, minor, type):
        self.major = major
        self.minor = minor
        self.type = type

class OWMATModelLook(OWMFile):
    def __init__(self, filename):
        super().__init__(filename)
        self.materials = {}

class OWMATMaterial(OWMFile):
    def __init__(self, textureCount, staticInputCount, shader):
        super().__init__()
        self.staticInputCount = staticInputCount
        self.textureCount = textureCount
        self.textures = []
        self.shader = shader
        self.staticInputs = {}

class OWMATMaterialTexture(OWMFile):
    def __init__(self, path, key, flag=0):
        super().__init__(path)
        self.flag = flag
        self.key = key
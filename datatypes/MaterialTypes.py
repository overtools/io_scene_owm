from ..readers import PathUtil

class OWMATFile:
    def __init__(self, guid, materials, keys=None):
        self.GUID = guid
        self.materials = materials
        self.keys = keys

class OWMATMaterial:
    def __init__(self, key, guid, textureCount, textures, shader=0, staticInputs={}):
        self.key = key
        self.GUID = guid
        self.textureCount = textureCount
        self.textures = textures
        self.shader = shader
        self.staticInputs = staticInputs

class OWMATMaterialTexture:
    def __init__(self, path, flag, key):
        self.path = path
        self.GUID = PathUtil.nameFromPath(path)
        self.flag = flag
        self.key = key
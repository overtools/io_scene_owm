from .CommonTypes import OWMFile

class OWMAPFile(OWMFile):
    def __init__(self, header, filepath):
        super().__init__(filepath)
        self.header = header
        self.objects = []
        self.details = []
        self.lights = []
        self.sounds = []


class OWMAPHeader:
    def __init__(self, major, minor, name, objectCount, detailCount, lightCount):
        self.major = major
        self.minor = minor
        self.name = name
        self.objectCount = objectCount
        self.detailCount = detailCount
        self.lightCount = lightCount
        self.soundCount = 0


class OWMAPObject:
    def __init__(self, model, entityCount):
        self.model = OWMFile(model)
        self.entityCount = entityCount
        self.entities = []


class OWMAPEntity:
    def __init__(self, material, recordCount):
        self.material = OWMFile(material)
        self.recordCount = recordCount
        self.records = []


class OWMAPRecord:
    def __init__(self, position, scale, rotation):
        self.position = position
        self.scale = scale
        self.rotation = rotation


class OWMAPDetail:
    def __init__(self, model, material, record):
        self.model = OWMFile(model)
        self.material = OWMFile(material)
        self.record = record


class OWMAPSound:
    def __init__(self, position, soundCount, sounds):
        self.position = position
        self.soundCount = soundCount
        self.sounds = []


class OWMAPLight:
    def __init__(self, position, rotation, typ, fov, color, intensity, projectionTextures):
        self.position = position
        self.rotation = rotation
        self.type = typ[0]
        self.fov = fov[0]
        self.color = color
        self.intensity = intensity[0]
        self.textures = projectionTextures

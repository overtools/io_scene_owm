from ..readers import PathUtil


class OWMAPFile:
    def __init__(self, header, objects, details, lights=list(), sounds=list()):
        self.header = header
        self.objects = objects
        self.details = details
        self.lights = lights
        self.sounds = sounds


class OWMAPHeader:
    def __init__(self, major, minor, name, objectCount, detailCount, lightCount=0, soundCount=0):
        self.major = major
        self.minor = minor
        self.name = name
        self.objectCount = objectCount
        self.detailCount = detailCount
        self.lightCount = lightCount
        self.soundCount = soundCount


class OWMAPObject:
    def __init__(self, model, entityCount, entities):
        self.model = PathUtil.normPath(model)
        self.modelGUID = PathUtil.nameFromPath(model)
        self.entityCount = entityCount
        self.entities = entities


class OWMAPEntity:
    def __init__(self, material, recordCount, records):
        self.material = PathUtil.normPath(material) if material else None
        self.materialGUID = PathUtil.nameFromPath(material) if material else None
        self.recordCount = recordCount
        self.records = records


class OWMAPRecord:
    def __init__(self, position, scale, rotation):
        self.position = position
        self.scale = scale
        self.rotation = rotation

    def __str__(self):
        return "map record"

    def __repr__(self):
        return "0"


class OWMAPDetail:
    def __init__(self, model, material, record):
        self.model = PathUtil.normPath(model)
        self.modelGUID = PathUtil.nameFromPath(model)
        self.material = PathUtil.normPath(material) if material else None
        self.materialGUID = PathUtil.nameFromPath(material) if material else None
        self.record = record


class OWMAPSound:
    def __init__(self, position, soundCount, sounds=list()):
        self.position = position
        self.soundCount = soundCount
        self.sounds = sounds


class OWMAPLight:
    defaultEx = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1, 1.0, 0, 0, 0, 0, 0,0, 0, 0, 0]

    def __init__(self, position, rotation, typ, fov, color, ex=defaultEx):
        self.position = position
        self.rotation = rotation
        self.type = typ
        self.fov = fov
        self.color = color
        self.ex = ex

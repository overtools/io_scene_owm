from .blender import BLMap as blenderMap
from ..readers import OWMapReader


class MapTree:
    def __init__(self):
        self.modelFilepaths = {}
        self.modelLookPaths = {}
        self.models = {}
        self.objects = {}
        self.details = set()
        self.lights = False

    def buildTreeFromObjects(self, mapData):
        for obj in mapData.objects:
            self.modelFilepaths.setdefault(obj.model.GUID, obj.model.filepath)

            self.objects.setdefault(obj.model.GUID, {})
            for entity in obj.entities:
                self.modelLookPaths.setdefault(entity.material.GUID, entity.material.filepath)

                self.objects[obj.model.GUID].setdefault(entity.material.GUID, [])
                self.objects[obj.model.GUID][entity.material.GUID] += entity.records

    def buildTreeFromDetails(self, mapData):
        for prop in mapData.details:
            self.details.add(prop.model.GUID)
            self.modelFilepaths.setdefault(prop.model.GUID, prop.model.filepath)
            self.modelLookPaths.setdefault(prop.material.GUID, prop.material.filepath)

            self.objects.setdefault(prop.model.GUID, {})
            self.objects[prop.model.GUID].setdefault(prop.material.GUID, [])
            self.objects[prop.model.GUID][prop.material.GUID].append(prop.record)

    def loadLights(self, data):
        if data.lights:
            self.lights = set(data.lights)


def init(filename, mapSettings, modelSettings, lightSettings, entitySettings):
    print("[owm]: Reading map data")
    data = OWMapReader.read(filename)
    if not data: return None
    mapName = data.header.name
    if len(mapName) == 0:
        mapName = data.GUID

    print("[owm]: Building map tree")
    mapTree = MapTree()

    if mapSettings.importObjects:
        mapTree.buildTreeFromObjects(data)

    if mapSettings.importDetails:
        mapTree.buildTreeFromDetails(data)
    
    if mapSettings.importLights:
        mapTree.loadLights(data)
    
    print("[owm]: {} Models to load, {} material looks".format(len(mapTree.modelFilepaths),len(mapTree.modelLookPaths)))

    # print(mapTree.modelLookPaths)

    blenderMap.init(mapTree, mapName, data.filepath, mapSettings, modelSettings, entitySettings, lightSettings)

    """name = data.header.name
    if len(name) == 0:
        name = os.path.splitext(file)[0]"""

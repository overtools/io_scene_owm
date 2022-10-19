from .blender import BLMap as blenderMap
from ..readers import OWMapReader
from ..readers import PathUtil


class MapTree:
    def __init__(self):
        self.modelFilepaths = {}
        self.modelLookPaths = {}
        self.models = {}
        self.objects = {}
        self.details = set()

    def buildTreeFromObjects(self, mapData):
        for obj in mapData.objects:
            self.modelFilepaths.setdefault(obj.modelGUID, obj.model)

            self.objects.setdefault(obj.modelGUID, {})
            for entity in obj.entities:
                self.modelLookPaths.setdefault(entity.materialGUID, entity.material)

                self.objects[obj.modelGUID].setdefault(entity.materialGUID, [])
                self.objects[obj.modelGUID][entity.materialGUID] += entity.records

    def buildTreeFromDetails(self, mapData):
        for prop in mapData.details:
            self.details.add(prop.modelGUID)
            self.modelFilepaths.setdefault(prop.modelGUID, prop.model)
            self.modelLookPaths.setdefault(prop.materialGUID, prop.material)

            self.objects.setdefault(prop.modelGUID, {})
            self.objects[prop.modelGUID].setdefault(prop.materialGUID, [])
            self.objects[prop.modelGUID][prop.materialGUID].append(prop.record)


def init(filename, mapSettings, modelSettings, lightSettings, entitySettings):
    print("[owm]: Reading map data")
    data = OWMapReader.read(filename)
    if not data: return None
    mapName = data.header.name
    if len(mapName) == 0:
        mapName = PathUtil.pathText(filename)

    print("[owm]: Building map tree")
    mapTree = MapTree()

    if mapSettings.importObjects:
        mapTree.buildTreeFromObjects(data)

    if mapSettings.importDetails:
        mapTree.buildTreeFromDetails(data)
    
    
    print("[owm]: {} Models to load, {} material looks".format(len(mapTree.modelFilepaths),len(mapTree.modelLookPaths)))

    # print(mapTree.modelLookPaths)

    blenderMap.init(mapTree, mapName, PathUtil.pathRoot(filename), mapSettings, modelSettings, entitySettings)

    """name = data.header.name
    if len(name) == 0:
        name = os.path.splitext(file)[0]"""

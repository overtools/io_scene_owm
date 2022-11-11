from ..readers import PathUtil
from .CommonTypes import OWMFile

class EntityData:
    def __init__(self, baseModel, children, name, entityData, childData=None):
        self.baseModel = baseModel
        self.children = children
        self.name = name
        self.entityData = entityData
        self.childData = childData

    def __str__(self):
        return "EntityData {}: {}, {} ({})".format(self.name, self.baseModel, self.children, len(self.children))


class OWEntityFile(OWMFile):
    def __init__(self, header):
        super().__init__(GUID=header.GUID)
        self.header = header
        self.model = None
        self.effect = None
        self.modelLook = None
        self.index = header.index
        self.modelIndex = header.modelIndex
        self.effectIndex = header.effectIndex
        self.children = []

    def fixPaths(self, filename):
        self.setPath(filename)
        entRootPath = PathUtil.pathRoot(filename)
        if self.header.modelGUID:
            self.model = OWMFile(PathUtil.buildAssetPath(entRootPath, self.header.relativePath, PathUtil.AssetTypes.Model, self.header.modelGUID))
        if self.header.modelLook:
            self.modelLook = OWMFile(PathUtil.buildAssetPath(PathUtil.pathRoot(self.model.filepath), "", PathUtil.AssetTypes.ModelLook, self.header.modelLook))
        if self.header.effectGUID:
            self.effect = OWMFile(PathUtil.buildAssetPath(entRootPath, self.header.relativePath, PathUtil.AssetTypes.Effect, self.header.effectGUID))

        for child in self.children:
            if child.filepath:
                child.filepath = PathUtil.buildAssetPath(entRootPath, PathUtil.joinPath("..",".."), PathUtil.AssetTypes.Entity, child.filepath)

class OWEntityHeader:
    def __init__(self, magic, major, minor, guid, modelGUID, effectGUID, idx, modelIndex, effectIndex, childCount):
        self.magic = magic
        self.major = major
        self.minor = minor
        self.GUID = guid
        self.modelGUID = modelGUID
        self.effectGUID = effectGUID
        self.childCount = childCount
        self.index = idx
        self.modelIndex = modelIndex
        self.effectIndex = effectIndex
        self.modelLook = None
        self.relativePath = PathUtil.joinPath("..","..")


class OWEntityChild(OWMFile):
    def __init__(self, file, hardpoint, var, hpIndex, varIndex, attachment):
        super().__init__(file)
        self.hardpoint = hardpoint
        self.var = var
        self.attachment = attachment
        self.varIndex = varIndex
        self.hardpointIndex = hpIndex

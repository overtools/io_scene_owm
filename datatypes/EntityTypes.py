from ..readers import PathUtil


class EntityData:
    def __init__(self, baseModel, children, name, entityData, childData=None):
        self.baseModel = baseModel
        self.children = children
        self.name = name
        self.entityData = entityData
        self.childData = childData

    def __str__(self):
        return "EntityData {}: {}, {} ({})".format(self.name, self.baseModel, self.children, len(self.children))


class OWEntityFile:
    def __init__(self, header, file, model, effect, idx, modelIndex, effectIndex, children):
        self.header = header
        self.file = file
        self.model = model
        self.effect = effect
        self.index = idx
        self.model_index = modelIndex
        self.effect_index = effectIndex
        self.children = children


class OWEntityHeader:
    def __init__(self, magic, major, minor, guid, modelGUID, effectGUID, idx, modelIndex, effectIndex, childCount):
        self.magic = magic
        self.major = major
        self.minor = minor
        self.guid = guid
        self.modelGUID = modelGUID
        self.effectGUID = effectGUID
        self.childCount = childCount
        self.index = idx
        self.model_index = modelIndex
        self.effect_index = effectIndex


class OWEntityChild:
    def __init__(self, file, hardpoint, var, hpIndex, varIndex, attachment):
        self.file = PathUtil.normPath(file)
        self.guid = PathUtil.nameFromPath(file)
        self.hardpoint = hardpoint
        self.var = var
        self.attachment = attachment
        self.varIndex = varIndex
        self.hardpoint_index = hpIndex

    def __repr__(self):
        return '<OWEntityChild: {} (attached to:{})>'.format(self.file, self.attachment)

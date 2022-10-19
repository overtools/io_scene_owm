from . import BLModel
from ...datatypes.EntityTypes import EntityData
from ...readers import OWEntityReader
from ...readers import PathUtil


def readEntity(filename, modelSettings, entitySettings, childData=None):
    data = OWEntityReader.read(filename)
    if not data: return None

    children = []

    baseModel = None
    if data.model:
        # print(data.model)
        baseModel = BLModel.readMDL(PathUtil.getModelPath(filename, data.model), modelSettings)

    if entitySettings.importChildren:
        for child in data.children:
            childPath = PathUtil.getEntPath(filename, child.file)

            children.append(readEntity(childPath, modelSettings, entitySettings, child))

            # TODO effects?

    return EntityData(baseModel, children, PathUtil.nameFromPath(filename), data, childData)

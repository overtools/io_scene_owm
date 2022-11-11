from . import BLModel
from ...datatypes.EntityTypes import EntityData
from ...readers import OWEntityReader


def readEntity(filename, modelSettings, entitySettings, childData=None):
    data = OWEntityReader.read(filename)
    if not data: return None

    children = []

    baseModel = None
    if data.model:
        # print(data.model)
        baseModel = BLModel.readMDL(data.model.filepath, modelSettings)

    if entitySettings.importChildren:
        for child in data.children:

            children.append(readEntity(child.filepath, modelSettings, entitySettings, child))

            # TODO effects?

    return EntityData(baseModel, children, data.header.GUID, data, childData)

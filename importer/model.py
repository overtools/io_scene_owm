from .blender import BLUtils
from .blender import BLModel
from .blender.BLMaterial import BlenderMaterialTree
from ..readers import PathUtil


def init(filename, modelSettings):
    modelData = BLModel.readMDL(filename, modelSettings)
    if not modelData:
        return

    modelFolder = modelData.armature if modelData.armature else BLUtils.createFolder(PathUtil.nameFromPath(filename), False)
    #if not modelData.armature:
    BLUtils.linkScene(modelFolder)

    if modelSettings.importMaterial:
        modelLook = modelData.meshData.header.material
        #print(modelLook)
        if modelLook: #TODO make it none
            modelLookGUID = PathUtil.nameFromPath(modelLook)
            matTree = BlenderMaterialTree({modelLookGUID: modelLook})
            matTree.bindModelLook(modelData, modelLookGUID)

    for obj in modelData.meshes:
        obj.parent = modelFolder
        BLUtils.linkScene(obj)

    if modelData.empties[0] is not None:  # this will be none if importEmpties is false
        modelData.empties[0].parent = modelFolder
        BLUtils.linkScene(modelData.empties[0])

        for emptyObj in modelData.empties[1].values():
            emptyObj.parent = modelData.empties[0]
            BLUtils.linkScene(emptyObj)
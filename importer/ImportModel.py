from .blender import BLUtils
from .blender import BLModel
from .blender.BLMaterial import BlenderMaterialTree
from ..ui import UIUtil


def init(filenames, modelSettings):
    UIUtil.lock_open_notification = False
    for filename in filenames:
        modelData = BLModel.readMDL(filename, modelSettings)
        if not modelData:
            return

        modelFolder = modelData.armature if modelData.armature else BLUtils.createFolder(modelData.meshData.GUID, False)
        #if not modelData.armature:
        BLUtils.linkScene(modelFolder)
        modelFolder["owm.modelPath"] = modelData.meshData.filepath

        if modelSettings.importMaterial:
            modelLook = modelData.meshData.header.material
            if modelLook: #TODO make it none
                modelFolder["owm.modelLook"] = modelLook.GUID
                matTree = BlenderMaterialTree({modelLook.GUID: modelLook.filepath})
                matTree.bindModelLook(modelData, modelLook.GUID)
                matTree.removeSkeletonNodeTrees()

        for obj in modelData.meshes:
            obj.parent = modelFolder
            BLUtils.linkScene(obj)

        if modelData.empties[0] is not None:  # this will be none if importEmpties is false
            modelData.empties[0].parent = modelFolder
            BLUtils.linkScene(modelData.empties[0])

            for emptyObj in modelData.empties[1].values():
                emptyObj.parent = modelData.empties[0]
                BLUtils.linkScene(emptyObj)

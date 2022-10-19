from mathutils import Matrix

from .blender import BLUtils
from .blender import BLEntity
from .blender.BLMaterial import BlenderMaterialTree
from ..readers import PathUtil


def buildMatPaths(entity):
    paths = {}

    def registerLook(ent):
        if ent.baseModel:
            look = ent.baseModel.meshData.header.material
            modelRootPath = PathUtil.pathRoot(ent.baseModel.meshData.filepath)
            paths.setdefault(PathUtil.nameFromPath(look), PathUtil.makePathAbsolute(modelRootPath, look))

        for child in ent.children:
            registerLook(child)

    registerLook(entity)

    return paths


def init(filename, modelSettings, entitySettings):
    def handleEntityModel(ent, parentFolder, parentEnt=None):
        modelData = ent.baseModel

        # Create Folder (ignores effects for now)
        if ent.entityData.model or len(ent.entityData.children) > 0:  # TODO Effects import, check if they're empty
            entityFolder = BLUtils.createFolder(("Child " if parentEnt else "") + "Entity {}".format(PathUtil.nameFromPath(ent.name)), hide=False,
                link=True)
            entityFolder.parent = parentFolder
            if parentEnt and ent.childData:
                hardpoint = ent.childData.attachment
                #print(hardpoint)
                if parentEnt.baseModel:
                    if hardpoint and hardpoint in parentEnt.baseModel.empties[1]:
                        constraint = entityFolder.constraints.new("COPY_TRANSFORMS")
                        constraint.target = parentEnt.baseModel.empties[1][hardpoint]

        # Deal with model
        if modelData:
            # Put armature inside folder
            if modelData.armature:
                modelData.armature.parent = entityFolder
                BLUtils.linkScene(modelData.armature)

            # Bind materials
            if modelSettings.importMaterial:
                modelLook = modelData.meshData.header.material
                matTree.bindModelLook(modelData, PathUtil.nameFromPath(modelLook))

            # Parent and link meshes
            for obj in modelData.meshes:
                obj.parent = modelData.armature if modelData.armature else entityFolder
                BLUtils.linkScene(obj)

            # Parent and link hardpoints
            if modelData.empties[0] is not None:  # this will be none if importEmpties is false
                modelData.empties[0].parent = modelData.armature if modelData.armature else entityFolder
                BLUtils.linkScene(modelData.empties[0])

                for emptyObj in modelData.empties[1].values():
                    emptyObj.parent = modelData.empties[0]
                    BLUtils.linkScene(emptyObj)

        for child in ent.children:
            handleEntityModel(child, entityFolder, ent)

    entityData = BLEntity.readEntity(filename, modelSettings, entitySettings)
    if not entityData:
        return
    matTree = BlenderMaterialTree(buildMatPaths(entityData))

    handleEntityModel(entityData, None)

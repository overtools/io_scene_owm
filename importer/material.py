from .blender.BLMaterial import BlenderMaterialTree

def init(files):
    matTree = BlenderMaterialTree(files)
    for mat in matTree.blendMaterials.values():
        mat.name = "(Imported) " + mat.name
    matTree.removeSkeletonNodeTrees()
from .blender.BLMaterial import BlenderMaterialTree

def init(filename):
    matTree = BlenderMaterialTree({"virtual": filename})
    for mat in matTree.blendMaterials.values():
        mat.name = "(Imported) " + mat.name
    matTree.removeSkeletonNodeTrees()
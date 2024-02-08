from .blender.BLMaterial import BlenderMaterialTree
from ..ui import UIUtil

def init(files):
    UIUtil.lock_open_notification = False
    matTree = BlenderMaterialTree(files)
    for mat in matTree.blendMaterials.values():
        mat.name = "(Imported) " + mat.name
    matTree.removeSkeletonNodeTrees()

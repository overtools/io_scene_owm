import bpy
from ..readers import PathUtil
import os, json
from . import DatatoolLibUtil

skip = set(["Effects", "Entities", "GUI", "Materials", "ModelLooks", "AnimationEffects", "Spray", "Sound", "Animations"])


class OWMBuildTextureDB(bpy.types.Operator):
    """Indexes all textures on the Datatool Export Path"""
    bl_idname = "owm3.build_tex_db"
    bl_label = "Build Texture DB"

    def execute(self, context):
        db = {}
        def recursiveScan(path):
            for item in os.scandir(path):
                if item.is_dir() and item.name not in skip:
                    recursiveScan(item.path)
                else:
                    if item.name.endswith(".tif") or item.name.endswith(".png") or item.name.endswith(".webp"):
                        db.setdefault(PathUtil.nameFromPath(item.path), item.path.replace(DatatoolLibUtil.getRoot(), ""))
        recursiveScan(DatatoolLibUtil.getRoot())
        json.dump(db,open(PathUtil.joinPath(DatatoolLibUtil.getRoot(),"texture_db.json"),"w"))
        self.report({'INFO'}, 'Indexed {} Textures.'.format(len(db)))  
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)
    
class OWMFixTextures(bpy.types.Operator):
    """Looks through all missing materials and checks against the indexed textures"""
    bl_idname = "owm3.fix_tex"
    bl_label = "Fix Missing Textures"

    def execute(self, context):
        db = json.load(open(PathUtil.joinPath(DatatoolLibUtil.getRoot(),"texture_db.json"), "r"))
        fixed=0
        missing=0
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    if node.image:
                        if not node.image.has_data:
                            guid = PathUtil.nameFromPath(node.image.filepath)
                            if guid in db:
                                node.image.filepath = PathUtil.joinPath(DatatoolLibUtil.getRoot(), db[guid])
                                fixed+=1
                            else:
                                missing+=1
        if fixed > 0 and missing == 0:
            self.report({'INFO'}, 'Fixed {} missing Textures.'.format(fixed))
        elif fixed > 0 or missing > 0:
            self.report({'INFO'}, 'Fixed {} missing Textures. {} Not found'.format(fixed, missing))
        else:
            self.report({'INFO'}, 'Nothing to Fix. ¯\_(ツ)_/¯')
        return {"FINISHED"}

    def invoke(self, context, event):
        if os.path.isfile(PathUtil.joinPath(DatatoolLibUtil.getRoot(),"texture_db.json")):
            return self.execute(context)
        else:
            self.report({'ERROR'}, 'Texture database not found. Run the "Scan Texture Directories" Operator first.')  
            return {'FINISHED'}
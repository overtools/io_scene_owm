import bpy

# todo:
# `from bpy_extras.io_utils import poll_file_object_drop``
# after we can drop 4.2 (added in 4.4)
def poll_file_object_drop(context):
    return context.area and context.area.type == "VIEW_3D"


class IO_FH_owmdl(bpy.types.FileHandler):
    bl_idname = "IO_FH_owmdl"
    bl_label = "owmdl"
    bl_import_operator = "import_mesh.overtools2_model"
    bl_file_extensions = ".owmdl"
 
    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)
    
class IO_FH_owmat(bpy.types.FileHandler):
    bl_idname = "IO_FH_owmat"
    bl_label = "owmdl"
    bl_import_operator = "import_mesh.overtools2_material"
    bl_file_extensions = ".owmat"
 
    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)
    
class IO_FH_owentity(bpy.types.FileHandler):
    bl_idname = "IO_FH_owentity"
    bl_label = "owentity"
    bl_import_operator = "import_mesh.overtools2_entity"
    bl_file_extensions = ".owentity"
 
    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)
    
class IO_FH_owanimclip(bpy.types.FileHandler):
    bl_idname = "IO_FH_owanimclip"
    bl_label = "owanimclip"
    bl_import_operator = "import_mesh.overtools2_animmclip"
    bl_file_extensions = ".owanimclip"
 
    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)
    
class IO_FH_owmap(bpy.types.FileHandler):
    bl_idname = "IO_FH_owmap"
    bl_label = "owmap"
    bl_import_operator = "import_mesh.overtools2_map"
    bl_file_extensions = ".owmap"
 
    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)

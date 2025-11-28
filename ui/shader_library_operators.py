import bpy
from ..importer.blender import shader_library_handler

class OWMShaderLoadOp(bpy.types.Operator):
    """Load OWM Material Library"""
    bl_idname = "owm3.load_library"
    bl_label = "Import OWM Library"

    def execute(self, context):
        shader_library_handler.load_data()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class OWMShaderSaveOp(bpy.types.Operator):
    """Export OWM Material Library"""
    bl_idname = "owm3.save_library"
    bl_label = "Export OWM Library"

    def execute(self, context):
        shader_library_handler.export_overwatch_shaders()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

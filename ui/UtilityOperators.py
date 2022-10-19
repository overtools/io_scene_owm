import bpy
from . import LibraryHandler

class OWMUtilityPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_owm_panel2"
    bl_label = "OWM Tools"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context): return 1

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator(LibraryHandler.OWMLoadOp.bl_idname, text="Import OWM Library", icon="LINK_BLEND")
        row.operator(LibraryHandler.OWMSaveOp.bl_idname, text="Export OWM Library", icon="APPEND_BLEND")
        row = layout.row()
        row.operator(LibraryHandler.OWMLoadJSONOp.bl_idname, text="Import OWM Library from JSON", icon="LINK_BLEND")
        #row = layout.row()
        #row.prop(bpy.context.scene.owm_internal_settings, "b_logsalot", text="Log Map Progress")

        box = layout.box()
        box.label(text="Cleanup")
        row = box.row()
        row.operator(OWMCleanupOp.bl_idname, text="Unused Folder Objects", icon="OBJECT_DATA")
        row = box.row()
        row.operator(OWMCleanupOp.bl_idname, text="Unused Socket Objects", icon="OBJECT_DATA")
        #row.operator(OWMCleanupTexOp.bl_idname, text="Unused Materials", icon="MATERIAL")

class OWMCleanupOp(bpy.types.Operator):
    """Deletes empty objects with no sub objects"""
    bl_idname = "owm.delete_unused_empties"
    bl_label = "Delete Unused Empties"

    def execute(self, context):
        relationships = {} #blender is dum dum and doesn't cache objects children so calling .children kills perf
        folders = set()
        for obj in bpy.data.objects:
            if obj.parent:
                parent = obj.parent.name
                relationships.setdefault(parent, 0)
                relationships[parent] += 1
            if "owm.folder" in obj.keys():
                folders.add(obj)
        toRemove = set()
        for folder in folders:
            if relationships.get(folder.name, 0) == 0:
                toRemove.add(folder)
        bpy.data.batch_remove(toRemove)
        self.report({'INFO'}, "Removed {} empty OWM folders".format(len(toRemove)))
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class OWMCleanupTexOp(bpy.types.Operator):
    """Deletes materials with no owners"""
    bl_idname = "owm.delete_unused_materials"
    bl_label = "Delete Unused Materials"

    def execute(self, context):
        bpyhelper.clean_materials()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)
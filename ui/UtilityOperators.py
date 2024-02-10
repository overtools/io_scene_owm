import bpy
from ..readers import PathUtil
from . import LibraryHandler
from . import Preferences
from . import DatatoolLibHandler
from . import DatatoolLibUtil
from ..importer.blender.BLMaterial import BlenderMaterialTree

class OWMUtilityPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_owm_panel2"
    bl_label = "OWM Tools V3"
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
        if Preferences.getPreferences().devMode:
            row.operator(LibraryHandler.OWMSaveOp.bl_idname, text="Export OWM Library", icon="APPEND_BLEND")
            row = layout.row()
            row.operator(LibraryHandler.OWMLoadJSONOp.bl_idname, text="Import OWM Library from JSON", icon="LINK_BLEND")
        #row = layout.row()
        #row.prop(bpy.context.scene.owm3_internal_settings, "b_logsalot", text="Log Map Progress")

        box = layout.box()
        box.label(text="Cleanup")
        row = box.row()
        row.operator(OWMCleanupOp.bl_idname, text="Unused Folder Objects", icon="OBJECT_DATA")
        row = box.row()
        row.operator(OWMCleanupOp.bl_idname, text="Unused Socket Objects", icon="OBJECT_DATA")
        #row.operator(OWMCleanupTexOp.bl_idname, text="Unused Materials", icon="MATERIAL")

        box = layout.box()
        box.label(text="Material Operators")
        row = box.row()
        row.operator(LibraryHandler.OWMConnectAOOp.bl_idname, text="Connect AO Textures", icon="OBJECT_DATA")
        row.operator(LibraryHandler.OWMDisconnectAOOp.bl_idname, text="Disconnect AO Textures", icon="OBJECT_DATA")
        if DatatoolLibUtil.isPathSet():
            row = box.row()
            row.operator(DatatoolLibHandler.OWMBuildTextureDB.bl_idname, text="Scan Texture Directories (CAN TAKE LONG)", icon="VIEWZOOM")
            
            row = box.row()
            row.operator(DatatoolLibHandler.OWMFixTextures.bl_idname, text="Fix Missing Textures", icon="LINK_BLEND")

class OWMCleanupOp(bpy.types.Operator):
    """Deletes empty objects with no sub objects"""
    bl_idname = "owm3.delete_unused_empties"
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

def getModelFolder(obj):
    if obj.type == 'MESH':
        return obj.parent
    elif obj.type == 'EMPTY':
        if obj.parent is not None:
            if "owm.modelPath" in obj.parent:
                return obj.parent
            if obj.parent.parent is not None:
                if "owm.modelPath" in obj.parent.parent:
                    return obj.parent.parent
        return None
    elif obj.type == 'ARMATURE': #???
        return obj
    return None

class OWMModelLookPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_owmmodellook"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "OWM"
    bl_label = "OWM Model Look Manager"
    
    @classmethod
    def poll(cls, context):
        if context.object:
            if context.object.type == 'MESH':
                return "owm.materialKey" in context.object.data
            if context.object.type == 'EMPTY': #idk yet
                folder = getModelFolder(context.object)
                if folder:
                    return "owm.modelPath" in folder
            if context.object.type == 'ARMATURE':
                return "owm.modelPath" in context.object
        return False

    def draw(self, context):
        layout = self.layout
        folder = getModelFolder(context.object)

        row = layout.row()
        """row.label(text="Current Model Look: {}".format(folder["owm.modelLook"]))
        if "owm.originalModelLook" in folder:
            row = layout.row()
            row.label(text="Original Model Look: {}".format(folder["owm.originalModelLook"]))"""
        
        rootFolder = PathUtil.joinPath(PathUtil.pathRoot(folder["owm.modelPath"]), "ModelLooks")
        if PathUtil.checkExistence(rootFolder):
            row = layout.row()
            row.operator_enum('owm3.change_modellook', 'modelLook')

        row = layout.row()

class OWMChangeModelLookOp(bpy.types.Operator):
    bl_idname = "owm3.change_modellook"
    bl_label = "Change ModelLook"
    __doc__ = bl_label
    bl_options = {'INTERNAL'}

    
    def getModelLooks(self, context):
        folder = getModelFolder(context.object)
        rootFolder = PathUtil.joinPath(PathUtil.pathRoot(folder["owm.modelPath"]), "ModelLooks")
        looks = []
        if PathUtil.checkExistence(rootFolder):
            files = list(PathUtil.listPath(rootFolder))
            for i,look in enumerate(files):
                lookName = look.replace(".owmat","")
                if lookName == folder["owm.modelLook"]:
                    tag = " (selected)"
                elif lookName == folder.get("owm.originalModelLook", ""):
                    tag = " (original)"
                else:
                    tag = ""
                looks.append((look,lookName+tag,"",i))
        return looks
    
    modelLook: bpy.props.EnumProperty(items=getModelLooks)

    def execute(self, context):
        folder = getModelFolder(context.object)

        rootPath = PathUtil.joinPath(PathUtil.pathRoot(folder["owm.modelPath"]), "ModelLooks")
        matTree = BlenderMaterialTree({"virtual": PathUtil.joinPath(rootPath, self.modelLook)}, True)
        if "owm.originalModelLook" not in folder:
            folder["owm.originalModelLook"] = folder["owm.modelLook"]
        elif folder["owm.originalModelLook"] == self.modelLook.replace(".owmat",""):
            del folder["owm.originalModelLook"]
        folder["owm.modelLook"] = self.modelLook.replace(".owmat","")
        if "virtual" in matTree.materialLooks:
            for meshI, blendObj in enumerate([child for child in folder.children if child.type == 'MESH']):
                blendMesh = blendObj.data

                if int(blendMesh.get("owm.materialKey", 0)) in matTree.materialLooks["virtual"].materials:
                    blendMaterial = matTree.blendMaterials[matTree.materialLooks["virtual"].materials[int(blendMesh["owm.materialKey"])]]
                    blendMesh.materials.clear()
                    blendMesh.materials.append(blendMaterial)
                    blendObj.material_slots[0].link = 'OBJECT'
                    blendObj.material_slots[0].material = blendMaterial
        else:
            pass #borked, todo warn
        matTree.removeSkeletonNodeTrees()
        return {"FINISHED"}

    def invoke(self, context, event): # uh idk
        return self.execute(context)

class OWMCleanupTexOp(bpy.types.Operator): #TODO remake this
    """Deletes materials with no owners"""
    bl_idname = "owm3.delete_unused_materials"
    bl_label = "Delete Unused Materials"

    def execute(self, context):
        bpyhelper.clean_materials()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

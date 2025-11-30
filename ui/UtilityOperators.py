import bpy
from ..readers import PathUtil
from . import Preferences
from . import DatatoolLibHandler
from . import DatatoolLibUtil
from ..importer.blender.BLMaterial import BlenderMaterialTree
from .. import shader_metadata
from .shader_library_operators import OWMShaderLoadOp, OWMShaderSaveOp

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
        row.operator(OWMShaderLoadOp.bl_idname, text="Import OWM Library", icon="LINK_BLEND")
        if Preferences.getPreferences().devMode:
            row.operator(OWMShaderSaveOp.bl_idname, text="Export OWM Library", icon="APPEND_BLEND")
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
        row.operator(OWMConnectAOOp.bl_idname, text="Connect AO Textures", icon="OBJECT_DATA")
        row.operator(OWMDisconnectAOOp.bl_idname, text="Disconnect AO Textures", icon="OBJECT_DATA")
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
    bl_options = {'INTERNAL', 'UNDO'}
    
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


def getAOTextures():
    mappings = shader_metadata.get_shader_metadata("Mapping")
    ao = {}
    for tex, mapping in mappings.items():
        if tex == 3761386704: 
            continue
        if "AO" in mapping.colorSockets or "AO" in mapping.alphaSockets or "Blend AO" in mapping.colorSockets:
            ao[str(tex)] = mapping
    return ao

class OWMConnectAOOp(bpy.types.Operator):
    """Connects all AO textures"""
    bl_idname = "owm3.enable_ao"
    bl_label = "Enable AO"
    bl_options = {'UNDO'}

    def execute(self, context):
        aoTexs = getAOTextures()
        connectCount = 0
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue
            if "OverwatchShader" in mat.node_tree.nodes:
                shaderNode = mat.node_tree.nodes["OverwatchShader"]
                aoNodes = [node for node in mat.node_tree.nodes if node.name in aoTexs]
                for node in aoNodes:
                    mapping = aoTexs[node.name]
                    for colorSocket in mapping.colorSockets:
                        if colorSocket in shaderNode.inputs:
                            mat.node_tree.links.new(node.outputs[0], shaderNode.inputs[colorSocket])
                            connectCount+=1
                    for alphaSocket in mapping.alphaSockets:
                        if alphaSocket in shaderNode.inputs:
                            mat.node_tree.links.new(node.outputs[1], shaderNode.inputs[alphaSocket])
                            connectCount+=1
                if "2903569922" in mat.node_tree.nodes and ("43" in shaderNode.label or "217" in shaderNode.label): # hero ao
                    mat.node_tree.links.new(mat.node_tree.nodes["2903569922"].outputs[1], shaderNode.inputs["AO"])
                    connectCount+=1
        self.report({'INFO'}, 'Connected {} AO Textures.'.format(connectCount))                   
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class OWMDisconnectAOOp(bpy.types.Operator):
    """Disconnects all AO textures"""
    bl_idname = "owm3.disable_ao"
    bl_label = "Disable AO"
    bl_options = {'UNDO'}

    def execute(self, context):
        aoTexs = getAOTextures()
        disconnectCount = 0
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue
            if "OverwatchShader" in mat.node_tree.nodes:
                aoNodes = [node for node in mat.node_tree.nodes if node.name in aoTexs]
                for node in aoNodes:
                    for link in node.outputs[0].links:
                        if "AO" in link.to_socket.name:
                            mat.node_tree.links.remove(link)
                        disconnectCount+=1
                    for link in node.outputs[1].links:
                        if "AO" in link.to_socket.name:
                            mat.node_tree.links.remove(link)
                            disconnectCount+=1
                
                shaderNode = mat.node_tree.nodes["OverwatchShader"]
                if "2903569922" in mat.node_tree.nodes and ("43" in shaderNode.label or "217" in shaderNode.label): # hero ao
                    for link in mat.node_tree.nodes["2903569922"].outputs[1].links:
                        mat.node_tree.links.remove(link)
                        disconnectCount+=1
        self.report({'INFO'}, 'Disonnected {} AO Textures.'.format(disconnectCount))                   
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

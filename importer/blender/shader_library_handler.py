import os
import bpy
from .blender_helper import log
from .addon_helper import get_addon_version

def get_library_path():
    return os.path.join(os.path.dirname(__file__), "..", "..", "library.blend")

def load_data():
    try:
        return import_overwatch_shaders()
    except BaseException as e:
        log("failed to load node groups: {}".format(e))

def import_overwatch_shaders():
    log("attempting to import shaders")
    path = get_library_path()
    addon_version = get_addon_version()

    already_appended_nodes = {}
    def check_existing_name(original_name, name):
        if name not in bpy.data.node_groups:
            # doesn't exist
            return False

        node_group = bpy.data.node_groups[name]
        if node_group.get("owm.libVersion", "0.0.0") == addon_version:
            # we already imported this exact version at some other time
            # use it
            already_appended_nodes[original_name] = node_group
            return True
        
        return False
    
    original_node_names = []
    original_text_names = []

    with bpy.data.libraries.load(path, link=False, relative=True) as (data_from, data_to):
        for node_name in data_from.node_groups:
            if not node_name.startswith("OWM: "):
                continue

            if check_existing_name(node_name, node_name):
                continue
            
            # alternate naming scheme for conflicts
            versioned_name = "{} ({})".format(node_name, addon_version)
            if check_existing_name(node_name, versioned_name):
                continue

            # didn't find it anywhere.
            # so we need to copy across this node group
            data_to.node_groups.append(node_name)
            original_node_names.append(node_name)

        for text_name in data_from.texts:
            if not text_name.startswith("OWM: "):
                continue

            if not text_name.endswith(".osl"):
                # we only intend to import shaders
                continue
                    
            data_to.texts.append(text_name)
            original_text_names.append(text_name)
        
        log("newly loaded node groups: %s" % (", ".join(data_to.node_groups)))
        log("newly loaded shader scripts: %s" % (", ".join(data_to.texts)))
        log("existing node groups: %s" % (", ".join(already_appended_nodes.keys())))

    blNodeGroups = dict(zip(original_node_names, data_to.node_groups))
    for original_name, block in blNodeGroups.items():
        block.use_fake_user = True
        block["owm.libVersion"] = addon_version

        if original_name != block.name:
            # blender renamed the block due to conflicts
            # specify exactly which version of the addon this is from
            versioned_name = "{} ({})".format(original_name, addon_version)
            block.name = versioned_name
    
    for original_name, block in already_appended_nodes.items():
        blNodeGroups[original_name] = block

    blTexts = dict(zip(original_text_names, data_to.texts))
    for original_name, block in blTexts.items():
        block.use_fake_user = True
    
    return blNodeGroups

def export_overwatch_shaders():
    log("attempting to export shaders")
    path = get_library_path()
    
    blocks_node = list([node for node in bpy.data.node_groups if node.name.startswith("OWM: ") ])
    for block_node in blocks_node:
        bpy.data.node_groups[block_node.name].use_fake_user = True
    blocks_text = list(
        [text for text in bpy.data.texts if text.name.startswith("OWM: ") and text.name.endswith(".osl")])
    for block_text in blocks_text:
        bpy.data.texts[block_text.name].use_fake_user = True
    blocks = set(blocks_node + blocks_text)
    if len(blocks) > 0:
        log("exported: %s" % (", ".join(map(lambda x: x.name, blocks))))
    bpy.data.libraries.write(path, blocks, fake_user=True, path_remap="RELATIVE_ALL", compress=False)
    log("saved %s" % (path))

class OWMLoadOp(bpy.types.Operator):
    """Load OWM Material Library"""
    bl_idname = "owm3.load_library"
    bl_label = "Import OWM Library"

    def execute(self, context):
        load_data()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class OWMSaveOp(bpy.types.Operator):
    """Export OWM Material Library"""
    bl_idname = "owm3.save_library"
    bl_label = "Export OWM Library"

    def execute(self, context):
        export_overwatch_shaders()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

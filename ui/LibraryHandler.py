import os

import bpy
import json
from . import UtilityOperators

from .. import textureMap

addonVersion = None

def get_library_path():
    return os.path.join(os.path.dirname(__file__), "..\\library.blend")

def create_overwatch_shader():
    print("[owm] attempting to import shaders")
    path = get_library_path()
    nodes = []
    existing = []
    with bpy.data.libraries.load(path, link=False, relative=True) as (data_from, data_to):
        #data_to.node_groups = [node_name for node_name in data_from.node_groups if node_name.startswith("OWM: ")]
        for node_name in data_from.node_groups:
            if node_name.startswith("OWM: "):
                if node_name in bpy.data.node_groups:
                    if bpy.data.node_groups[node_name].get("owm.libVersion", "0.0.0") == addonVersion:
                        existing.append(node_name)
                        continue
                    else:
                        data_to.node_groups.append(node_name)
                        nodes.append(node_name)
                else:
                    if "{} ({})".format(node_name,addonVersion) in bpy.data.node_groups:
                        if bpy.data.node_groups["{} ({})".format(node_name,addonVersion)].get("owm.libVersion", "0.0.0") == addonVersion:
                            existing.append("{} ({})".format(node_name,addonVersion))
                            continue
                    data_to.node_groups.append(node_name)
                    nodes.append(node_name)
                    
        data_to.texts = [text_name for text_name in data_from.texts if
                         not text_name in bpy.data.texts and text_name.startswith("OWM: ") and text_name.endswith(
                             ".osl")]
        
        if len(data_to.node_groups) > 0:
            print("[owm] imported node groups: %s" % (", ".join(data_to.node_groups)))
        if len(data_to.texts) > 0:
            print("[owm] imported scripts: %s" % (", ".join(data_to.texts)))

    blNodeGroups = dict(zip(nodes, data_to.node_groups))

    #blocks = [node for node in bpy.data.node_groups if node.name.startswith("OWM: ")]
    for origName, block in blNodeGroups.items():
        bpy.data.node_groups[block.name].use_fake_user = True

        bpy.data.node_groups[block.name]["owm.libVersion"] = addonVersion

        if origName != block.name:
            newName = "{} ({})".format(origName,addonVersion)
            bpy.data.node_groups[block.name].name = newName
            blNodeGroups[origName] = bpy.data.node_groups[newName]
        else:
            blNodeGroups[origName] = bpy.data.node_groups[block.name]
    
    for node in existing:
        blNodeGroups[node] = bpy.data.node_groups[node]

    blocks = [text for text in bpy.data.texts if text.name.startswith("OWM: ") and text.name.endswith(".osl")]
    for block in blocks:
        bpy.data.texts[block.name].use_fake_user = True
    return blNodeGroups

def dump_json_library():
    path = get_library_path()
    library = {}

    inputFields = ["name","bl_socket_idname","type","default_value","min_value","max_value"]
    outputFields = ["name","bl_socket_idname"]

    for nodeGroup in bpy.data.node_groups:
        if nodeGroup.name.startswith("OWM: "):
            nodeGroupData = {"name":"","inputs":[],"outputs":[],"nodes":{}}
            nodeGroupData["name"] = nodeGroup.name
            
            for input in nodeGroup.inputs:
                inputData = {}
                for field in inputFields:
                    try:
                        if field == "default_value" and input.type != "VALUE":
                            data = []
                            for v in getattr(input, field):
                                data.append(v)
                            inputData[field] = data
                        else:
                            inputData[field] = getattr(input, field)
                    except AttributeError:
                        pass
                nodeGroupData["inputs"].append(inputData)  
            
            for output in nodeGroup.outputs:
                if output.name == "tmp_viewer": continue
                outputData = {}
                for field in outputFields:
                    try:
                        outputData[field] = getattr(output, field)
                    except AttributeError:
                        pass
                nodeGroupData["outputs"].append(outputData)
                        
            for node in nodeGroup.nodes:
                nodeData={
                    "bl_idname": node.bl_idname,
                    "name": node.name,
                    "label": node.label,
                    "location": list(node.location),
                    "dimensions": (int(node.width),int(node.height)),
                    "inputs": [],
                    "attributes": {},
                    "links": []
                    }
                if "tmp_viewer" == node.name:
                    continue
                
                if node.label:
                    nodeData["label"]=node.label
                else:
                    del nodeData["label"]

                if node.hide:
                    nodeData["attributes"]["hide"] = True

                if node.parent:
                    nodeData["parent"]=node.parent.name
                    
                for i,v in enumerate(nodeData["location"]):
                    nodeData["location"][i]=int(nodeData["location"][i])
                    
                
                for attr in node.bl_rna.properties.keys():
                    if attr not in  bpy.types.Node.bl_rna.properties.keys():
                        if attr == "interface":
                            continue
                        value = getattr(node, attr)
                        if isinstance(value, bpy.types.Node) or isinstance(value, bpy.types.NodeTree):
                            nodeData["attributes"][attr] = value.name
                        else:
                            nodeData["attributes"][attr] = value
                    
                for i, input in enumerate(node.inputs):
                    inputData={}
                    if input.identifier == "__extend__": continue
                    for field in inputFields:
                        if input.is_linked:
                            continue
                        try:
                            if field == "default_value" and input.type != "VALUE":
                                data = []
                                for v in getattr(input, field):
                                    data.append(v)
                                inputData[field] = data
                            else:
                                inputData[field] = getattr(input, field)
                        except AttributeError:
                            pass
                    if len(inputData) > 0:
                        inputData["index"] = i
                        nodeData["inputs"].append(inputData)
                nodeGroupData["nodes"][nodeData["name"]] = nodeData
            nodeGroupData["nodes"] = dict(sorted(nodeGroupData["nodes"].items()))
            library[nodeGroup.name] = nodeGroupData
            
            for link in nodeGroup.links:
                if "tmp_viewer" == link.from_socket.name or "tmp_viewer" == link.to_socket.name:
                    continue
                from_sockets = link.from_node.outputs if link.from_socket.is_output else link.from_node.inputs
                from_index = from_sockets.values().index(link.from_socket)
                to_sockets = link.to_node.outputs if link.to_socket.is_output else link.to_node.inputs
                to_index = to_sockets.values().index(link.to_socket)
                nodeGroupData["nodes"][link.from_node.name]["links"].append({
                    "fn": link.from_node.name,
                    "fs": from_index,
                    "fo": link.from_socket.is_output,
                    "tn": link.to_node.name,
                    "ts": to_index,
                    "to": link.to_socket.is_output,
                    })

        json.dump(library,open(path.replace(".blend",".json"),"w"), indent='\t')

def load_from_json():
    path = get_library_path()
    library = json.load(open(path.replace(".blend",".json"), "r"))
    groupNodes = {}
    groupLinks = {}

    def createNode(blendNodeGroup, node):
        #print(node)
        blendNode = blendNodeGroup.nodes.new(node["bl_idname"])
        blendNode.name = node["name"]
        blendNode.width = node["dimensions"][0]
        blendNode.height = node["dimensions"][1]
        blendNode.location = node["location"]
        if "label" in node:
            blendNode.label = node["label"]
            
        for attr,value in node["attributes"].items():
            #print(attr,value)
            if attr == "node_tree" and value != None:
                blendNode.node_tree = bpy.data.node_groups[value]
            else:
                setattr(blendNode, attr, value)
        
        for input in node["inputs"]:
            #print(input)
            if len(blendNode.inputs) > int(input["index"]) and "default_value" in input:
                blendNode.inputs[int(input["index"])].default_value = input["default_value"]

            
    def createLink(blendNodeGroup, link):
        #print(link)
        if link["fn"] in blendNodeGroup.nodes and link["tn"] in blendNodeGroup.nodes:
            #print(blendNodeGroup.nodes[link["tn"]].inputs.keys())
            from_node = blendNodeGroup.nodes[link["fn"]]
            to_node = blendNodeGroup.nodes[link["tn"]]
            if link["fo"]:
                if len(from_node.outputs) < link["fs"]+1:
                    return
                from_socket = from_node.outputs[link["fs"]]
            else:
                if len(from_node.inputs) < link["fs"]+1:
                    return
                from_socket = from_node.inputs[link["fs"]]
            if link["to"]:
                if len(to_node.outputs) < link["ts"]+1:
                    return
                to_socket = to_node.outputs[link["ts"]]
            else:
                if len(to_node.inputs) < link["ts"]+1:
                    return
                to_socket = to_node.inputs[link["ts"]]
                
            blendNodeGroup.links.new(from_socket, to_socket)
        

    for group in library.values():
        blendNodeGroup = bpy.data.node_groups.new(group["name"], 'ShaderNodeTree')
        blendNodeGroup["owm.libVersion"] = addonVersion
        treeLinks = []
        groupRelationships = {}

        for output in group["outputs"]:
            if output["name"] == "tmp_viewer": continue
            blendoutput = blendNodeGroup.outputs.new(output["bl_socket_idname"], output["name"])
        
        for input in group["inputs"]:
            blendInput = blendNodeGroup.inputs.new(input["bl_socket_idname"], input["name"])
            if "default_value" in input:
                if blendInput.type != "VALUE":
                    blendInput.default_value.foreach_set(input["default_value"])
                else:
                    blendInput.default_value = input["default_value"]
                    blendInput.min_value = input["min_value"]
                    blendInput.max_value = input["max_value"]
            
            
        for node in group["nodes"].values():
            #print(node)
            for link in node["links"]:
                treeLinks.append(link)
            if node["bl_idname"] == "ShaderNodeGroup":
                groupNodes.setdefault(blendNodeGroup, [])
                groupNodes[blendNodeGroup].append(node)
                continue
            createNode(blendNodeGroup, node)
            if "parent" in node:
                groupRelationships[node["name"]] = node["parent"]
            
        for node, parent in groupRelationships.items():
            blendNodeGroup.nodes[node].parent = blendNodeGroup.nodes[parent]

        if len(groupRelationships) > 0:
            for node in blendNodeGroup.nodes:
                node.location = group["nodes"][node.name]["location"]
        

        for link in treeLinks:
            if link["fn"] in blendNodeGroup.nodes and link["tn"] in blendNodeGroup.nodes:
                createLink(blendNodeGroup, link)
            else:
                groupLinks.setdefault(blendNodeGroup, [])
                groupLinks[blendNodeGroup].append(link)
                    
    #print(groupNodes)
    for blendNodeGroup, nodes in groupNodes.items():
        for node in nodes:
            createNode(blendNodeGroup, node)
        
    for blendNodeGroup, links in groupLinks.items():
        for link in links:
            createLink(blendNodeGroup, link)

def create_overwatch_library():
    path = get_library_path()
    print("[owm] attempting to export shaders")
    blocks_node = list([node for node in bpy.data.node_groups if node.name.startswith("OWM: ") ])
    for block_node in blocks_node:
        bpy.data.node_groups[block_node.name].use_fake_user = True
    blocks_text = list(
        [text for text in bpy.data.texts if text.name.startswith("OWM: ") and text.name.endswith(".osl")])
    for block_text in blocks_text:
        bpy.data.texts[block_text.name].use_fake_user = True
    blocks = set(blocks_node + blocks_text)
    dump_json_library()
    if len(blocks) > 0:
        print("[owm] exported: %s" % (", ".join(map(lambda x: x.name, blocks))))
    bpy.data.libraries.write(path, blocks, fake_user=True, path_remap="RELATIVE_ALL", compress=False)
    print("[owm] saved %s" % (path))

def load_data():
    print("[owm] attempting to load texture info")
    try:
    # print("[owm] %s = %s" % (fname, json.dumps(tdata)))
        for node in [node for node in bpy.data.node_groups if node.users == 0 and node.name.startswith("OWM: ")]:
            print("[owm] removing unused node group: %s" % (node.name))
            bpy.data.node_groups.remove(node)
        return create_overwatch_shader()
    except BaseException as e:
        print("[owm] failed to load node groups: {}".format(e))

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
        create_overwatch_library()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class OWMLoadJSONOp(bpy.types.Operator):
    """Import OWM Library from JSON"""
    bl_idname = "owm3.load_library_json"
    bl_label = "Import OWM Library from JSON"

    def execute(self, context):
        load_from_json()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

def getAOTextures():
    ao = {}
    for tex, mapping in textureMap.TextureTypes["Mapping"].items():
        if tex == 3761386704: 
            continue
        if "AO" in mapping.colorSockets or "AO" in mapping.alphaSockets or "Blend AO" in mapping.colorSockets:
            ao[str(tex)] = mapping
    return ao

class OWMConnectAOOp(bpy.types.Operator):
    """Connects all AO textures"""
    bl_idname = "owm3.enable_ao"
    bl_label = "Enable AO"

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

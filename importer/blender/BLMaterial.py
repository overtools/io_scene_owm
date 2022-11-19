import bpy
import json 

from ...readers import OWMaterialReader, PathUtil
from ...textureMap import TextureTypes as textureMap
from ...textureMap import StaticInputsByType, ScalesByName
from ...datatypes import MaterialTypes

class BlenderMaterialTree:
    def __init__(self, modelLooks, dedup=False):
        self.materialLooks = {}
        self.materials = {}
        self.blendMaterials = {}
        if dedup:
            self.blendMaterials = {material.name:material for material in bpy.data.materials}
        self.nodeTreeCache = {}
        self.blendTextures = {}
        self.texPaths = {}
        self.dedup = dedup
        self.unusedMaterials = set()
        print("[owm]: Reading material looks")
        self.batchLoadMaterials(modelLooks)
        print("[owm]: Creating {} materials".format(len(self.materials)))
        self.createMaterials()

    def batchLoadMaterials(self, modelLooks):
        read = set()
        for modelLookGUID, modelLookPath in modelLooks.items():
            if modelLookGUID is None: continue
            if modelLookGUID not in read:
                modelLookData = OWMaterialReader.read(modelLookPath)
                if not modelLookData:
                    continue
                if type(modelLookData) == MaterialTypes.OWMATMaterial:
                    mats= {"virtual": modelLookData}
                    modelLookData = MaterialTypes.OWMATModelLook("virtual")
                    modelLookData.materials = mats

                for key, material in modelLookData.materials.items():
                    if not material:
                        continue
                    self.materials.setdefault(material.GUID, material)
                    for texture in material.textures:
                        self.texPaths.setdefault(texture.GUID, texture.filepath)

                    modelLookData.materials[key] = material.GUID

                self.materialLooks.setdefault(modelLookGUID, modelLookData)
        self.materialLooks[None] = None

    def createMaterials(self):
        materialNodeTree = self.buildShaderNodeTrees()
        for nodeTree in materialNodeTree:
            for material in materialNodeTree[nodeTree]:
                if material in self.blendMaterials and self.dedup:
                    continue
                blendMaterial = self.nodeTreeCache[nodeTree].copy()
                self.insertMaterialData(blendMaterial, self.materials[material])
                self.blendMaterials[material] = blendMaterial
                self.unusedMaterials.add(blendMaterial)

    def bindModelLook(self, model, modelLookID):
        if modelLookID not in self.materialLooks:
            return
        modelLook = self.materialLooks[modelLookID]
        if modelLook is None:
            return
        for meshI, blendObj in enumerate(model.meshes):
            blendMesh = blendObj.data
            meshData = model.meshData.meshes[meshI]

            if meshData.materialKey in modelLook.materials:
                materialGUID = modelLook.materials[meshData.materialKey]
                if not materialGUID:
                    blendMesh.materials.clear()
                    blendObj["owm.material"] = materialGUID
                    continue
                blendMaterial = self.blendMaterials[materialGUID]
                blendMesh.materials.clear()
                blendMesh.materials.append(blendMaterial)
                blendObj.material_slots[0].link = 'OBJECT'
                blendObj.material_slots[0].material = blendMaterial
                self.markUsed(blendMaterial)
                blendObj["owm.material"] = materialGUID
            else:
                print("[owm]: Unable to find material {:016X} in provided material set (BLMaterial)".format(
                    meshData.materialKey))

    def bindEntityLook(self, entity, modelLookID):
        if entity.baseModel:
            self.bindModelLook(entity.baseModel, modelLookID)
        for child in entity.children:
            self.bindEntityLook(child, modelLookID)

    def buildShaderNodeTrees(self):
        materialNodeTree = {}
        textureInputs = {}
        for materialGUID, materialData in self.materials.items():
            shaderKey = generateShaderKey(materialData)
            materialNodeTree.setdefault(shaderKey, set())
            textureInputs.setdefault(shaderKey, materialData.textures)
            materialNodeTree[shaderKey].add(materialGUID)

        for nodeTree in materialNodeTree:
            self.nodeTreeCache[nodeTree] = buildNodeTree(textureInputs[nodeTree], nodeTree)

        return materialNodeTree

    def insertMaterialData(self, blendMaterial, material):
        blendMaterial.name = material.GUID
        nodes = blendMaterial.node_tree.nodes
        #print(blendMaterial.name)

        # parms
        shaderGroup = nodes["OverwatchShader"]
        for input in StaticInputsByType["ShaderParm"]:
            if input in material.staticInputs:
                if textureMap["StaticInputs"][input].field in shaderGroup.inputs.keys(): #TODO might need opt
                    shaderGroup.inputs[textureMap["StaticInputs"][input].field].default_value = material.staticInputs[input]

        # uvs
        layerCount = 2
        curLayer = 1
        for input in StaticInputsByType["UVLayer"]: #this might not scale well for maps so up to changes
            if input in material.staticInputs or input < -100: # -100 and .gets are hacks for basic textures

                UVNode = None
                mappingNode = None
                scalingNode = None
                
                for target in textureMap["StaticInputs"][input].uvTargets:
                    if str(target) in nodes:
                        def createUVLayer():
                            UVNode = createUVNode(nodes, material.staticInputs.get(input, 1), (2,layerCount))
                            UVNode.label = uvName+" UV"
                            return UVNode, layerCount, layerCount+2.5
                        texNode = nodes[str(target)]
                        uvName = textureMap["StaticInputs"][input].uvName

                        # Check if this UV Layer has tied scaling
                        if uvName in ScalesByName:
                            if ScalesByName[uvName] in material.staticInputs: # check if it's in inputs
                                mode = material.staticInputs.get(2135242209, [0, 0])
                                if UVNode is None:
                                    UVNode, curLayer, layerCount = createUVLayer()

                                if mode == [0, 0]: #mapping node is good enough 
                                    if mappingNode is None:
                                        mappingNode = createMappingNode(nodes, str(uvName)+" Scale", (1.5, curLayer))
                                        blendMaterial.node_tree.links.new(UVNode.outputs[0], mappingNode.inputs[0])
                                        setMappingScale(mappingNode, material.staticInputs[ScalesByName[uvName]])
                                    
                                    blendMaterial.node_tree.links.new(mappingNode.outputs[0], texNode.inputs[0])
                                else:
                                    if scalingNode is None and "OWM: Scale UV" in bpy.data.node_groups:
                                        scalingNode = nodes.new("ShaderNodeGroup")
                                        scalingNode.location = getLocation(1.5,curLayer)
                                        scalingNode.label = uvName+" Scaling"
                                        scalingNode.node_tree = bpy.data.node_groups["OWM: Scale UV"]
                                        scalingNode.color = [.245, .245, .575]
                                        scalingNode.use_custom_color = True
                                        scalingNode.hide = True
                                        
                                        blendMaterial.node_tree.links.new(UVNode.outputs[0], scalingNode.inputs[0])
                                        scalingNode.inputs[1].default_value = material.staticInputs[ScalesByName[uvName]][0]
                                        scalingNode.inputs[2].default_value = material.staticInputs[ScalesByName[uvName]][1]

                                        scalingNode.inputs[3].default_value = getScaleVector(mode[0])
                                        scalingNode.inputs[4].default_value = getScaleVector(mode[1])

                                    if scalingNode:
                                        blendMaterial.node_tree.links.new(scalingNode.outputs[0], texNode.inputs[0])
                        elif material.staticInputs.get(input, 1) != 1:
                            if UVNode is None:
                                UVNode, curLayer, layerCount = createUVLayer()
                            blendMaterial.node_tree.links.new(UVNode.outputs[0], texNode.inputs[0])
                
        for texture in material.textures:
            blendTex = self.loadTexture(texture)
            texNode = nodes[str(texture.key)]

            if blendTex is None:
                texNode.color = [.75, 0, 0]
                texNode.use_custom_color = True
                texNode.label += " ({} not found)".format(texture.GUID)
            else:
                texNode.image = blendTex
                texNode.image.colorspace_settings.name = 'sRGB' if texNode["owm.issRGB"] == 1 else 'Raw'
                texNode.image.alpha_mode = 'CHANNEL_PACKED'
            
            # shader specific
            if material.shader == 217 or material.shader == 43: # detail
                if texture.key in textureMap["DetailTextures"].keys() and 4081294361 in material.staticInputs:
                    index = textureMap["DetailTextures"][texture.key]
                    if material.shader == 43:
                        index-=1
                    scale = material.staticInputs[4081294361][index]

                    scaleNode = nodes[str(texture.key)+" Detail Scale"]
                    scaleNode.inputs[1].default_value = scale[0]
                    scaleNode.inputs[2].default_value = scale[-1]
                    scaleNode.inputs[3].default_value = scale[1]
                    scaleNode.inputs[4].default_value = scale[2]
        
        # shader specific fixes
        if material.shader == 51 and "4101268840" in nodes: # ow2 hair
            if "758934576" in nodes: # doomfist doesn't have strands apparently or alpha in uvlayer2
                #alpha
                albedoNode = nodes["1239794147"]
                texNode = createTexNode(nodes, albedoNode.name+"_A", albedoNode.label+" (Alpha)", locationFromNode(albedoNode, y=-1))
                texNode.image = albedoNode.image

                UVNode = createUVNode(nodes, 2, locationFromNode(texNode, x=1))
                
                blendMaterial.node_tree.links.new(texNode.inputs[0], UVNode.outputs[0])
                blendMaterial.node_tree.links.new(texNode.outputs[1], shaderGroup.inputs["Alpha"])

            
                # strands
                strandMapTexNode = nodes["4101268840"]
                strandMapTexNode2 = createTexNode(nodes, strandMapTexNode.name+"_Pixel", strandMapTexNode.label+" (Closest)", locationFromNode(strandMapTexNode, x=1.5))
                strandMapTexNode2.image = strandMapTexNode.image
                strandMapTexNode2.interpolation = 'Closest'

                strandTexNode = nodes["758934576"]

                strandTexNode2 = createTexNode(nodes, strandTexNode.name+"_2", strandTexNode.label, locationFromNode(strandTexNode, y=1))
                strandTexNode2.image = strandTexNode.image

                strandsNode = nodes.new("ShaderNodeGroup")
                strandsNode.location = getLocation(*locationFromNode(strandTexNode, x=.5))
                strandsNode.node_tree = bpy.data.node_groups["OWM: Hair Strand Preprocess"]
                strandsNode.inputs["Density"].default_value = material.staticInputs[3604494376][0]

                blendMaterial.node_tree.links.new(strandMapTexNode2.outputs[0], strandsNode.inputs["Strand"])
                blendMaterial.node_tree.links.new(strandsNode.outputs[0], strandTexNode.inputs[0])
                blendMaterial.node_tree.links.new(strandsNode.outputs[1], strandTexNode2.inputs[0])
                blendMaterial.node_tree.links.new(strandTexNode.outputs[0], shaderGroup.inputs["Detail 1"])
                blendMaterial.node_tree.links.new(strandTexNode2.outputs[0], shaderGroup.inputs["Detail 2"])
            else:
                albedoNode = nodes["1239794147"]
                blendMaterial.node_tree.links.new(texNode.outputs[1], shaderGroup.inputs["Alpha"])
            

    def loadTexture(self, texture):
        if texture.GUID in self.blendTextures:
            return self.blendTextures[texture.GUID]

        texPath = self.texPaths[texture.GUID]

        if not PathUtil.checkExistence(texPath):
            return None

        blendTex = bpy.data.images.load(texPath, check_existing=True)
        self.blendTextures[texture.GUID] = blendTex
        return blendTex

    def markUsed(self, mat):
        if mat in self.unusedMaterials:
            self.unusedMaterials.remove(mat)
    
    def removeSkeletonNodeTrees(self):
        bpy.data.batch_remove(self.nodeTreeCache.values())

    def createMaterialDatabase(self, objects, filepath):
        database = {"Mappings": {}, "Materials": {}, "Textures": {}}
        textures = database["Textures"]
        for textureGUID, texture in self.blendTextures.items():
            textures[textureGUID] = {"filepath":self.texPaths[textureGUID], "sRGB": texture.colorspace_settings.name == "sRGB"}

        materials = database["Materials"]
        mappings = database["Mappings"]
        for materialGUID, material in self.materials.items():
            materials[materialGUID] = {
                "shaderGroup": material.shader,
                "textures": [],
                "users": [],
            }
            
            for texture in material.textures:
                mapping = textureMapping[texture.key] if texture.key in textureMapping else None
                materials[materialGUID]["textures"].append({"GUID": texture.GUID, "mapping": texture.key})
                if mapping and texture.key not in mappings:
                    mappings[texture.key] = mapping.__dict__

        for object in objects:
            if "owm.material" in object:
                materials[object["owm.material"]]["users"].append(object.name)

        json.dump(database, open(PathUtil.joinPath(filepath,"..", "materials.json"), "w"))
            


tile_x = 400
tile_y = 50
textureMapping = textureMap["Mapping"]

def buildNodeTree(textureInputs, shaderKey):
    shaderGroup = shaderKey[-2]
    if shaderKey[-1]: # check for node group variant
        shaderKeyStr = str(shaderGroup)+"_"+str(shaderKey[-1])
    else:
        shaderKeyStr = shaderGroup

    textureInputs = [data.key for data in textureInputs]
    blendMaterial = bpy.data.materials.new(name="".join([str(key) if key else "" for key in shaderKey]))
    blendMaterial.use_nodes = True
    blendMaterial.blend_method = 'HASHED'
    blendMaterial.shadow_method = 'HASHED'

    nodes = blendMaterial.node_tree.nodes
    links = blendMaterial.node_tree.links

    for node in [node for node in nodes if node.type != "OUTPUT_MATERIAL"]:
        nodes.remove(node)

    outputNode = None

    try:
        outputNode = [node for node in nodes if node.type == "OUTPUT_MATERIAL"][0]
    except:
        outputNode = nodes.new("ShaderNodeOutputMaterial")

    outputNode.location = (tile_x, 0)

    shaderNode = nodes.new("ShaderNodeGroup")
    renameNode(shaderNode, "OverwatchShader", "OWM Shader {}".format(shaderGroup))
    shaderNode["owm.shaderkey"] = shaderKeyStr

    if str(shaderKeyStr) in textureMap['NodeGroups'] and textureMap['NodeGroups'][str(shaderKeyStr)] in bpy.data.node_groups:
        shaderNode.node_tree = bpy.data.node_groups[textureMap['NodeGroups'][str(shaderKeyStr)]]
    else:
        if textureMap['NodeGroups']['Default'] in bpy.data.node_groups:
            shaderNode.node_tree = bpy.data.node_groups[textureMap['NodeGroups']['Default']]

    shaderNode.location = (0, 0)
    shaderNode.width = 300
    if shaderNode.node_tree is not None:
        links.new(shaderNode.outputs[0], outputNode.inputs[0])

    # sort texture inputs so that the nodes are created and placed in the same order as the node group takes in
    shaderInputs = []
    for input in shaderNode.inputs:
        for mappingID, mapping in textureMapping.items():
            if input.name in mapping.colorSockets and mappingID in textureInputs and mappingID not in shaderInputs:
                shaderInputs.append(mappingID)

    # add back at the end inputs that the node group doesn't use
    shaderInputs += [input for input in textureInputs if input not in shaderInputs]

    # Shader specific stuff
    if (shaderGroup == 217 or shaderGroup == 43) and 250510254 in shaderKey: #detail
        UVNode = createUVNode(nodes, 1, (2,8))

    for i, texture in enumerate(shaderInputs):
        mapping = textureMapping[texture] if texture in textureMapping else None
        label = mapping.readableName if mapping else f'{texture:x}'.upper()

        texNode = createTexNode(nodes, texture, label, (1,i+2))

        if mapping:
            for colorSocket in mapping.colorSockets:
                if colorSocket in shaderNode.inputs:
                    links.new(texNode.outputs[0], shaderNode.inputs[colorSocket])
            for alphaSocket in mapping.alphaSockets:
                if alphaSocket in shaderNode.inputs:
                    links.new(texNode.outputs[1], shaderNode.inputs[alphaSocket])

        texNode["owm.issRGB"] = mapping.sRGB if mapping else False

        # Shader specific
        if texture == 3335614873: #AO
            UVNodeAO = createUVNode(nodes, 2, (2,i+2), "AO")
            links.new(UVNodeAO.outputs[0], texNode.inputs[0])
        if (shaderGroup == 217 or shaderGroup == 44) and texture == 2903569922: # hero ao
            links.new(texNode.outputs[1], shaderNode.inputs["AO"])
        if (shaderGroup == 217 or shaderGroup == 43) and texture in textureMap["DetailTextures"].keys(): #detail
            #mappingNode = createMappingNode(nodes, str(texture)+" Detail Mapping", (1.5, i+2))
            scalingNode = nodes.new("ShaderNodeGroup")
            scalingNode.name = str(texture)+" Detail Scale"
            scalingNode.location = getLocation(1.5, i+2)
            scalingNode.node_tree = bpy.data.node_groups["OWM: Detail Scale UV"]
            scalingNode.hide = True
            links.new(UVNode.outputs[0], scalingNode.inputs[0])

            links.new(scalingNode.outputs[0], texNode.inputs[0])
            
    return blendMaterial

def createTexNode(nodes, name, label, location):
    texNode = nodes.new('ShaderNodeTexImage')
    texNode.location = getLocation(*location)
    texNode.width = 250
    texNode.hide = True
    renameNode(texNode, name, label)
    return texNode

def createMappingNode(nodes, name, location):
    mappingNode = nodes.new('ShaderNodeMapping')
    if name:
        mappingNode.name = name
    mappingNode.location = getLocation(*location)
    mappingNode.hide = True
    return mappingNode

def createUVNode(nodes, mapIndex, location, name=None):
    UVNode = nodes.new('ShaderNodeUVMap')
    if name:
        UVNode.name = name
    UVNode.uv_map = "UVMap"+str(mapIndex)
    UVNode.location = getLocation(*location)
    return UVNode

def getLocation(x, y):
    return (-(tile_x * x), -(tile_y * y))

def locationFromNode(node, x=0.0, y=0.0):
    return [-(node.location[0]/tile_x)+x, -(node.location[1]/tile_y)+y]

def renameNode(node, name, label=None):
    node.name = str(name)
    if label:
        node.label = str(label)

def getScaleVector(mode):
    if mode == 3:
        return (1,0,0)
    elif mode == 1:
        return (0,0,1)
    elif mode == 2:
        return (0,1,0)
    else:
        return (0,0,0)

def setMappingScale(mappingNode, scale):
    mappingNode.inputs[3].default_value[0] = scale[0]
    mappingNode.inputs[3].default_value[1] = scale[-1]

def generateShaderKey(material):
    textures = [texData.key for texData in material.textures]
    textures.sort()
    textures.append(material.shader)
    if material.shader == 37: # I'll hate you forever, shader 37
        mode = material.staticInputs[2241837981]
        if mode == 2: #if aouvu is not 2 we need a sec layer node
            if 3120512190 not in textures: #Overlay not present
                mode = 4
        elif mode == 1: #I still can't tell what makes a 1 flip to mode 3
            if "00000000000E" in material.textures[0].GUID: #dummy overlay, nothing matters
                mode = 2
        textures.append(mode)
    elif material.shader == 43: # ow1/ow2 skin
        textures.append(2 if 4081294361 in material.staticInputs else 1)
    elif material.shader == 51: # ow1/ow2 hair
        textures.append(2 if 4101268840 in textures else 1)
    else: #this is hacky but can be used to create specific shader groups like separating ow1 and ow2 hair
        textures.append(None)
    return tuple(textures)

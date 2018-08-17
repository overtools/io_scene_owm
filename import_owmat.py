import os
from . import bpyhelper
from . import read_owmat
from . import owm_types
import bpy

def cleanUnusedMaterials(materials):
    if materials is None:
        return
    m = {}
    for name in materials[1]:
        mat = materials[1][name]
        if mat.users == 0:
            print("[import_owmat]: removed material: {}".format(mat.name))
            bpy.data.materials.remove(mat)
        else:
            m[name] = mat
    bpy.context.scene.update()
    t = {}
    for name in materials[0]:
        tex = materials[0][name]
        if tex.users == 0:
            bpy.data.textures.remove(tex)
        else:
            t[name] = tex
    bpy.context.scene.update()
    return (t, m)

def mutate_texture_path(file, new_ext):
    return os.path.splitext(file)[0] + new_ext

def load_textures(texture, root, t):
    """ Loads an overwatch texture.
 
    Priority (high to low): TIFF, TGA, DDS (doesn't work properly)
    """
    realpath = bpyhelper.normpath(texture)
    if not os.path.isabs(realpath):
        realpath = bpyhelper.normpath('%s/%s' % (root, realpath))

    tga_file = mutate_texture_path(realpath, ".tga")
    if os.path.exists(tga_file):
        realpath = tga_file
    
    tif_file = mutate_texture_path(realpath, ".tif")
    if os.path.exists(tif_file):
        realpath = tif_file

    fn = os.path.splitext(os.path.basename(realpath))[0]
    
    try:
        tex = None
        if fn in t:
            tex = t[fn]
        else:
            img = None
            for eimg in bpy.data.images:
                if eimg.name == fn or eimg.filepath == realpath:
                    img = eimg
            if img is None:
                img = bpy.data.images.load(realpath)
                img.name = fn
            tex = None
            for etex in bpy.data.textures:
                if etex.name == fn:
                    tex = etex
            if tex == None:
                tex = bpy.data.textures.new(fn, type='IMAGE')
                tex.image = img
            t[fn] = tex
        return tex
    except Exception as e:
        print("[import_owmat]: error loading texture: {}".format(e))
    return None

def create_overwatch_shader(tile=300): # Creates the Overwatch nodegroup, if it doesn't exist yet
    if(bpy.data.node_groups.find("OverwatchGenerated") is not -1):
        return
   
    bpy.data.node_groups.new("OverwatchGenerated", "ShaderNodeTree")
    ng = bpy.data.node_groups["OverwatchGenerated"]
 
    # Clearing nodegroup
    ng.nodes.clear()
    ng.inputs.clear()
    ng.outputs.clear()
 
    # Creating Output node
    nodeOutput = ng.nodes.new("NodeGroupOutput")
    nodeOutput.location = (0, 0)
 
    # Adding outputs
    ng.outputs.new("NodeSocketShader", "Shader")
 
    # Creating inputs and setting their default values - Input node is created at the end.
    inputCol = ng.inputs.new("NodeSocketColor", "Color")
    inputOpacity = ng.inputs.new("NodeSocketFloat", "Opacity")
    inputOpacity.default_value = 1
    inputSpec = ng.inputs.new("NodeSocketColor", "OWSpecMap")
    inputSpec.default_value = (0, 0, 0, 1)
    inputNormal = ng.inputs.new("NodeSocketColor", "Normal")
    inputNormal.default_value = (.5, .5, 1, 1)
    inputNormalStrength = ng.inputs.new("NodeSocketFloat", "Normal Strength")
    inputNormalStrength.default_value = 1
    inputEmission = ng.inputs.new("NodeSocketFloat", "Emission Mask")
    inputEmissionStrength = ng.inputs.new("NodeSocketFloat", "Emission Strength")
    inputEmissionStrength.default_value = 1
 
    ### SPAWNING NODES ###
    nodeMixTransp = ng.nodes.new("ShaderNodeMixShader")
    nodeMixTransp.location = (-tile, 0)
 
    nodeMixEmission = ng.nodes.new("ShaderNodeMixShader")
    nodeMixEmission.location = (-tile*2, 0)
 
    nodePrincipled = ng.nodes.new("ShaderNodeBsdfPrincipled")
    nodePrincipled.location = (-tile*3, 0)
 
    nodeTransp = ng.nodes.new("ShaderNodeBsdfTransparent")
    nodeTransp.location = (-tile*3, 200)
 
    nodeEmission = ng.nodes.new("ShaderNodeEmission")
    nodeEmission.location = (-tile*3, -600)
 
    nodeTangent = ng.nodes.new("ShaderNodeTangent")
    nodeTangent.location = (-tile*4, -tile*3)
    nodeTangent.direction_type = 'UV_MAP'
 
    nodeNormal = ng.nodes.new("ShaderNodeNormalMap")
    nodeNormal.location = (-tile*4, -tile*2)
    
    nodeCombineRGBNormal = ng.nodes.new("ShaderNodeCombineRGB")
    nodeCombineRGBNormal.location = (-tile*5, -tile*2)
    nodeCombineRGBNormal.inputs[2].default_value = 1    # Discarding normal map Z channel and setting it to 1.
    
    nodeInvertNormalGreen = ng.nodes.new("ShaderNodeInvert")
    nodeInvertNormalGreen.location = (-tile*6, -tile*2)
    
    nodeSeparateRGBNormal = ng.nodes.new("ShaderNodeSeparateRGB")
    nodeSeparateRGBNormal.location = (-tile*7, -tile*2)
 
    ## SPECULAR SETUP ##
    nodeMathSpec2 = ng.nodes.new("ShaderNodeMath")
    nodeMathSpec2.location = (-tile*4, 0)
    nodeMathSpec2.operation = 'MULTIPLY'
    nodeMathSpec2.inputs[1].default_value = 0.5
 
    nodeMathSpec = ng.nodes.new("ShaderNodeMath")
    nodeMathSpec.location = (-tile*5, 0)
    nodeMathSpec.operation = 'MULTIPLY'
    nodeMathSpec.inputs[1].default_value = 2
    nodeMathSpec.use_clamp = True
 
    nodeMathMetal2 = ng.nodes.new("ShaderNodeMath")
    nodeMathMetal2.location = (-tile*4, -tile/2)
    nodeMathMetal2.operation = 'MULTIPLY'
    nodeMathMetal2.inputs[1].default_value = 2
 
    nodeMathMetal = ng.nodes.new("ShaderNodeMath")
    nodeMathMetal.location = (-tile*5, -tile/2)
    nodeMathMetal.operation = 'SUBTRACT'
    nodeMathMetal.inputs[1].default_value = 0.5
    nodeMathMetal.use_clamp = True
 
    nodeGamma = ng.nodes.new("ShaderNodeGamma")
    nodeGamma.location = (-tile*4, -tile)
 
    nodeInvertRoughness = ng.nodes.new("ShaderNodeInvert")
    nodeInvertRoughness.location = (-tile*5, -tile)
 
    nodeSeparateRGBSpec = ng.nodes.new("ShaderNodeSeparateRGB")
    nodeSeparateRGBSpec.location = (-tile*6, -tile/2)
 
    # Input node
    nodeInput = ng.nodes.new("NodeGroupInput")
    nodeInput.location = (-tile*8, -tile/2)
 
    ### CONNECTING NODES ###
    links = ng.links
    links.new(nodeInput.outputs["Color"], nodePrincipled.inputs["Base Color"])
    links.new(nodeInput.outputs["Opacity"], nodeMixTransp.inputs["Fac"])
    links.new(nodeInput.outputs["OWSpecMap"], nodeSeparateRGBSpec.inputs["Image"])
    links.new(nodeInput.outputs["Emission Mask"], nodeMixEmission.inputs["Fac"])
    links.new(nodeInput.outputs["Emission Strength"], nodeEmission.inputs["Strength"])
    links.new(nodeInput.outputs["Normal"], nodeSeparateRGBNormal.inputs[0])
    links.new(nodeInput.outputs['Normal Strength'], nodeNormal.inputs["Strength"])
    
    links.new(nodeSeparateRGBNormal.outputs[0], nodeCombineRGBNormal.inputs[0])
    links.new(nodeSeparateRGBNormal.outputs[1], nodeInvertNormalGreen.inputs["Color"])
    links.new(nodeInvertNormalGreen.outputs[0], nodeCombineRGBNormal.inputs[1])
    links.new(nodeCombineRGBNormal.outputs[0], nodeNormal.inputs["Color"])
 
    links.new(nodeSeparateRGBSpec.outputs["R"], nodeMathSpec.inputs[0])
    links.new(nodeSeparateRGBSpec.outputs["R"], nodeMathMetal.inputs[0])
    links.new(nodeSeparateRGBSpec.outputs["G"], nodeInvertRoughness.inputs["Color"])
 
    links.new(nodeMathSpec.outputs[0], nodeMathSpec2.inputs[0])
    links.new(nodeMathMetal.outputs[0], nodeMathMetal2.inputs[0])
    links.new(nodeInvertRoughness.outputs[0], nodeGamma.inputs[0])
 
    links.new(nodeMathSpec2.outputs[0], nodePrincipled.inputs["Specular"])
    links.new(nodeMathMetal2.outputs[0], nodePrincipled.inputs["Metallic"])
    links.new(nodeGamma.outputs[0], nodePrincipled.inputs["Roughness"])
    links.new(nodeNormal.outputs[0], nodePrincipled.inputs["Normal"])
    links.new(nodeTangent.outputs[0], nodePrincipled.inputs["Tangent"])
 
    links.new(nodeInput.outputs["Color"], nodeEmission.inputs["Color"])
 
    links.new(nodePrincipled.outputs[0], nodeMixEmission.inputs[1])
    links.new(nodeEmission.outputs[0], nodeMixEmission.inputs[2])
    links.new(nodeTransp.outputs[0], nodeMixTransp.inputs[1])
    links.new(nodeMixEmission.outputs[0], nodeMixTransp.inputs[2])
 
    links.new(nodeMixTransp.outputs[0], nodeOutput.inputs[0])
    print("Creating Overwatch nodegroup has finished.")

def read(filename, prefix = '', importNormal = True, importEffect = True):
    root, file = os.path.split(filename)
    data = read_owmat.read(filename)
    if not data:
        return None

    t = {}
    m = {}

    if bpy.context.scene.render.engine == 'CYCLES':
        create_overwatch_shader()

    for i in range(len(data.materials)):
        if bpy.context.scene.render.engine == 'CYCLES':
            m[data.materials[i].key] = process_material_Cycles(data.materials[i], prefix, root, t)
        else:
            m[data.materials[i].key] = process_material_BI(data.materials[i], prefix, importNormal, importEffect, root, t)

    return (t, m)

def process_material_Cycles(material, prefix, root, t):    
    mat = bpy.data.materials.new('%s%016X' % (prefix, material.key))

    if material.shader != 0:
        print("[import_owmat]: {} uses shader {}".format(mat.name, material.shader))
    
    # print("Processing material: " + mat.name)
    mat.use_nodes = True
   
    tile = 300
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
       
    # Remove default diffuse node
    nodes.remove(nodes.get('Diffuse BSDF'))
 
    # Get material output node
    material_output = nodes.get('Material Output')
    material_output.location = (tile, 0)
 
    # Create Overwatch NodeGroup Instance
    nodeOverwatch = nodes.new('ShaderNodeGroup')
    nodeOverwatch.node_tree = bpy.data.node_groups["OverwatchGenerated"]
    nodeOverwatch.location = (0, 0)
    nodeOverwatch.width = 250
    links.new(nodeOverwatch.outputs[0], material_output.inputs[0])

    for i, texData in enumerate(material.textures):
        nodeTex = nodes.new("ShaderNodeTexImage")
        nodeTex.location = (-tile, -tile*(i))
        nodeTex.width = 250
        nodeTex.color_space = 'NONE'
        
        tex = load_textures(texData[0], root, t)
        if tex is None:
            print("[import_owmat]: failed to load texture: {}".format(texData[0]))
            continue
        nodeTex.image = tex.image

        if len(texData) == 2:
            continue

        typ = texData[2]
        named = False
        for name, num in owm_types.TextureTypes.items():
            if num == typ:
                print("[import_owmat]: {} is {}".format(texData[0], name))
                nodeTex.label = "Texture: {}".format(name)
                named = True
        if not named:
            nodeTex.label = "Texture: Unknown-{}".format(typ)
        tt = owm_types.TextureTypes
        if typ == tt['DiffuseAO'] or typ == tt['DiffuseOpacity'] or typ == tt['DiffuseBlack'] \
            or typ == tt['DiffusePlant'] or typ == tt['DiffuseFlag'] or typ == tt['Diffuse2']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Color"])
            nodeTex.color_space = 'COLOR'
            nodeTex.name = "Color"
        if typ == tt['DiffuseAO']:
            nodeTex.image.use_alpha = False
        if typ == tt['DiffuseOpacity']:
            links.new(nodeTex.outputs["Alpha"], nodeOverwatch.inputs["Opacity"])
        if typ == tt['DiffuseBlack']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Opacity"])
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Emission Mask"])
        if typ == tt['Opacity'] or typ == tt['Opacity2']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Opacity"])
        if typ == tt['Tertiary'] or typ == tt['Tertiary2']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["OWSpecMap"])
        if typ == tt['Emission'] or typ == tt['Emission2'] or typ == tt['Emission3']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Emission Mask"])
        if typ == tt['Normal'] or typ == tt['HairNormal'] or typ == tt['CorneaNormal']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Normal"])
    
    nodes.active = nodes.get("Color")
    
    return mat

def process_material_BI(material, prefix, importNormal, importEffect, root, t):
    mat = bpy.data.materials.new('%s%016X' % (prefix, material.key))
    mat.diffuse_intensity = 1.0
    for texturetype in material.textures:
        typ = texturetype[1]
        texture = texturetype[0]
        if importNormal == False and typ == owm_types.OWMATTypes['NORMAL']:
            continue
        if importEffect == False and typ == owm_types.OWMATTypes['SHADER']:
            continue
 
        tex = load_textures(texture, root, t)
       
        try:
            mattex = mat.texture_slots.add()
            mattex.use_map_color_diffuse = True
            mattex.diffuse_factor = 1
            if typ == owm_types.OWMATTypes['NORMAL']:
                tex.use_alpha = False
                tex.use_normal_map = True
                mattex.use_map_color_diffuse = False
                mattex.use_map_normal = True
                mattex.normal_factor = 1
                mattex.diffuse_factor = 0
            elif typ == owm_types.OWMATTypes['SHADER']:
                mattex.use = False
            mattex.texture = tex
            mattex.texture_coords = 'UV'
        except Exception as e:
            print("[import_owmat]: error creating BI material: {}".format(e))
    
    return mat

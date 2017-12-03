import os

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
    return os.path.dirname(file) + "//" + os.path.splitext(os.path.basename(file))[0] + new_ext


def load_textures(texture, root, t):
    """ Loads an overwatch texture file.

    Will attempt to load the default path (DDS) first,
    then fall back to Tiff, and lastly TGA.
    """
    realpath = texture
    if not os.path.isabs(realpath):
        realpath = os.path.normpath('%s/%s' % (root, realpath))
        fn = os.path.splitext(os.path.basename(realpath))[0]
    tif_file = mutate_texture_path(realpath, ".tif")
    is_tif = False
    if os.path.exists(tif_file):
        realpath = tif_file
        is_tif = True

    tga_file = mutate_texture_path(realpath, ".tga")
    if not os.path.exists(tif_file) and os.path.exists(tga_file):
        realpath = tga_file
        is_tif = False

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
            if tex is None:
                tex = bpy.data.textures.new(fn, type='IMAGE')
                tex.image = img
        return tex, is_tif
    except Exception as e:
        print(e)
    return None, False


def create_overwatch_shader(tile=300):
    """Creates the Overwatch nodegroup, if it doesn't exist yet"""

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

    # Creating inputs and setting their default values
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
    inputEmissionStrength.default_value = 3

    # SPAWNING NODES
    nodeMixTransp = ng.nodes.new("ShaderNodeMixShader")
    nodeMixTransp.location = (-tile, 0)

    nodeMixEmission = ng.nodes.new("ShaderNodeMixShader")
    nodeMixEmission.location = (-tile * 2, 0)

    nodePrincipled = ng.nodes.new("ShaderNodeBsdfPrincipled")
    nodePrincipled.location = (-tile * 3, 0)

    nodeTransp = ng.nodes.new("ShaderNodeBsdfTransparent")
    nodeTransp.location = (-tile * 3, 200)

    nodeEmission = ng.nodes.new("ShaderNodeEmission")
    nodeEmission.location = (-tile * 3, -600)

    nodeTangent = ng.nodes.new("ShaderNodeTangent")
    nodeTangent.location = (-tile * 4, -tile * 3)
    nodeTangent.direction_type = 'UV_MAP'

    nodeNormal = ng.nodes.new("ShaderNodeNormalMap")
    nodeNormal.location = (-tile * 4, -tile * 2)

    nodeCombineRGB = ng.nodes.new("ShaderNodeCombineRGB")
    nodeCombineRGB.location = (-tile * 5, -tile * 2)
    nodeInvert = ng.nodes.new("ShaderNodeInvert")
    nodeInvert.location = (-tile * 6, -tile * 2)
    nodeSeparateRGBNorm = ng.nodes.new("ShaderNodeSeparateRGB")
    nodeSeparateRGBNorm.location = (-tile * 7, -tile * 2)

    # SPECULAR SETUP
    nodeMathSpec2 = ng.nodes.new("ShaderNodeMath")
    nodeMathSpec2.location = (-tile * 4, 0)
    nodeMathSpec2.operation = 'MULTIPLY'
    nodeMathSpec2.inputs[1].default_value = 0.5

    nodeMathSpec = ng.nodes.new("ShaderNodeMath")
    nodeMathSpec.location = (-tile * 5, 0)
    nodeMathSpec.operation = 'MULTIPLY'
    nodeMathSpec.inputs[1].default_value = 2
    nodeMathSpec.use_clamp = True

    nodeMathMetal2 = ng.nodes.new("ShaderNodeMath")
    nodeMathMetal2.location = (-tile * 4, -tile / 2)
    nodeMathMetal2.operation = 'MULTIPLY'
    nodeMathMetal2.inputs[1].default_value = 2

    nodeMathMetal = ng.nodes.new("ShaderNodeMath")
    nodeMathMetal.location = (-tile * 5, -tile / 2)
    nodeMathMetal.operation = 'SUBTRACT'
    nodeMathMetal.inputs[1].default_value = 0.5
    nodeMathMetal.use_clamp = True

    nodeGamma = ng.nodes.new("ShaderNodeGamma")
    nodeGamma.location = (-tile * 4, -tile)

    nodeInvertRoughness = ng.nodes.new("ShaderNodeInvert")
    nodeInvertRoughness.location = (-tile * 5, -tile)

    nodeSeparateRGBSpec = ng.nodes.new("ShaderNodeSeparateRGB")
    nodeSeparateRGBSpec.location = (-tile * 6, -tile / 2)

    # Input node
    nodeInput = ng.nodes.new("NodeGroupInput")
    nodeInput.location = (-tile * 8, -tile / 2)

    # CONNECTING NODES
    links = ng.links
    links.new(nodeInput.outputs["Color"], nodePrincipled.inputs["Base Color"])
    links.new(nodeInput.outputs["Opacity"], nodeMixTransp.inputs["Fac"])
    links.new(nodeInput.outputs["OWSpecMap"], nodeSeparateRGBSpec.inputs["Image"])
    links.new(nodeInput.outputs["Normal"], nodeSeparateRGBNorm.inputs["Image"])
    links.new(nodeInput.outputs["Emission Mask"], nodeMixEmission.inputs["Fac"])
    links.new(nodeInput.outputs["Emission Strength"], nodeEmission.inputs["Strength"])

    links.new(nodeSeparateRGBSpec.outputs["R"], nodeMathSpec.inputs[0])
    links.new(nodeSeparateRGBSpec.outputs["R"], nodeMathMetal.inputs[0])
    links.new(nodeSeparateRGBSpec.outputs["G"], nodeInvertRoughness.inputs["Color"])

    links.new(nodeMathSpec.outputs[0], nodeMathSpec2.inputs[0])
    links.new(nodeMathMetal.outputs[0], nodeMathMetal2.inputs[0])
    links.new(nodeInvertRoughness.outputs[0], nodeGamma.inputs[0])

    links.new(nodeSeparateRGBNorm.outputs["R"], nodeCombineRGB.inputs["R"])
    links.new(nodeSeparateRGBNorm.outputs["G"], nodeInvert.inputs["Color"])
    links.new(nodeInvert.outputs["Color"], nodeCombineRGB.inputs["G"])
    links.new(nodeSeparateRGBNorm.outputs["B"], nodeCombineRGB.inputs["B"])
    links.new(nodeCombineRGB.outputs["Image"], nodeNormal.inputs["Color"])
    links.new(nodeInput.outputs['Normal Strength'], nodeNormal.inputs["Strength"])

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


def read(filename, prefix='', importNormal=True, importEffect=True):
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
    print("Processing material: " + mat.name)
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
        nodeTex.location = (-tile, -tile * (i))
        nodeTex.width = 250
        nodeTex.color_space = 'NONE'

        tex, is_tif = load_textures(texData[0], root, t)
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
            nodeTex.label = "Texture: Unknown"
        if typ == owm_types.TextureTypes['DiffuseAO'] or typ == owm_types.TextureTypes['DiffuseOpacity'] or typ == owm_types.TextureTypes['DiffuseBlack']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Color"])
            nodeTex.color_space = 'COLOR'
        if typ == typ == owm_types.TextureTypes['DiffuseOpacity']:
            links.new(nodeTex.outputs["Alpha"], nodeOverwatch.inputs["Opacity"])
        if typ == owm_types.TextureTypes['DiffuseBlack']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Opacity"])
        if typ == owm_types.TextureTypes['Opacity']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Opacity"])
        if typ == owm_types.TextureTypes['Tertiary']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["OWSpecMap"])
        if typ == owm_types.TextureTypes['Emission'] or typ == owm_types.TextureTypes['Emission2']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Emission Mask"])
        if typ == owm_types.TextureTypes['Normal'] or typ == owm_types.TextureTypes['HairNormal'] or typ == owm_types.TextureTypes['CorneaNormal']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Normal"])
            if is_tif:
                nodeOverwatch.inputs["Normal Strength"].default_value = -1

    return mat


def process_material_BI(material, prefix, importNormal, importEffect, root, t):
    mat = bpy.data.materials.new('%s%016X' % (prefix, material.key))
    mat.diffuse_intensity = 1.0
    for texturetype in material.textures:
        typ = texturetype[1]
        texture = texturetype[0]
        if importNormal is False and typ == owm_types.OWMATTypes['NORMAL']:
            continue
        if importEffect is False and typ == owm_types.OWMATTypes['SHADER']:
            continue

        tex, is_tif = load_textures(texture, root, t)

        try:
            mattex = mat.texture_slots.add()
            mattex.use_map_color_diffuse = True
            mattex.diffuse_factor = 1
            if typ == owm_types.OWMATTypes['NORMAL']:
                tex.use_alpha = False
                tex.use_normal_map = True
                mattex.use_map_color_diffuse = False
                mattex.use_map_normal = True
                mattex.normal_factor = -1
                mattex.diffuse_factor = 0
            elif typ == owm_types.OWMATTypes['SHADER']:
                mattex.use = False
            mattex.texture = tex
            mattex.texture_coords = 'UV'
        except Exception as e:
            print(e)

    return mat

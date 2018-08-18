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

OVERWATCH_NODEGROUP_PRIMARY_NAME = "OWM: Physically Based Shading"

def create_overwatch_shader(tile=300): # Creates the Overwatch nodegroup, if it doesn't exist yet
    global OVERWATCH_NODEGROUP_PRIMARY_NAME
    if(bpy.data.node_groups.find(OVERWATCH_NODEGROUP_PRIMARY_NAME) is not -1):
        return
    path = os.path.join(os.path.dirname(__file__), "library.blend")
    with bpy.data.libraries.load(path, False) as (data_from, data_to):
        data_to.node_groups = [node_name for node_name in data_from.node_groups if not node_name in bpy.data.node_groups and node_name.startswith("OWM")]
        print("[import_owmat] imported node groups: %s" % (', '.join(data_to.node_groups)))

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
    global OVERWATCH_NODEGROUP_PRIMARY_NAME
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
    nodeOverwatch.node_tree = bpy.data.node_groups[OVERWATCH_NODEGROUP_PRIMARY_NAME]
    nodeOverwatch.location = (0, 0)
    nodeOverwatch.width = 250
    links.new(nodeOverwatch.outputs[0], material_output.inputs[0])

    hasColorEnv = False
    baseColorMap = None
    hasNormalEnv = False
    baseNormalMap = None
    hasPBREnv = False
    basePBRMap = None

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
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Base Color Map"])
            nodeTex.color_space = 'COLOR'
            baseColorMap = nodeTex 
        if typ == tt['DiffuseAO']:
            nodeTex.image.use_alpha = False
        if typ == tt['DiffuseEnv']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Secondary Color Map"])
            nodeTex.color_space = 'COLOR'
            hasColorEnv = True
        if typ == tt['DiffuseOpacity']:
            links.new(nodeTex.outputs["Alpha"], nodeOverwatch.inputs["Opacity Map"])
        if typ == tt['DiffuseBlack']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Opacity Map"])
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Emission Map"])
        if typ == tt['Opacity'] or typ == tt['Opacity2']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Opacity Map"])
        if typ == tt['Tertiary'] or typ == tt['Tertiary2']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Base PBR Map"])
            basePBRMap = nodeTex
        if typ == tt['TertiaryEnv']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Secondary PBR Map"])
            hasColorEnv = True
        if typ == tt['Emission'] or typ == tt['Emission2'] or typ == tt['Emission3']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Emission Map"])
        if typ == tt['Normal'] or typ == tt['AnisotropyNormal'] or typ == tt['RefractNormal']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Base Normal Map"])
            baseNormalMap = nodeTex
        if typ == tt['NormalEnv']:
            links.new(nodeTex.outputs["Color"], nodeOverwatch.inputs["Secondary Normal Map"])
            hasNormalEnv = True
    
    if not hasColorEnv and baseColorMap is not None: links.new(baseColorMap.outputs["Color"], nodeOverwatch.inputs["Secondary Color Map"])
    if not hasNormalEnv and baseNormalMap is not None: links.new(baseNormalMap.outputs["Color"], nodeOverwatch.inputs["Secondary Normal Map"])
    if not hasPBREnv and basePBRMap is not None: links.new(basePBRMap.outputs["Color"], nodeOverwatch.inputs["Secondary PBR Map"])

    nodes.active = baseColorMap
    
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

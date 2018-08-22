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
            print('[import_owmat]: removed material: {}'.format(mat.name))
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
    ''' Loads an overwatch texture.
 
    Priority (high to low): TIFF, TGA, DDS (doesn't work properly)
    '''
    realpath = bpyhelper.normpath(texture)
    if not os.path.isabs(realpath):
        realpath = bpyhelper.normpath('%s/%s' % (root, realpath))

    tga_file = mutate_texture_path(realpath, '.tga')
    if os.path.exists(tga_file):
        realpath = tga_file
    
    tif_file = mutate_texture_path(realpath, '.tif')
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
        print('[import_owmat]: error loading texture: {}'.format(e))
    return None

def read(filename, prefix = '', importNormal = True, importEffect = True):
    root, file = os.path.split(filename)
    data = read_owmat.read(filename)
    if not data:
        return None

    t = {}
    m = {}

    if bpy.context.scene.render.engine.startswith('BLENDER'):
        bpy.context.scene.render.engine = 'CYCLES'

    for i in range(len(data.materials)):
        m[data.materials[i].key] = process_material_Cycles(data.materials[i], prefix, root, t)

    return (t, m)

def process_material_Cycles(material, prefix, root, t):
    mat = bpy.data.materials.new('%s%016X' % (prefix, material.key))

    # print('Processing material: ' + mat.name)
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
    if material.shader != 0:
        print('[import_owmat]: {} uses shader {}'.format(mat.name, material.shader))
        nodeOverwatch.label = 'OWM Shader %d' % (material.shader)
    
    if str(material.shader) in owm_types.TextureTypes['NodeGroups'] and owm_types.TextureTypes['NodeGroups'][str(material.shader)] in bpy.data.node_groups:
        nodeOverwatch.node_tree = bpy.data.node_groups[owm_types.TextureTypes['NodeGroups'][str(material.shader)]]
    else:
        print('[import_owmat]: could not find node group for shader %s, using default' % (material.shader))
        if owm_types.TextureTypes['NodeGroups']['Default']+"s" in bpy.data.node_groups:
            nodeOverwatch.node_tree = bpy.data.node_groups[owm_types.TextureTypes['NodeGroups']['Default']]
        else:
            print('[import_owmat]: could not find fallback shader %s' % (owm_types.TextureTypes['NodeGroups']['Default']))
    nodeOverwatch.location = (0, 0)
    nodeOverwatch.width = 250
    if nodeOverwatch.node_tree is not None:
        links.new(nodeOverwatch.outputs[0], material_output.inputs[0])

    tt = owm_types.TextureTypesById
    tm = owm_types.TextureTypes
    scratchSocket = {}
    for i, texData in enumerate(material.textures):
        nodeTex = nodes.new('ShaderNodeTexImage')
        nodeTex.location = (-tile, -tile*(i))
        nodeTex.width = 250
        nodeTex.color_space = 'NONE'
        
        tex = load_textures(texData[0], root, t)
        if tex is None:
            print('[import_owmat]: failed to load texture: {}'.format(texData[0]))
            continue
        nodeTex.image = tex.image

        if len(texData) == 2:
            continue

        if nodeOverwatch.node_tree is None:
            continue

        typ = texData[2]
        nodeTex.label = str(typ)
        if typ in tt:
            bfTyp = tm['Mapping'][tt[typ]]
            print('[import_owmat]: {} is {}'.format(os.path.basename(texData[0]), tt[typ]))
            nodeTex.label = str(tt[typ])
            nodeTex.name = str(tt[typ])
            for colorSocketPoint in bfTyp[0]:
                nodeSocketName = colorSocketPoint
                if colorSocketPoint in tm['Alias']:
                    nodeSocketName = tm['Alias'][colorSocketPoint]
                if colorSocketPoint not in scratchSocket:
                    if nodeSocketName in nodeOverwatch.inputs:
                        links.new(nodeTex.outputs['Color'], nodeOverwatch.inputs[nodeSocketName])
                        scratchSocket[colorSocketPoint] = nodeTex.outputs['Color']
                    else:
                        print('[import_owmat] could not find node %s on shader group' % (nodeSocketName))
            for alphaSocketPoint in bfTyp[1]:
                nodeSocketName = alphaSocketPoint
                if alphaSocketPoint in tm['Alias']:
                    nodeSocketName = tm['Alias'][alphaSocketPoint]
                if alphaSocketPoint not in scratchSocket:
                    if nodeSocketName in nodeOverwatch.inputs:
                        links.new(nodeTex.outputs['Alpha'], nodeOverwatch.inputs[nodeSocketName])
                        scratchSocket[alphaSocketPoint] = nodeTex.outputs['Alpha']
                    else:
                        print('[import_owmat] could not find node %s on shader group' % (nodeSocketName))

    if nodeOverwatch.node_tree is None:
        return mat
            
    for envPoint, basePoint in tm['Env'].items():
        if envPoint in scratchSocket or basePoint not in scratchSocket: continue
        nodeSocketName = envPoint
        if envPoint in tm['Alias']:
            nodeSocketName = tm['Alias'][envPoint]
        if nodeSocketName in nodeOverwatch.inputs:
            links.new(scratchSocket[basePoint], nodeOverwatch.inputs[nodeSocketName])
            scratchSocket[envPoint] = scratchSocket[basePoint]

    for activeNodePoint in tm['Active']:
        if activeNodePoint in scratchSocket:
            nodes.active = scratchSocket[activeNodePoint].node
            break
    
    return mat

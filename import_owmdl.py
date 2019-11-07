import os
from math import radians

from . import bpyhelper
from . import read_owmdl
from . import import_owmat
from . import owm_types
from mathutils import *
import bpy, bpy_extras, mathutils, bmesh, random, collections

root = ''
settings = None
data = None
rootObject = None
blenderBoneNames = []

def newBoneName():
    global blenderBoneNames
    blenderBoneNames = []
def addBoneName(newName):
    global blenderBoneNames
    blenderBoneNames += [newName]
def getBoneName(originalIndex):
    if originalIndex >= len(blenderBoneNames) or originalIndex == -1:
        return None
    return blenderBoneNames[originalIndex]

def importArmature(autoIk):
    bones = data.refpose_bones
    if len(bones) == 0:
        return

    armature = None
    armData = bpy.data.armatures.new('Armature')
    armData.display_type = 'STICK'
    armature = bpy.data.objects.new('Armature', armData)
    armature.show_in_front = True

    bpyhelper.scene_link(armature)

    bpyhelper.scene_active_set(armature)
    bpy.ops.object.mode_set(mode='EDIT')

    # The bones are not topologically sorted, so make two passes
    # over the list. The first computes the matrices for all
    # bones, and the second pass applies parenting since all bones
    # are guaranteed to exist then.
    newBoneName()
    matrices = {}
    for bone in bones:
        bbone = armData.edit_bones.new(bone.name)
        bbone.tail = 0, 0.05, 0 # Blender removes zero-length bones
        addBoneName(bbone.name)
        
        mpos = Matrix.Translation(xzy(bone.pos))
        mrot = euler(bone.rot).to_matrix().to_4x4()
        matrices[bone.name] = mpos @ mrot

        
        
    for i, bone in enumerate(bones):
        if getBoneName(bone.parent) is not None:
            bbone = armData.edit_bones[i]
            bbone.parent = armature.data.edit_bones[bone.parent]

    # Pose the skeleton by applying the computed matrices.
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    for bone in armature.pose.bones:
        bone.matrix_basis.identity()
        bone.matrix = matrices[bone.name]

    bpy.ops.pose.armature_apply()

    # Visualization for the bones. Based on code from SEAnim importer.
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=2)
    bone_vis = bpy.context.active_object
    bone_vis.data.name = bone_vis.name = "smd_bone_vis"
    bone_vis.use_fake_user = True
    bpyhelper.scene_unlink(bone_vis)
    bpy.context.view_layer.objects.active = armature

    # Calculate armature dimensions...Blender should be doing this!
    maxs = [0,0,0]
    mins = [0,0,0]

    j = 0
    for bone in armData.bones:
        for i in range(3):
            maxs[i] = max(maxs[i],bone.head_local[i])
            mins[i] = min(mins[i],bone.head_local[i])
    
    dimensions = []
    for i in range(3):
            dimensions.append(maxs[i] - mins[i])
    
    length = max(0.001, (dimensions[0] + dimensions[1] + dimensions[2]) / 600) # very small indeed, but a custom bone is used for display
    
    # Apply spheres
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in [armData.edit_bones[b.name] for b in bones]:
            bone.tail = bone.head + (bone.tail - bone.head).normalized() * length # Resize loose bone tails based on armature size
            armature.pose.bones[bone.name].custom_shape = bone_vis # apply bone shape    
    bpy.ops.object.mode_set(mode='OBJECT')
    # armData.use_auto_ik = autoIk

    bpy.ops.object.mode_set(mode='OBJECT')
    # armature.data.use_auto_ik = autoIk
    return armature

def euler(rot): return Euler(rot[0:3])

def xzy(pos): return Vector(pos)

def wxzy(rot):
    quat = Quaternion()
    quat.x = rot[0]
    quat.y = rot[1]
    quat.z = rot[2]
    quat.w = rot[3]
    return quat

def segregate(vertex):
    pos = []
    norms = []
    uvs = []
    boneData = []
    col1 = []
    col2 = []
    for vert in vertex:
        pos += [xzy(vert.position)]
        norm = Vector(vert.normal).normalized()
        norm[0] = -norm[0]
        norm[1] = -norm[1]
        norm[2] = -norm[2]
        norms += [norm]
        uvs += [vert.uvs]
        boneData += [[vert.boneIndices, vert.boneWeights]]
        col1 += [vert.color1]
        col2 += [vert.color2]
    return (pos, norms, uvs, boneData, col1, col2)

def detach(faces):
    f = []
    for face in faces:
        f += [face.points]
    return f

def makeVertexGroups(mesh, boneData):
    for vidx in range(len(boneData)):
        indices, weights = boneData[vidx]
        for idx in range(len(indices)):
            i = indices[idx]
            w = weights[idx]

            if w != 0:
                name = getBoneName(i)
                if name != None:
                    vgrp = mesh.vertex_groups.get(name)
                    if vgrp == None:
                        vgrp = mesh.vertex_groups.new(name = name)
                    vgrp.add([vidx], w, 'REPLACE')

def randomColor():
    randomR = random.random()
    randomG = random.random()
    randomB = random.random()
    return (randomR, randomG, randomB)

def bindMaterials(meshes, data, materials):
    if materials == None:
        return
    for i, obj in enumerate(meshes):
        mesh = obj.data
        meshData = data.meshes[i]
        if materials != None and meshData.materialKey in materials[1]:
            mesh.materials.clear()
            mesh.materials.append(materials[1][meshData.materialKey])
        else:
            print('[import_owmdl]: Unable to find material: {}'.format(meshData.materialKey))

def bindMaterialsUniq(meshes, data, materials):
    if materials == None:
        return
    for i, obj in enumerate(meshes):
        mesh = obj.data
        meshData = data.meshes[i]
        if meshData.materialKey in materials[1]:
            mesh.materials.clear()
            mesh.materials.append(None)
            obj.material_slots[0].link = 'OBJECT'
            obj.material_slots[0].material = materials[1][meshData.materialKey]
        else:
            print('[import_owmdl]: Unable to find material %016X in provided material set' % (meshData.materialKey))

def importMesh(armature, meshData):
    global settings
    global rootObject
    mesh = bpy.data.meshes.new(meshData.name)
    obj = bpy.data.objects.new(mesh.name, mesh)
    obj.parent = rootObject
    bpyhelper.scene_link(obj)

    pos, norms, uvs, boneData, col1, col2 = segregate(meshData.vertices)
    faces = detach(meshData.indices)
    mesh.from_pydata(pos, [], faces)
    mesh.polygons.foreach_set('use_smooth', [True] * len(mesh.polygons))
    obj['owm.mesh.name'] = mesh.name

    if armature:
        mod = obj.modifiers.new(type='ARMATURE', name='OWM Skeleton')
        mod.use_vertex_groups = True
        mod.object = armature
        obj.parent = armature

        makeVertexGroups(obj, boneData)

        current_theme = bpy.context.preferences.themes.items()[0][0]
        theme = bpy.context.preferences.themes[current_theme]

        bgrp = armature.pose.bone_groups.new(name = obj.name)
        bgrp.color_set = 'CUSTOM'
        bgrp.colors.normal = (randomColor())
        bgrp.colors.select = theme.view_3d.bone_pose
        bgrp.colors.active = theme.view_3d.bone_pose_active

        vgrps = obj.vertex_groups.keys()
        pbones = armature.pose.bones
        for bname in vgrps:
            pbones[bname].bone_group = bgrp

    if settings.importColor and len(col1) > 0 and len(col1[0]) > 0:
        bpyhelper.new_color_layer(mesh, 'ColorMap1')
        bpyhelper.new_color_layer(mesh, 'ColorMap1Blue')
        bpyhelper.new_color_layer(mesh, 'ColorMap2')
        bpyhelper.new_color_layer(mesh, 'ColorMap2Blue')
    for i in range(meshData.uvCount):
        bpyhelper.new_uv_layer(mesh, 'UVMap%d' % (i + 1))
    bm = bmesh.new()
    bm.from_mesh(mesh)
    for fidx, face in enumerate(bm.faces):
        fraw = faces[fidx]
        for vidx, vert in enumerate(face.loops):
            ridx = fraw[vidx]
            for idx in range(len(mesh.uv_layers)):
                layer = bm.loops.layers.uv[idx]]
                vert[layer].uv = Vector([uvs[ridx][idx][0] + settings.uvDisplaceX, 1 + settings.uvDisplaceY - uvs[ridx][idx][1]])
            if settings.importColor and len(col1) > 0 and len(col1[0]) > 0:
                vert[bm.loops.layers.color[0]] = bpyhelper.safe_color(col1[ridx][3], col1[ridx][0], col1[ridx][1])
                vert[bm.loops.layers.color[1]] = bpyhelper.safe_color(col1[ridx][2], col1[ridx][2], col1[ridx][2])
                vert[bm.loops.layers.color[2]] = bpyhelper.safe_color(col2[ridx][3], col2[ridx][0], col2[ridx][1])
                vert[bm.loops.layers.color[3]] = bpyhelper.safe_color(col2[ridx][2], col2[ridx][2], col2[ridx][2])
    bm.to_mesh(mesh)

    mesh.update()

    bpyhelper.select_obj(obj, True)
    if settings.importNormals:
        mesh.create_normals_split()
        mesh.validate(clean_customdata = False)
        mesh.update(calc_edges = True)
        mesh.normals_split_custom_set_from_vertices(norms)
        mesh.use_auto_smooth = False
    else:
        mesh.validate()

    return obj

def create_refpose_armature(armature_name):
    a = bpy.data.objects.new(armature_name,bpy.data.armatures.new(armature_name))
    a.show_in_front = True
    a.data.display_type = 'STICK'
    bpyhelper.scene_link(a)
    for i in bpy.context.selected_objects:
        bpyhelper.select_obj(i, False) #deselect all objects
    bpyhelper.select_obj(a, True)
    bpy.context.view_layer.objects.active = a
    bpy.ops.object.mode_set(mode='OBJECT')

    return a

def import_refpose_armature(autoIk, this_data):
    a = create_refpose_armature('AnimationArmature')
    boneIDs = {}  # temp

    newBoneName()
    def addBone(num,name):
        bone = a.data.edit_bones.new(name)
        addBoneName(name)
        bone.tail = 0,5,0 # Blender removes zero-length bones
        bone.tail = 0,1,0 # Blender removes zero-length bones
        bone.tail = 0,0.005,0
        # fixLength(bone)
        boneIDs[num] = bone.name
        return bone
    
    bpy.ops.object.mode_set(mode='EDIT',toggle=False)
    index = 0
    for bone in this_data.refpose_bones:
        addBone(index,str(bone.name))
        index += 1
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    index = 0
    for bone in this_data.refpose_bones:
        if bone.parent != -1:
            a.data.edit_bones[index].parent = a.data.edit_bones[bone.parent]
        index += 1

    bpy.context.view_layer.objects.active = a
    bpy.ops.object.mode_set(mode='POSE')

    # sect 2: get frame
    index = 0
    for refpose_bone in this_data.refpose_bones:
        pos = Vector([refpose_bone.pos[0], refpose_bone.pos[1], refpose_bone.pos[2]])
        rot = Euler([refpose_bone.rot[0], refpose_bone.rot[1], refpose_bone.rot[2]])
        # rot = wxzy(refpose_bone.rot).to_matrix().to_4x4()  # maybe use existing def?
        bone = a.pose.bones[getBoneName(index)]
        bone.matrix_basis.identity()
        bone.matrix = Matrix.Translation(pos) @ rot.to_matrix().to_4x4()
        index += 1

    # sect 3: apply
    bpy.ops.pose.armature_apply()
    
    bpy.ops.object.mode_set(mode='OBJECT')
    # a.data.use_auto_ik = autoIk
    return a

def importMeshes(armature):
    global data
    meshes = [importMesh(armature, meshData) for meshData in data.meshes]
    return meshes

def importEmpties(armature = None):
    global data
    global settings
    global rootObject

    if not settings.importEmpties:
        return None, {}

    att = bpy.data.objects.new('Hardpoints', None)
    att.parent = rootObject
    att.hide_viewport = att.hide_render = True
    att['owm.hardpoint_container'] = True
    bpyhelper.scene_link(att)

    e_dict = {}
    for emp in data.empties:
        bpy.ops.object.empty_add(type='CIRCLE', radius=0.05 )
        empty = bpy.context.active_object
        empty.parent = att
        empty.name = emp.name
        empty.location = xzy(emp.position)
        empty.rotation_mode = 'QUATERNION'
        empty.rotation_quaternion = wxzy(emp.rotation)
        empty['owm.hardpoint.bone'] = emp.hardpoint
        bpyhelper.select_obj(empty, True)
        e_dict[emp.name] = empty
    bpy.ops.object.select_all(action='DESELECT')

    if armature is not None:
        for pbone in armature.pose.bones:
            pbone.bone.select = False
        for name, hardpoint in e_dict.items():
            # erm
            bpy.ops.object.select_all(action='DESELECT')
            bpyhelper.select_obj(hardpoint, True)
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')

            if hardpoint['owm.hardpoint.bone'] not in armature.pose.bones:
                bpy.ops.object.mode_set(mode='OBJECT') # fixes 'context is incorrect'
                continue  # todo: why

            bone = armature.pose.bones[hardpoint['owm.hardpoint.bone']].bone
            bone.select = True
            armature.data.bones.active = bone
            bpy.ops.object.parent_set(type='ARMATURE')
            bone.select = False
            bpyhelper.select_obj(hardpoint, False)
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
    
    try:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    except: pass

    return att, e_dict


def select_all(ob):
    if bpyhelper.LOCK_UPDATE: pass
    bpyhelper.select_obj(ob, True)
    for obj in ob.children: select_all(obj)

def readmdl(materials = None, rotate=True):
    global root
    global data
    global rootObject
    root, file = os.path.split(settings.filename)

    data = read_owmdl.read(settings.filename)
    if not data: return None

    rootName = os.path.splitext(file)[0]
    if len(data.header.name) > 0:
        rootName = data.header.name

    rootObject = bpy.data.objects.new(rootName, None)
    rootObject.hide_viewport = rootObject.hide_render = True
    rootObject['owm.model.guid'] = data.guid
    bpyhelper.scene_link(rootObject)

    armature = None
    if settings.importSkeleton and data.header.boneCount > 0:
        armature = importArmature(settings.autoIk)
        armature.name = rootName + '_Skeleton'
        armature.parent = rootObject
        armature.show_in_front = True
        armature['owm.skeleton.name'] = armature.name
        armature['owm.skeleton.model'] = data.guid

        if rotate and not settings.importEmpties:
            armature.rotation_euler = (radians(90), 0, 0)
    meshes = importMeshes(armature)

    impMat = False
    materials = None
    if materials == None and settings.importMaterial and len(data.header.material) > 3:
        impMat = True
        matpath = data.header.material

        if not os.path.isabs(matpath):
            matpath = bpyhelper.normpath('%s/%s' % (root, matpath))
        materials = import_owmat.read(matpath, '')
        bindMaterials(meshes, data, materials)

    empties = (None, [])
    if settings.importEmpties:
        empties = importEmpties(armature)
        if rotate:
            empties[0].rotation_euler = (radians(90), 0, 0)
            if armature is not None:
                armature.rotation_euler = (radians(90), 0, 0)
    
    if impMat:
        import_owmat.cleanUnusedMaterials(materials)

    if len(data.cloths) > 0:
        for cloth in data.cloths:
            bpy.ops.object.select_all(action='DESELECT')
            i = 0
            for clothSubmesh in cloth.meshes:
                submesh = meshes[clothSubmesh.id]
                if i == 0:
                    bpy.context.view_layer.objects.active = submesh
                bpyhelper.select_obj(submesh, True)
                vgrp = submesh.vertex_groups.new('clothPin')
                vgrp.add(clothSubmesh.pinnedVerts, 1.0, 'REPLACE')
                i += 1

            bpy.ops.object.join()
            bpy.context.object.name = cloth.name

            # do it manually because I don't want to be responsible for broken models:
            # https://i.imgur.com/6Jxg91T.png?1
            # bpy.context.view_layer.objects.active = mainObj
            # bpy.ops.object.editmode_toggle()
            # bpy.ops.mesh.select_all(action='SELECT')
            # bpy.ops.mesh.remove_doubles()
            # bpy.ops.object.editmode_toggle()

    bpy.ops.object.select_all(action='DESELECT')
    select_all(rootObject)

    return (rootObject, armature, meshes, empties, data)

def read(aux, materials = None, mutated = False, rotate=True):
    global settings
    settings = aux

    setup()
    status = readmdl(materials, rotate)
    if not mutated:
        bpyhelper.scene_update()
    finalize()
    return status

def setup():
    mode()
    if bpyhelper.LOCK_UPDATE: return
    bpy.ops.object.select_all(action='DESELECT')

def finalize():
    mode()

def mode():
    currentMode = bpy.context.mode
    if bpyhelper.scene_active() and currentMode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

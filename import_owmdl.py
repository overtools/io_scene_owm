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
prefix_ow = "bone_0"
# Hopefully this works for all characters.
overwatch = {
    #"000" : "useless",
    "001" : "Root_Ground",
    #"38D" : "useless",
    #"180" : "useless",
    #"3BE" : "useless",
    #"181" : "useless",
    #"07D" : "useless",
    #"5F0" : "useless",
    #"07E" : "useless",
    #"0C1" : "useless",
    #"0C2" : "useless",
    "002" : "Root_Pelvis",      #!
    #"97F" : "useless",
    #"985" : "useless",
    "052" : "Spine1_Def",
    "003" : "Spine1",           #!
    "004" : "Spine2",           #!
    "005" : "Spine3",           #!
    "051" : "Spine2_Def",
    #"109" : "useless",
    "00F" : "Spine3_Def",
    "010" : "Neck_Def",
    "0EF" : "Collar_Back",      #Sombra
    "0EE" : "Collar.R",         #Sombra
    "0EC" : "Collar_Front",     #Sombra
    "0ED" : "Collar.L",         #Sombra
    "050" : "Clavicle.L",       #!
    "035" : "Clavicle.R",       #!
    "034" : "Clavicle_Def.L",
    "00D" : "Shoulder.L",       #!
    "031" : "Shoulder_Def.L",
    "04D" : "Shoulder_Def.R",
    "00E" : "Elbow.L",          #!
    "032" : "Twist_Arm_6.L",
    "04F" : "Twist_Arm_5.L",
    "01A" : "Twist_Arm_4.L",
    "01B" : "Twist_Arm_3.L",
    "030" : "Twist_Arm_2.L",
    "01C" : "Hand_Def.L",
    "029" : "Thumb1.L",
    "02A" : "Thumb2.L",
    "02B" : "Thumb3.L",
    "0E6" : "Thumb_Adjust_1.L",
    "0E4" : "Thumb_Adjust_2.L",
    "0DE" : "Thumb_Adjust_3.L",
    "0E2" : "Palm_Adjust_1.L",
    "835" : "Index1.L",
    "01D" : "Index2.L",
    "01E" : "Index3.L",
    "01F" : "Index4.L",
    "837" : "Middle1.L",
    "020" : "Middle2.L",
    "021" : "Middle3.L",
    "022" : "Middle4.L",
    "839" : "Ring1.L",
    "026" : "Ring2.L",
    "027" : "Ring3.L",
    "028" : "Ring4.L",
    "0E0" : "Pinky1.L",
    "023" : "Pinky2.L",
    "024" : "Pinky3.L",
    "025" : "Pinky4.L",
    "0EA" : "Palm_Adjust_2.L",
    "036" : "Shoulder.R",       #!
    "00C" : "Clavicle_Def.R",
    "037" : "Elbow.R",          #!
    "04E" : "Twist_Arm_6.R",
    "033" : "Twist_Arm_5.R",
    "038" : "Twist_Arm_4.R",
    "039" : "Twist_Arm_3.R",
    #"04A" : "useless",
    "04C" : "Twist_Arm_2.R",
    "03A" : "Hand_Def.R",
    "047" : "Thumb1.R",
    "0E7" : "Thumb_Adjust_1.R",
    "0E5" : "Thumb_Adjust_2.R",
    "0DF" : "Thumb_Adjust_3.R",
    "048" : "Thumb2.R",
    "049" : "Thumb3.R",
    "0E3" : "Palm_Adjust_1.R",
    "836" : "Index1.R",
    "03B" : "Index2.R",
    "03C" : "Index3.R",
    "03D" : "Index4.R",
    "838" : "Middle1.R",
    "03E" : "Middle2.R",
    "03F" : "Middle3.R",
    "040" : "Middle4.R",
    "83A" : "Ring1.R",
    "044" : "Ring2.R",
    "045" : "Ring3.R",
    "046" : "Ring4.R",
    "0E1" : "Pinky1.R",
    "041" : "Pinky2.R",
    "042" : "Pinky3.R",
    "043" : "Pinky4.R",
    "0EB" : "Palm_Adjust_2.R",
    "011" : "Head_Def",
    "016" : "Eyebrow_Mid",
    "017" : "EyeBrow1.L",
    "018" : "EyeBrow2.L",
    "019" : "EyeBrow3.L",
    "385" : "EyeBrow4.L",
    "012" : "Head_Top",
    "388" : "Nose_Bridge.L",
    "39A" : "Eye.L",
    "397" : "Eyelid_Top_2_Rot.L",
    "396" : "Eyelid_Bot_2_Rot.L",
    "007" : "Eyelid_Corner_Outer.L",
    "38C" : "Eyelid_Top_3.L",
    "38B" : "Eyelid_Top_2.L",
    "38A" : "Eyelid_Top_1.L",
    "006" : "Eyelid_Corner_Inner.L",
    "38D" : "Eyelid_Bot_1.L",
    "38E" : "Eyelid_Bot_2.L",
    "38F" : "Eyelid_Bot_3.L",
    "608" : "Cheek_Upper_Inner.L",
    "3A2" : "Cheek_Upper_Middle.L",
    "60A" : "Cheek_Upper_Outer.L",
    "71D" : "Cheek_Mid_Outer.L",
    "39E" : "Cheek_Mid.L",
    "3A4" : "Cheek_Mid_Inner.L",
    "009" : "Nose.L",
    "008" : "Nose_Tip",
    "00B" : "Face_Lower",       #!
    "3BC" : "Jaw",
    "3B7" : "Teeth_Top",
    "3B8" : "Teeth_Bottom",
    "3BB" : "Tongue1",
    "3BA" : "Tongue2",
    "3B9" : "Tongue3",
    "3A0" : "Cheek_Jaw_2.L",
    "3A6" : "Cheek_Jaw_1.L",
    "60C" : "Cheek_LaughLine.L",
    "3AA" : "Lip_Top_Mid",
    "3A9" : "Lip_Top_2.L",
    "3A8" : "Lip_Top_3.L",
    "3B0" : "Lip_Corner.L",
    "3AF" : "Lip_Bottom_3.L",
    "3AC" : "Lip_Bottom_2.L",
    "3AD" : "Chin_Outer.L",
    "3AB" : "Lip_Bottom_Mid",
    "3B6" : "Chin_Mid",
    "015" : "EyeBrow1.R",
    "014" : "EyeBrow2.R",
    "013" : "EyeBrow3.R",
    "384" : "EyeBrow4.R",
    "39B" : "Eye.R",
    "398" : "Eyelid_Bot_2_Rot.R",
    "399" : "Eyelid_Top_2_Rot.R",
    "389" : "Nose_Bridge.R",
    "386" : "Eyelid_Corner_Outer.R",
    "395" : "Eyelid_Top_3.R",
    "394" : "Eyelid_Top_2.R",
    "393" : "Eyelid_Top_1.R",
    "387" : "Eyelid_Corner_Inner.R",
    "391" : "Eyelid_Bot_1.R",
    "390" : "Eyelid_Bot_2.R",
    "392" : "Eyelid_Bot_3.R",
    "609" : "Cheek_Upper_Inner.R",
    "3A3" : "Cheek_Upper_Middle.R",
    "60B" : "Cheek_Upper_Outer.R",
    "71E" : "Cheek_Mid_Outer.R",
    "39F" : "Cheek_Mid.R",
    "3A5" : "Cheek_Mid_Inner.R",
    "00A" : "Nose.R",
    "60D" : "Cheek_LaughLine.R",
    "3A7" : "Cheek_Jaw_1.R",
    "3A1" : "Cheek_Jaw_2.R",
    "3B4" : "Lip_Top_2.R",
    "3B5" : "Lip_Top_3.R",
    "3B3" : "Lip_Corner.R",
    "3B2" : "Lip_Bottom_3.R",
    "3B1" : "Lip_Bottom_2.R",
    "3AE" : "Chin_Outer.R",
    "056" : "Thigh_Def.L",
    "055" : "Thigh.L",          #!
    "059" : "Knee.L",           #!
    "060" : "Thigh_Def.R",
    "05F" : "Thigh.R",          #!
    "063" : "Knee.R",
    "057" : "Twist_Leg_4.L",
    "061" : "Twist_Leg_4.R",
    "058" : "Twist_Leg_3.L",
    "062" : "Twist_Leg_3.R",
    "05C" : "Knee_Def.L",
    "066" : "Knee_Def.R",
    "05D" : "Twist_Leg_2.L",
    "067" : "Twist_Leg_2.R",
    "05E" : "Twist_Leg_1.L",
    "068" : "Twist_Leg_1.R",
    "05A" : "Foot_Def.L",
    "064" : "Foot_Def.R",
    "05B" : "Toe_Def.L",
    "065" : "Toe_Def.R",
    #"3BD" : "useless",
    #"180" : "useless",
    "17A" : "BackThing",
    #"984" : "useless",
    "054" : "Hip_Def",
    "053" : "Hip",          #!
    "7B3" : "Hair_1",
    "7B4" : "Hair_2",
    "7B5" : "Hair_3",
    "7B6" : "Hair_4",
    "624" : "Twist_Arm_1.L",
    "61F" : "Twist_Arm_1.R",
    "0E8" : "Hand_Adjust.L",
    "0E9" : "Hand_Adjust.R",
    "57B" : "Clavicle_Adjust.L",
    "57C" : "Clavicle_Adjust.R",
    "57E" : "Neck_Def"
}

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

def rename_bones(armature):
    ''' Rename bones using a dictionary ''' # Relies on the assumption that all characters use the same bone IDs for roughly the same bones. Possibly wrong.
    
    prefix = prefix_ow
    name_dict = overwatch

    for b in armature.pose.bones:
        try:
            new_name = name_dict[b.name[len(prefix):]]
            print("Renaming " + b.name + " to: " + new_name)
            for i, bn in enumerate(blenderBoneNames):
                if bn == b.name:
                    blenderBoneNames[i] = new_name
            b.name = new_name
        except KeyError:
            print("Not renaming:" + b.name)

def fix_bone_tail(edit_bones, bone=None):
    ''' Recursive function to go through a bone hierarchy and move the bone tails to useful positions when possible. '''
    
    assert len(edit_bones) > 0, "Armature needs to be in edit mode and has to have bones."
    
    scale = 0.005
    
    default = ["Teeth_Top", "Teeth_Bottom", "Lip_Bottom_2.L", "Lip_Bottom_2.R", "Lip_Bottom_3.L", "Lip_Bottom_3.R", "Lip_Bottom_Mid", "Lip_Corner.L", "Lip_Corner.R", "Chin_Outer.L", "Chin_Outer.R", "Cheek_Jaw_1.L", "Cheek_Jaw_1.R", "Cheek_Jaw_2.L", "Cheek_Jaw_2.R", "Cheek_Mid.L", "Cheek_Mid.R", "Lip_Top_2.L", "Lip_Top_2.R", "Lip_Top_3.L", "Lip_Top_3.R", "Lip_Top_Mid", "Cheek_Mid_Outer.L", "Cheek_Mid_Outer.R", "Cheek_LaughLine.L", "Cheek_LaughLine.R", "Eyelid_Bot_1.L", "Eyelid_Bot_2.L", "Eyelid_Bot_3.L", "Eyelid_Bot_1.R", "Eyelid_Bot_2.R", "Eyelid_Bot_3.R", "Eyelid_Top_1.L", "Eyelid_Top_2.L", "Eyelid_Top_3.L", "Eyelid_Top_1.R", "Eyelid_Top_2.R", "Eyelid_Top_3.R", "Nose_Tip", "Nose.L", "Nose.R"]

    # Dictionary for connecting specific bones
    connect_dict = {
        'Head_Def' : 'Head_Top',
        'Eyelid_Top_2_Rot.L' : 'Eyelid_Top_2.L',
        'Eyelid_Top_2_Rot.R' : 'Eyelid_Top_2.R',
        'Spine3' : 'Neck_Def',
        'Spine2' : 'Spine3',
        'Spine1' : 'Spine2',
        'Hip' : 'Spine2',
        'Hand_Def.L' : 'Middle2.L',
        'Hand_Def.R' : 'Middle2.R',
    }

    if(bone == None):
        bone=edit_bones[0]
    
    # Give some bones a default scale and orientation
    if(bone.name in default):
        bone.tail = bone.head + Vector((0, 0, 0.01))
    # If a bone is in connect_dict, just move its tail to the bone specified in the dictionary.
    elif(bone.name in connect_dict):
        target = edit_bones.get(connect_dict[bone.name])
        if(target != None):
            bone.tail = target.head
    else:
        # For bones with multiple children, we connect the bone to the farthest away child.
        if(len(bone.children) > 0):
            farthest_child = bone.children[0]
            farthest_distance = 0
            for c in bone.children:
                distance = (bone.head - c.head).length
                if(distance > farthest_distance):
                    farthest_child = c
                    farthest_distance = distance
            
            if(farthest_distance > 0.001):
                bone.tail = farthest_child.head
        
        # For bones with no children...
        else:
            if(bone.parent != None):
                # Get the parent's head->tail vector
                parent_vec = bone.parent.tail - bone.parent.head
                # If the bone has siblings, set the scale to an arbitrary amount.
                if( len(bone.parent.children) > 1): 
                    bone.tail = bone.head + parent_vec.normalized() * scale
                # If no siblings, just use the parents transforms.
                else:
                    bone.tail = bone.head + parent_vec
        
    if(bone.name in default):
        bone.tail = bone.head + Vector((0, scale, 0))
    # Recursion over this bone's children.
    for c in bone.children:
        fix_bone_tail(edit_bones, c)

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
            #armature.pose.bones[bone.name].custom_shape = bone_vis # apply bone shape    
    bpy.ops.object.mode_set(mode='OBJECT')
    armature.pose.use_auto_ik = autoIk

    bpy.ops.object.mode_set(mode='OBJECT')
    armature.pose.use_auto_ik = autoIk
    
    if(settings.renameBones):
        rename_bones(armature)
    
    if(settings.adjustTails):
        bpy.ops.object.mode_set(mode='EDIT')
        fix_bone_tail(armature.data.edit_bones, armature.data.edit_bones.get("Root_Pelvis"))
    bpy.ops.object.mode_set(mode='OBJECT')

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
    for i in range(meshData.uvCount):
        bpyhelper.new_uv_layer(mesh, 'UVMap%d' % (i + 1))

    if settings.importColor and len(col1) > 0 and len(col1[0]) > 0:
        bpyhelper.new_color_layer(mesh, 'ColorMap1')
        bpyhelper.new_color_layer(mesh, 'ColorMap1Blue')
        bpyhelper.new_color_layer(mesh, 'ColorMap2')
        bpyhelper.new_color_layer(mesh, 'ColorMap2Blue')
        i = 0
        for loop in mesh.loops: # ARGB
            mesh.vertex_colors['ColorMap1'].data[i].color = bpyhelper.safe_color(col1[loop.vertex_index][3], col1[loop.vertex_index][0], col1[loop.vertex_index][1])
            mesh.vertex_colors['ColorMap1Blue'].data[i].color = bpyhelper.safe_color(col1[loop.vertex_index][2], col1[loop.vertex_index][2], col1[loop.vertex_index][2])
            mesh.vertex_colors['ColorMap2'].data[i].color = bpyhelper.safe_color(col2[loop.vertex_index][3], col2[loop.vertex_index][0], col2[loop.vertex_index][1])
            mesh.vertex_colors['ColorMap2Blue'].data[i].color = bpyhelper.safe_color(col2[loop.vertex_index][2], col2[loop.vertex_index][2], col2[loop.vertex_index][2])
            i += 1

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

    bm = bmesh.new()
    bm.from_mesh(mesh)
    for fidx, face in enumerate(bm.faces):
        fraw = faces[fidx]
        for vidx, vert in enumerate(face.loops):
            ridx = fraw[vidx]
            for idx in range(len(mesh.uv_layers)):
                layer = bm.loops.layers.uv[idx]
                vert[layer].uv = Vector([uvs[ridx][idx][0] + settings.uvDisplaceX, 1 + settings.uvDisplaceY - uvs[ridx][idx][1]])
    bm.to_mesh(mesh)

    mesh.update()

    bpyhelper.select_obj(obj, True)
    if settings.importNormals:
        mesh.create_normals_split()
        mesh.validate(clean_customdata = False)
        mesh.update(calc_edges = True)
        mesh.normals_split_custom_set_from_vertices(norms)
        mesh.use_auto_smooth = True
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
    a.pose.use_auto_ik = autoIk
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
        import_owmat.clean_unused_materials(materials)

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
        bpyhelper.viewlayer_update()
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

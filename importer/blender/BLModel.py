import itertools
import random

import bpy
from mathutils import *
from math import radians


from . import BLUtils
from ...datatypes.ModelTypes import ModelData
from ...readers import OWModelReader
from ...readers import PathUtil


def euler(rot):
    rot = (rot[0], -rot[2], rot[1])
    rot = Euler(rot[0:3])
    return rot

rotation = Euler(map(radians, (90, 0, 0)), 'XYZ').to_matrix().to_4x4()

def xzy(pos):
    pos = Vector(pos).xzy
    pos[1] = -pos[1]
    return pos


def wxzy(rot):
    quat = Quaternion()
    quat.x = rot[0]
    quat.y = rot[1]
    quat.z = rot[2]
    quat.w = rot[3]
    return quat


def randomColor():
    randomR = random.random()
    randomG = random.random()
    randomB = random.random()
    return (randomR, randomG, randomB)


def importEmpties(meshData, armature=None, blendBones=[]):
    socketsFolder = bpy.data.objects.new('Sockets', None)
    socketsFolder.hide_viewport = socketsFolder.hide_render = True
    socketsFolder['owm.hardpoint_container'] = True

    empties = {}
    for emp in meshData.empties:
        empty = bpy.data.objects.new(emp.name, None)
        empty.empty_display_size = .05
        empty.empty_display_type = "SPHERE"
        #empty.parent = socketsFolder
        empty.location = xzy(emp.position)
        empty.rotation_mode = 'QUATERNION'
        empty.rotation_quaternion = wxzy(emp.rotation)
        empty['owm.hardpoint.bone'] = emp.hardpoint

        if armature is not None and emp.hardpoint in blendBones:
            constraint = empty.constraints.new(type="ARMATURE")
            target = constraint.targets.new()
            target.target = armature
            target.subtarget = emp.hardpoint

        empties[emp.name] = empty

    return socketsFolder, empties


def importArmature(meshData):  # honestly fuck this 2x
    restPoseBones = meshData.refPoseBones

    armature = None
    armData = bpy.data.armatures.new('Armature')
    armData.display_type = 'STICK'
    armature = bpy.data.objects.new('Armature', armData)
    armature.show_in_front = True

    BLUtils.linkScene(armature)

    BLUtils.setActive(armature)
    bpy.ops.object.editmode_toggle()

    matrices = {}
    blendBoneNames = []
    for bone in restPoseBones:
        blendBone = armData.edit_bones.new(bone.name)
        blendBone.tail = 0, 0.05, 0  # Blender removes zero-length bones
        blendBoneNames.append(blendBone.name)

        mpos = Matrix.Translation(bone.pos)
        mrot = Euler(bone.rot).to_matrix().to_4x4()
        """mrot = mrot @ Matrix(((-1, 0, 0, 0),
        (0, 0, 1, 0),
        (0, 1, 0, 0),
        (0, 0, 0, 1)))"""
        matrices[bone.name] = mpos @ mrot

    for i, bone in enumerate(restPoseBones):
        if bone.parent != -1:
            blendBone = armData.edit_bones[i]
            blendBone.parent = armature.data.edit_bones[bone.parent]
            blendBone.tail = blendBone.head + (blendBone.tail - blendBone.head).normalized() * .001

    # Pose the skeleton by applying the computed matrices.
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.posemode_toggle()

    for bone in armature.pose.bones:
        bone.matrix_basis.identity()
        bone.matrix = matrices[bone.name]

    
    bpy.ops.pose.armature_apply()
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    armature.data.transform(rotation)
    BLUtils.unlinkScene(armature)
    return armature, blendBoneNames


def makeVertexGroups(mesh, meshData, blendBoneNames):
    # store weights per bone
    boneMap = {}

    # loop through all vertices
    for vertexIndex, indices in enumerate(meshData.boneIndices):
        for index, boneIndex in enumerate(indices):
            boneWeight = meshData.boneWeights[vertexIndex][index]

            if boneWeight != 0 and boneIndex != -1 and boneIndex < len(blendBoneNames):
                boneName = blendBoneNames[boneIndex]
                boneMap.setdefault(boneName, {})
                boneMap[boneName].setdefault(boneWeight, [])
                boneMap[boneName][boneWeight].append(vertexIndex)

    for boneName in boneMap:
        vgrp = mesh.vertex_groups.get(boneName)
        if vgrp is None:
            vgrp = mesh.vertex_groups.new(name=boneName)
        for boneWeight in boneMap[boneName]:
            vgrp.add(boneMap[boneName][boneWeight], boneWeight, 'REPLACE')


def importMesh(meshData, modelSettings, armature, blendBoneNames):
    mesh = bpy.data.meshes.new(meshData.name)
    obj = bpy.data.objects.new(mesh.name, mesh)
    mesh.from_pydata(meshData.vertices, [], meshData.indices)
    mesh.polygons.foreach_set('use_smooth', [True] * len(mesh.polygons))

    if armature:
        mod = obj.modifiers.new(type='ARMATURE', name='OWM Skeleton')
        mod.use_vertex_groups = True
        mod.object = armature

        makeVertexGroups(obj, meshData, blendBoneNames)

        # TODO wots this
        current_theme = bpy.context.preferences.themes.items()[0][0]
        theme = bpy.context.preferences.themes[current_theme]

        bgrp = armature.pose.bone_groups.new(name=obj.name)
        bgrp.color_set = 'CUSTOM'
        bgrp.colors.normal = (randomColor())
        bgrp.colors.select = theme.view_3d.bone_pose
        bgrp.colors.active = theme.view_3d.bone_pose_active

        vgrps = obj.vertex_groups.keys()
        pbones = armature.pose.bones
        for bname in vgrps:
            pbones[bname].bone_group = bgrp

    for i in range(meshData.uvCount):
        layer = mesh.uv_layers.new(name='UVMap%d' % (i + 1))
        uv = meshData.uvs[i]
        layer.data.foreach_set("uv", list(itertools.chain.from_iterable(uv)))

    if modelSettings.importColor and len(meshData.color1) > 0:
        layer = mesh.color_attributes.new("ColorMap1", 'BYTE_COLOR', 'POINT')
        layer.data.foreach_set("color", meshData.color1)
        layer = mesh.color_attributes.new("ColorMap2", 'BYTE_COLOR', 'POINT')
        layer.data.foreach_set("color", meshData.color2)

    mesh.update()

    mesh.use_auto_smooth = True  # TODO determine if this should be optional
    if modelSettings.importNormals:
        mesh.create_normals_split()
        mesh.validate(clean_customdata=False)
        mesh.update(calc_edges=True)
        mesh.normals_split_custom_set_from_vertices(meshData.normals)
    else:
        mesh.validate()

    return obj


def readMDL(filename, modelSettings):
    data = OWModelReader.read(filename)
    if not data: return None

    armature = blendBoneNames = None
    if modelSettings.importSkeleton and data.header.boneCount > 0:
        armature, blendBoneNames = importArmature(data)
        armature.name = PathUtil.nameFromPath(filename) + '_Skeleton'
        # armature.parent = rootObject
        armature.show_in_front = True
        armature['owm.skeleton.name'] = armature.name
        armature['owm.skeleton.model'] = data.GUID
        
    meshes = [importMesh(meshData, modelSettings, armature, blendBoneNames) for meshData in data.meshes]

    empties = (None, [])
    if modelSettings.importEmpties:
        empties = importEmpties(data, armature, blendBoneNames)

    return ModelData(armature, meshes, empties, data)

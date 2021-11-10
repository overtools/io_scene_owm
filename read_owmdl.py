import struct

from . import bin_ops
from . import owm_types
from . import bpyhelper
import io

def openStream(filename):
    stream = None
    with open(filename, 'rb') as f:
        stream = io.BytesIO(f.read())
    return stream

def read(filename):
    stream = openStream(bpyhelper.normpath(filename))
    if stream == None:
        return Falseowm_types.OWMDLIndex.exFormat[0]

    major, minor, materialstr, namestr, boneCount, meshCount, emptyCount = bin_ops.readFmtFlat(stream, owm_types.OWMDLHeader.structFormat)

    header = owm_types.OWMDLHeader(major, minor, materialstr, namestr, boneCount, meshCount, emptyCount)

    bones = []
    if boneCount > 0:
        for i in range(boneCount):
            name, parent, pos, scale, rot = bin_ops.readFmt(stream, owm_types.OWMDLBone.structFormat)
            bones += [owm_types.OWMDLBone(name, parent[0], pos, scale, rot)]
    meshes = []
    for i in range(meshCount):
        name, materialKey, uvCount, vertexCount, indexCount = bin_ops.readFmtFlat(stream, owm_types.OWMDLMesh.structFormat)

        vertex_format = [*owm_types.OWMDLVertex.structFormat]
        vertex_format = "".join(vertex_format)
        for k in range(uvCount):
            vertex_format += owm_types.OWMDLVertex.exFormat[0]
        vertex_size = bin_ops.getSize(vertex_format)
        stream.seek(vertex_size,1)
        boneDataCount = bin_ops.read(stream, owm_types.OWMDLVertex.exFormat[1])[0]
        stream.seek(-(vertex_size+bin_ops.getSize(owm_types.OWMDLVertex.exFormat[1])),1)
        vertex_format += owm_types.OWMDLVertex.exFormat[1]
        if boneDataCount > 0:
            for k in range(boneDataCount):
                vertex_format+=owm_types.OWMDLVertex.exFormat[2]
            for k in range(boneDataCount):
                vertex_format+=owm_types.OWMDLVertex.exFormat[3]
        if major >= 1 and minor >= 6:
            vertex_format += owm_types.OWMDLVertex.exFormat[4]
            vertex_format += owm_types.OWMDLVertex.exFormat[4]
        vertex_size=bin_ops.getSize(vertex_format)
        verts = []
        uv_pointer = 6+(2*uvCount)+1
        bonesI_pointer = uv_pointer+boneDataCount
        bonesW_pointer = bonesI_pointer+boneDataCount
        col1_pointer = bonesW_pointer+4
        col2_pointer = col1_pointer+4
        for vert in struct.iter_unpack("<"+vertex_format.replace("<",""),stream.read(vertex_size*vertexCount)):
            position = vert[:3]
            normal = vert[3:6]

            uvs = []#vert[6:uv_pointer]
            if uvCount > 0:
                pointer = 6
                for k in range(uvCount):
                    uvs+=[vert[pointer:pointer+2]]
                    pointer+=2

            boneIndices = vert[uv_pointer:bonesI_pointer]
            boneWeights = vert[bonesI_pointer:bonesW_pointer]

            col1 = vert[bonesW_pointer:col1_pointer]
            col2 = vert[col1_pointer:col2_pointer]

            verts += [owm_types.OWMDLVertex(position, normal, uvs, boneDataCount, boneIndices, boneWeights, col1, col2)]
        faces = []
        face_format = [*owm_types.OWMDLIndex.structFormat]
        face_format = "".join(face_format)
        face_format+= owm_types.OWMDLIndex.exFormat[0]*3
        face_size = bin_ops.getSize(face_format)

        for face in struct.iter_unpack("<" + face_format.replace("<", ""), stream.read(face_size * indexCount)):
            faces+=[owm_types.OWMDLIndex(3, face[1:])]

        meshes += [owm_types.OWMDLMesh(name, materialKey, uvCount, vertexCount, indexCount, verts, faces)]

    empties = []
    if emptyCount > 0: #whatevs
        for i in range(emptyCount):
            name, position, rotation = bin_ops.readFmt(stream, owm_types.OWMDLEmpty.structFormat)
            empties += [owm_types.OWMDLEmpty(name, position, rotation)]
        if major >= 1 and minor >= 1:
            for i in range(emptyCount): empties[i].hardpoint = bin_ops.readFmt(stream, owm_types.OWMDLEmpty.exFormat)

    cloths = []
    refpose_bones = []
    guid = 0

    try:
        if minor >= 3 and major >= 1:
            count = bin_ops.readFmt(stream, owm_types.OWMDLCloth.beforeFmt)[0]
            for i in range(count):
                name, meshCount = bin_ops.readFmtFlat(stream, owm_types.OWMDLCloth.structFormat)
                clothMeshes = []
                for j in range(meshCount):
                    id, vertCount, subname = bin_ops.readFmtFlat(stream, owm_types.OWMDLClothMesh.structFormat)
                    pinnedVerts = []

                    for k in range(vertCount):
                        pinnedVerts.append(bin_ops.readFmtFlat(stream, owm_types.OWMDLClothMesh.pinnedVertFmt))

                    clothMeshes.append(owm_types.OWMDLClothMesh(subname, id, pinnedVerts))

                cloths.append(owm_types.OWMDLCloth(name, clothMeshes))

        if boneCount > 0 and minor >= 4 and major >= 1:
            for i in range(boneCount):
                name, parent, pos, scale, rot = bin_ops.readFmt(stream, owm_types.OWMDLRefposeBone.structFormat)
                refpose_bones += [owm_types.OWMDLRefposeBone(name, parent[0], pos, scale, rot)]

        if minor >= 5 and major >= 1:
            guid = bin_ops.readFmtFlat(stream, owm_types.OWMDLHeader.guidFormat)
    except: pass

    return owm_types.OWMDLFile(header, bones, refpose_bones, meshes, empties, cloths, guid)

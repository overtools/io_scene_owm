from . import bin_ops
from . import owm_types
import io

def openStream(filename):
    stream = None
    with open(filename, "rb") as f:
        stream = io.BytesIO(f.read())
    return stream

def read(filename):
    stream = openStream(filename)
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
        verts = []
        for j in range(vertexCount):
            position, normal = bin_ops.readFmt(stream, owm_types.OWMDLVertex.structFormat)
            uvs = []
            if uvCount > 0:
                for k in range(uvCount):
                    uvs += [bin_ops.read(stream, owm_types.OWMDLVertex.exFormat[0])]
            boneDataCount = bin_ops.read(stream, owm_types.OWMDLVertex.exFormat[1])[0]
            boneIndices = []
            boneWeights = []
            if boneDataCount > 0:
                for k in range(boneDataCount):
                    boneIndices += [bin_ops.readFmtFlat(stream, owm_types.OWMDLVertex.exFormat[2])]
                for k in range(boneDataCount):
                    boneWeights += [bin_ops.readFmtFlat(stream, owm_types.OWMDLVertex.exFormat[3])]
            verts += [owm_types.OWMDLVertex(position, normal, uvs, boneDataCount, boneIndices, boneWeights)]
        faces = []
        for j in range(indexCount):
            pointCount = bin_ops.readFmt(stream, owm_types.OWMDLIndex.structFormat)[0]
            points = []
            for k in range(pointCount):
                points += [bin_ops.readFmtFlat(stream, owm_types.OWMDLIndex.exFormat[0])]
            faces += [owm_types.OWMDLIndex(pointCount, points)]
        meshes += [owm_types.OWMDLMesh(name, materialKey, uvCount, vertexCount, indexCount, verts, faces)]

    empties = []
    if emptyCount > 0:
        for i in range(emptyCount):
            name, position, rotation = bin_ops.readFmt(stream, owm_types.OWMDLEmpty.structFormat)
            empties += [owm_types.OWMDLEmpty(name, position, rotation)]
        if major >= 1 and minor >= 1:
            for i in range(emptyCount): empties[i].hardpoint = bin_ops.readFmt(stream, owm_types.OWMDLEmpty.exFormat)

    cloths = []
    if minor >= 3 and minor >= 1:
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

    refpose_bones = []
    if boneCount > 0 and minor >= 4 and minor >= 1:
        for i in range(boneCount):
            name, parent, pos, scale, rot = bin_ops.readFmt(stream, owm_types.OWMDLRefposeBone.structFormat)
            refpose_bones += [owm_types.OWMDLRefposeBone(name, parent[0], pos, scale, rot)]

    return owm_types.OWMDLFile(header, bones, refpose_bones, meshes, empties, cloths)

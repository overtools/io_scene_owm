import struct
from mathutils import Vector

from . import BinaryUtil
from . import PathUtil
from ..datatypes import ModelTypes
from ..ui import UIUtil

class OWMDLFormat():
    header = ('<HH', str, str, '<IHII')
    boneRef = (str, '<h', '<fff', '<fff', '<fff')
    boneWeight = 'f'
    boneIndex = 'h'
    mesh = (str, '<QBIIb')
    meshVertex = '<fff'
    meshNormal = '<fff'
    meshTangent = '<ffff'
    meshUV = '<ff'
    meshColor = '<ffff'
    meshIndex = '<III'
    empty = (str, str, '<fff', '<ffff')
    

def read(filename):
    stream = BinaryUtil.openStream(filename)
    if stream == None:
        return None # what

    try:
        major, minor, materialstr, namestr, guid, boneCount, meshCount, emptyCount = BinaryUtil.readFmtFlat(stream, OWMDLFormat.header)
    except:
        UIUtil.fileFormatError("owmdl")
        return None

    if major < 2:
        UIUtil.legacyFileError()
        return False
        
    if materialstr:
        materialstr = PathUtil.makePathAbsolute(PathUtil.pathRoot(filename), materialstr)
    header = ModelTypes.OWMDLHeader(major, minor, materialstr, namestr, boneCount, meshCount, emptyCount)

    refPoseBones = []

    if boneCount > 0:
        for i in range(boneCount):
            name, parent, pos, scale, rot = BinaryUtil.readFmt(stream, OWMDLFormat.boneRef)
            refPoseBones += [ModelTypes.OWMDLRefposeBone(name, parent[0], pos, scale, rot)]

    meshes = []
    for i in range(meshCount):
        name, materialKey, uvCount, vertexCount, indexCount, boneDataCount = BinaryUtil.readFmtFlat(stream, OWMDLFormat.mesh)

        verts = BinaryUtil.readFmtArray(stream, OWMDLFormat.meshVertex, vertexCount)

        rawNormals = BinaryUtil.readFmtArray(stream, OWMDLFormat.meshNormal, vertexCount)

        tangents = BinaryUtil.readFmtArray(stream, OWMDLFormat.meshTangent, vertexCount)

        uvs = []
        for i in range(uvCount):
            uvs.append(BinaryUtil.readFmtArray(stream, OWMDLFormat.meshUV, vertexCount))

        if boneDataCount > 0:
            boneIndices = BinaryUtil.readFmtArray(stream, OWMDLFormat.boneIndex*boneDataCount, vertexCount)
            boneWeights = BinaryUtil.readFmtArray(stream, OWMDLFormat.boneWeight*boneDataCount, vertexCount)
        else:
            boneIndices = boneWeights = []

        color1 = BinaryUtil.readFmtArray(stream, OWMDLFormat.meshColor, vertexCount)

        color2 = BinaryUtil.readFmtArray(stream, OWMDLFormat.meshColor, vertexCount)

        faces = BinaryUtil.readFmtArray(stream, OWMDLFormat.meshIndex, indexCount)

        #TODO move this processing elsewhere
        meshcolor1 = []
        meshcolor2 = []
        meshuvs = [list() for l in range(uvCount)]

        normals = []

        for i in range(vertexCount):
            normals.append(Vector(rawNormals[i]).normalized())
            col1=color1[i]
            meshcolor1+=[col1[3],col1[0],col1[1],col1[2]]
            col2=color2[i]
            meshcolor2+=[col2[3],col2[0],col2[1],col2[2]]

        for face in faces:
            for vert in face:
                for k in range(uvCount):
                    meshuvs[k] += [uvs[k][vert]]

        meshes += [ModelTypes.OWMDLMesh(name, materialKey, uvCount, vertexCount, indexCount, meshuvs, normals, meshcolor1,
                                   meshcolor2, boneIndices, boneWeights, verts, faces)]

    empties = []
    if emptyCount > 0:  # whatevs
        for i in range(emptyCount):
            name, hardpoint, position, rotation = BinaryUtil.readFmt(stream, OWMDLFormat.empty)
            empties += [ModelTypes.OWMDLEmpty(name, position, rotation, hardpoint)]

    return ModelTypes.OWMDLFile(header, refPoseBones, meshes, empties, guid, filename)

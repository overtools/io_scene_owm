from . import BinaryUtil
from ..datatypes import ModelTypes

class OWMDLFormat():
    extension = "owmdl"
    major,minor = (2,0)
    minimum = (2,0)
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
    stream = BinaryUtil.openStream(filename, OWMDLFormat.extension)
    if stream == None:
        return None 

    header = stream.readClass(OWMDLFormat.header, ModelTypes.OWMDLHeader, absPath=True, flat=True)

    if not BinaryUtil.compatibilityCheck(OWMDLFormat, header.major, header.minor):
        return False

    data = ModelTypes.OWMDLFile(header, filename)

    if header.boneCount:
        data.refPoseBones = stream.readClassArray(OWMDLFormat.boneRef, ModelTypes.OWMDLBone, header.boneCount, flat=False)

    for i in range(header.meshCount):
        mesh = stream.readClass(OWMDLFormat.mesh, ModelTypes.OWMDLMesh)

        mesh.vertices = stream.readFmtArray(OWMDLFormat.meshVertex, mesh.vertexCount)

        mesh.rawNormals = stream.readFmtArray(OWMDLFormat.meshNormal, mesh.vertexCount)

        mesh.tangents = stream.readFmtArray(OWMDLFormat.meshTangent, mesh.vertexCount)

        for i in range(mesh.uvCount):
            mesh.rawUVs.append(stream.readFmtArray(OWMDLFormat.meshUV, mesh.vertexCount))

        if mesh.boneDataCount > 0:
            mesh.boneIndices = stream.readFmtArray(OWMDLFormat.boneIndex*mesh.boneDataCount, mesh.vertexCount)
            mesh.boneWeights = stream.readFmtArray(OWMDLFormat.boneWeight*mesh.boneDataCount, mesh.vertexCount)

        mesh.rawColor1 = stream.readFmtArray(OWMDLFormat.meshColor, mesh.vertexCount)

        mesh.rawColor2 = stream.readFmtArray(OWMDLFormat.meshColor, mesh.vertexCount)

        mesh.indices = stream.readFmtArray(OWMDLFormat.meshIndex, mesh.indexCount)

        mesh.blendProcess()

        data.meshes.append(mesh)

    data.empties = stream.readClassArray(OWMDLFormat.empty, ModelTypes.OWMDLEmpty, header.emptyCount, flat=False)

    return data

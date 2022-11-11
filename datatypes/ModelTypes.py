from .CommonTypes import OWMFile
from mathutils import Vector

class ModelData:
    def __init__(self, armature, meshes, empties, meshData):
        self.armature = armature
        self.meshes = meshes
        self.empties = empties
        self.meshData = meshData

    def __str__(self):
        return "ModelData: {} meshes".format(len(self.meshes))


class OWMDLFile(OWMFile):
    def __init__(self, header, filepath):
        super().__init__(filepath)
        self.header = header
        self.refPoseBones = []
        self.meshes = []
        self.empties = []


class OWMDLHeader:
    def __init__(self, major, minor, material, name, guid, boneCount, meshCount, emptyCount):
        self.major = major
        self.minor = minor
        self.guid = guid
        self.material = OWMFile(material)
        self.name = name
        self.boneCount = boneCount
        self.meshCount = meshCount
        self.emptyCount = emptyCount

class OWMDLBone:
    def __init__(self, name, parent, pos, scale, rot):
        self.name = name
        self.parent = parent[0]
        self.pos = pos
        self.scale = scale
        self.rot = rot


class OWMDLMesh:
    def __init__(self, name, materialKey, uvCount, vertexCount, indexCount, boneDataCount):
        self.name = name
        self.materialKey = materialKey
        self.uvCount = uvCount
        self.vertexCount = vertexCount
        self.indexCount = indexCount
        self.boneDataCount = boneDataCount
        # raw
        self.vertices = []
        self.rawUVs = []
        self.rawNormals = []
        self.rawColor1 = []
        self.rawColor2 = []
        self.tangents = [] # unused ¯\_(ツ)_/¯
        # processed for blender
        self.normals = []
        self.color1 = []
        self.color2 = []
        self.uvs = [list() for l in range(uvCount)]
        self.boneIndices = []
        self.boneWeights = []
        self.indices = []

    def blendProcess(self):
        for i in range(self.vertexCount):
            self.normals.append(Vector(self.rawNormals[i]).normalized())
            col1=self.rawColor1[i]
            self.color1+=[col1[3],col1[0],col1[1],col1[2]]
            col2=self.rawColor2[i]
            self.color2+=[col2[3],col2[0],col2[1],col2[2]]

        for face in self.indices:
            for vert in face:
                for k in range(self.uvCount):
                    self.uvs[k].append(self.rawUVs[k][vert])

class OWMDLEmpty:
    def __init__(self, name, hardpoint, position, rotation):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.hardpoint = hardpoint
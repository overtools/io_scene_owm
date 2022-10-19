from ..readers import PathUtil


class ModelData:
    def __init__(self, armature, meshes, empties, meshData):
        self.armature = armature
        self.meshes = meshes
        self.empties = empties
        self.meshData = meshData

    def __str__(self):
        return "ModelData: {} meshes".format(len(self.meshes))


class OWMDLFile:
    def __init__(self, header, refPoseBones, meshes, empties, guid, filepath):
        self.header = header
        self.refPoseBones = refPoseBones
        self.meshes = meshes
        self.empties = empties
        self.GUID = guid
        self.filepath = filepath


class OWMDLHeader:
    def __init__(self, major, minor, material, name, boneCount, meshCount, emptyCount):
        self.major = major
        self.minor = minor
        self.material = PathUtil.normPath(material) if material else None
        self.name = name
        self.boneCount = boneCount
        self.meshCount = meshCount
        self.emptyCount = emptyCount


class OWMDLRefposeBone:
    def __init__(self, name, parent, pos, scale, rot):
        self.name = name
        self.parent = parent
        self.pos = pos
        self.scale = scale
        self.rot = rot


class OWMDLBone:
    def __init__(self, name, parent, pos, scale, rot):
        self.name = name
        self.parent = parent
        self.pos = pos
        self.scale = scale
        self.rot = rot


class OWMDLMesh:
    def __init__(self, name, materialKey, uvCount, vertexCount, indexCount, uvs, normals, color1, color2, boneIndices,
                 boneWeights, vertices, indices):
        self.name = name
        self.materialKey = materialKey
        self.uvCount = uvCount
        self.vertexCount = vertexCount
        self.indexCount = indexCount
        self.vertices = vertices
        self.uvs = uvs
        self.normals = normals
        self.color1 = color1
        self.color2 = color2
        self.boneIndices = boneIndices
        self.boneWeights = boneWeights
        self.indices = indices


class OWMDLIndex:
    def __init__(self, pointCount, points):
        self.pointCount = pointCount
        self.points = points


class OWMDLEmpty:
    def __init__(self, name, position, rotation, hardpoint=''):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.hardpoint = hardpoint
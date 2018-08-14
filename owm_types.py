import copy
from . import bin_ops
from enum import Enum
import os

OWMATTypes = {
    "ALBEDO": 0x00,
    "NORMAL": 0x01,
    "SHADER": 0x02
}

TextureTypes = {
    "Unknown": 0,
    "DiffuseAO": 2903569922,  # Alpha channel is AO
    "DiffuseOpacity": 1239794147,
    "DiffuseBlack": 3989656707,  # Alpha is black ???
    "DiffusePlant": 3093211343,
    "DiffuseFlag": 1281400944,
    "Diffuse2": 1716930793,
    "Normal": 378934698,
    "HairNormal": 562391268, # why?
    "CorneaNormal": 562391268, # maybe not
    "Tertiary": 548341454,  # Metal (R) + Highlight (G) + Detail (B)
    "Tertiary2": 3852121246,  # used for Mei's ice wall
    "Opacity": 1482859648,
    "Opacity2": 1140682086,
    "MaterialMask": 1557393490, # ?
    "SubsurfaceScattering": 3004687613,
    "Emission": 3166598269,
    "Emission2": 1523270506,
    "Emission3": 4243598436, # used for Mei's ice wall
    "HairAnisotropy": 2337956496,
    "Specular": 1117188170, # maybe hairspec
    "AO": 3761386704  # maybe hairao
}

class OWSettings:
    def __init__(self, filename, uvDisplaceX, uvDisplaceY, autoIk, importNormals, importEmpties, importMaterial,
                 importSkeleton, importTexNormal, importTexEffect, importColor):
        self.filename = filename
        self.uvDisplaceX = uvDisplaceX
        self.uvDisplaceY = uvDisplaceY
        self.autoIk = autoIk
        self.importNormals = importNormals
        self.importEmpties = importEmpties
        self.importMaterial = importMaterial
        self.importSkeleton = importSkeleton
        self.importTexNormal = importTexNormal
        self.importTexEffect = importTexEffect
        self.importColor = importColor

    def mutate(self, filename):
        return OWSettings(filename, self.uvDisplaceX, self.uvDisplaceY, self.autoIk, self.importNormals,
                          self.importEmpties, self.importMaterial, self.importSkeleton, self.importTexNormal,
                          self.importTexEffect)

class OWLightSettings:
    def __init__(self, enabled = False, multipleImportance = False, enabledTypes = [False, False, False], adjustValues = [1.0, 1.0], useStrength = False):
        self.enabled = enabled
        self.multipleImportance = multipleImportance
        self.enabledTypes = enabledTypes
        self.adjuistValues = {
            "VALUE": adjustValues[0],
            "STRENGTH": adjustValues[1]
        }
        self.useStrength = useStrength

class OWEffectSettings:
    def __init__(self, settings, filename, force_fps, target_fps, import_DMCE, import_CECE, import_NECE,
                 import_SVCE, svce_line_seed, svce_sound_seed, create_camera, cleanup_hardpoints):
        self.settings = settings
        self.filename = filename
        self.force_fps = force_fps
        self.target_fps = target_fps
        self.import_DMCE = import_DMCE
        self.import_CECE = import_CECE
        self.import_NECE = import_NECE
        self.import_SVCE = import_SVCE
        self.svce_line_seed = svce_line_seed
        self.svce_sound_seed = svce_sound_seed
        self.create_camera = create_camera
        self.cleanup_hardpoints = cleanup_hardpoints

    def mutate(self, path):
        new = copy.deepcopy(self)
        new.filename = path
        return new

class OWMDLFile:
    def __init__(self, header, bones, refpose_bones, meshes, empties, cloths, guid):
        self.header = header
        self.bones = bones
        self.refpose_bones = refpose_bones
        self.meshes = meshes
        self.empties = empties
        self.cloths = cloths
        self.guid = guid


class OWMATFile:
    def __init__(self, header, materials):
        self.header = header
        self.materials = materials


class OWEntityFile:
    def __init__(self, header, file, model, effect, idx, model_idx, effect_idx, children):
        self.header = header
        self.file = file
        self.model = model
        self.effect = effect
        self.index = idx
        self.model_index = model_idx
        self.effect_index = effect_idx
        self.children = children


class OWMAPFile:
    def __init__(self, header, objects, details, lights=list()):
        self.header = header
        self.objects = objects
        self.details = details
        self.lights = lights

class OWAnimFile:
    def __init__(self, header, filename, data, path, model_path):
        self.header = header
        self.filename = filename
        self.data = data
        self.anim_path = path
        self.model_path = model_path

class OWEffectHeader:
    magic_format = [str,]


class CECEAction(Enum):
    UnknownTODO = 0
    Show = 1
    PlayAnimation = 4

    
class OWEffectData:
    time_format = ['<?ff', str]
    header_format = ['<HHIfiiiiiii']

    def __init__(self, guid, length, dmces, ceces, neces, rpces, svces):
        self.guid = guid
        self.length = length
        self.dmces = dmces
        self.ceces = ceces
        self.neces = neces
        self.rpces = rpces
        self.svces = svces
        self.filename = None

    class EffectTimeInfo:
        def __init__(self, use_time, start, end, hardpoint):
            self.use_time = use_time
            self.start = start
            self.end = end
            self.hardpoint = hardpoint
        
        def __repr__(self):
            return '<EffectTimeInfo>: Start:{} End:{} Hardpoint:{}'.format(self.start, self.end, self.hardpoint)
        
        @classmethod
        def read(cls, stream):
            do_time, start, end, hardpoint = bin_ops.readFmtFlat(stream, OWEffectData.time_format)
            return cls(do_time, start, end, hardpoint)

    class DMCEInfo:
        format = ['<QQQ', str, str]

        def __init__(self, time, animation, material, model, model_path, anim_path):
            self.time = time
            self.animation = animation
            self.material = material
            self.model = model
            self.model_path = model_path
            self.anim_path = anim_path

        def __repr__(self):
            return '<DMCEInfo>: {} {} ({})'.format(os.path.basename(self.model_path), os.path.basename(self.anim_path), self.time.hardpoint)

        @classmethod
        def read(cls, stream):
            time = OWEffectData.EffectTimeInfo.read(stream)
            animation, material, model, anim_path, model_path = bin_ops.readFmtFlat(stream, OWEffectData.DMCEInfo.format)
            return cls(time, animation, material, model, anim_path, model_path)

    class CECEInfo:
        format = ['<bQQI', str]

        def __init__(self, time, action, animation, var, var_index, path):
            self.time = time
            self.action = action
            self.animation = animation
            self.var = var
            self.var_index = var_index
            self.path = path

        def __repr__(self):
            return '<CECEInfo>: {} {} ({})'.format(self.action, self.var, self.time.hardpoint)

        @classmethod
        def read(cls, stream):
            time = OWEffectData.EffectTimeInfo.read(stream)
            action, animation, var, var_index, path = bin_ops.readFmtFlat(stream, OWEffectData.CECEInfo.format)
            action = CECEAction(action)
            return cls(time, action, animation, var, var_index, path)

    class NECEInfo:
        format = ['<QI', str]

        def __init__(self, time, guid, variable, path):
            self.time = time
            self.guid = guid
            self.variable = variable
            self.path = path

        def __repr__(self):
            return '<NECEInfo>: {} ({})'.format(self.path, self.time.hardpoint)

        @classmethod
        def read(cls, stream):
            time = OWEffectData.EffectTimeInfo.read(stream)
            guid, var, path = bin_ops.readFmtFlat(stream, OWEffectData.NECEInfo.format)
            return cls(time, guid, var, path)

    class RPCEInfo:
        format = ['<QQ', str]

        def __init__(self, time, model, model_path, material):
            self.time = time
            self.model = model
            self.model_path = model_path
            self.material = material

        def __repr__(self):
            return '<RPCEInfo>: {} ({})'.format(self.model_path, self.time.hardpoint)

        @classmethod
        def read(cls, stream):
            time = OWEffectData.EffectTimeInfo.read(stream)
            model, material, model_path  = bin_ops.readFmtFlat(stream, OWEffectData.RPCEInfo.format)
            return cls(time, model, model_path, material)

    class SVCEInfo:
        format = ['<Ii',]
        line_format = ['i',]
        line_sound_format = [str,]

        class SVCELine:
            def __init__(self, sounds):
                self.sounds = sounds

        def __init__(self, time, guid, lines):
            self.time = time
            self.guid = guid
            self.lines = lines

        def __repr__(self):
            return '<SVCEInfo>: {} ({})'.format(self.guid, self.time.hardpoint)

        @classmethod
        def read(cls, stream):
            time = OWEffectData.EffectTimeInfo.read(stream)
            guid, line_count  = bin_ops.readFmtFlat(stream, OWEffectData.SVCEInfo.format)
            lines = []
            for i in range(line_count):
                sound_count = bin_ops.readFmtFlat(stream, OWEffectData.SVCEInfo.line_format)

                sounds = []
                for j in range(sound_count):
                    sounds.append(bin_ops.readFmtFlat(stream, OWEffectData.SVCEInfo.line_sound_format))
                
                lines.append(OWEffectData.SVCEInfo.SVCELine(sounds))
            return cls(time, guid, lines)

    @classmethod
    def read(cls, stream):
        major, minor, guid, length, dmce_count, cece_count, nece_count, rpce_count, fece_count, osce_count, svce_count = bin_ops.readFmtFlat(stream, OWEffectData.header_format)

        dmces = []
        for i in range(dmce_count):
            dmces.append(OWEffectData.DMCEInfo.read(stream))

        ceces = []
        for i in range(cece_count):
            ceces.append(OWEffectData.CECEInfo.read(stream))

        neces = []
        for i in range(nece_count):
            neces.append(OWEffectData.NECEInfo.read(stream))

        rpces = []
        for i in range(rpce_count):
            rpces.append(OWEffectData.RPCEInfo.read(stream))

        svces = []
        for i in range(svce_count):
            svces.append(OWEffectData.SVCEInfo.read(stream))

        # print("[import_effect]: dmces={}".format(dmces))
        # print("[import_effect]: ceces={}".format(ceces))
        # print("[import_effect]: neces={}".format(neces))
        # print("[import_effect]: rpces={}".format(rpces))
        # print("[import_effect]: svces={}".format(svces))
            
        return cls(guid, length, dmces, ceces, neces, rpces, svces)


class OWAnimType(Enum):
    Unknown = -1
    Data = 0
    Reference = 1
    Reset = 2


class OWAnimHeader:
    format = ['<HHIfi']
    reference_format = [str]
    data_format = [str, str] # .. oweffect

    def __init__(self, major, minor, guid, fps, anim_type):
        self.major = major
        self.minor = minor
        self.guid = guid
        self.fps = fps
        self.anim_type = anim_type
    
    @classmethod
    def read(cls, stream):
        major, minor, guid, fps, anim_type = bin_ops.readFmtFlat(stream, OWAnimHeader.format)
        anim_type = OWAnimType(anim_type)
        return cls(major, minor, guid, fps, anim_type)


    @staticmethod
    def read_reference(stream):
        return bin_ops.readFmtFlat(stream, OWAnimHeader.reference_format)

    @staticmethod
    def read_data(stream):
        return bin_ops.readFmtFlat(stream, OWAnimHeader.data_format)


class OWEntityHeader:
    structFormat = [str, '<HH', str, str, str, '<IIIi']

    def __init__(self, magic, major, minor, guid, model_guid, effect_guid, idx, model_idx, effect_idx, child_count):
        self.magic = magic
        self.major = major
        self.minor = minor
        self.guid = guid
        self.model_guid = model_guid
        self.effect_guid = effect_guid
        self.child_count = child_count
        self.index = idx
        self.model_index = model_idx
        self.effect_index = effect_idx

class OWEntityChild:
    structFormat = [str, '<QQII', str]

    def __init__(self, file, hardpoint, var, hp_index, var_index, attachment):
        self.file = file
        self.hardpoint = hardpoint
        self.var = var
        self.attachment = attachment
        self.var_index = var_index
        self.hardpoint_index = hp_index

    def __repr__(self):
        return '<OWEntityChild: {} (attached to:{})>'.format(self.file, self.attachment)


class OWMDLHeader:
    structFormat = ['<HH', str, str, '<HII']
    guidFormat = ['<I']

    def __init__(self, major, minor, material, name, boneCount, meshCount, emptyCount):
        self.major = major
        self.minor = minor
        self.material = material
        self.name = name
        self.boneCount = boneCount
        self.meshCount = meshCount
        self.emptyCount = emptyCount



class OWMatType(Enum):
    Material = 0
    ModelLook = 1


class OWMATHeader:
    structFormat = ['<HHQ']
    new_format = ['<I']
    new_material_header_format = ['<Ii']
    new_id_format = ['<Q']

    def __init__(self, major, minor, materialCount):
        self.major = major
        self.minor = minor
        self.materialCount = materialCount


class OWMATMaterial:
    structFormat = ['<QI']
    exFormat = [str]
    typeFormat = ['<I']
    new_material_format = [str, '<I']
    new_modellook_format = [str]

    def __init__(self, key, textureCount, textures, shader=0):
        self.key = key
        self.textureCount = textureCount
        self.textures = textures
        self.shader = shader


class OWMAPHeader:
    structFormat = ['<HH', str, '<II']
    structFormat11 = ['<I']

    def __init__(self, major, minor, name, objectCount, detailCount, lightCount=0):
        self.major = major
        self.minor = minor
        self.name = name
        self.objectCount = objectCount
        self.detailCount = detailCount
        self.lightCount = lightCount


class OWMDLRefposeBone:
    structFormat = [str, '<h', '<fff', '<fff', '<fff']

    def __init__(self, name, parent, pos, scale, rot):
        self.name = name
        self.parent = parent
        self.pos = pos
        self.scale = scale
        self.rot = rot


class OWMDLBone:
    structFormat = [str, '<h', '<fff', '<fff', '<ffff']

    def __init__(self, name, parent, pos, scale, rot):
        self.name = name
        self.parent = parent
        self.pos = pos
        self.scale = scale
        self.rot = rot


class OWMDLMesh:
    structFormat = [str, '<QBII']

    def __init__(self, name, materialKey, uvCount, vertexCount, indexCount, vertices, indices):
        self.name = name
        self.materialKey = materialKey
        self.uvCount = uvCount
        self.vertexCount = vertexCount
        self.indexCount = indexCount
        self.vertices = vertices
        self.indices = indices


class OWMDLVertex:
    structFormat = ['<fff', '<fff']
    exFormat = ['<ff', 'B', '<H', '<f', '<ffff']

    def __init__(self, position, normal, uvs, boneCount, boneIndices, boneWeights, col1, col2):
        self.position = position
        self.normal = normal
        self.uvs = uvs
        self.boneCount = boneCount
        self.boneIndices = boneIndices
        self.boneWeights = boneWeights
        self.color1 = col1
        self.color2 = col2


class OWMDLIndex:
    structFormat = ['B']
    exFormat = ['<I']

    def __init__(self, pointCount, points):
        self.pointCount = pointCount
        self.points = points


class OWMDLEmpty:
    structFormat = [str, '<fff', '<ffff']
    exFormat = [str]

    def __init__(self, name, position, rotation, hardpoint=""):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.hardpoint = hardpoint


class OWMDLCloth:
    structFormat = [str, '<I']
    beforeFmt = ['<I']

    def __init__(self, name, meshes):
        self.name = name
        self.meshes = meshes


class OWMDLClothMesh:
    structFormat = ['<II', str]
    pinnedVertFmt = ['<I']

    def __init__(self, name, id, pinnedVerts):
        self.name = name
        self.id = id
        self.pinnedVerts = pinnedVerts


class OWMAPObject:
    structFormat = [str, '<I']

    def __init__(self, model, entityCount, entities):
        self.model = model
        self.entityCount = entityCount
        self.entities = entities


class OWMAPEntity:
    structFormat = [str, '<I']

    def __init__(self, material, recordCount, records):
        self.material = material
        self.recordCount = recordCount
        self.records = records


class OWMAPRecord:
    structFormat = ['<fff', '<fff', '<ffff']

    def __init__(self, position, scale, rotation):
        self.position = position
        self.scale = scale
        self.rotation = rotation


class OWMAPDetail:
    structFormat = [str, str]
    exFormat = ['<fff', '<fff', '<ffff']

    def __init__(self, model, material, position, scale, rotation):
        self.model = model
        self.material = material
        self.position = position
        self.scale = scale
        self.rotation = rotation


class OWMAPLight:
    structFormat = ['<fff', '<ffff', '<I', '<f', '<fff']
    exFormat = ['<IIBBBBII', '<fff', '<ffff', '<fff', '<ffff', '<fff', '<ffff', '<ffIHHII']

    def __init__(self, position, rotation, typ, fov, color, strength = 1.0):
        self.position = position
        self.rotation = rotation
        self.type = typ
        self.fov = fov
        self.color = color
        self.strength = strength

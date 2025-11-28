from . import ui

_shader_metadata_initialized = False
_shader_metadata = {}

class Mapping:
    def __init__(self, item):
        self.colorSockets = item[0]
        self.sRGB = False
        for socket in self.colorSockets:
            if socket in _shader_metadata["Color"]:
                self.sRGB = True
        self.alphaSockets = item[1]
        self.readableName = item[2]


class StaticInput:
    def __init__(self, item):
        self.hash = item[0]
        self.format = item[1]
        self.type = item[2]
        _shader_metadata["StaticInputsByType"][self.type].add(self.hash)

        if self.type == "UVLayer":
            self.uvName = item[3]
            self.uvTargets = item[4]
        elif self.type == "Array":
            self.count = item[3]
        else:
            self.field = item[3]
            if self.type == "UVScale":
                _shader_metadata["ScalesByName"][self.field] = self.hash

def init():
    global _shader_metadata_initialized
    if _shader_metadata_initialized:
        return
    _shader_metadata_initialized = True

    ui.UIUtil.log("initializing shader metadata classes")

    # populated by StaticInput.__init__
    _shader_metadata["ScalesByName"] = {}
    _shader_metadata["StaticInputsByType"] = {
        
        "UVLayer":set(),
        "UVScale":set(),
        "ShaderParm":set(),
        "Array":set(),
        "Dummy":set()
    }

    _shader_metadata["Mapping"] = {
        # "Hash": [["Color Nodes"], ["Alpha Nodes"], "Readable Name"]
        # Basic
        3166598269: [['Emission'], [], 'Emission'],
        378934698: [['Normal'], [], 'Normal'],
        548341454: [['PBR'], [], 'PBR'],
        2018946191: [['PBR'], [], 'PBR'],  # (?)
        2903569922: [['Color'], [], 'Albedo'],
        845901908: [['Cloth'], [], 'Cloth Mask'],
        3335614873: [['AO'], [], 'AO'],
        1482859648: [['Alpha'], [], 'Alpha'],  # (?)
        1557393490: [['Cloth Mask'], [], 'Mask'],  # (?) cloth maybe except not?
        # Blends
        3038474910: [['Blend AO'], [], 'Blend AO'],
        571210053: [['Normal B'], [], 'Blend Normal'],
        682378068: [['Color B'], [], 'Blend Albedo 2'],
        1724830523: [['Blend'], [], 'Blend Mask'],
        1897827336: [['Normal2'], [], 'Blend Normal'],
        2637552222: [['Normal B'], [], 'Blend Normal 2'],
        2959599704: [['Color B'], [], 'Blend Albedo'],
        3120512190: [['Color C'], [], 'Blend Overlay'],
        824205512: [['PBR B'], [], 'Blend PBR'],
        # Grass
        # 165438316: [[], [], 'Grass Emission'], not rly
        1435463780: [[], [], 'Grass Noise'],
        763550166: [['PBR'], [], 'Grass PBR'],
        3093211343: [['Color'], [], 'Grass Color + SSS'],
        # Glass
        2955762069: [['Dirt'], ['Dirt Color'], 'Dirt Albedo + Alpha'],
        67369114: [['Color'], ['Alpha'], 'Glass Albedo + Alpha'],
        229655782: [['Normal'], [], 'Glass Normal'],
        1239777102: [['PBR'], [], 'Glass PBR'],
        2838344713: [['Normal Strength'], [], 'Glass Normal Fac'],
        1493127177: [['Emission Color'], [], 'Glass Emission'],
        # Decals
        3989656707: [['Color', 'Alpha', 'Emission'], [], 'Decal Albedo + Alpha + Emission'],
        562391268: [['Normal'], [], 'Normal'],
        3111105361: [['PBR'], [], 'Decal PBR'],
        1716930793: [['Color'], [], 'Decal Albedo'],
        1140682086: [['Alpha'], [], 'Decal Alpha'],
        # Complex Test
        #1281400944: [['Color'], [], 'Flag Albedo'],
        #996643046: [['PBR'], [], 'Flag PBR'],
        #996643046: [['Color'], [], 'Complex Albedo'],
        #996643046: [['Color'], [], 'Complex Albedo'],
        # OW1 Hair
        1117188170: [['Roughness'], [], 'Hair Roughness'],
        1239794147: [['Color'], ['Alpha'], 'Hair Albedo + Alpha'],
        2337956496: [['Tangent'], [], 'Hair Tangent'],
        3761386704: [['AO'], [], 'Hair AO'],
        # OW2 Hair
        4101268840: [['Strand'], ['Strand Blend'], 'Hair Strand Map'],
        758934576: [[], [], 'Hair Strand'],
        # OW1 Skin
        1523270506: [['Emission'], [], 'Skin Emission'],
        3004687613: [['Subsurface Color'], [], 'Subsurface'],
        # OW2 Skin
        3610823797: [['Subsurface Depth'], [], 'Subsurface'],
        # OW2 Detail
        1268722198: [['Detail Black'], ['Detail BlackR'], 'Detail Region Black'],
        1016601216: [['Detail Red'], ['Detail RedR'], 'Detail Region Red'],
        2777762618: [['Detail Green'], ['Detail GreenR'], 'Detail Region Green'],
        1290989071: [['Detail Blue'], ['Detail BlueR'], 'Detail Region Blue'],
        3533077420: [['Detail Yellow'], ['Detail YellowR'], 'Detail Region Yellow'],
        2734460707: [['Detail Cyan'], ['Detail CyanR'], 'Detail Region Cyan'],
        1005969049: [['Detail Pink'], ['Detail PinkR'], 'Detail Region Pink'],
        3590045621: [['Detail White'], ['Detail WhiteR'], 'Detail Region White'],
        250510254: [['Detail Map'], ['Detail Blend'], 'Detail Map'],
        #OW2 Eye
        3411049489: [['Color'], [], 'Eye Albedo + Mask'],
        2762290483: [['Normal'], [], 'Eye Normal'],
        2454590718: [[], [], 'Eye Normal 2'],
        861945942: [[], [], 'Eye Mask'],
    }

    # List of names to import as sRGB
    _shader_metadata["Color"] = ["Color", "Dirt Color", "Subsurface", "Subsurf2", "Color B", "Color C", "Emission Color"]

    # Active texture to display in the viewport
    _shader_metadata["Active"] = ["Color", "Color2", "Color3"]

    _shader_metadata["DetailTextures"] = {
        1268722198: 0,  # not sure if right
        1016601216: 1,
        2777762618: 2,
        3533077420: 3,
        1290989071: 4,
        1005969049: 5,
        2734460707: 6,
        3590045621: 7
    }

    _shader_metadata["StaticInputs"] = {
        3344068240:StaticInput((3344068240, "I", "UVLayer", "Emission", (3166598269,))),  # emission uv
        2241837981:StaticInput((2241837981, "I", "UVLayer", "Blend 2", (682378068,571210053,3120512190))),
        -300:StaticInput((-300, "I", "UVLayer", "Blend 1", (2637552222,1724830523,824205512))),
        -200:StaticInput((-200, "I", "UVLayer", "Basic", (2903569922,548341454,378934698))),
        1701780890:StaticInput((1701780890, "ff", "UVScale", "Blend 2")),  # blend2 uv scale
        3260151041:StaticInput((3260151041, "ff", "UVScale", "Blend 1")),  # blend1 uv scale
        1883253226:StaticInput((1883253226, "ff", "UVScale", "Basic")),
        2166182138:StaticInput((2166182138, "ff", "UVScale", "default")),  # default uv scale
        3561634072:StaticInput((3561634072, "f", "ShaderParm", "Blend Factor")),  # 
        3250491852:StaticInput((3250491852, "f", "ShaderParm", "Emission Strength")),  # emission Strength
        2446772623:StaticInput((2446772623, "f", "ShaderParm", "Emission Strength")),  # idk
        565460110:StaticInput((565460110, "f", "ShaderParm", "Opacity")),  # decal opacity
        3604494376:StaticInput((3604494376, "ffff", "ShaderParm", "Hair Strand Density")),  # hardcoded
        4081294361:StaticInput((4081294361, "ffff", "Array", 8)),
        3249912104:StaticInput((3249912104, "ffff", "Array", 8)),
        2135242209:StaticInput((2135242209, "II", "Dummy", "Scaling Mode")),
        #2241837981:StaticInput((2241837981, "I", "Dummy", "Blend2")),  # blend2 uv
        # 62081fbd overlay normal fac
    }

    _shader_metadata["CollisionMaterials"] = set([
        "0000000034A0",
        "000000002DD4",
        "000000002D77",
        "0000000034A2",
        "000000002D77",
        "000000000796", 
        "000000000005", 
        "000000000794", 
        "0000000048EF", 
        "0000000034A3",
        "000000000797",
        "0000000007A2",
        "0000000007A0",
        "0000000007C0",
        "0000000007A1"
    ])

    _shader_metadata["NodeGroups"] = {
        "Default": "OWM: Basic",
        "34": "OWM: Decal",
        "36": "OWM: Blend",
        "37": "OWM: Map",
        "37_1": "OWM: Blend 1 A",
        "37_2": "OWM: Blend 2 A",
        "37_3": "OWM: Blend 1 B",
        "37_4": "OWM: Blend 2 B",
        "38": "OWM: Glass",
        "43_1": "OWM: OW1 Skin",
        "43_2": "OWM: OW2 Skin",
        "167": "OWM: OW2 Skin",
        "44": "OWM: Cloth",  # not cloth actually sadge
        "50": "OWM: Complex",
        "51_1": "OWM: OW1 Hair",  # 53 tree leaves 39 bushes
        "51_2": "OWM: OW2 Hair", 
        "54": "OWM: Refractive",
        "56": "OWM: Decal",  # 101 water
        "217": "OWM: OW2 Detail",
        "221": "OWM: OW2 Eye",
    }

    for mappingID, mappingData in _shader_metadata["Mapping"].items():
        _shader_metadata["Mapping"][mappingID] = Mapping(mappingData)

def get_shader_metadata(name):
    init()
    return _shader_metadata[name]
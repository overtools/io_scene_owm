TextureTypes = {
    "Mapping": {
        # "Readable Name": [["Color Nodes"], ["Alpha Nodes"], "Shader Input Hash Id", "UV Index", "UV Input Id", "UV Input Data Offset", "UV Input Data Modifier"]
        # if UV Index is negative, it will try to look up UV Input Data Id in Static Inputs
        # and decode a single byte at the specified offset
        # UV Input Data Modifier adds this value to the resulting UV value
        "Map AO": [["AO"], [], 3335614873, -2, 1644699581, 0, 0],
        "Decal AO": [["AO", "Opacity"], [], 3761386704],
        "Albedo + AO": [["Color"], ["AO"], 2903569922],
        "Map Albedo": [["Color2"], [], 682378068, 2],
        "Blend Albedo": [["Color2"], [], 2959599704, 2],
        "Blend Albedo 2": [["Color3"], [], 3120512190, 2],
        "Decal Albedo": [["Color"], [], 1716930793],
        "Decal Albedo + Alpha + Emission": [["Color", "Alpha", "Emission"], [], 3989656707],
        "Hair Albedo + Alpha": [["Color"], ["Alpha"], 1239794147],
        "Dirt Albedo + Alpha": [["Dirt"], ["DirtColor"], 2955762069],
        "Glass Albedo + Alpha": [["Color"], ["Alpha"], 67369114],
        "Subsurface": [["Subsurf"], [], 3004687613],
        "PBR": [["PBR"], [], 548341454],
        "Decal PBR": [["PBR"], [], 3111105361],
        "Glass PBR": [["PBR"], [], 1239777102],
        "Hair Roughness": [["Roughness"], [], 1117188170],
        "Emission": [["Emission"], [], 3166598269],
        "Alpha": [["Alpha"], [], 1482859648],
        "Decal Alpha": [["Alpha"], [], 1140682086],
        "Normal": [["Normal"], [], 378934698],
        "Map Normal": [["Normal2"], [], 571210053, 2],
        "Decal Normal": [["Normal"], [], 562391268],
        "Glass Normal": [["Normal"], [], 229655782],
        "Blend Normal": [["Normal2"], [], 1897827336],
        "Blend Normal 2": [["Normal2"], [], 2637552222],
        "Hair Tangent": [["Tangent"], [], 2337956496],
        "Blend": [["Blend"], [], 1724830523],
        "Material": [[], [], 1557393490],
        "Grass Color + Param": [["Color"], [], 3093211343],
        "Grass Noise": [[], [], 1435463780],
        "Grass PBR": [["PBR"], [], 763550166],
        "Grass Emission": [["Emission"], [], 165438316]
    },
    "Alias": { # List of texture name rewrites, used for convenience
        "Color": "Color",
        "Normal": "Normal",
        "PBR": "Packed PBR",
        "Alpha": "Alpha",
        "Emission": "Emission",
        "Subsurf": "Subsurface Color",
        "Color2": "Color B",
        "Normal2": "Normal B",
        "PBR2": "Packed PBR B",
        "Alpha2": "Alpha B",
        "Emission2": "Emission B",
        "Subsurf2": "Subsurface Color B",
        "Color3": "Color C",
        "Normal3": "Normal C",
        "PBR3": "Packed PBR C",
        "Alpha3": "Alpha C",
        "Emission3": "Emission C",
        "Subsurf3": "Subsurface Color C",
        "Dirt": "Dirt",
        "DirtColor": "Dirt Color"
    },
    "Env": { # Environment Remapping for when nodes are left open
        "Color2": "Color",
        "Normal2": "Normal",
        "PBR2": "PBR",
        "Alpha2": "Alpha",
        "Emission2": "Emission",
        "Subsurf2": "Subsurf",
        "Color": "Color2",
        "Normal": "Normal2",
        "PBR": "PBR2",
        "Alpha": "Alpha2",
        "Emission": "Emission2",
        "Subsurf": "Subsurf2",
        "Color3": "Color2",
        "Normal3": "Normal2",
        "PBR3": "PBR2",
        "Alpha3": "Alpha2",
        "Emission3": "Emission2",
        "Subsurf3": "Subsurf2"
    },
    # List of names to import as sRGB
    "Color": ["Color", "DirtColor", "Color2", "Color3", "Subsurf", "Subsurf2", "Subsurf3", "PBR", "PBR2", "PBR3"],
    # Active texture to display in the viewport
    "Active": ["Color", "Color2"],
    # OWM Shader remaps for shader ids
    "NodeGroups": {
        "Default": "OWM: Metallic",
        "34": "OWM: Decal",
        "36": "OWM: Map",
        "37": "OWM: Blend",
        "38": "OWM: Glass",
        "43": "OWM: Skin",
        "50": "OWM: Complex",
        "51": "OWM: Hair",
        "54": "OWM: Refractive",
        "56": "OWM: Decal"
    },
    # List of static input ids for texture scaling
    "Scale": [],
    # TODO
    "Static": {}
}

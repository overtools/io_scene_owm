import os

from enum import IntEnum
from . import BinaryUtil
from . import PathUtil
from ..datatypes import MaterialTypes
from .. import textureMap
from ..ui import UIUtil

class OWMatType(IntEnum):
    Material = 0
    ModelLook = 1

class OWMATFormat():
    header = '<HHI'
    materialHeader = '<QQI'
    texture = [str, '<I']
    staticInput = '<II'
    modelLookHeader = '<Q'
    modelLookMaterial = ['<Q', str]

def read(filename, sub=False):
    stream = BinaryUtil.openStream(PathUtil.normPath(filename))
    if stream == None:
        return None
    matRootPath = PathUtil.pathRoot(filename)

    try:
        major, minor, matType = BinaryUtil.readFmtFlat(stream, OWMATFormat.header)
    except:
        UIUtil.fileFormatError("owmat")
        return None

    if major < 3:
        UIUtil.legacyFileError()
        return False

    if matType == OWMatType.Material:
        textureCount, staticInputCount, shader = BinaryUtil.readFmtFlat(stream, OWMATFormat.materialHeader)
        matGuid = PathUtil.nameFromPath(filename)

        textures = []
        for i in range(textureCount):
            texture, textureType = BinaryUtil.readFmtFlat(stream, OWMATFormat.texture)
            textures += [MaterialTypes.OWMATMaterialTexture(PathUtil.makePathAbsolute(matRootPath, texture), 0, textureType)]

        staticInputs = {}
        for i in range(staticInputCount):
            inputHash, inputDataLength = BinaryUtil.readFmtFlat(stream, OWMATFormat.staticInput)
        
            if inputHash in textureMap.TextureTypes["StaticInputs"]:
                input = textureMap.TextureTypes["StaticInputs"][inputHash]
                if input.type == "Array":
                    data = BinaryUtil.readFmtArray(stream, input.format, int(inputDataLength/16))
                else:
                    data = BinaryUtil.readFmtFlat(stream, input.format)
                staticInputs[inputHash] = data
            else:
                staticInputs[inputHash] = stream.read(inputDataLength)

        if sub:
            return textures, shader, staticInputs
        else:
            return MaterialTypes.OWMATFile(PathUtil.nameFromPath(filename), [MaterialTypes.OWMATMaterial(None, matGuid, textureCount, textures, shader, staticInputs)])

    elif matType == OWMatType.ModelLook:
        materialCount = BinaryUtil.readFmtFlat(stream, OWMATFormat.modelLookHeader)
        materials = []
        keys = []
        for i in range(materialCount):
            key, materialFile = BinaryUtil.readFmtFlat(stream, OWMATFormat.modelLookMaterial)
            matGuid = PathUtil.nameFromPath(materialFile)  # this totally won't cause issues
            textures, shader, staticInputs = read(os.path.join(filename, PathUtil.normPath(materialFile)), True)

            materials += [MaterialTypes.OWMATMaterial(key, matGuid, len(textures), textures, shader, staticInputs)]
            keys.append(key)

        return MaterialTypes.OWMATFile(PathUtil.nameFromPath(filename), materials, keys)

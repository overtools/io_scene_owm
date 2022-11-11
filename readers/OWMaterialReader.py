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
    extension = "owmat"
    major,minor = (3,0)
    minimum = (3,0)
    header = '<HHI'
    materialHeader = '<QQI'
    texture = (str, '<I')
    staticInput = '<II'
    modelLookHeader = '<Q'
    modelLookMaterial = ('<Q', str)

def readMaterial(filename, stream):
    material = stream.readClass(OWMATFormat.materialHeader, MaterialTypes.OWMATMaterial)
    material.setPath(filename)

    material.textures = stream.readClassArray(OWMATFormat.texture, MaterialTypes.OWMATMaterialTexture, material.textureCount, absPath=True)

    for i in range(material.staticInputCount):
        inputHash, inputDataLength = stream.readFmt(OWMATFormat.staticInput)
    
        if inputHash in textureMap.TextureTypes["StaticInputs"]:
            input = textureMap.TextureTypes["StaticInputs"][inputHash]
            if input.type == "Array":
                data = stream.readFmtArray(input.format, int(inputDataLength/16))
            else:
                data = stream.readFmt(input.format)
            material.staticInputs[inputHash] = data
        else:
            material.staticInputs[inputHash] = stream.read(inputDataLength)
    return material

def readModelLook(filename, stream):
    data = MaterialTypes.OWMATModelLook(filename)
    materialCount = stream.readFmt(OWMATFormat.modelLookHeader)
    for i in range(materialCount):
        key, materialFile = stream.readFmt(OWMATFormat.modelLookMaterial)
        material = read(PathUtil.joinPath(filename, materialFile))
        data.materials.setdefault(key, material)
    return data

def read(filename):
    stream = BinaryUtil.openStream(filename, OWMATFormat.extension)
    if stream == None:
        return None
    
    header = stream.readClass(OWMATFormat.header, MaterialTypes.OWMATHeader, absPath=True)

    if header.major < 3:
        UIUtil.ow1FileError()
        return False
    if not BinaryUtil.compatibilityCheck(OWMATFormat, header.major, header.minor):
        return False

    if header.type == OWMatType.Material:
        return readMaterial(filename, stream)
    elif header.type == OWMatType.ModelLook:
        return readModelLook(filename, stream)

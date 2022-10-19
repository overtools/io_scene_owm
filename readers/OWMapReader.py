from . import BinaryUtil
from . import PathUtil
from ..datatypes import MapTypes
from ..ui import UIUtil

class OWMAPFormat():
    header = ('<HH', str, '<III')
    object = (str, '<I')
    record = ('<fff', '<fff', '<ffff')
    detail = (str, str)
    light = ('<fff', '<ffff', '<I', '<f', '<fff')
    lightExtra = ('<IIBBBBII', '<fff', '<ffff', '<fff', '<ffff', '<fff', '<ffff', '<ffIHHII')
    soundCount = ('<I') #grr
    sound = ('<fff', '<i')
    soundFile = (str,)
    

def read(filename):
    stream = BinaryUtil.openStream(PathUtil.normPath(filename))
    if stream == None:
        return None
    mapRootPath = PathUtil.pathRoot(filename)

    try:
        major, minor, name, objectCount, detailCount, lightCount = BinaryUtil.readFmtFlat(stream, OWMAPFormat.header)
    except:
        UIUtil.fileFormatError("owmap")
        return None

    if major < 2:
        UIUtil.legacyFileError()
        return False
    
    header = MapTypes.OWMAPHeader(major, minor, name, objectCount, detailCount, lightCount)

    objects = []
    for i in range(objectCount):
        model, entityCount = BinaryUtil.readFmtFlat(stream, OWMAPFormat.object)
        model = PathUtil.makePathAbsolute(mapRootPath,model)

        entities = []
        for j in range(entityCount):
            material, recordCount = BinaryUtil.readFmtFlat(stream, OWMAPFormat.object)
            material = PathUtil.makePathAbsolute(mapRootPath,material) if material else None

            records = []
            for k in range(recordCount):
                position, scale, rotation = BinaryUtil.readFmt(stream, OWMAPFormat.record)
                records += [MapTypes.OWMAPRecord(position, scale, rotation)]
            entities += [MapTypes.OWMAPEntity(material, recordCount, records)]
        objects += [MapTypes.OWMAPObject(model, entityCount, entities)]

    details = []
    for i in range(detailCount):
        model, material = BinaryUtil.readFmtFlat(stream, OWMAPFormat.detail)
        model = PathUtil.makePathAbsolute(mapRootPath,model)
        material = PathUtil.makePathAbsolute(mapRootPath,material) if material else None
        
        position, scale, rotation = BinaryUtil.readFmt(stream, OWMAPFormat.record)
        details += [MapTypes.OWMAPDetail(model, material, MapTypes.OWMAPRecord(position, scale, rotation))]

    lights = []
    for i in range(lightCount):
        position, rotation, typ, fov, color = BinaryUtil.readFmt(stream, OWMAPFormat.light)
        ex = BinaryUtil.readFmtFlat(stream, OWMAPFormat.lightExtra)
        lights += [MapTypes.OWMAPLight(position, rotation, typ[0], fov[0], color, ex)]

    sounds = []
    soundCount = BinaryUtil.readFmtFlat(stream, OWMAPFormat.soundCount)
    header.soundCount = soundCount

    for i in range(soundCount):
        position, filecount = BinaryUtil.readFmt(stream, OWMAPFormat.sound)
        files = []
        for j in range(filecount[0]):
            files += [BinaryUtil.readFmtFlat(stream, OWMAPFormat.soundFile)]
        sounds += [MapTypes.OWMAPSound(position, filecount, files)]

    return MapTypes.OWMAPFile(header, objects, details, lights, sounds)

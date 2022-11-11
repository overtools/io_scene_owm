from . import BinaryUtil
from ..datatypes import MapTypes

class OWMAPFormat():
    extension = "owmap"
    major,minor = (2,1)
    minimum = (2,0)
    header = ('<HH', str, '<III')
    object = (str, '<I')
    record = ('<fff', '<fff', '<ffff')
    detail = (str, str)
    light = ('<fff', '<ffff', '<I', '<f', '<fff')
    lightExtra = ('<IIBBBBII', '<fff', '<ffff', '<fff', '<ffff', '<fff', '<ffff', '<ffIHHII')
    lightNew = ('<fff', '<ffff', '<I', '<f', '<fff', '<f', '<QQ') # 2.1
    soundCount = ('<I') #grr
    sound = ('<fff', '<i')
    soundFile = (str,)
    

def read(filename):
    stream = BinaryUtil.openStream(filename, OWMAPFormat.extension)
    if stream == None:
        return None

    header = stream.readClass(OWMAPFormat.header, MapTypes.OWMAPHeader)

    if not BinaryUtil.compatibilityCheck(OWMAPFormat, header.major, header.minor):
        return False
    
    mapData = MapTypes.OWMAPFile(header, filename)

    # Objects
    for i in range(header.objectCount):
        object = stream.readClass(OWMAPFormat.object, MapTypes.OWMAPObject, absPath=True)

        for j in range(object.entityCount):
            entity = stream.readClass(OWMAPFormat.object, MapTypes.OWMAPEntity, absPath=True)
            entity.records = stream.readClassArray(OWMAPFormat.record, MapTypes.OWMAPRecord, entity.recordCount, flat=False)
            object.entities.append(entity)

        mapData.objects.append(object)

    # Details
    mapData.details = stream.readCoupledClassArray(OWMAPFormat.detail, MapTypes.OWMAPDetail, OWMAPFormat.record, MapTypes.OWMAPRecord, False, header.detailCount,coupledFlat=False)
    
    # Lights
    if header.major == 2 and header.minor == 0:
        mapData.lights = False
        for i in range(header.lightCount):
            position = stream.readFmt(OWMAPFormat.light)
            ex = stream.readFmt(OWMAPFormat.lightExtra)
    else:
        mapData.lights = stream.readClassArray(OWMAPFormat.lightNew, MapTypes.OWMAPLight, header.lightCount, flat=False)
            
    # Sounds
    soundCount = stream.readFmt(OWMAPFormat.soundCount)
    header.soundCount = soundCount

    for i in range(soundCount):
        position, filecount = stream.readFmt(OWMAPFormat.sound, flat=False)
        files = []
        for j in range(filecount[0]):
            files.append(stream.readFmt(OWMAPFormat.soundFile))
        mapData.sounds.append(MapTypes.OWMAPSound(position, filecount, files))

    return mapData

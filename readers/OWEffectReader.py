from . import BinaryUtil
from . import PathUtil
from ..datatypes import EffectTypes


def openStream(filename):
    stream = None
    with open(filename, 'rb') as f:
        stream = BinaryUtil.BytesIO(f.read())
    return stream

time_format = ['<?ff', str]
header_format = ['<HHIfiiiiiii']
DMCEformat = ['<QQQ', str, str]
CECEformat = ['<bQQI', str]
NECEformat = ['<QI', str]
RPCEformat = ['<QQ', str]
SVCEformat = ['<Ii', ]
SVCEline_format = ['i', ]
SVCEline_sound_format = [str, ]

def read(filename):
    stream = openStream(PathUtil.normPath(filename))
    if stream == None:
        return None
    major, minor, guid, length, dmce_count, cece_count, nece_count, rpce_count, fece_count, osce_count, svce_count = BinaryUtil.readFmtFlat(
        stream, header_format)

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

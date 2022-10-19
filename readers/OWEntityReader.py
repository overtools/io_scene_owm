from . import BinaryUtil
from . import PathUtil
from ..datatypes import EntityTypes
from ..ui import UIUtil

class OWENTITYFormat():
    headerFormat = (str, '<HH', str, str, str, '<IIIi')
    childFormat = (str, '<QQII', str)
    
def read(filename):
    stream = BinaryUtil.openStream(PathUtil.normPath(filename))
    if stream == None:
        return None

    try:
        magic, major, minor, guid, modelGUID, effectGUID, idx, modelIndex, effectIndex, childCount = BinaryUtil.readFmtFlat(stream, OWENTITYFormat.headerFormat)
    except:
        UIUtil.fileFormatError("owentity")
        return None
        
    
    if major < 2:
        UIUtil.legacyFileError()
        return False

    header = EntityTypes.OWEntityHeader(magic, major, minor, guid, modelGUID, effectGUID, idx, modelIndex, effectIndex,childCount)

    children = []
    for i in range(childCount):
        child_file, child_hardpoint, child_variable, child_hpIndex, child_varIndex, child_attachment = BinaryUtil.readFmtFlat(stream, OWENTITYFormat.childFormat)
        children.append(EntityTypes.OWEntityChild(child_file, child_hardpoint, child_variable, child_hpIndex, child_varIndex,child_attachment))
    return EntityTypes.OWEntityFile(header, guid, modelGUID, effectGUID, idx, modelIndex, effectIndex, children)

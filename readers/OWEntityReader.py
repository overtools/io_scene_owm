from . import BinaryUtil
from ..datatypes import EntityTypes

class OWENTITYFormat():
    extension = "owentity"
    major,minor = (2,1)
    minimum = (2,0)
    headerFormat = (str, '<HH', str, str, str, '<IIIi')
    childFormat = (str, '<QQII', str)
    modelLook = (str, str) # 2.1
    
def read(filename):
    stream = BinaryUtil.openStream(filename, OWENTITYFormat.extension)
    if stream == None:
        return None

    header = stream.readClass(OWENTITYFormat.headerFormat, EntityTypes.OWEntityHeader)
    data = EntityTypes.OWEntityFile(header)
        
    if not BinaryUtil.compatibilityCheck(OWENTITYFormat, header.major, header.minor):
        return False

    data.children = stream.readClassArray(OWENTITYFormat.childFormat, EntityTypes.OWEntityChild, header.childCount, absPath=True)

    # 2.1 
    if header.major >= 2 and header.minor >= 1:
        data.header.modelLook, data.header.relativePath = stream.readFmt(OWENTITYFormat.modelLook)
    
    data.fixPaths(filename)
    
    return data

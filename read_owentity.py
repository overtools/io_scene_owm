from . import bin_ops
from . import owm_types
import io

def openStream(filename):
    stream = None
    with open(filename, "rb") as f:
        stream = io.BytesIO(f.read())
    return stream

def read(filename):
    stream = openStream(filename)
    if stream == None:
        return None

    magic, major, minor, guid, model_guid, child_count = bin_ops.readFmtFlat(stream, owm_types.OWEntityHeader.structFormat)
    header = owm_types.OWEntityHeader(magic, major, minor, guid, model_guid, child_count)

    children = []
    for i in range(child_count):
        child_file, child_hardpoint, child_variable, child_attachment = bin_ops.readFmtFlat(stream, owm_types.OWEntityChild.structFormat)
        children.append(owm_types.OWEntityChild(child_file, child_hardpoint, child_variable, child_attachment))
    print(magic, major, minor, guid, model_guid, child_count, children)
    return owm_types.OWEntityFile(header, guid, model_guid, children)

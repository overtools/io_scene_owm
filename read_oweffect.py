from . import bin_ops
from . import owm_types
import io
import os
from . import bpyhelper

def openStream(filename):
    stream = None
    with open(filename, "rb") as f:
        stream = io.BytesIO(f.read())
    return stream

def get_pooled_dir(this_path, new_path):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(this_path)))), new_path)

def read_stream(filename, stream):
    magic = bin_ops.readFmtFlat(stream, owm_types.OWEffectHeader.magic_format)
    if magic == "owanim":
        header = owm_types.OWAnimHeader.read(stream)
        if header.anim_type == owm_types.OWAnimType.Reference:
            written_path = owm_types.OWAnimHeader.read_reference(stream)
            path = get_pooled_dir(filename, written_path)
            return read(path)
        if header.anim_type == owm_types.OWAnimType.Data:
            path, model_path = owm_types.OWAnimHeader.read_data(stream)
            # embedded oweffect
            data = read_stream(filename, stream)
            return owm_types.OWAnimFile(header, filename, data, path, model_path)
    if magic == "oweffect":
        data = owm_types.OWEffectData.read(stream)
        data.filename = bpyhelper.normpath(filename)
        return data
        
    return None

def read(filename):
    stream = openStream(filename)
    if stream == None:
        return None

    return read_stream(filename, stream)
    

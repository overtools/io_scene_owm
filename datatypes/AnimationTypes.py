from enum import Enum

from ..readers import PathUtil


class OWAnimFile:
    def __init__(self, header, filename, data, path, model_path):
        self.header = header
        self.filename = PathUtil.normPath(filename)
        self.data = data
        self.anim_path = path
        self.model_path = model_path


class OWAnimType(Enum):
    Unknown = -1
    Data = 0
    Reference = 1
    Reset = 2


class OWAnimHeader:
    format = ['<HHIfi']
    reference_format = [str]
    data_format = [str, str]  # .. oweffect

    def __init__(self, major, minor, guid, fps, anim_type):
        self.major = major
        self.minor = minor
        self.guid = guid
        self.fps = fps
        self.anim_type = anim_type

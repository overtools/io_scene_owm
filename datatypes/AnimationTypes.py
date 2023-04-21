from enum import Enum

from ..readers import PathUtil
from .CommonTypes import OWMFile


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

class OWAnimClipFile(OWMFile):
    def __init__(self, header, filepath):
        super().__init__(filepath)
        self.header = header
        self.bones = []

class OWAnimClipHeader:
    def __init__(self, major, minor, boneCount, fps, duration):
        self.major = major
        self.minor = minor
        self.boneCount = boneCount
        self.fps = fps
        self.duration = duration

class OWAnimClipBone:
    def __init__(self, name, trackCount):
        self.name = name
        self.trackCount = trackCount
        self.positions = OWAnimClipTrack(0,0,0)
        self.rotations = OWAnimClipTrack(0,0,0)
        self.scale = OWAnimClipTrack(0,0,0)

class OWAnimClipTrack:
    def __init__(self, trackType, keyframeCount, componentCount):
        self.trackType = trackType
        self.keyframeCount = keyframeCount
        self.componentCount = componentCount
        self.keyframes = []

class OWAnimClipKeyframe:
    def __init__(self, frame):
        self.frame = frame[0]
        self.data = None
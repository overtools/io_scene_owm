from . import BinaryUtil
from enum import IntEnum
from ..datatypes import AnimationTypes

class OWAnimClipTrackType(IntEnum):
    positions = 0
    rotations = 1
    scale = 2

class OWAnimClipFormat():
    extension = "owanimclip"
    major,minor = (2,0)
    minimum = (2,0)
    header = "<HHIfI"
    bone = (str,"<I")
    track = "<III"
    keyframe = ["<I"]
    vec3 = ["<fff"]
    quat = ["<ffff"]

def read(filename):
    stream = BinaryUtil.openStream(filename, OWAnimClipFormat.extension)
    if stream == None:
        return None

    header = stream.readClass(OWAnimClipFormat.header, AnimationTypes.OWAnimClipHeader)

    if not BinaryUtil.compatibilityCheck(OWAnimClipFormat, header.major, header.minor):
        return False
    
    animData = AnimationTypes.OWAnimClipFile(header, filename)

    TrackTypes = OWAnimClipTrackType.__members__
    for i in range(header.boneCount):
        bone = stream.readClass(OWAnimClipFormat.bone, AnimationTypes.OWAnimClipBone)
        for j in range(bone.trackCount):
            track = readTrack(stream)
            if track.trackType in TrackTypes.values():
                bone.__dict__[list(TrackTypes.keys())[track.trackType]] = track
        animData.bones.append(bone)
    return animData

def readTrack(stream):
    track = stream.readClass(OWAnimClipFormat.track, AnimationTypes.OWAnimClipTrack)
    for i in range(track.keyframeCount):
        keyframe = stream.readClass(OWAnimClipFormat.keyframe, AnimationTypes.OWAnimClipKeyframe, flat=False)
        keyframe.data = stream.readFmt("f"*track.componentCount)
        track.keyframes.append(keyframe)
    return track
import os
from enum import Enum

from ..readers import PathUtil


class OWEffectHeader:
    magic_format = [str, ]


class CECEAction(Enum):
    UnknownTODO = 0
    Show = 1
    PlayAnimation = 4


class OWEffectData:  # what the fuck even is this
    def __init__(self, guid, length, dmces, ceces, neces, rpces, svces):
        self.guid = guid
        self.length = length
        self.dmces = dmces
        self.ceces = ceces
        self.neces = neces
        self.rpces = rpces
        self.svces = svces
        self.filename = None

    class EffectTimeInfo:
        def __init__(self, use_time, start, end, hardpoint):
            self.use_time = use_time
            self.start = start
            self.end = end
            self.hardpoint = hardpoint

        def __repr__(self):
            return '<EffectTimeInfo>: Start:{} End:{} Hardpoint:{}'.format(self.start, self.end, self.hardpoint)

    class DMCEInfo:
        def __init__(self, time, animation, material, model, model_path, anim_path):
            self.time = time
            self.animation = animation
            self.material = material
            self.model = model
            self.model_path = PathUtil.normPath(model_path)
            self.anim_path = PathUtil.normPath(anim_path)

        def __repr__(self):
            return '<DMCEInfo>: {} {} ({})'.format(os.path.basename(self.model_path), os.path.basename(self.anim_path),
                                                   self.time.hardpoint)

    class CECEInfo:
        def __init__(self, time, action, animation, var, varIndex, path):
            self.time = time
            self.action = action
            self.animation = animation
            self.var = var
            self.varIndex = varIndex
            self.path = PathUtil.normPath(path)

        def __repr__(self):
            return '<CECEInfo>: {} {} ({})'.format(self.action, self.var, self.time.hardpoint)

    class NECEInfo:
        def __init__(self, time, guid, variable, path):
            self.time = time
            self.guid = guid
            self.variable = variable
            self.path = PathUtil.normPath(path)

        def __repr__(self):
            return '<NECEInfo>: {} ({})'.format(self.path, self.time.hardpoint)

    class RPCEInfo:
        def __init__(self, time, model, model_path, material):
            self.time = time
            self.model = model
            self.model_path = PathUtil.normPath(model_path)
            self.material = PathUtil.normPath(material)

        def __repr__(self):
            return '<RPCEInfo>: {} ({})'.format(self.model_path, self.time.hardpoint)

    class SVCEInfo:
        class SVCELine:
            def __init__(self, sounds):
                self.sounds = sounds

        def __init__(self, time, guid, lines):
            self.time = time
            self.guid = guid
            self.lines = lines

        def __repr__(self):
            return '<SVCEInfo>: {} ({})'.format(self.guid, self.time.hardpoint)

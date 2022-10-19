from . import BinaryUtil
from . import PathUtil
from ..datatypes import AnimationTypes, EffectTypes



def read(filename, stream=None):
    if stream == None:
        stream = BinaryUtil.openStream(PathUtil.normPath(filename))
    if stream == None:
        return None
    magic = BinaryUtil.readFmtFlat(stream, EffectTypes.OWEffectHeader.magic_format)
    if magic == 'owanim':  # weirdmush why is this like this
        header = AnimationTypes.OWAnimHeader.read(stream)
        if header.anim_type == AnimationTypes.OWAnimType.Reference:
            written_path = AnimationTypes.OWAnimHeader.read_reference(stream)
            path = PathUtil.makePathAbsolute(filename, written_path)
            major, minor, guid, fps, anim_type = BinaryUtil.readFmtFlat(stream, AnimationTypes.OWAnimHeader.format)
            anim_type = AnimationTypes.OWAnimType(anim_type)
            return AnimationTypes.OWAnimHeader(major, minor, guid, fps, anim_type)

        if header.anim_type == AnimationTypes.OWAnimType.Data:
            path, model_path = BinaryUtil.readFmtFlat(stream, AnimationTypes.OWAnimHeader.data_format)
            # embedded oweffect
            data = read(filename, stream)
            return AnimationTypes.OWAnimFile(header, filename, data, path, model_path)

    if magic == 'oweffect':
        def readTimeInfo(stream):
            do_time, start, end, hardpoint = BinaryUtil.readFmtFlat(stream, EffectTypes.OWEffectData.time_format)
            return EffectTypes.OWEffectData.EffectTimeInfo(do_time, start, end, hardpoint)

        major, minor, guid, length, dmce_count, cece_count, nece_count, rpce_count, fece_count, osce_count, svce_count = BinaryUtil.readFmtFlat(
            stream, EffectTypes.OWEffectData.header_format)

        dmces = []
        for i in range(dmce_count):
            time = readTimeInfo(stream)
            animation, material, model, anim_path, model_path = BinaryUtil.readFmtFlat(stream,
                                                                                         EffectTypes.OWEffectData.DMCEInfo.format)
            dmces.append(EffectTypes.OWEffectData.DMCEInfo(time, animation, material, model, anim_path, model_path))

        ceces = []
        for i in range(cece_count):
            time = readTimeInfo(stream)
            action, animation, var, varIndex, path = BinaryUtil.readFmtFlat(stream,
                                                                              EffectTypes.OWEffectData.CECEInfo.format)
            action = EffectTypes.CECEAction(action)
            ceces.append(EffectTypes.OWEffectData.CECEInfo(time, action, animation, var, varIndex, path))

        neces = []
        for i in range(nece_count):
            time = readTimeInfo(stream)
            guid, var, path = BinaryUtil.readFmtFlat(stream, EffectTypes.OWEffectData.NECEInfo.format)
            neces.append(EffectTypes.OWEffectData.NECEInfo(time, guid, var, path))

        rpces = []
        for i in range(rpce_count):
            time = readTimeInfo(stream)
            model, material, model_path = BinaryUtil.readFmtFlat(stream, EffectTypes.OWEffectData.RPCEInfo.format)
            rpces.append(EffectTypes.OWEffectData.RPCEInfo(time, model, model_path, material))

        svces = []
        for i in range(svce_count):
            time = readTimeInfo(stream)
            guid, line_count = BinaryUtil.readFmtFlat(stream, EffectTypes.OWEffectData.SVCEInfo.format)
            lines = []
            for i in range(line_count):
                sound_count = BinaryUtil.readFmtFlat(stream, EffectTypes.OWEffectData.SVCEInfo.line_format)

                sounds = []
                for j in range(sound_count):
                    sounds.append(BinaryUtil.readFmtFlat(stream, EffectTypes.OWEffectData.SVCEInfo.line_sound_format))

                lines.append(EffectTypes.OWEffectData.SVCEInfo.SVCELine(sounds))
            svces.append(EffectTypes.OWEffectData.SVCEInfo(time, guid, lines))

        data = EffectTypes.OWEffectData(guid, length, dmces, ceces, neces, rpces, svces)
        data.filename = PathUtil.normPath(filename)
        return data

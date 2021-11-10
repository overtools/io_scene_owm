from . import bin_ops
from . import owm_types
import io
import os
from . import bpyhelper

def openStream(filename):
    stream = None
    with open(filename, 'rb') as f:
        stream = io.BytesIO(f.read())
    return stream

def read(filename, sub=False):
    stream = openStream(bpyhelper.normpath(filename))
    if stream == None:
        return False

    major, minor, materialCount = bin_ops.readFmtFlat(stream, owm_types.OWMATHeader.structFormat)
    header = owm_types.OWMATHeader(major, minor, materialCount)

    if major >= 2 and minor >= 0:  
        staticInputCount = 00
        if (major == 2 and minor >= 1) or major >= 3:
            staticInputCount = bin_ops.readFmtFlat(stream, owm_types.OWMATHeader.new_format_21)
        mat_type = owm_types.OWMatType(bin_ops.readFmtFlat(stream, owm_types.OWMATHeader.new_format))
        if mat_type == owm_types.OWMatType.Material:
            shader, id_count = bin_ops.readFmtFlat(stream, owm_types.OWMATHeader.new_material_header_format)
            ids = []
            for i in range(id_count):
                ids.append(bin_ops.readFmtFlat(stream, owm_types.OWMATHeader.new_id_format))
            textures = []
            for i in range(materialCount):
                texture, texture_type = bin_ops.readFmtFlat(stream, owm_types.OWMATMaterial.new_material_format)
                textures += [(bpyhelper.normpath(texture), 0, texture_type)]
            static_inputs = {}
            for i in range(staticInputCount):
                input_hash, input_data_length = bin_ops.readFmtFlat(stream, owm_types.OWMATMaterial.static_input_format)
                static_inputs[input_hash] = stream.read(input_data_length)
            if sub:
                return textures, shader, ids, static_inputs
            else:
                materials = []
                for mat_id in ids:
                    materials.append(owm_types.OWMATMaterial(mat_id, None, len(textures), textures, shader, static_inputs))
                return owm_types.OWMATFile(header, materials)
        elif mat_type == owm_types.OWMatType.ModelLook:
            materials = []
            for i in range(materialCount):
                material_file = bin_ops.readFmtFlat(stream, owm_types.OWMATMaterial.new_modellook_format)
                mat_guid = os.path.splitext(os.path.basename(material_file))[0]  #this totally won't cause issues
                textures, shader, ids, static_inputs = read(os.path.join(filename, bpyhelper.normpath(material_file)), True)
                for mat_id in ids:
                    materials += [owm_types.OWMATMaterial(mat_id, mat_guid, len(textures), textures, shader, static_inputs)]
            return owm_types.OWMATFile(header, materials)
    else:
        materials = []
        for i in range(materialCount):
            key, textureCount = bin_ops.readFmtFlat(stream, owm_types.OWMATMaterial.structFormat)
            textures = []
            for j in range(textureCount):
                t = bin_ops.readFmtFlat(stream, [owm_types.OWMATMaterial.exFormat[0]])
                y = 0
                properType = 0
                if major >= 1 and minor >= 1:
                    y = ord(stream.read(1))
                if major >= 1 and minor >= 2:
                    properType = bin_ops.readFmtFlat(stream, [owm_types.OWMATMaterial.typeFormat[0]])
                textures += [(bpyhelper.normpath(t), y, properType)]
            materials += [owm_types.OWMATMaterial(key, None, textureCount, textures)]

    return owm_types.OWMATFile(header, materials)

import os

from . import read_owentity
from . import import_owmdl
from . import bpyhelper
from mathutils import *
import math
import bpy, bpy_extras, mathutils


def get_mdl_settings(settings, modelname):
    return settings.mutate(bpyhelper.normpath(os.path.dirname(os.path.dirname(os.path.dirname(settings.filename))) + "/Models/" + modelname + "/" + modelname.replace(".00C", "") + ".owmdl"))


def read(settings, import_children=False, is_child=False):
    global sets

    root, file = os.path.split(settings.filename)

    data = read_owentity.read(settings.filename)
    if data is None: return None, None

    mdl_settings = get_mdl_settings(settings, data.model)

    root_object = bpy.data.objects.new("Entity " + data.file, None)
    root_object.hide = root_object.hide_render = True
    root_object['owm.entity.guid'] = data.index
    root_object['owm.entity.model'] = data.model_index

    base_model = None
    if data.model != "null":
        base_model = import_owmdl.read(mdl_settings, None, False, not is_child)
        base_model[0].parent = root_object

    if import_children:
        for child in data.children:
            child_settings = settings.mutate(bpyhelper.normpath(os.path.dirname(os.path.dirname(settings.filename)) + "/{}/{}.owentity".format(child.file, child.file)))
            if not os.path.exists(child_settings.filename): continue
            child_object, child_data = read(child_settings, import_children, True)
            child_object.parent = root_object

            child_object['owm.entity.child.var'] = child.var_index
            child_object['owm.entity.child.hardpoint'] = child.attachment

            if child.attachment != "null" and child.attachment in base_model[3][1]: # eww
                bpyhelper.select_obj(child_object, True)
                copy_location = child_object.constraints.new("COPY_LOCATION")
                copy_location.name = "ChildEntity Location"
                copy_location.target = base_model[3][1][child.attachment]

                copy_rotation = child_object.constraints.new("COPY_ROTATION")
                copy_rotation.name = "ChildEntity Rotation"
                copy_rotation.target = base_model[3][1][child.attachment]

                copy_scale = child_object.constraints.new("COPY_SCALE")
                copy_scale.name = "ChildEntity Scale"
                copy_scale.target = base_model[3][1][child.attachment]
    bpyhelper.scene_link(root_object)

    if base_model is not None:
        bpy.context.scene.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        import_owmdl.select_all(base_model[0])
        if base_model[1] is not None:
            bpy.context.scene.objects.active = base_model[1]
    
    return root_object, data

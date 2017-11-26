import os

from . import read_owentity
from . import import_owmdl
from . import bpyhelper
from mathutils import *
import math
import bpy, bpy_extras, mathutils


def get_mdl_settings(settings, modelname):
    return settings.mutate(os.path.dirname(os.path.dirname(os.path.dirname(settings.filename))) + "\\Models\\" + modelname + "\\" + modelname.replace(".00C", "") + ".owmdl")


def read(settings, import_children=False, is_child=False):
    global sets

    root, file = os.path.split(settings.filename)

    data = read_owentity.read(settings.filename)
    if data is None: return

    mdl_settings = get_mdl_settings(settings, data.model)

    root_object = bpy.data.objects.new("Entity:" + data.file, None)
    root_object.hide = root_object.hide_render = True
    
    base_model = import_owmdl.read(mdl_settings, None, False, not is_child)
    base_model[0].parent = root_object

    if import_children:
        for child in data.children:
            child_settings = settings.mutate(os.path.dirname(os.path.dirname(settings.filename)) + "\\{}\\{}.owentity".format(child.file, child.file))
            if not os.path.exists(child_settings.filename): continue
            child_object = read(child_settings, import_children, True)
            child_object.parent = root_object

            if child.attachment != "null": # eww
                bpyhelper.select_obj(child_object, True)
                childOf = child_object.constraints.new("CHILD_OF")
                childOf.name = "ChildEntity: %s" % (child.file)
                childOf.target = base_model[3][1][child.attachment]
##                context_cpy = bpy.context.copy()
##                context_cpy["constraint"] = childOf
##                child_object.update_tag({"DATA"})
##                bpy.ops.constraint.childof_set_inverse(context_cpy, constraint=childOf.name, owner="OBJECT")
##                child_object.update_tag({"DATA"})
        
    bpyhelper.scene_link(root_object)
    print(data)

    return root_object

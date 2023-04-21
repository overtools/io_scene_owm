import bpy
import bpy_extras
import mathutils

acm = bpy_extras.io_utils.axis_conversion(from_forward='-Z', from_up='Y').to_4x4()

VISIBLE_SELECTION = set()


def selectObj(obj, value, track=True):
    obj.select_set(value)
    if value is True and obj.hide_viewport is False and track is True:
        VISIBLE_SELECTION.add(obj)


def deselectAll():
    global VISIBLE_SELECTION
    for obj in VISIBLE_SELECTION:
        try:
            obj.select_set(False)
        except:
            pass
    VISIBLE_SELECTION = set()


def isSelected(obj):
    return obj in VISIBLE_SELECTION


def setActive(obj):
    bpy.context.view_layer.objects.active = obj


def pos_matrix(pos):
    global acm
    posMtx = mathutils.Matrix.Translation(pos)
    mtx = acm @ posMtx
    return mtx.to_translation()

def rotateLight(blendLightObj, lightData):
    blendLightObj.rotation_euler = mathutils.Quaternion(wxzy(lightData.rotation)).to_euler('XYZ')
    blendLightObj.rotation_euler.x -= 1.5708

def xpzy(vec):
    return vec[0], vec[2], vec[1]


def wxzy(vec):
    return vec[3], vec[0], -vec[2], vec[1]


def forceSceneUpdate():
    bpy.context.view_layer.update()


def createFolder(name, hide=True, link=False):  # folder=empty. could be collections but those are iffy to manage sometimes
    folder = bpy.data.objects.new(name, None)
    folder["owm.folder"] = True
    if hide:
        folder.hide_viewport = folder.hide_render = True
    if link:
        linkScene(folder)
    return folder


def linkScene(obj, collection=None):
    if collection is None:
        collection = bpy.context.view_layer.active_layer_collection.collection
    collection.objects.link(obj)

def unlinkScene(obj, collection=None):
    if collection is None:
        collection = bpy.context.view_layer.active_layer_collection.collection
    collection.objects.unlink(obj)

def bulkDelete(objs):
    bpy.data.batch_remove(objs)
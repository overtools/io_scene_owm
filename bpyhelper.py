import bpy
import os.path
import traceback

IS_BLENDER280 = bpy.app.version >= (2, 80, 0)

def clean_empties():
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY' and obj.hide_viewport == True and len(obj.children) == 0:
            print('[owm]: removed object: {}'.format(obj.name))
            scene_unlink(obj)
            bpy.data.objects.remove(obj)
    scene_update()

def format_exc(e):
    return ''.join(traceback.format_exception(type(e), e, e.__traceback__))

def clean_materials():
    for mat in bpy.data.materials:
        if mat.users == 0:
            print('[owm]: removed material: {}'.format(mat.name))
            bpy.data.materials.remove(mat)
    scene_update()
    t = {}
    for tex in bpy.data.textures:
        if tex.users == 0:
            print('[owm]: removed texture: {}'.format(tex.name))
            bpy.data.textures.remove(tex)
    scene_update()

LOCK_UPDATE = False

VISIBLE_SELECTION = []

def scene_update():
    if LOCK_UPDATE: return
    bpy.context.view_layer.update()


def select_obj(object, value, track=True):
     object.select_set(value)
     if value is True and object.hide_viewport is False and track is True:
         VISIBLE_SELECTION.append(object)


def deselect_all():
    global VISIBLE_SELECTION
    for object in VISIBLE_SELECTION:
        try:
            object.select_set(False)
        except: pass
    VISIBLE_SELECTION = []

def create_collection(name, parent):
    if parent is None:
        parent = bpy.context.view_layer.active_layer_collection.collection
    collection = bpy.data.collections.new(name)
    parent.children.link(collection)
    return collection


def instance_collection(collection, name, parent_collection):
    instance = bpy.data.objects.new(name, object_data=None)
    instance.instance_collection = collection
    instance.instance_type = 'COLLECTION'
    parent_collection.objects.link(instance)


def is_selected(object): return object.select_get()
def scene_link(object, collection=None):
    if collection is None:
        collection = bpy.context.view_layer.active_layer_collection.collection
    collection.objects.link(object)
def scene_unlink(object, collection=None):
    if collection is None:
        collection = bpy.context.view_layer.active_layer_collection.collection
    collection.objects.unlink(object)
def scene_active(): return bpy.context.view_layer.objects.active
def scene_active_set(object): bpy.context.view_layer.objects.active = object
def new_uv_layer(mesh, name): return mesh.uv_layers.new(name = name)
def new_color_layer(mesh, name): return mesh.vertex_colors.new(name = name)
def normpath(path): return os.path.normpath(path.replace('\\', os.path.sep).replace('/', os.path.sep))
def valid_path(path): return path is not None and len(path) > 4
def safe_color(r, g, b): return (r, g, b, 1.0)

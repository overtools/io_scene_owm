import bpy
import os.path
import traceback

IS_BLENDER280 = bpy.app.version >= (2, 80, 0)

def clean_empties():
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY' and obj.hide_render == True and obj.hide_viewport == True and len(obj.children) == 0:
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

def scene_update():
    if LOCK_UPDATE: return
    bpy.context.scene.update()
def select_obj(object, value): object.select_set(value)
def is_selected(object): return object.select_get()
def scene_link(object): bpy.context.view_layer.active_layer_collection.collection.objects.link(object)
def scene_unlink(object): bpy.context.view_layer.active_layer_collection.collection.objects.unlink(object)
def scene_active(): return bpy.context.view_layer.objects.active
def scene_active_set(object): bpy.context.view_layer.objects.active = object
def get_objects(): return bpy.context.scene_layer.objects
def new_uv_layer(mesh, name): return mesh.uv_layers.new(name = name)
def new_color_layer(mesh, name): return mesh.vertex_colors.new(name = name)
def normpath(path): return os.path.normpath(path.replace('\\', os.path.sep).replace('/', os.path.sep))
def safe_color(r, g, b): return (r, g, b, 1.0)

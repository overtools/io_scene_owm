import bpy
import os.path

IS_BLENDER280 = bpy.app.version >= (2, 80, 0)

def select_obj(object, value): object.select = value
def is_selected(object): return object.select
def scene_link(object): bpy.context.scene.objects.link(object)
def scene_unlink(object): bpy.context.scene.objects.unlink(object)
def scene_active(): return bpy.context.scene.objects.active
def scene_active_set(object): bpy.context.scene.objects.active = object
def get_objects(): return bpy.context.scene.objects
def new_uv_layer(mesh, name): return mesh.uv_textures.new(name)
def normpath(path): return os.path.normpath(path.replace('\\', os.path.sep).replace('/', os.path.sep))

if IS_BLENDER280:
    def new_uv_layer(mesh, name): return mesh.uv_layers.new(name)
    def select_obj(object, value):
        if value: object.select_set(action='SELECT')
        else: object.select_set(action='DESELECT')
    def is_selected(object): return object.select_get()
    def scene_link(object): bpy.context.scene_collection.objects.link(object)
    def scene_unlink(object): bpy.context.scene_collection.objects.unlink(object)
    try:
        if bpy.context.scene_layer != None:
            def scene_active(): return bpy.context.scene_layer.objects.active
            def scene_active_set(object): bpy.context.scene_layer.objects.active = object
            def get_objects(): return bpy.context.scene_layer.objects
    except: pass

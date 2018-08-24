import bpy
import os.path

IS_BLENDER280 = bpy.app.version >= (2, 80, 0)

def clean_empties(): 
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY' and obj.hide == True and len(obj.children) == 0:
            print('[owm]: removed object: {}'.format(obj.name))
            scene_unlink(obj)
            bpy.data.objects.remove(obj) 
    scene_update()

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

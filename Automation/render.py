# blender -P render.py -- <owentity_path> <owmat_path> <render_path>

import bpy, sys, os, math
from mathutils import Vector
import io_scene_owm

entity_path = sys.argv[-3]
material_path = sys.argv[-2]
render_path = sys.argv[-1]

objects = bpy.context.scene.collection.objects
for obj in objects:
    objects.unlink(obj)
camera_data = bpy.data.cameras.new("Camera")
camera = bpy.data.objects.new("Camera", camera_data)
objects.link(camera)

def bind_materials(meshes, data, materials):
    if materials == None:
        return
    for i, obj in enumerate(meshes):
        mesh = obj.data
        mesh_data = data.meshes[i]
        if mesh_data.materialKey in materials[1]:
            mesh.materials.clear()
            mesh.materials.append(materials[1][mesh_data.materialKey])

owentity_settings = io_scene_owm.owm_types.OWSettings(
    entity_path, # self.filepath,
    0, # self.uvDisplX,
    0, # self.uvDisplY,
    False, # self.autoIk,
    True, # self.importNormals,
    True,  # self.importEmpties
    False, # self.importMaterial,
    True,  # self.importSkeleton
    True, # self.importColor
    True, # self.autoSmoothNormals
)

light1_data = bpy.data.lights.new("Light A", "AREA")
light1 = bpy.data.objects.new("Light A", light1_data)
objects.link(light1)
light2_data = bpy.data.lights.new("Light B", "AREA")
light2 = bpy.data.objects.new("Light B", light2_data)
objects.link(light2)

io_scene_owm.owm_types.update_data()
(entity_root, entity_data, model) = io_scene_owm.import_owentity.read(owentity_settings, False)
if material_path != "null":
    material = io_scene_owm.import_owmat.read(material_path, '')
    bind_materials(model[2], model[4], material)

max_top = [0, 0, 0]
min_top = [0, 0, 0]
for i, obj in enumerate(model[2]):
    for j in range(0, 8):
        for k in range(0, 3):
            max_top[k] = max([max_top[k], obj.bound_box[j][k]])
            min_top[k] = min([min_top[k], obj.bound_box[j][k]])
size_base = (Vector(max_top) - Vector(min_top)).length
size = size_base * 5
light1_data.energy = size_base * 20
light2_data.energy = size_base * 10
camera_data.lens = size_base * 200

for i, obj in enumerate(model[2]):
    max_extent = 0
    for j in range(0, 8):
        for k in range(0, 3):
            max_extent = max([max_extent, obj.bound_box[j][k]])
    max_extent *= size
    corner = obj.location + Vector((max_extent * size, -max_extent * size, max_extent * (size_base + 1.0)))
    side = obj.location + Vector((max_extent, 0, max_extent * size_base))
    if camera.location < corner:
        camera.location = corner 
        light1.location = corner
    if light2.location < side:
        light2.location = side

bpy.context.view_layer.objects.active = camera
bpy.ops.object.constraint_add(type='TRACK_TO')
bpy.context.object.constraints["Track To"].target = entity_root
bpy.context.object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'
bpy.context.view_layer.objects.active = light1
bpy.ops.object.constraint_add(type='TRACK_TO')
bpy.context.object.constraints["Track To"].target = entity_root
bpy.context.object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'
bpy.context.view_layer.objects.active = light2
bpy.ops.object.constraint_add(type='TRACK_TO')
bpy.context.object.constraints["Track To"].target = entity_root
bpy.context.object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'
bpy.context.scene.camera = camera
bpy.context.scene.render.resolution_x = 2048
bpy.context.scene.render.resolution_y = 2048
bpy.context.scene.render.film_transparent = True

bpy.context.view_layer.update()

bpy.context.scene.render.filepath = render_path
bpy.ops.render.render(write_still=True)

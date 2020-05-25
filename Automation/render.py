# blender -P render.py -- <owentity_path> <owmat_path> <render_path>

import bpy, sys, os, mathutils

entity_path = sys.argv[-3]
material_path = sys.argv[-2]
render_path = sys.argv[-1]

objects = bpy.context.scene.collection.objects

for object in objects:
    objects.unlink(object)

def bind_materials(meshes, data, materials):
    if materials == None:
        return
    for i, obj in enumerate(meshes):
        mesh = obj.data
        mesh_data = data.meshes[i]
        if mesh_data.materialKey in materials[1]:
            mesh.materials.clear()
            mesh.materials.append(materials[1][mesh_data.materialKey])

(entity, entity_data, entity_model)  = bpy.ops.import_mesh.overtools_entity(filepath=entity_path)
if material_path != "null":
    material = bpy.ops.import_material.overtools_material(filepath=material_path)
    bind_materials(entity_model[2], entity_model[4], material)

dg = bpy.context.evaluated_depsgraph_get()

camera = camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
objects.link(camera)

# set up camera

for object in enumerate(entity_model[2]):
    corner = object.location + mathutils.Vector(object.bound_box[5][:]) + mathutils.Vector(2, -2, 2)
    if camera.location < corner:
        camera.location = corner 

bpy.context.view_layer.objects.active = camera
bpy.ops.object.constraint_add(type='TRACK_TO')
bpy.context.object.constraints["Track To"].target = entity
bpy.context.object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'

dg.update()

# bpy.context.scene.render.filepath = render_path
# bpy.ops.render.render(write_still=True)

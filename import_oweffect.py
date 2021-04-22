import os

from . import read_oweffect
from . import import_owmdl
from . import import_owentity
from . import bpyhelper
from . import owm_types
from . import import_owmdl
from . import read_owmdl
from mathutils import *
import math
import bpy, bpy_extras, mathutils
import os
import random

def get_object(obj=None): # return => is_entity, object, model_index
    if obj is None:
        obj = bpy.context.object
    if 'owm.entity.guid' in obj:
        return True, obj, obj['owm.entity.model']
    if 'owm.model.guid' in obj:
        model = obj['owm.model.guid']
        if obj.parent is not None and 'owm.entity.model' in obj.parent:
            return True, obj.parent, model
        else:
            return False, obj, model
    elif obj.parent is not None:
        return get_object(obj.parent)

    return False, None, 0

def get_skeleton(is_entity, obj, model):
    model_container = None
    if is_entity:
        for o in obj.children:
            if 'owm.model.guid' in o:
                model_container = o
    else:
        model_container = obj

    skeleton = None
    for o in model_container.children:
        if 'owm.skeleton.model' in o:
            if o['owm.skeleton.model'] == model:
                return o


def get_meshes(skeleton):
    meshes = list()
    for o in skeleton.children:
        if 'owm.mesh.name' in o:
            meshes.append(o)
    return meshes


def create_refpose(model_path):
    model_data = read_owmdl.read(model_path)
    arm = import_owmdl.import_refpose_armature(False, model_data)

    att = bpy.data.objects.new('Sockets', None)
    att.parent = arm
    att.parent_type = "ARMATURE"
    att.hide_viewport = att.hide_render = True
    att['owm.hardpoint_container'] = True
    bpyhelper.scene_link(att)

    e_dict = {}
    for emp in model_data.empties:
        bpy.ops.object.empty_add(type='SPHERE', radius=0.05 )
        empty = bpy.context.active_object
        empty.parent = att
        empty.parent_type = "OBJECT"
        empty.name = emp.name
        empty.show_in_front = True
        empty.location = import_owmdl.xzy(emp.position)
        empty.rotation_euler = import_owmdl.wxzy(emp.rotation).to_euler('XYZ')
        empty['owm.hardpoint.bone'] = emp.hardpoint
        bpyhelper.select_obj(empty, True)
            
        e_dict[emp.name] = empty

    for pbone in arm.pose.bones:
        pbone.bone.select = False
    # this might be a little more than what we need
    for name, hardpoint in e_dict.items():
        bpy.ops.object.select_all(action='DESELECT')
        bpyhelper.select_obj(hardpoint, True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')

        
        if hardpoint['owm.hardpoint.bone'] not in arm.pose.bones:
            bpy.ops.object.mode_set(mode='OBJECT') # fixes 'context is incorrect'
            continue  # todo: why
        bone = arm.pose.bones[hardpoint['owm.hardpoint.bone']].bone
        bone.select = True
        arm.data.bones.active = bone
        bpy.ops.object.parent_set(type='BONE')
        bone.select = False
        bpyhelper.select_obj(hardpoint, False)
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    return arm, e_dict, att


def attach(par, obj):
    print("attaching %s to %s" % (obj, par))
    copy_transforms = obj.constraints.new('COPY_TRANSFORMS')
    copy_transforms.name = 'Socket Attachment'
    copy_transforms.target = par
    copy_transforms.mix_mode = 'REPLACE'

    return copy_transforms

def delete(obj):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    if obj is None:
        return
    bpyhelper.select_obj(obj, True)
    bpy.ops.object.delete()


def deselect_tree(obj):
    bpyhelper.select_obj(hardpoint, False)
    for child in obj.children:
        deselect_tree(child)


def process(settings, data, pool, parent, target_framerate, hardpoints, variables):
    if type(data) == owm_types.OWAnimFile:
        if target_framerate is None:
            target_framerate = int(data.header.fps)
        
        is_entity, obj, model = get_object()
        
        this_obj = bpy.data.objects.new('Animation {}'.format(os.path.splitext(os.path.basename(data.anim_path))[0]), None)
        this_obj.hide_viewport = this_obj.hide_render = True
        bpyhelper.scene_link(this_obj)
        if parent is None:
            parent = this_obj
            this_obj.parent = obj
        else:
            this_obj.parent = parent
        
        skeleton = get_skeleton(is_entity, obj, model)
        
        bpy.ops.object.select_all(action='DESELECT')

        new_skeleton, hardpoints, hp_container = create_refpose(os.path.join(pool, data.model_path))
        new_skeleton.parent = this_obj

        for mesh in get_meshes(skeleton):
            if 'OWM Skeleton' in mesh.modifiers:
                mod = mesh.modifiers['OWM Skeleton']
                mod.object = new_skeleton

        new_skeleton.rotation_euler = (math.radians(90), 0, 0)
        
        directory, file = os.path.split(data.anim_path)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = new_skeleton
        bpy.ops.import_scene.seanim
        bpy.ops.import_scene.seanim(filepath=bpyhelper.normpath(os.path.join(pool, directory)) + os.path.sep, files=[{'name': file}])

        if target_framerate != int(data.header.fps):
            scale = target_framerate / int(data.header.fps)
            bpy.context.scene.frame_end *= scale
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = new_skeleton

            for f in new_skeleton.animation_data.action.fcurves:
                for kp in f.keyframe_points:
                    kp.co[0] *= scale

        bpy.context.scene.render.fps = target_framerate

        if is_entity:
            for c in obj.children:
                if 'owm.entity.child.var' in c:
                    var = c['owm.entity.child.var']
                    ent_obj = bpy.data.objects.new('EffectEntityWrapper {}'.format(var), None)
                    ent_obj.hide_viewport = this_obj.hide_render = True
                    if c['owm.entity.child.hardpoint'] != 'null' and c['owm.entity.child.hardpoint'] in hardpoints:
                        ent_obj.parent = hardpoints[c['owm.entity.child.hardpoint']]
                        ent_obj.parent['owm.effect.hardpoint.used'] = True
                    else:
                        ent_obj.parent = this_obj
                    bpyhelper.scene_link(ent_obj)
                    variables[var] = 'entity_child', ent_obj, c

                    if 'Socket Attachment' in c.constraints:
                        c.constraints['Socket Attachment'].target = ent_obj
        
        process(settings, data.data, pool, this_obj, target_framerate, hardpoints, variables)

        if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


        if settings.cleanup_hardpoints:
            for hp_name,hp in hardpoints.items():
                if 'owm.effect.hardpoint.used' not in hp:
                    delete(hp)
                else:
                    del hp['owm.effect.hardpoint.used']

            if len(hp_container.children) == 0:
                delete(hp_container)

        return this_obj, new_skeleton

    if type(data) == owm_types.OWEffectData:
        obj = bpy.data.objects.new('Effect {}'.format(data.guid), None)
        obj.parent = parent
        obj.hide_viewport = obj.hide_render = True
        bpyhelper.scene_link(obj)

        for svce in data.svces:
            if not settings.import_SVCE:
                continue

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            bpy.context.scene.frame_set(int(target_framerate * svce.time.start))
            
            bpy.ops.object.speaker_add()
            speaker = bpy.context.view_layer.objects.active
            speaker.name = 'SVCE Speaker'
            speaker.location = (0, 0, 0)
            
            speaker.animation_data.nla_tracks['SoundTrack'].strips['NLA Strip'].frame_start = target_framerate * svce.time.start

            line_seed = settings.svce_line_seed
            if line_seed == -1:
                line_seed = random.randint(0, 99999999)
            sound_seed = settings.svce_sound_seed
            if sound_seed == -1:
                sound_seed = random.randint(0, 99999999)

            line_random = random.Random(line_seed)
            sound_random = random.Random(sound_seed)
            
            line = line_random.choice(svce.lines)
            sound = sound_random.choice(line.sounds)
            
            speaker.data.sound = bpy.data.sounds.load(os.path.join(os.path.dirname(data.filename), sound), check_existing=True)

            # these are probably incorrect
            speaker.data.volume = 0.7
            speaker.data.attenuation = 0.3

            speaker.parent = obj

            if svce.time.hardpoint != 'null':
                attach(hardpoints[svce.time.hardpoint], speaker)
            elif 'hardpoint_0012' in hardpoints:
                # erm, seems to be in the head
                attach(hardpoints['hardpoint_0012'], speaker)
                hardpoints['hardpoint_0012']['owm.effect.hardpoint.used'] = True

            bpy.context.scene.frame_set(0)

##        for rpce in data.rpces:
##            # if not settings.import_RPCE:
##            #     continue
##            mutate = settings.settings.mutate(os.path.join(pool, rpce.model_path))
##            mutate.importEmpties = False
##            rpce_model = import_owmdl.read(mutate) # rootObject, armature, meshes, empties, data
##
##            for mesh in rpce_model[2]:
##                # if dmce_skele is not None:
##                #     mesh.parent = dmce_skele
##                # else:
##                #     mesh.parent = obj
##                if rpce.time.ref_hardpoint != 'null':
##                    attach(hardpoints[rpce.time.ref_hardpoint], mesh)
##
##            if rpce.time.ref_hardpoint != 'null':
##                attach(hardpoints[rpce.time.ref_hardpoint], rpce_model[0])
##                hardpoints[rpce.time.ref_hardpoint]['owm.effect.hardpoint.used'] = True
##
##            deselect_tree(rpce_model[0])
            
            

        for dmce in data.dmces:
            if not settings.import_DMCE:
                continue
            end_frame = bpy.context.scene.frame_end
            mutate = settings.settings.mutate(os.path.join(pool, dmce.model_path))
            mutate.importEmpties = False
            # mutate.importEmpties = True
            dmce_model = import_owmdl.read(mutate) # rootObject, armature, meshes, empties, data
            dmce_model[0].parent = obj
            dmce_skele = None
            if dmce.anim_path != 'null':
                mutate2 = settings.mutate(os.path.join(pool, dmce.anim_path))
                mutate2.force_fps = True
                mutate2.target_fps = target_framerate
                dmce_obj, dmce_skele = read(mutate2, obj)

                for f in dmce_skele.animation_data.action.fcurves:
                    for kp in f.keyframe_points:
                        kp.co[0] += int(target_framerate * dmce.time.start)
            else:
                pass # todo: cleanup hardpoints

            delete(dmce_model[0])
            delete(dmce_model[1])
            for mesh in dmce_model[2]:
                if dmce_skele is not None:
                    mesh.parent = dmce_skele
                else:
                    mesh.parent = obj
                if dmce.time.hardpoint != 'null' and dmce.time.hardpoint in hardpoints:
                    attach(hardpoints[dmce.time.hardpoint], mesh)

            bpy.context.scene.frame_end = end_frame
            if dmce.time.hardpoint != 'null' and dmce.time.hardpoint in hardpoints:
                if dmce_skele is not None:
                    attach(hardpoints[dmce.time.hardpoint], dmce_skele)
                    dmce_model[0].parent = dmce_obj
                else:
                    if dmce_model[1] is not None:
                        dmce_model[1].rotation_euler = (0, 0, 0)
                attach(hardpoints[dmce.time.hardpoint],dmce_model[0])
                hardpoints[dmce.time.hardpoint]['owm.effect.hardpoint.used'] = True

        for nece in data.neces:
            if not settings.import_NECE:
                continue

            act = bpy.context.view_layer.objects.active

            mutate = settings.settings.mutate(os.path.join(pool, nece.path))
            nece_entity, nece_data, obj_data = import_owentity.read(mutate, True, True)

            deselect_tree(nece_entity)

            bpy.context.view_layer.objects.active = act

            ent_obj = bpy.data.objects.new('EffectEntityWrapper {}'.format(nece.variable), None)
            ent_obj.hide_viewport = ent_obj.hide_render = True
            bpyhelper.scene_link(ent_obj)

            if nece.time.hardpoint != 'null' and nece.time.hardpoint in hardpoints:
                ent_obj.parent = hardpoints[nece.time.hardpoint]
                ent_obj.parent['owm.effect.hardpoint.used'] = True
            else:
                ent_obj.parent = obj
            attach(ent_obj, nece_entity)

            nece_entity.parent = obj
            nece_entity['owm.entity.child.var'] = nece.variable

            variables[nece.variable] = 'entity_child', ent_obj, nece_entity
       
        show_ents = []
                    
        for cece in data.ceces:
            if not settings.import_CECE:
                continue
            if cece.var_index not in variables:
                print('[import_effect]: Could not find CECE entity {} (animation={})'.format(cece.var_index, cece.path))
                continue
            else:
                var_id, cece_container, cece_entity = variables[cece.var_index]
            if cece.action == owm_types.CECEAction.Show:
                show_ents.append(cece.var_index)
            if cece.action == owm_types.CECEAction.PlayAnimation:
                mutate = settings.mutate(os.path.join(pool, bpyhelper.normpath('Models/{0:012x}.00C/{1}').format(cece_entity['owm.entity.model'],cece.path)))
                mutate.force_fps = True
                mutate.target_fps = target_framerate

                if not os.path.exists(mutate.filename):
                    print('[import_effect]: Missing CECE \'Models/{0:012x}.00C/{1}\''.format(cece_entity['owm.entity.model'],cece.path))
                    continue

                if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = cece_entity

                end_frame = bpy.context.scene.frame_end

                anim_container, anim_skele = read(mutate, obj)
                bpy.context.scene.frame_end = end_frame
                anim_skele.rotation_euler = (0, 0, 0)
                attach(cece_container, anim_container)

                for f in anim_skele.animation_data.action.fcurves:
                    for kp in f.keyframe_points:
                        kp.co[0] += int(target_framerate * cece.time.start)
        
        for var, var_data in variables.items():
            if not settings.import_CECE:
                continue
            if var_data[0] != 'entity_child':
                continue
            var_id, cece_container, cece_entity = var_data
            if cece_entity['owm.entity.child.var'] not in show_ents:
                pass
                # cycles dies at init time when this is used. todo: why
                # cece_container.scale = (0, 0, 0)
                
                # this is using keyframes
##                act = bpy.context.view_layer.objects.active
##                if bpy.context.object.mode != 'OBJECT':
##                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
##                bpy.ops.object.select_all(action='DESELECT')
##                bpy.context.view_layer.objects.active = cece_container
##                cece_container.select = True
##                
##                frame = 0
##                end_frame = 0 # not used
##                
##                bpy.context.scene.frame_set(frame)
##                cece_container.scale = (0, 0, 0)
##                bpy.ops.anim.keyframe_insert_menu(type='Scaling')
##                bpy.context.scene.frame_set(1)
##                cece_container.select = False
##                bpy.context.view_layer.objects.active = act
                
        
def read(settings, existing_parent=None):
    root, file = os.path.split(settings.filename)

    data = read_oweffect.read(settings.filename)
    if data is None: return None

    if type(data) == owm_types.OWAnimFile:
        pool = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(data.filename)))))
        t = None
        if settings.force_fps:
            t = settings.target_fps
        ret = process(settings, data, pool, existing_parent, t, None, {})
        
        if existing_parent is None and settings.create_camera:
            bpy.ops.object.add(type='CAMERA')
            cam = bpy.context.active_object
            cam.name = 'AnimationCamera {}'.format(os.path.splitext(os.path.basename(data.anim_path))[0])
            transform = attach(ret[1], cam)
            transform.subtarget = 'bone_007D'
            cam.rotation_euler = (0, math.radians(180), 0)
            cam.parent = ret[0]
            # this value looks close?
            cam.data.lens = 24
        return ret

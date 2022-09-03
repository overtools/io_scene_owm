import os

from . import read_owmap
from . import import_owmdl
from . import import_owmat
from . import import_owentity
from . import bpyhelper
from . import owm_types
from mathutils import *
import math
import bpy, bpy_extras, mathutils

sets = None

acm = bpy_extras.io_utils.axis_conversion(from_forward='-Z', from_up='Y').to_4x4()


def pos_matrix(pos):
    global acm
    posMtx = mathutils.Matrix.Translation(pos)
    mtx = acm @ posMtx
    return mtx.to_translation()


link_queue = []

parents = {}
children = {}

def buildRelationships():
    for obj in bpy.context.scene.objects:
        if obj.name not in parents:
            if obj.parent is None: continue
            parents[obj.name] = obj.parent.name
    for obj in parents:
        if parents[obj] not in children:
            children[parents[obj]] = []
        children[parents[obj]].append(obj)

def destroyRelationships():
    global parents, children
    parents = {}
    children = {}

def copy(obj, parent, linked: bool = False):
    if obj is None: return None
    new_obj = obj.copy()
    if obj.data is not None:
        if linked:
            new_obj.data = obj.data
        else:
            new_obj.data = obj.data.copy()

        if 'OWM Skeleton' in new_obj.modifiers:
            mod = new_obj.modifiers['OWM Skeleton']
            mod.object = parent
    new_obj.parent = parent
    link_queue.append(new_obj)
    try:
        for child in children[obj.name]:
            copy(bpy.data.objects[child], new_obj, linked)
    except KeyError:
        pass # screw that
    return new_obj


def remove(obj):
    if obj.name in children:
        for child in children[obj.name]:
            remove(bpy.data.objects[child])
        del children[obj.name]
    try:
        bpyhelper.scene_unlink(obj)
    except Exception as e:
        print('[import_owmap]: error removing object: {}'.format(bpyhelper.format_exc(e)))


def xpzy(vec):
    return vec[0], vec[2], vec[1]


def wxzy(vec):
    return vec[3], vec[0], -vec[2], vec[1]


def progress_update(total, progress, nextFile):
    if owm_types.LOG_ALOT:
        print('%d/%d (%d%%) %s' % (progress, total, progress / total * 100, nextFile))
    bpy.context.window_manager.progress_update(progress)

def hide_recursive(obj):
    obj.hide_viewport = obj.hide_render = True
    for child in obj.children:
        hide_recursive(child)

def import_mdl(mdls):
    try:
        obj = None
        if mdls.filename.endswith(".owentity"):
            mdls.importEmpties = True
            mdls.importSkeleton = True
            obj = import_owentity.read(mdls, True)
            #     0         1            2       3          4
            #     root,    armature,  meshes,    empties,   data
            obj = (obj[0], obj[2][1], obj[2][2], obj[2][3], obj[2][4])
            if obj[1] is None:
                obj[0].rotation_euler = (math.radians(90), 0, 0) # reeee
                if len(obj[3]) > 0 and obj[3][0] is not None:
                    obj[3][0].rotation_euler = (0, 0, 0) # :ahh:
        else:
            obj = import_owmdl.read(mdls, None)
            obj[0].rotation_euler = (math.radians(90), 0, 0)
        wrapObj = bpy.data.objects.new(obj[0].name + '_WRAP', None)
        wrapObj.hide_viewport = True
        obj[0].parent = wrapObj
        bpyhelper.scene_link(wrapObj)
        return wrapObj, obj
    except Exception as e:
        print('[import_owmap]: error importing map object: {}'.format(bpyhelper.format_exc(e)))
        return None, None


def import_mat(path, prefix):
    try:
        return import_owmat.read(path, prefix)
    except Exception as e:
        print('[import_owmap]: error importing map: {}'.format(bpyhelper.format_exc(e)))
        return None


def read(settings, importObjects=False, importDetails=True, importPhysics=False, light_settings=owm_types.OWLightSettings(), removeCollision=True, importSound=True, link_objects: bool = False):
    global sets, link_queue
    bpyhelper.LOCK_UPDATE = True
    sets = settings

    root, file = os.path.split(settings.filename)

    data = read_owmap.read(settings.filename)
    if not data: return None

    name = data.header.name
    if len(name) == 0:
        name = os.path.splitext(file)[0]
    rootObj = bpy.data.objects.new(name, None)
    rootObj.hide_viewport = True
    bpyhelper.scene_link(rootObj)

    wm = bpy.context.window_manager
    prog = 0
    total = 0
    if importPhysics: total += 1
    if importObjects:
        for ob in data.objects:
            total += len(ob.entities)
            for ent in ob.entities:
                total += len(ent.records)
    if importDetails:
        total += len(data.details) * 3
    if light_settings.enabled:
        total += len(data.lights)
    if importSound:
        total += len(data.sounds)
    wm.progress_begin(prog, total)

    matCache = {}

    collision_materials = {"000000000794", "0000000048EF", "0000000034A3","000000000797","0000000007A2","0000000007A0","0000000007C0","0000000007A1"}#blozzord pls

    if importObjects:
        globObj = bpy.data.objects.new(name + '_OBJECTS', None)
        globObj.hide_viewport = True
        globObj.parent = rootObj
        bpyhelper.scene_link(globObj)
        for ob in data.objects:
            obpath = ob.model
            if not os.path.isabs(obpath):
                obpath = bpyhelper.normpath('%s/%s' % (root, obpath))
            if not os.path.isfile(obpath): continue
            progress_update(total, prog, obpath)

            obn = os.path.splitext(os.path.basename(obpath))[0]

            mutated = settings.mutate(obpath)
            mutated.importMaterial = False

            obj, internal_obj = import_mdl(mutated)
            if obj is None:
                continue

            obnObj = bpy.data.objects.new(obn + '_COLLECTION', None)
            obnObj.hide_viewport = True
            obnObj.parent = globObj
            bpyhelper.scene_link(obnObj)
            buildRelationships()

            for idx, ent in enumerate(ob.entities):
                matpath = ent.material
                if not os.path.isabs(matpath):
                    matpath = bpyhelper.normpath('%s/%s' % (root, matpath))

                mat = None
                hideModel = False
                if settings.importMaterial and bpyhelper.valid_path(ent.material):
                    if matpath not in matCache:
                        mat = import_owmat.read(matpath, '%s:%X_' % (name, idx))
                        matCache[matpath] = mat
                    else:
                        mat = matCache[matpath]
                if mat != None and removeCollision:
                    ids = [True for mat in mat[1].values() if mat.name in collision_materials]
                    if len(ids) > 0:
                        hideModel=True

                prog += 1

                if hideModel:
                    continue

                matObj = bpy.data.objects.new(os.path.splitext(os.path.basename(matpath))[0], None)
                matObj.hide_viewport = True
                matObj.parent = obnObj
                bpyhelper.scene_link(matObj)

                import_owmdl.bindMaterialsUniq(internal_obj[2], internal_obj[4], mat)
                # eobj = copy(obj, None, link_objects)

                for idx2, rec in enumerate(ent.records):
                    progress_update(total, prog, obpath)
                    nobj = copy(obj, matObj, link_objects)
                    nobj.location = pos_matrix(rec.position)
                    nobj.rotation_euler = Quaternion(wxzy(rec.rotation)).to_euler('XYZ')
                    nobj.scale = xpzy(rec.scale)
                    if hideModel:
                        hide_recursive(nobj)
                    prog += 1
            remove(obj)

    if importDetails:
        globDet = bpy.data.objects.new(name + '_DETAILS', None)
        globDet.hide_viewport = True
        globDet.parent = rootObj
        bpyhelper.scene_link(globDet)
        objCache = {}
        objCol = []
        for idx, ob in enumerate(data.details):
            obpath = ob.model
            prog += 1
            if not os.path.isabs(obpath):
                obpath = bpyhelper.normpath('%s/%s' % (root, obpath))
            if not os.path.isfile(obpath):
                continue
            progress_update(total, prog, obpath)
            cacheKey = obpath
            if settings.importMaterial and bpyhelper.valid_path(ob.material):
                cacheKey = cacheKey + ob.material
            if cacheKey in objCache:
                continue

            obn = os.path.splitext(os.path.basename(obpath))[0]
            if not importPhysics and obn == 'physics':
                continue

            mutated = settings.mutate(obpath)
            mutated.importMaterial = False

            mdl, internal_obj = import_mdl(mutated)
            if mdl is None:
                continue

            matpath = ob.material
            if not os.path.isabs(matpath):
                matpath = bpyhelper.normpath('%s/%s' % (root, matpath))

            mat = None
            hideModel = False
            if settings.importMaterial and bpyhelper.valid_path(ob.material):
                if matpath not in matCache:
                    mat = import_owmat.read(matpath, '%s:%X_' % (name, idx))
                    matCache[matpath] = mat
                else:
                    mat = matCache[matpath]
                if removeCollision:
                    ids = [True for mat in mat[1].values() if mat.name in collision_materials]
                    if len(ids) > 0:
                        hideModel=True
            if hideModel:
                objCol.append(cacheKey)
                #continue

            import_owmdl.bindMaterialsUniq(internal_obj[2], internal_obj[4], mat)

            objCache[cacheKey] = mdl
        buildRelationships()
        for obj in objCol:
            try:
                remove(objCache[cacheKey])
                del objCache[cacheKey]
            except:
                pass #shrug
        objCol=set(objCol)
        for ob in data.details:
            obpath = ob.model
            prog += 1
            if not os.path.isabs(obpath):
                obpath = bpyhelper.normpath('%s/%s' % (root, obpath))
            cacheKey = obpath
            progress_update(total, prog, obpath)
            if settings.importMaterial and bpyhelper.valid_path(ob.material):
                cacheKey = cacheKey + ob.material
            if cacheKey not in objCache or objCache[cacheKey] is None or cacheKey in objCol:
                continue

            objnode = copy(objCache[cacheKey], globDet, link_objects)
            objnode.location = pos_matrix(ob.position)
            objnode.rotation_euler = Quaternion(wxzy(ob.rotation)).to_euler('XYZ')
            objnode.scale = xpzy(ob.scale)

        for ob in objCache:
            prog += 1
            remove(objCache[ob])
            progress_update(total, prog, ob)

    for obj in link_queue:
        bpyhelper.scene_link(obj)
    link_queue = []
    destroyRelationships()

    LIGHT_MAP = ['POINT', 'FRUSTUM', 'NONE']

    if light_settings.enabled:
        globLight = bpy.data.objects.new(name + '_LIGHTS', None)
        globLight.hide_viewport = True
        globLight.parent = rootObj
        bpyhelper.scene_link(globLight)
        for light in data.lights:
            prog += 1
            is_spot = light.fov > 0
            if light.ex[6] >= 2:
                print("[owmap] Light is type NONE!?")
            lamp_data = bpy.data.lights.new(name='%s_%s' % (name, LIGHT_MAP[min([2, light.ex[6]])]), type='SPOT' if is_spot else 'POINT')
            lamp_ob = bpy.data.objects.new(name=name, object_data=lamp_data)
            bpyhelper.scene_link(lamp_ob)
            lamp_ob.location = pos_matrix(light.position)
            if light.ex[6] == 1:
                print("[owmap] warning: importing frustum light at X: %f, Y: %f, Z: %f" % (lamp_ob.location.x, lamp_ob.location.y, lamp_ob.location.z))
            lamp_ob.rotation_euler = Quaternion(wxzy(light.rotation)).to_euler('XYZ')
            lamp_ob.rotation_euler.x -= 1.5708
            light_scale = light.ex[light_settings.sizeIndex % len(light.ex)]
            lamp_ob.scale = (light_scale, light_scale, light_scale)
            lamp_col = Color(light.color)
            lamp_col.v *= light_settings.adjuistValues['VALUE']
            lamp_data.cycles.use_multiple_importance_sampling = light_settings.multipleImportance
            lamp_str = light_settings.adjuistValues['STRENGTH']
            if is_spot:
                lamp_data.spot_size = math.radians(light.fov)
                lamp_data.spot_blend = light.ex[light_settings.spotIndex % len(light.ex)]
            if light_settings.useStrength:
                lamp_str = light_settings.adjuistValues['STRENGTH'] * light.ex[light_settings.index % len(light.ex)]
            lamp_data.use_nodes = True
            lamp_data.shadow_soft_size = light_settings.bias
            enode = lamp_data.node_tree.nodes.get('Emission')
            enode.inputs.get('Color').default_value = (lamp_col.r, lamp_col.g, lamp_col.b, 1.0)
            enode.inputs.get('Strength').default_value = lamp_str
            lamp_ob.parent = globLight
            progress_update(total, prog, "Lamp")

    if importSound:
        globSound = bpy.data.objects.new(name + '_SOUNDS', None)
        globSound.hide_viewport = True
        globSound.parent = rootObj
        bpyhelper.scene_link(globSound)
        for sound in data.sounds:
            prog += 1
            soundWrap = bpy.data.objects.new(name = '%s_SPEAKER_WRAP' % (name), object_data = None)
            soundWrap.parent = globSound
            soundWrap.hide_viewport = True
            soundWrap.location = pos_matrix(sound.position)
            bpyhelper.scene_link(soundWrap)
            for soundFile in sound.sounds:
                print("[import_owmap] %s" % (soundFile))
                speaker_data = bpy.data.speakers.new(name = '%s_SPEAKER' % (name))
                speaker_ob = bpy.data.objects.new(name = '%s_SPEAKER' % (name), object_data=speaker_data)
                speaker_ob.parent = soundWrap
                speaker_data.sound = bpy.data.sounds.load(soundFile, check_existing=True)
                speaker_data.volume = 0.7
                speaker_data.attenuation = 0.3
                bpyhelper.scene_link(speaker_ob)
            progress_update(total, prog, "Sound")

    wm.progress_end()
    bpyhelper.deselect_all()
    print('Finished loading map')
    bpyhelper.LOCK_UPDATE = False
    bpyhelper.scene_update()

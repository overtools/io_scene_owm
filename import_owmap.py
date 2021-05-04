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

def copy(obj, parent,original=True,col=None):
    if obj is None: return None
    new_obj = obj.copy()
    if obj.data is not None:
        if original is True:
            new_obj.data = obj.data.copy()
        
        if obj.get('owm.mesh.armature',0) is 1:
            mod = new_obj.modifiers['OWM Skeleton']
            mod.object = parent
    new_obj.parent = parent
    col.objects.link(new_obj)
    if original:
        children[new_obj.name] = []
    for child in children.get(obj.name,[]):
        new_child = copy(bpy.data.objects[child], new_obj,original,col)
        if original:
            children[new_obj.name].append(new_child.name)
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
                    obj[3][0].rotation_euler = (0, 0, 0) # :ahh: TODO check if this causes boat crosses
            return obj
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


def read(settings, importObjects=False, importDetails=True, importPhysics=False, light_settings=owm_types.OWLightSettings(), removeCollision=True, importSound=True):
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

    instancecols = True # TODO option checkbox

    if importObjects:
        globObj = bpy.data.collections.new(name + '_OBJECTS')
        cols = []
        to_exclude = []
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

            obnObj = bpy.data.collections.new(obn + '_COLLECTION')
            cols.append(obnObj)
            buildRelationships()

            for idx, ent in enumerate(ob.entities):
                matpath = ent.material
                if not os.path.isabs(matpath):
                    matpath = bpyhelper.normpath('%s/%s' % (root, matpath))

                
                mat = None
                hideModel = False
                if settings.importMaterial and len(ent.material) > 3:
                    if matpath not in matCache:
                        mat = import_owmat.read(matpath, '%s:%X_' % (name, idx))
                        matCache[matpath] = mat
                    else:
                        mat = matCache[matpath]
                if mat != None and removeCollision:
                    for tex_name, tex in mat[0].items():
                        if tex_name == '000000001B8D' or tex_name == '000000001BA4': # Is this broken?
                            hideModel = True

                prog += 1

                if instancecols:
                    matObj = bpy.data.collections.new(os.path.splitext(os.path.basename(matpath))[0])
                    to_exclude.append(matObj.name)
                    obnObj.children.link(matObj)
                else:
                    matObj = bpy.data.objects.new(os.path.splitext(os.path.basename(matpath))[0], None)
                    matObj.hide_viewport = True
                    bpyhelper.scene_link(matObj,obnObj)
                
                import_owmdl.bindMaterialsUniq(internal_obj[2], internal_obj[4], mat)
                # eobj = copy(obj, None)

                is_orig=True
                cobj = obj
                for idx2, rec in enumerate(ent.records):
                    progress_update(total, prog, obpath)
                    if instancecols:
                        if is_orig:
                            cobj = copy(cobj,None,True,matObj)
                        nobj = bpyhelper.instance_collection(matObj, matObj.name,obnObj)
                    else:
                        nobj = copy(cobj, matObj,is_orig,obnObj)
                    nobj.location = pos_matrix(rec.position)
                    nobj.rotation_euler = Quaternion(wxzy(rec.rotation)).to_euler('XYZ')
                    nobj.scale = xpzy(rec.scale)
                    if is_orig:
                        cobj=nobj
                    if hideModel:
                        hide_recursive(nobj)
                    is_orig=False
                    prog += 1
            remove(obj)

    if importDetails:
        globDet = bpy.data.collections.new(name + '_DETAILS')
        objCache = {}
        origObjs = []
        for idx, ob in enumerate(data.details):
            obpath = ob.model
            prog += 1
            if not os.path.isabs(obpath):
                obpath = bpyhelper.normpath('%s/%s' % (root, obpath))
            if not os.path.isfile(obpath):
                continue
            progress_update(total, prog, obpath)
            cacheKey = os.path.splitext(os.path.basename(obpath))[0]
            matpath = ob.material
            matkey = os.path.splitext(os.path.basename(matpath))[0]
            if settings.importMaterial and bpyhelper.valid_path(ob.material):
                cacheKey = cacheKey + matkey
            if cacheKey in objCache:
                continue

            obn = os.path.splitext(os.path.basename(obpath))[0]
            if not importPhysics and obn == 'physics':
                continue

            mutated = settings.mutate(obpath)
            mutated.importMaterial = False

            internal_obj = import_mdl(mutated)

            if not os.path.isabs(matpath):
                matpath = bpyhelper.normpath('%s/%s' % (root, matpath))

            mat = None
            hideModel = False
            if settings.importMaterial and bpyhelper.valid_path(ob.material):
                if matkey not in matCache:
                    mat = import_owmat.read(matpath, '%s:%X_' % (name, idx))
                    matCache[matkey] = mat
                else:
                    mat = matCache[matkey]
                if removeCollision:
                    for tex_name, tex in mat[0].items():
                        if tex_name == '000000001B8D' or tex_name == '000000001BA4':
                            hideModel = True
            if hideModel:
                hide_recursive(internal_obj[0])

            import_owmdl.bindMaterialsUniq(internal_obj[2], internal_obj[4], mat)

            if instancecols:
                col = bpy.data.collections.new(internal_obj[0].name + '_COLLECTION')
                objwrap = bpy.data.collections.new(internal_obj[0].name + '_WRAP')
                objCache[cacheKey] = [internal_obj[0], col, objwrap, True,internal_obj[0]]
                col.children.link(objwrap)
                to_exclude.append(objwrap.name)
            else:
                objCache[cacheKey] = [internal_obj[0],bpy.data.collections.new(internal_obj[0].name + '_COLLECTION')]
            origObjs.append(internal_obj[0])
        buildRelationships()

        for ob in data.details:
            obpath = ob.model
            prog += 1
            if not os.path.isabs(obpath):
                obpath = bpyhelper.normpath('%s/%s' % (root, obpath))
            cacheKey = os.path.splitext(os.path.basename(obpath))[0]
            progress_update(total, prog, obpath)
            if settings.importMaterial and bpyhelper.valid_path(ob.material):
                cacheKey = cacheKey + os.path.splitext(os.path.basename(ob.material))[0]
            #print(cacheKey)
            if cacheKey not in objCache or objCache[cacheKey] is None:
                continue

            if instancecols:
                cached = objCache[cacheKey]
                if cached[3]:
                    cached[3] = False
                    cached[0] = copy(cached[0], None, True, cached[2])
                objnode = bpyhelper.instance_collection(cached[2], cached[0].name,cached[1])
            else:
                objnode = copy(objCache[cacheKey][0], None, False, objCache[cacheKey][1])
            objnode.location = pos_matrix(ob.position)
            rot = Quaternion(wxzy(ob.rotation)).to_euler('XYZ')
            objnode.rotation_euler.rotate(rot)
            objnode.scale = xpzy(ob.scale)
            is_orig=False

        for ob in origObjs:
            prog += 1
            remove(ob)
            progress_update(total, prog, "")


    for ob in cols:
        bpy.data.collections[name + '_OBJECTS'].children.link(ob)
    if importDetails:
        for ob in objCache:
            bpy.data.collections[name + '_DETAILS'].children.link(objCache[ob][1])
        bpy.data.collections["Collection"].children.link(bpy.data.collections[name + '_DETAILS']) # TODO get active collection or something
    bpy.data.collections["Collection"].children.link(bpy.data.collections[name + '_OBJECTS'])

    for obj in link_queue: # still needed?
        bpyhelper.scene_link(obj)
    link_queue = []
    bpyhelper.exclude_collections(to_exclude)
    destroyRelationships()
    LIGHT_MAP = ['SUN', 'SPOT', 'POINT']

    if light_settings.enabled: #TODO make collections for these
        globLight = bpy.data.objects.new(name + '_LIGHTS', None)
        globLight.hide_viewport = True
        globLight.parent = rootObj
        bpyhelper.scene_link(globLight)
        for light in data.lights:
            prog += 1
            if not light_settings.enabledTypes[light.type]:
                continue
            # print('light, fov: %s, type: %s (%d%%)' % (light.fov, light.type, (total_C/total) * 100))
            lamp_data = bpy.data.lights.new(name='%s_%s' % (name, LIGHT_MAP[light.type]), type=LIGHT_MAP[light.type])
            lamp_ob = bpy.data.objects.new(name='%s_%s' % (name, LIGHT_MAP[light.type]), object_data=lamp_data)
            bpyhelper.scene_link(lamp_ob)
            lamp_ob.location = pos_matrix(light.position)
            lamp_ob.rotation_euler = Quaternion(wxzy(light.rotation)).to_euler('XYZ')
            light_scale = light.ex[light_settings.sizeIndex % len(light.ex)]
            lamp_ob.scale = (light_scale, light_scale, light_scale)
            lamp_col = Color(light.color)
            lamp_col.v *= light_settings.adjuistValues['VALUE']
            lamp_data.cycles.use_multiple_importance_sampling = light_settings.multipleImportance
            lamp_str = light_settings.adjuistValues['STRENGTH']
            if lamp_data.type == 'SPOT':
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

import os

from . import read_owmap
from . import import_owmdl
from . import import_owmat
from . import owm_types
from . import bpyhelper
from mathutils import *
import math
import bpy, bpy_extras, mathutils

sets = None

acm = bpy_extras.io_utils.axis_conversion(from_forward='-Z', from_up='Y').to_4x4()

def pos_matrix(pos):
    global acm
    posMtx = mathutils.Matrix.Translation(pos)
    mtx = acm * posMtx
    return mtx.to_translation()

def copy(obj, parent):
    if obj == None: return None
    new_obj = obj.copy()
    if obj.data != None:
        new_obj.data == obj.data.copy()
    new_obj.parent = parent
    bpyhelper.scene_link(new_obj)
    for child in obj.children:
        copy(child, new_obj)
    return new_obj

def remove(obj):
    for child in obj.children:
        remove(child)
    try:
        bpyhelper.scene_unlink(obj)
    except Exception as e: print(e)

def xpzy(vec):
    return (vec[0], vec[2], vec[1])

def wxzy(vec):
    return (vec[3], vec[0], -vec[2], vec[1])

def progress_update(total, progress):
    # print("%d/%d (%d%%)" % (progress, total, progress / total * 100))
    bpy.context.window_manager.progress_update(progress)

def import_mdl(mdls):
    try:
        obj = import_owmdl.read(mdls, None)
        obj[0].rotation_euler = (math.radians(90), 0, 0)
        wrapObj = bpy.data.objects.new(obj[0].name + '_WRAP', None)
        wrapObj.hide = True
        obj[0].parent = wrapObj
        bpyhelper.scene_link(wrapObj)
        return (wrapObj, obj[2], obj[4])
    except Exception as e:
        print(e)
        return None

def import_mat(path, prefix, norm, efct):
    try:
        return import_owmat.read(path, prefix, norm, efct)
    except Exception as e:
        print(e)
        return None

def read(settings, importObjects = False, importDetails = True, importPhysics = False, importLights = True, importLightType = [True, True, True]):
    global sets
    sets = settings

    root, file = os.path.split(settings.filename)

    data = read_owmap.read(settings.filename)
    if not data: return None

    name = data.header.name
    if len(name) == 0:
        name = os.path.splitext(file)[0]
    rootObj = bpy.data.objects.new(name, None)
    rootObj.hide = True
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
    if importDetails: total += len(data.details) * 3
    if importLights: total += len(data.lights)
    wm.progress_begin(prog, total)

    if importObjects:
        globObj = bpy.data.objects.new(name + '_OBJECTS', None)
        globObj.hide = True
        globObj.parent = rootObj
        bpyhelper.scene_link(globObj)
        for ob in data.objects:
            obpath = ob.model
            if not os.path.isabs(obpath):
                obpath = os.path.normpath('%s/%s' % (root, obpath))
            if not os.path.isfile(obpath): continue

            obn = os.path.splitext(os.path.basename(obpath))[0]

            mutated = settings.mutate(obpath)
            mutated.importMaterial = False

            obj = import_mdl(mutated)
            if obj == None: continue
            objData = obj[2]
            objMeshData = obj[1]
            obj = obj[0]
            
            obnObj = bpy.data.objects.new(obn + '_COLLECTION', None)
            obnObj.hide = True
            obnObj.parent = globObj
            bpyhelper.scene_link(obnObj)

            for idx, ent in enumerate(ob.entities):
                prog += 1
                matpath = ent.material
                if not os.path.isabs(matpath):
                    matpath = os.path.normpath('%s/%s' % (root, matpath))
                    
                mat = None
                if settings.importMaterial:
                    mat = import_owmat(matpath, os.path.splitext(os.path.basename(matpath))[0] + '_', settings.importTexNormal, settings.importTexEffect)
                    
                matObj = bpy.data.objects.new(os.path.splitext(os.path.basename(matpath))[0], None)
                matObj.hide = True
                matObj.parent = obnObj
                bpyhelper.scene_link(matObj)
                
                import_owmdl.bindMaterialsUniq(objMeshData, objData, mat)
                eobj = copy(obj, None)
                
                for idx2, rec in enumerate(ent.records):
                    prog += 1
                    nobj = copy(eobj, matObj)
                    nobj.location = pos_matrix(rec.position)
                    nobj.rotation_euler = Quaternion(wxzy(rec.rotation)).to_euler('XYZ')
                    nobj.scale = xpzy(rec.scale)
                    progress_update(total, prog)
                progress_update(total, prog)
                remove(eobj)
            remove(obj)

    if importDetails:
        globDet = bpy.data.objects.new(name + '_DETAILS', None)
        globDet.hide = True
        globDet.parent = rootObj
        bpyhelper.scene_link(globDet)
        objCache = {}
        for ob in data.details:
            obpath = ob.model
            prog += 1
            if not os.path.isabs(obpath):
                obpath = os.path.normpath('%s/%s' % (root, obpath))
            if not os.path.isfile(obpath): continue
            cacheKey = obpath
            if settings.importMaterial and len(ob.material) > 0:
                cacheKey = cacheKey + ob.material
            if obpath in objCache: continue

            obn = os.path.splitext(os.path.basename(obpath))[0]
            if not importPhysics and obn == 'physics':
                continue

            mutated = settings.mutate(obpath)
            mutated.importMaterial = False

            mdl = import_mdl(mutated)
            if mdl == None: continue
            
            mat = None
            
            if settings.importMaterial and len(ob.material) > 0:
                matpath = ent.material
                if not os.path.isabs(matpath):
                    matpath = os.path.normpath('%s/%s' % (root, matpath))
                if settings.importMaterial:
                    mat = import_owmat(matpath, os.path.splitext(os.path.basename(ob.material))[0] + '_', settings.importTexNormal, settings.importTexEffect)
                    
            if mat is not None:
                import_owmdl.bindMaterialsUniq(mdl[1], mdl[2], mat)

            objCache[cacheKey] = mdl[0]
            progress_update(total, prog)

        for ob in data.details:
            obpath = ob.model
            prog += 1
            if not os.path.isabs(obpath):
                obpath = os.path.normpath('%s/%s' % (root, obpath))
            cacheKey = obpath
            if settings.importMaterial and len(ob.material) > 0:
                cacheKey = cacheKey + ob.material
            if cacheKey not in objCache or objCache[cacheKey] == None: continue

            objnode = copy(objCache[cacheKey], globDet)
            objnode.location = pos_matrix(ob.position)
            objnode.rotation_euler = Quaternion(wxzy(ob.rotation)).to_euler('XYZ')
            objnode.scale = xpzy(ob.scale)
            progress_update(total, prog)

        for ob in objCache:
            prog += 1
            remove(objCache[ob])
            progress_update(total, prog)

    LIGHT_MAP = ['SUN', 'SPOT', 'POINT']

    if importLights:
        globLight = bpy.data.objects.new(name + '_LIGHTS', None)
        globLight.hide = True
        globLight.parent = rootObj
        bpyhelper.scene_link(globLight)
        for light in data.lights:
            prog += 1
            if not importLightType[light.type]: continue
            # print("light, fov: %s, type: %s (%d%%)" % (light.fov, light.type, (total_C/total) * 100))
            lamp_data = bpy.data.lamps.new(name = "%s_%s" % (name, LIGHT_MAP[light.type]), type = LIGHT_MAP[light.type])
            lamp_ob = bpy.data.objects.new(name = "%s_%s" % (name, LIGHT_MAP[light.type]), object_data = lamp_data)
            bpyhelper.scene_link(lamp_ob)
            lamp_ob.location = pos_matrix(light.position)
            lamp_ob.rotation_euler = Quaternion(wxzy(light.rotation)).to_euler('XYZ')
            lamp_data.color = light.color
            if lamp_data.type == 'SPOT':
                lamp_data.spot_size = math.radians(light.fov)
            lamp_ob.parent = globLight
            progress_update(total, prog)
    wm.progress_end()
    print("Finished loading map")
    bpy.context.scene.update()

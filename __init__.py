import bpy

bl_info = {
    'name': 'OWM Import',
    'author': 'overtools',
    'version': (3, 2, 5),
    'blender': (3, 4, 0),
    'location': 'File > Import > OWM',
    'description': 'Import exported assets from TankLib or DataTool',
    'wiki_url': '',
    'tracker_url': 'https://github.com/overtools/io_scene_owm/issues',
    "support": "COMMUNITY",
    'category': 'Import-Export'
}

modules = ["datatypes","importer","readers","ui","TextureMap"]
if "sys" in locals():
    from importlib import reload 
    for module in modules:
        module = __package__+"."+module
        if module in sys.modules:
            reload(sys.modules[module])
        else:
            import_module("."+module, __package__)
else:
    import sys
    from importlib import import_module
    for module in modules:
        import_module("."+module, __package__)

if bpy.app.version < bl_info["blender"]:
    sys.tracebacklimit = 0
    raise SystemExit("This addon is not compatible with Blender {}.{}.{}. Update to the latest Blender version or at least {}.{}.{}.".format(*bpy.app.version, *bl_info["blender"]))

def register():
    ui.BlenderManager.register()
    ui.LibraryHandler.addonVersion = ".".join([str(i) for i in bl_info['version']])


def unregister():
    ui.BlenderManager.unregister()


if __name__ == '__main__':
    register()

import addon_utils
import sys

# legacy info for publishing as addon only
# loading from extension will ignore this
# please keep in sync
bl_info = {
    'name': 'OWM Import',
    'author': 'overtools',
    'version': (3, 2, 7),
    'blender': (3, 5, 0),
    'location': 'File > Import > Overtools',
    'description': 'Import exported assets from DataTool or TankLib',
    'wiki_url': '',
    'tracker_url': 'https://github.com/overtools/io_scene_owm/issues',
    "support": "COMMUNITY",
    'category': 'Import-Export'
}

from . import ui

def register():
    bl_info = addon_utils.module_bl_info(sys.modules[__package__])
    ui.LibraryHandler.addonVersion = ".".join([str(i) for i in bl_info['version']])

    ui.BlenderManager.register()

def unregister():
    ui.BlenderManager.unregister()


if __name__ == '__main__':
    register()

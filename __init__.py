import bpy

bl_info = {
    'name': 'OWM Import',
    'author': 'overtools',
    'version': (3, 2, 6),
    'blender': (3, 5, 0),
    'location': 'File > Import > Overtools',
    'description': 'Import exported assets from DataTool or TankLib',
    'wiki_url': '',
    'tracker_url': 'https://github.com/overtools/io_scene_owm/issues',
    "support": "COMMUNITY",
    'category': 'Import-Export'
}

from . import datatypes
from . import importer
from . import readers
from . import ui
from . import TextureMap

def register():
    ui.BlenderManager.register()
    ui.LibraryHandler.addonVersion = ".".join([str(i) for i in bl_info['version']])


def unregister():
    ui.BlenderManager.unregister()


if __name__ == '__main__':
    register()

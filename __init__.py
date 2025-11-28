# legacy info for publishing as addon only
# loading from extension will ignore this
# please keep in sync
bl_info = {
    'name': 'OWM Import',
    'author': 'overtools',
    'version': (3, 2, 8),
    'blender': (3, 5, 0),
    'location': 'File > Import > Overtools',
    'description': 'Import files from the Overwatch extraction tools (DataTool)',
    'wiki_url': '',
    'tracker_url': 'https://github.com/overtools/io_scene_owm/issues',
    "support": "COMMUNITY",
    'category': 'Import-Export'
}

from . import ui

def register():
    ui.BlenderManager.register()

def unregister():
    ui.BlenderManager.unregister()


if __name__ == '__main__':
    register()

rld = False

if 'bpy' in locals():
    import imp
    rld = True

from . import bin_ops
from . import import_owmap
from . import import_owmdl
from . import import_owmat
from . import import_owentity
from . import import_oweffect
from . import owm_types
from . import read_owmap
from . import read_owmdl
from . import read_owmat
from . import read_owentity
from . import read_oweffect
from . import bpyhelper
from . import manager


bl_info = {
    'name': 'OWM Import',
    'author': 'Overtools Community',
    'version': (2, 2, 4),
    'blender': (2, 81, 0),
    'location': 'File > Import > OWM',
    'description': 'Import TankLib/DataTool OWM files',
    'warning': '',
    'wiki_url': '',
    'tracker_url': 'https://github.com/overtools/io_scene_owm/issues',
    'category': 'Import-Export'
}

if rld:
    imp.reload(bin_ops)
    imp.reload(import_owmap)
    imp.reload(import_owmdl)
    imp.reload(import_owmat)
    imp.reload(import_owentity)
    imp.reload(import_oweffect)
    imp.reload(owm_types)
    imp.reload(read_owmap)
    imp.reload(read_owmdl)
    imp.reload(read_owmat)
    imp.reload(read_owentity)
    imp.reload(read_oweffect)
    imp.reload(bpyhelper)
    imp.reload(manager)

import bpy

def register():
    manager.register()

def unregister():
    manager.unregister()

if __name__ == '__main__':
    register()

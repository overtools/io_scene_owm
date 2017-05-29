bl_info = {
    "name": "OWM Import",
    "author": "dynaomi",
    "version": (1, 0, 7),
    "blender": (2, 74, 0),
    "location": "File > Import > OWM",
    "description": "Import Overwatch-Toolchain OWM files",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

rld = False

if "bpy" in locals():
    import imp
    rld = True

from . import bin_ops
from . import import_owmap
from . import import_owmdl
from . import import_owmat
from . import owm_types
from . import read_owmap
from . import read_owmdl
from . import read_owmat
from . import manager

if rld:
    imp.reload(bin_ops)
    imp.reload(import_owmap)
    imp.reload(import_owmdl)
    imp.reload(import_owmtl)
    imp.reload(owm_types)
    imp.reload(read_owmap)
    imp.reload(read_owmdl)
    imp.reload(read_owmtl)
    imp.reload(manager)

import bpy

def register():
    bpy.utils.register_module(__name__)
    manager.register()

def unregister():
    bpy.utils.unregister_module(__name__)
    manager.unregister()

if __name__ == '__main__':
    register()

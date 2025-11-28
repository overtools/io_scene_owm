import addon_utils
import sys

from ... import __package__ as base_package

def get_addon_version():
    bl_info = addon_utils.module_bl_info(sys.modules[base_package])
    return ".".join([str(i) for i in bl_info['version']])

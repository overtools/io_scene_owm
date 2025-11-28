import addon_utils
import sys

def get_addon_version():
    bl_info = addon_utils.module_bl_info(sys.modules[__package__])
    return ".".join([str(i) for i in bl_info['version']])
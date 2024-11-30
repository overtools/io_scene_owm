from datetime import datetime

import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy.utils import smpte_from_seconds
from bpy_extras.io_utils import ImportHelper

from . import LibraryHandler
from . import SettingTypes
from . import UIUtil
from ..importer import ImportAnimation
from ..readers import PathUtil


class ImportOWANIMCLIP(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_mesh.overtools2_animmclip'
    bl_label = 'Import Overtools Animation Clip'
    __doc__ = bl_label
    bl_options = {'UNDO'}

    filename_ext = '.owanimclip'
    filter_glob: StringProperty(
        default='*.owanimclip',
        options={'HIDDEN'},
    )

    directory: StringProperty(
        options={'HIDDEN'}
    )

    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    
    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if context.active_object.type == 'ARMATURE':
                return True
        self.poll_message_set('No Armature selected.\nBefore importing an animation you have to select the target Armature/Skeleton. (the black dots)')
            
    def invoke(self, context, event):
        if "owm.modelPath" in context.active_object:
            self.directory = PathUtil.pathRoot(context.active_object["owm.modelPath"])
        return super().invoke(context,event)

    def execute(self, context):
        t = datetime.now()
        files = [PathUtil.joinPath(self.directory, file.name) for file in self.files]
        ImportAnimation.init(files, context)

        UIUtil.log('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - t)))
        return {'FINISHED'}

    def draw(self, context):
        pass
        
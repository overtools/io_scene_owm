from datetime import datetime

import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy.utils import smpte_from_seconds
from bpy_extras.io_utils import ImportHelper

from . import LibraryHandler
from . import SettingTypes
from ..importer import model
from ..readers import PathUtil


class ImportOWMDL(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_mesh.overtools2_model'
    bl_label = 'Import Overtools Model'
    __doc__ = bl_label
    bl_options = {'UNDO'}

    filename_ext = '.owmdl'
    filter_glob: StringProperty(
        default='*.owmdl',
        options={'HIDDEN'},
    )

    directory: StringProperty(
        options={'HIDDEN'}
    )

    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    modelSettings: bpy.props.PointerProperty(type=SettingTypes.OWModelSettings)
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        LibraryHandler.load_data()
        t = datetime.now()
        files = [PathUtil.joinPath(self.directory, file.name) for file in self.files]
        model.init(files, self.modelSettings)
        print('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - t)))
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        SettingTypes.OWModelSettings.draw(self, self.modelSettings, col)

        col = layout.column(align=True)
        SettingTypes.OWModelSettings.draw_armature(self, self.modelSettings, col)
        
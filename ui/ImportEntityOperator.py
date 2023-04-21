from datetime import datetime

import bpy
from bpy.utils import smpte_from_seconds
from bpy_extras.io_utils import ImportHelper

from . import LibraryHandler
from . import SettingTypes
from ..importer import entity


class ImportOWENTITY(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_mesh.overtools2_entity'
    bl_label = 'Import Overtools Entity'
    __doc__ = bl_label
    bl_options = {'UNDO'}

    filename_ext = '.owentity'
    filter_glob: bpy.props.StringProperty(
        default='*.owentity',
        options={'HIDDEN'},
    )

    modelSettings: bpy.props.PointerProperty(type=SettingTypes.OWModelSettings)

    entitySettings: bpy.props.PointerProperty(type=SettingTypes.OWEntitySettings)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        t = datetime.now()
        entity.init(self.filepath, self.modelSettings, self.entitySettings)
        print('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - t)))
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        SettingTypes.OWEntitySettings.draw(self, self.entitySettings, col)

        col = layout.column(align=True)
        SettingTypes.OWModelSettings.draw(self, self.modelSettings, col)

        col = layout.column(align=True)
        SettingTypes.OWModelSettings.draw_armature(self, self.modelSettings, col)
        
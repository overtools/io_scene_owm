import cProfile as Profile
from datetime import datetime

import bpy
from bpy.utils import smpte_from_seconds
from bpy_extras.io_utils import ImportHelper

from . import LibraryHandler
from ..importer import owmap
from . import SettingTypes
from . import Preferences


class ImportOWMAP(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_mesh.overtools2_map'
    bl_label = 'Import Overtools Map'
    __doc__ = bl_label
    bl_options = {'UNDO'}

    filename_ext = '.owmap'
    filter_glob: bpy.props.StringProperty(
        default='*.owmap',
        options={'HIDDEN'},
    )

    modelSettings: bpy.props.PointerProperty(type=SettingTypes.OWModelSettings)

    mapSettings: bpy.props.PointerProperty(type=SettingTypes.OWMapSettings)

    entitySettings: bpy.props.PointerProperty(type=SettingTypes.OWEntitySettings)

    lightSettings: bpy.props.PointerProperty(type=SettingTypes.OWLightSettings)

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        # Defaults overrides
        self.modelSettings.importEmpties = False
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        LibraryHandler.load_data()
        t = datetime.now()
        owmap.init(self.filepath, self.mapSettings, self.modelSettings, self.lightSettings, self.entitySettings)
        print('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - t)))
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        SettingTypes.OWMapSettings.draw(self, self.mapSettings, col)

        col = layout.column(align=True)
        SettingTypes.OWModelSettings.draw(self, self.modelSettings, col)
        SettingTypes.OWModelSettings.draw_armature(self, self.modelSettings, col, False)
        if Preferences.getPreferences().devMode:
            col2 = col.column()
            col2.enabled = self.modelSettings.importMaterial
            col2.prop(self.modelSettings, 'saveMaterialDB')

        col = layout.column(align=True)
        SettingTypes.OWEntitySettings.draw(self, self.entitySettings, col)

        col = layout.column(align=True)
        SettingTypes.OWLightSettings.draw(self, self.lightSettings, col)
        
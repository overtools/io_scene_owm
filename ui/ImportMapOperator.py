import cProfile as Profile
from datetime import datetime

import bpy
from bpy.utils import smpte_from_seconds
from bpy_extras.io_utils import ImportHelper

from . import LibraryHandler
from ..importer import owmap
from . import SettingTypes


class ImportOWMAP(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_mesh.overtools2_map'
    bl_label = 'Import Overtools Map (owmap)'
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

    def menu_func(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'
        self.layout.operator(
            ImportOWMAP.bl_idname,
            text='Text Export Operator')

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
        col.label(text='Map')
        col.prop(self.mapSettings, 'importObjects')
        col.prop(self.mapSettings, 'importDetails')
        #col.prop(self.mapSettings, 'importLights')
        #col.prop(self.mapSettings, 'importSounds')
        col.prop(self.mapSettings, 'removeCollision')

        col = layout.column(align=True)
        col.label(text='Meshes')
        col.prop(self.modelSettings, 'importMaterial')
        col.prop(self.modelSettings, 'importColor')
        col.prop(self.modelSettings, 'importNormals')
        col.prop(self.modelSettings, 'autoSmoothNormals')
        col.prop(self.modelSettings, 'importEmpties')
        col.prop(self.modelSettings, 'importSkeleton')
        #col.prop(self.mapSettings, 'joinMeshes') #planned

        col = layout.column(align=True)
        col.label(text='Entities')
        col.prop(self.entitySettings, 'importChildren')

        """col = layout.column(align=True)
        col.label(text='Lights')
        col.enabled = self.mapSettings.importLights
        col.prop(self.lightSettings, 'multipleImportance')
        col.prop(self.lightSettings, 'useLightStrength')
        col.prop(self.lightSettings, 'shadowSoftBias')
        col.prop(self.lightSettings, 'adjustLightValue')
        col2 = col.column(align=True)
        col2.enabled = self.lightSettings.useLightStrength
        col2.prop(self.lightSettings, 'adjustLightStrength')"""
        
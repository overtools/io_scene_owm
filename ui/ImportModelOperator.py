from datetime import datetime

import bpy
from bpy.props import StringProperty
from bpy.utils import smpte_from_seconds
from bpy_extras.io_utils import ImportHelper

from . import LibraryHandler
from . import SettingTypes
from ..importer import model


class ImportOWMDL(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_mesh.overtools2_model'
    bl_label = 'Import Overtools Model (owmdl)'
    bl_options = {'UNDO'}

    filename_ext = '.owmdl'
    filter_glob: StringProperty(
        default='*.owmdl',
        options={'HIDDEN'},
    )

    modelSettings: bpy.props.PointerProperty(type=SettingTypes.OWModelSettings)

    def menu_func(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'
        self.layout.operator(
            ImportOWMDL.bl_idname,
            text='Text Export Operator')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        LibraryHandler.load_data()
        t = datetime.now()
        model.init(self.filepath, self.modelSettings)
        print('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - t)))
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text='Mesh')
        col.prop(self.modelSettings, 'importMaterial')
        col.prop(self.modelSettings, 'importColor')
        col.prop(self.modelSettings, 'importNormals')
        col.prop(self.modelSettings, 'autoSmoothNormals')
        col.prop(self.modelSettings, 'importEmpties')

        col = layout.column(align=True)
        col.label(text='Armature')
        col.prop(self.modelSettings, 'importSkeleton')

        # col = layout.column(align=True)
        # col.enabled = self.importMaterial  and bpy.context.scene.render.engine != 'CYCLES'
        # col.label(text = 'Material')
        
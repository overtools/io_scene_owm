from datetime import datetime

import bpy
from bpy.props import StringProperty
from bpy.utils import smpte_from_seconds
from bpy_extras.io_utils import ImportHelper
from ..importer import material

from . import LibraryHandler


class ImportOWMAT(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_material.overtools2_material'
    bl_label = 'Import Overtools Material (owmat)'
    bl_options = {'UNDO'}

    filename_ext = '.owmat'
    filter_glob: StringProperty(
        default='*.owmat',
        options={'HIDDEN'},
    )

    def menu_func(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'
        self.layout.operator(
            ImportOWMAT.bl_idname,
            text='Text Export Operator')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        LibraryHandler.load_data()
        t = datetime.now()
        material.init(self.filepath)
        print('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - t)))
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        # col = layout.column(align=True)
        # col.label(text = 'Material')
        # col.enabled = bpy.context.scene.render.engine != 'CYCLES'

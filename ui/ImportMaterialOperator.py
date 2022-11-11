from datetime import datetime

import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy.utils import smpte_from_seconds
from bpy_extras.io_utils import ImportHelper
from ..importer import material
from ..readers import PathUtil

from . import LibraryHandler


class ImportOWMAT(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_material.overtools2_material'
    bl_label = 'Import Overtools Material'
    __doc__ = bl_label
    bl_options = {'UNDO'}

    filename_ext = '.owmat'
    filter_glob: StringProperty(
        default='*.owmat',
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
    def poll(cls, context):
        return True

    def execute(self, context):
        LibraryHandler.load_data()
        t = datetime.now()
        files = {PathUtil.nameFromPath(file.name):PathUtil.joinPath(self.directory, file.name) for file in self.files}
        material.init(files)
        print('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - t)))
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        # col = layout.column(align=True)
        # col.label(text = 'Material')
        # col.enabled = bpy.context.scene.render.engine != 'CYCLES'

from datetime import datetime

import bpy
from bpy.props import BoolProperty, IntProperty
from bpy.utils import smpte_from_seconds
from bpy_extras.io_utils import ImportHelper


class ImportOWEFFECT(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_anim.overtools2_effect'
    bl_label = 'Import Overtools Animation Effect (oweffect, owanim)'
    bl_options = {'UNDO'}

    filename_ext = '.oweffect;.owanim'
    filter_glob: bpy.props.StringProperty(
        default='*.oweffect;*.owanim',
        options={'HIDDEN'},
    )

    import_dmce: BoolProperty(
        name='Import DMCE (Models)',
        description='Import DMCE',
        default=True,
    )

    import_cece: BoolProperty(
        name='Import CECE (Entity Control)',
        description='Import CECE',
        default=True,
    )

    import_nece: BoolProperty(
        name='Import NECE (Entities)',
        description='Import NECE',
        default=True,
    )

    import_svce: BoolProperty(
        name='Import SVCE (Voice) (EXPERIMENTAL)',
        description='Import SVCE. WARNING: CAN CRASH BLENDER',
        default=False,
    )

    svce_line_seed: IntProperty(
        name='SVCE Line seed',
        description='SVCE Line seed',
        default=-1,
        min=-1
    )

    svce_sound_seed: IntProperty(
        name='SVCE Sound seed',
        description='SVCE Sound seed',
        default=-1,
        min=-1
    )

    cleanup_hardpoints: BoolProperty(
        name='Cleanup Sockets',
        description='Remove unused sockets',
        default=True,
    )

    force_framerate: BoolProperty(
        name='Force Framerate',
        description='Force Framerate',
        default=False,
    )

    target_framerate: IntProperty(
        name='Target Framerate',
        description='Target Framerate',
        default=60,
        min=1
    )

    import_camera: BoolProperty(
        name='Create Camera',
        description='Create an estimation of the animation camera',
        default=False,
    )

    def menu_func(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'
        self.layout.operator(
            ImportOWMAP.bl_idname,
            text='Text Export Operator')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = settings.OWSettings(
            self.filepath,
            0,
            0,
            True,
            True,
            True,
            True,
            True,
            True,
            True
        )

        efct_settings = settings.OWEffectSettings(settings, self.filepath, self.force_framerate,
                                                  self.target_framerate, self.import_dmce, self.import_cece,
                                                  self.import_nece,
                                                  self.import_svce, self.svce_line_seed, self.svce_sound_seed,
                                                  self.import_camera,
                                                  self.cleanup_hardpoints)
        settings.load_data()
        t = datetime.now()
        bpyhelper.LOCK_UPDATE = False
        try:
            import_oweffect.read(efct_settings)
        except KeyboardInterrupt:
            bpyhelper.LOCK_UPDATE = False
        import_owmat.cleanup()
        print('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - t)))
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text='Effect')
        col.prop(self, 'import_dmce')
        col.prop(self, 'import_cece')
        col.prop(self, 'import_nece')
        col.prop(self, 'import_svce')
        svce_col = col.column(align=True)
        svce_col.enabled = self.import_svce
        svce_col.prop(self, 'svce_line_seed')
        svce_col.prop(self, 'svce_sound_seed')

        col.label(text='Animation')
        col.prop(self, 'import_camera')
        col.prop(self, 'cleanup_hardpoints')
        col.prop(self, 'force_framerate')
        col2 = layout.column(align=True)
        col2.enabled = self.force_framerate
        col2.prop(self, 'target_framerate')


def effect_import(self, context):
    self.layout.operator(
        ImportOWEFFECT.bl_idname,
        text='Overtools Animation Effect (.oweffect/.owanim)'
    )

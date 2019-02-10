from . import import_owmap
from . import import_owentity
from . import import_owmdl
from . import import_owmat
from . import import_oweffect
from . import owm_types
from . import bpyhelper
import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty
from bpy_extras.io_utils import ImportHelper
from bpy.app.handlers import persistent


class ImportOWMDL(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_mesh.overtools_model'
    bl_label = 'Import Overtools Model (owmdl)'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = '.owmdl'
    filter_glob : StringProperty(
        default='*.owmdl',
        options={'HIDDEN'},
    )

    uvDisplX : IntProperty(
        name='X',
        description='Displace UV X axis',
        default=0,
    )

    uvDisplY : IntProperty(
        name='Y',
        description='Displace UV Y axis',
        default=0,
    )

    autoIk : BoolProperty(
        name='AutoIK',
        description='Set AutoIK',
        default=True,
    )

    importNormals : BoolProperty(
        name='Import Normals',
        description='Import Custom Normals',
        default=True,
    )

    importColor : BoolProperty(
        name='Import Color',
        description='Import Custom Colors',
        default=True,
    )

    importEmpties : BoolProperty(
        name='Import Hardpoints',
        description='Import Hardpoints (attachment points)',
        default=False,
    )

    importMaterial : BoolProperty(
        name='Import Material',
        description='Import Referenced OWMAT',
        default=True,
    )

    importSkeleton : BoolProperty(
        name='Import Skeleton',
        description='Import Bones',
        default=True,
    )

    def menu_func(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'
        self.layout.operator(
            ImportOWMDL.bl_idname,
            text='Text Export Operator')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = owm_types.OWSettings(
            self.filepath,
            self.uvDisplX,
            self.uvDisplY,
            self.autoIk,
            self.importNormals,
            self.importEmpties,
            self.importMaterial,
            self.importSkeleton,
            self.importColor
        )
        owm_types.update_data()
        bpyhelper.LOCK_UPDATE = False
        try:
            import_owmdl.read(settings)
        except KeyboardInterrupt:
            bpyhelper.LOCK_UPDATE = False
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text = 'Mesh')
        col.prop(self, 'importNormals')
        col.prop(self, 'importEmpties')
        col.prop(self, 'importColor')
        col.prop(self, 'importMaterial')
        sub = col.row()
        sub.label(text = 'UV')
        sub.prop(self, 'uvDisplX')
        sub.prop(self, 'uvDisplY')

        col = layout.column(align=True)
        col.label(text = 'Armature')
        col.prop(self, 'importSkeleton')
        sub = col.row()
        sub.prop(self, 'autoIk')
        sub.enabled = self.importSkeleton

        # col = layout.column(align=True)
        # col.enabled = self.importMaterial  and bpy.context.scene.render.engine != 'CYCLES'
        # col.label(text = 'Material')


class ImportOWMAT(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_material.overtools_material'
    bl_label = 'Import Overtools Material (owmat)'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = '.owmat'
    filter_glob : StringProperty(
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
        owm_types.update_data()
        bpyhelper.LOCK_UPDATE = False
        import_owmat.read(self.filepath, '')
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        # col = layout.column(align=True)
        # col.label(text = 'Material')
        # col.enabled = bpy.context.scene.render.engine != 'CYCLES'


class ImportOWMAP(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_mesh.overtools_map'
    bl_label = 'Import Overtools Map (owmap)'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = '.owmap'
    filter_glob = bpy.props.StringProperty(
        default='*.owmap',
        options={'HIDDEN'},
    )

    uvDisplX : IntProperty(
        name='X',
        description='Displace UV X axis',
        default=0,
    )

    uvDisplY : IntProperty(
        name='Y',
        description='Displace UV Y axis',
        default=0,
    )

    importNormals : BoolProperty(
        name='Import Normals',
        description='Import Custom Normals',
        default=True,
    )

    importColor : BoolProperty(
        name='Import Color',
        description='Import Custom Colors',
        default=True,
    )

    importObjects : BoolProperty(
        name='Import Objects',
        description='Import Map Objects',
        default=True,
    )

    importDetails : BoolProperty(
        name='Import Props',
        description='Import Map Props',
        default=True,
    )

    importLights : BoolProperty(
        name='Import Lights',
        description='Import Map Lights',
        default=True,
    )

    importPhysics : BoolProperty(
        name='Import Collision Model',
        description='Import Map Collision Model',
        default=False,
    )

    importMaterial : BoolProperty(
        name='Import Material',
        description='Import Referenced OWMAT',
        default=True,
    )

    importLampSun : BoolProperty(
        name='Import Sun lamps',
        description='Import lamps of type Sun',
        default=False,
    )

    importLampSpot : BoolProperty(
        name='Import Spot lamps',
        description='Import lamps of type Spot',
        default=True,
    )

    importLampPoint : BoolProperty(
        name='Import Point lamps',
        description='Import lamps of type Point',
        default=True,
    )

    multipleImportance : BoolProperty(
        name='Multiple Importance',
        default=False,
    )

    adjustLightValue : FloatProperty(
        name='Adjust Light Value',
        description='Multiply value (HSV) by this amount',
        default=1.0,
        step=0.1,
        min=0.0,
        max=1.0,
        precision=3
    )

    useLightStrength : BoolProperty(
        name='Use Light Strength',
        description='Use light strength data (Experimental)',
        default=True,
    )

    shadowSoftBias : FloatProperty(
        name='Light Shadow Size',
        description='Light size for ray shadow sampling',
        default=0.5,
        step=0.1,
        min=0.0,
        precision=3
    )

    adjustLightStrength : FloatProperty(
        name='Adjust Light Strength',
        description='Multiply strength by this amount',
        default=10.0,
        step=1,
        min=0.0,
        precision=3
    )

    lightIndex : IntProperty(
        name='Light Value Index',
        description='Used for debug purposes, leave it at 25',
        default=25,
        step=1,
        min=0,
        max=35
    )

    edgeIndex : IntProperty(
        name='Light Spot Edge Index',
        description='Used for debug purposes, leave it at 26',
        default=26,
        step=1,
        min=0,
        max=35
    )

    sizeIndex : IntProperty(
        name='Light Size Index',
        description='Used for debug purposes, leave it at 12',
        default=12,
        step=1,
        min=0,
        max=35
    )

    importRemoveCollision : BoolProperty(
        name='Remove Collision Models',
        description='Remove the collision models',
        default=True,
    )

    importSounds : BoolProperty(
        name='Import Sounds',
        description='Imports sound nodes',
        default=True,
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
        settings = owm_types.OWSettings(
            self.filepath,
            self.uvDisplX,
            self.uvDisplY,
            False,
            self.importNormals,
            False,
            self.importMaterial,
            False,
            self.importColor
        )
        light_settings = owm_types.OWLightSettings(
            self.importLights,
            self.multipleImportance,
            [self.importLampSun, self.importLampSpot, self.importLampPoint],
            [self.adjustLightValue, self.adjustLightStrength],
            self.useLightStrength,
            self.shadowSoftBias,
            [self.lightIndex, self.edgeIndex, self.sizeIndex]
        )
        owm_types.update_data()
        bpyhelper.LOCK_UPDATE = False
        import_owmap.read(settings, self.importObjects, self.importDetails, self.importPhysics, light_settings,
                          self.importRemoveCollision, self.importSounds)
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text = 'Mesh')
        col.prop(self, 'importNormals')
        col.prop(self, 'importColor')
        col.prop(self, 'importMaterial')

        sub = col.row()
        sub.label(text = 'UV')
        sub.prop(self, 'uvDisplX')
        sub.prop(self, 'uvDisplY')

        col = layout.column(align=True)
        col.label(text = 'Map')
        col.prop(self, 'importObjects')
        col.prop(self, 'importDetails')
        col.prop(self, 'importSounds')

        sub = col.row()
        sub.prop(self, 'importPhysics')
        sub.enabled = self.importDetails

        col.prop(self, 'importLights')
        col.prop(self, 'importRemoveCollision')

        # col = layout.column(align=True)
        # col.label(text = 'Material')
        # col.enabled = self.importMaterial and bpy.context.scene.render.engine != 'CYCLES'

        col = layout.column(align=True)
        col.label(text = 'Lights')
        col.enabled = self.importLights
        col.prop(self, 'importLampSun')
        col.prop(self, 'importLampSpot')
        col.prop(self, 'importLampPoint')
        col.prop(self, 'multipleImportance')
        col.prop(self, 'useLightStrength')
        col.prop(self, 'shadowSoftBias')
        col.prop(self, 'adjustLightValue')
        col2 = col.column(align=True)
        col2.enabled = self.useLightStrength
        col2.prop(self, 'adjustLightStrength')
        col2.prop(self, 'lightIndex')
        col.prop(self, 'edgeIndex')
        col.prop(self, 'sizeIndex')


class ImportOWENTITY(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_mesh.overtools_entity'
    bl_label = 'Import Overtools Entity (owentity)'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filter_glob = bpy.props.StringProperty(
        default='*.owentity',
        options={'HIDDEN'},
    )

    import_children : BoolProperty(
        name='Import Children',
        description='Import child entities',
        default=True,
    )

    uvDisplX : IntProperty(
        name='X',
        description='Displace UV X axis',
        default=0,
    )

    uvDisplY : IntProperty(
        name='Y',
        description='Displace UV Y axis',
        default=0,
    )

    autoIk : BoolProperty(
        name='AutoIK',
        description='Set AutoIK',
        default=True,
    )

    importNormals : BoolProperty(
        name='Import Normals',
        description='Import Custom Normals',
        default=True,
    )

    importColor : BoolProperty(
        name='Import Color',
        description='Import Custom Colors',
        default=True,
    )

    importEmpties : BoolProperty(
        name='Import Empties',
        description='Import Empty Objects',
        default=False,
    )

    importMaterial : BoolProperty(
        name='Import Material',
        description='Import Referenced OWMAT',
        default=True,
    )

    importSkeleton : BoolProperty(
        name='Import Skeleton',
        description='Import Bones',
        default=True,
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
        settings = owm_types.OWSettings(
            self.filepath,
            self.uvDisplX,
            self.uvDisplY,
            self.autoIk,
            self.importNormals,
            True,  # self.importEmpties
            self.importMaterial,
            True,  # self.importSkeleton
            self.importColor
        )
        owm_types.update_data()
        bpyhelper.LOCK_UPDATE = False
        import_owentity.read(settings, self.import_children)
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text = 'Entity')
        col.prop(self, 'import_children')

        col = layout.column(align=True)
        col.label(text = 'Mesh')
        col.prop(self, 'importNormals')
        col.prop(self, 'importColor')
        col.prop(self, 'importMaterial')
        sub = col.row()
        sub.label(text = 'UV')
        sub.prop(self, 'uvDisplX')
        sub.prop(self, 'uvDisplY')

        col = layout.column(align=True)
        col.label(text = 'Armature')
        sub = col.row()
        sub.prop(self, 'autoIk')
        sub.enabled = self.importSkeleton

        # col = layout.column(align=True)
        # col.enabled = self.importMaterial and bpy.context.scene.render.engine != 'CYCLES'
        # col.label(text = 'Material')


class ImportOWEFFECT(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_anim.overtools_effect'
    bl_label = 'Import Overtools Animation Effect (oweffect, owanim)'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = '.oweffect;.owanim'
    filter_glob : bpy.props.StringProperty(
        default='*.oweffect;*.owanim',
        options={'HIDDEN'},
    )

    import_dmce : BoolProperty(
        name='Import DMCE (Models)',
        description='Import DMCE',
        default=True,
    )

    import_cece : BoolProperty(
        name='Import CECE (Entity Control)',
        description='Import CECE',
        default=True,
    )

    import_nece : BoolProperty(
        name='Import NECE (Entities)',
        description='Import NECE',
        default=True,
    )

    import_svce : BoolProperty(
        name='Import SVCE (Voice) (EXPERIMENTAL)',
        description='Import SVCE. WARNING: CAN CRASH BLENDER',
        default=False,
    )

    svce_line_seed : IntProperty(
        name='SVCE Line seed',
        description='SVCE Line seed',
        default=-1,
        min=-1
    )

    svce_sound_seed : IntProperty(
        name='SVCE Sound seed',
        description='SVCE Sound seed',
        default=-1,
        min=-1
    )

    cleanup_hardpoints : BoolProperty(
        name='Cleanup Hardpoints',
        description='Remove unused hardpoints',
        default=True,
    )

    force_framerate : BoolProperty(
        name='Force Framerate',
        description='Force Framerate',
        default=False,
    )

    target_framerate : IntProperty(
        name='Target Framerate',
        description='Target Framerate',
        default=60,
        min=1
    )

    import_camera : BoolProperty(
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
        settings = owm_types.OWSettings(
            self.filepath,
            0,
            0,
            True,
            True,
            True,
            True,
            True,
            True
        )

        efct_settings = owm_types.OWEffectSettings(settings, self.filepath, self.force_framerate,
                                                   self.target_framerate, self.import_dmce, self.import_cece,
                                                   self.import_nece,
                                                   self.import_svce, self.svce_line_seed, self.svce_sound_seed,
                                                   self.import_camera,
                                                   self.cleanup_hardpoints)
        owm_types.update_data()
        bpyhelper.LOCK_UPDATE = False
        import_oweffect.read(efct_settings)
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text = 'Effect')
        col.prop(self, 'import_dmce')
        col.prop(self, 'import_cece')
        col.prop(self, 'import_nece')
        col.prop(self, 'import_svce')
        svce_col = col.column(align=True)
        svce_col.enabled = self.import_svce
        svce_col.prop(self, 'svce_line_seed')
        svce_col.prop(self, 'svce_sound_seed')

        col.label(text = 'Animation')
        col.prop(self, 'import_camera')
        col.prop(self, 'cleanup_hardpoints')
        col.prop(self, 'force_framerate')
        col2 = layout.column(align=True)
        col2.enabled = self.force_framerate
        col2.prop(self, 'target_framerate')


def mdlimp(self, context):
    self.layout.operator(
        ImportOWMDL.bl_idname,
        text='Overtools Model (.owmdl)'
    )


def matimp(self, context):
    self.layout.operator(
        ImportOWMAT.bl_idname,
        text='Overtools Material (.owmat)'
    )


def mapimp(self, context):
    self.layout.operator(
        ImportOWMAP.bl_idname,
        text='Overtools Map (.owmap)'
    )


def entity_import(self, context):
    self.layout.operator(
        ImportOWENTITY.bl_idname,
        text='Overtools Entity (.owentity)'
    )


def effect_import(self, context):
    self.layout.operator(
        ImportOWEFFECT.bl_idname,
        text='Overtools Animation Effect (.oweffect, .owanim)'
    )


class OWMUtilityPanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_select'
    bl_label = 'OWM Tools'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    @classmethod
    def poll(cls, context): return 1

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator(OWMLoadOp.bl_idname, text='Load OWM Library', icon='LINK_BLEND')
        row.operator(OWMSaveOp.bl_idname, text='Save OWM Library', icon='APPEND_BLEND')
        row = layout.row()
        row.prop(bpy.context.scene.owm_internal_settings, 'b_logsalot', text='Log Map Progress')
        row.prop(bpy.context.scene.owm_internal_settings, 'b_download', text='Always Download Library')

        box = layout.box()
        box.label(text = 'Cleanup')
        row = box.row()
        row.operator(OWMCleanupOp.bl_idname, text='Unused Empties', icon='OBJECT_DATA')
        row = box.row()
        row.operator(OWMCleanupTexOp.bl_idname, text='Unused Materials', icon='MATERIAL')


class OWMLoadOp(bpy.types.Operator):
    bl_idname = 'owm.load_library'
    bl_label = 'Load OWM Library'

    def execute(self, context):
        owm_types.update_data(True)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class OWMSaveOp(bpy.types.Operator):
    bl_idname = 'owm.save_library'
    bl_label = 'Save OWM Library'

    def execute(self, context):
        owm_types.create_overwatch_library()
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class OWMCleanupOp(bpy.types.Operator):
    bl_idname = 'owm.delete_unused_empties'
    bl_label = 'Delete Unused Empties'

    def execute(self, context):
        bpyhelper.clean_empties()
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class OWMCleanupTexOp(bpy.types.Operator):
    bl_idname = 'owm.delete_unused_materials'
    bl_label = 'Delete Unused Materials'

    def execute(self, context):
        bpyhelper.clean_materials()
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class OWMInternalSettings(bpy.types.PropertyGroup):
    b_logsalot : bpy.props.BoolProperty(update=lambda self, context: self.update_logs_alot(context))
    b_download : bpy.props.BoolProperty(update=lambda self, context: self.update_download(context))
    i_library_state : IntProperty(update=lambda self, context: self.dummy(context))

    def update_logs_alot(self, context):
        owm_types.LOG_ALOT = self.b_logsalot

    def update_download(self, context):
        owm_types.ALWAYS_DOWNLOAD = self.b_download

    def dummy(self, context): pass


@persistent
def owm_reset(_):
    owm_types.reset();

classes = (
    OWMUtilityPanel,
    OWMLoadOp,
    OWMSaveOp,
    OWMCleanupOp,
    OWMCleanupTexOp,
    OWMInternalSettings,
    ImportOWMDL,
    ImportOWMAT,
    ImportOWMAP,
    ImportOWENTITY,
    ImportOWEFFECT
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(mdlimp)
    bpy.types.TOPBAR_MT_file_import.append(matimp)
    bpy.types.TOPBAR_MT_file_import.append(mapimp)
    bpy.types.TOPBAR_MT_file_import.append(entity_import)
    bpy.types.TOPBAR_MT_file_import.append(effect_import)
    bpy.types.Scene.owm_internal_settings = bpy.props.PointerProperty(type=OWMInternalSettings)
    bpy.app.handlers.load_post.append(owm_reset)


def unregister():
    owm_reset()

    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.load_post.remove(owm_reset)
    bpy.types.TOPBAR_MT_file_import.remove(mdlimp)
    bpy.types.TOPBAR_MT_file_import.remove(matimp)
    bpy.types.TOPBAR_MT_file_import.remove(mapimp)
    bpy.types.TOPBAR_MT_file_import.remove(entity_import)
    bpy.types.TOPBAR_MT_file_import.remove(effect_import)
    bpy.types.Scene.owm_internal_settings = None

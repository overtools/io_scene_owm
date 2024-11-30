import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty

class OWModelSettings(bpy.types.PropertyGroup):
    importNormals: BoolProperty(
        name='Import Normals',
        description='Import Custom Normals',
        default=True,
    )

    autoSmoothNormals: BoolProperty(
        name='Auto Smooth Normals',
        description='Auto Smooth Normals around soft edges',
        default=True,
    )

    importColor: BoolProperty(
        name='Import Color',
        description='Import Custom Colors',
        default=True,
    )

    importEmpties: BoolProperty(
        name='Import Empties',
        description='Import Empty Objects',
        default=True,
    )

    importMaterial: BoolProperty(
        name='Import Material',
        description='Import Referenced OWMAT',
        default=True,
    )

    importSkeleton: BoolProperty(
        name='Import Skeleton',
        description='Import Bones',
        default=True,
    )

    importMatless: BoolProperty(
        name='import matless meshes',
        description='hidden attribute for mythic skins',
        default=True,
    )

    saveMaterialDB: BoolProperty(
        name='(DEV) Dump Materials JSON',
        description='Save a material database in json for use in other applications',
        default=False,
    )

    def draw(cls, me, layout):
        layout.label(text='Mesh')
        layout.prop(me, 'importMaterial')
        layout.prop(me, 'importColor')
        layout.prop(me, 'importNormals')
        if bpy.app.version < (4,1,0):
            layout.prop(me, 'autoSmoothNormals')
        layout.prop(me, 'importEmpties')

    def draw_armature(cls, me, layout, label=True):
        if label:
            layout.label(text='Armature')
        layout.prop(me, 'importSkeleton')


class OWEntitySettings(bpy.types.PropertyGroup):
    importChildren: BoolProperty(
        name='Import Children',
        description='Import child entities',
        default=True,
    )

    def draw(cls, me, layout):
        layout.label(text='Entity')
        layout.prop(me, 'importChildren')


class OWMapSettings(bpy.types.PropertyGroup):
    importObjects: BoolProperty(
        name='Import Models',
        description='Import Map Models',
        default=True,
    )

    importDetails: BoolProperty(
        name='Import Entities',
        description='Import Map Entities',
        default=True,
    )

    importLights: BoolProperty(
        name='Import Lights',
        description='Import Map Lights',
        default=True,
    )

    importSounds: BoolProperty(
        name='Import sounds',
        description='nobody caes lolol',
        default=False,
    )

    removeCollision: BoolProperty(
        name='Remove Engine Hit Tests',
        description='Remove the meshes used by the engine to calculate hit layers',
        default=True,
    )

    joinMeshes: BoolProperty(
        name='Join Meshes (EXPERIMENTAL)',
        description='Join Separate meshes into a single object, faster for viewport operations',
        default=False,
    )

    def draw(cls, me, layout):
        layout.label(text='Map')
        layout.prop(me, 'importObjects')
        layout.prop(me, 'importDetails')
        layout.prop(me, 'importLights')
        layout.prop(me, 'removeCollision')
        layout.prop(me, 'joinMeshes')


class OWLightSettings(bpy.types.PropertyGroup):
    multipleImportance: BoolProperty(
        name='Multiple Importance',
        default=False,
    )

    adjustLightValue: FloatProperty(
        name='Adjust Light Value',
        description='Multiply value (HSV) by this amount',
        default=1.0,
        step=0.1,
        min=0.0,
        max=1.0,
        precision=3
    )

    shadowSoftBias: FloatProperty(
        name='Light Shadow Size',
        description='Light size for ray shadow sampling',
        default=0.5,
        step=0.1,
        min=0.0,
        precision=3
    )

    adjustLightStrength: FloatProperty(
        name='Adjust Light Strength',
        description='Multiply strength by this amount',
        default=10.0,
        step=0.1,
        min=0.0,
        precision=3
    )

    def draw(cls, me, layout):
        layout.label(text='Lights')
        layout.prop(me, 'multipleImportance')
        layout.prop(me, 'shadowSoftBias')
        # layout.prop(me, 'adjustLightValue')
        layout.prop(me, 'adjustLightStrength')


class OWEffectSettings:
    def __init__(self, settings, force_fps, target_fps, import_DMCE, import_CECE, import_NECE,
                 import_SVCE, svce_line_seed, svce_sound_seed, create_camera, cleanup_hardpoints):
        self.settings = settings
        self.force_fps = force_fps
        self.target_fps = target_fps
        self.import_DMCE = import_DMCE
        self.import_CECE = import_CECE
        self.import_NECE = import_NECE
        self.import_SVCE = import_SVCE
        self.svce_line_seed = svce_line_seed
        self.svce_sound_seed = svce_sound_seed
        self.create_camera = create_camera
        self.cleanup_hardpoints = cleanup_hardpoints
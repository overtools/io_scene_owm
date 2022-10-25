import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty

from . import LibraryHandler


class OWMInternalSettings2(bpy.types.PropertyGroup):
    b_logsalot: bpy.props.BoolProperty(name="Log alot", description="Verbose logging",
                                       default=False, update=lambda self, context: self.update_logs_alot(context))

    def update_logs_alot(self, context):
        LibraryHandler.LOG_ALOT = self.b_logsalot

    def dummy(self, context): pass


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


class OWEntitySettings(bpy.types.PropertyGroup):
    importChildren: BoolProperty(
        name='Import Children',
        description='Import child entities',
        default=True,
    )


class OWMapSettings(bpy.types.PropertyGroup):
    importObjects: BoolProperty(
        name='Import Objects',
        description='Import Map Objects',
        default=True,
    )

    importDetails: BoolProperty(
        name='Import Props',
        description='Import Map Props',
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
        name='Join Meshes',
        description='Join Separate meshes into a single object, faster for viewport operations and import',
        default=False,
    )


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

    useLightStrength: BoolProperty(
        name='Use Light Strength',
        description='Use light strength data (Experimental)',
        default=True,
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
        step=1,
        min=0.0,
        precision=3
    )

    lightIndex: IntProperty(
        name='Light Value Index',
        description='Used for debug purposes, leave it at 25',
        default=25,
        step=1,
        min=0,
        max=35
    )

    edgeIndex: IntProperty(
        name='Light Spot Edge Index',
        description='Used for debug purposes, leave it at 26',
        default=26,
        step=1,
        min=0,
        max=35
    )

    sizeIndex: IntProperty(
        name='Light Size Index',
        description='Used for debug purposes, leave it at 12',
        default=12,
        step=1,
        min=0,
        max=35
    )


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
from . import import_owmap
from . import import_owentity
from . import import_owmdl
from . import import_owmat
from . import import_oweffect
from . import owm_types
from . import bpyhelper
import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy_extras.io_utils import ImportHelper

class import_mdl_op(bpy.types.Operator, ImportHelper):
    bl_idname = "owm_importer.import_model"
    bl_label = "Import OWMDL"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".owmdl"
    filter_glob = bpy.props.StringProperty(
        default="*.owmdl",
        options={'HIDDEN'},
    )

    uvDisplX = bpy.props.IntProperty(
        name="X",
        description="Displace UV X axis",
        default=0,
    )

    uvDisplY = bpy.props.IntProperty(
        name="Y",
        description="Displace UV Y axis",
        default=0,
    )

    autoIk = BoolProperty(
        name="AutoIK",
        description="Set AutoIK",
        default=True,
    )

    importNormals = BoolProperty(
        name="Import Normals",
        description="Import Custom Normals",
        default=True,
    )

    importColor = BoolProperty(
        name="Import Color",
        description="Import Custom Colors",
        default=True,
    )

    importEmpties = BoolProperty(
        name="Import Hardpoints",
        description="Import Hardpoints (attachment points)",
        default=False,
    )

    importMaterial = BoolProperty(
        name="Import Material",
        description="Import Referenced OWMAT",
        default=True,
    )

    importSkeleton = BoolProperty(
        name="Import Skeleton",
        description="Import Bones",
        default=(not bpyhelper.IS_BLENDER280),
    )

    importTexNormal = BoolProperty(
        name="Import Normal Maps",
        description="Import Normal Textures",
        default=True,
    )

    importTexEffect = BoolProperty(
        name="Import Misc Maps",
        description="Import Misc Texutures (Effects, highlights)",
        default=True,
    )

    def menu_func(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'
        self.layout.operator(
            import_mdl_op.bl_idname,
            text="Text Export Operator")

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
            self.importTexNormal,
            self.importTexEffect,
            self.importColor
        )
        import_owmdl.read(settings)
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label('Mesh')
        col.prop(self, "importNormals")
        col.prop(self, "importEmpties")
        col.prop(self, "importColor")
        col.prop(self, "importMaterial")
        sub = col.row()
        sub.label('UV')
        sub.prop(self, "uvDisplX")
        sub.prop(self, "uvDisplY")

        col = layout.column(align=True)
        col.label('Armature')
        col.prop(self, "importSkeleton")
        sub = col.row()
        sub.prop(self, "autoIk")
        sub.enabled = self.importSkeleton

        col = layout.column(align=True)
        col.enabled = self.importMaterial  and bpy.context.scene.render.engine != 'CYCLES'
        col.label('Material')
        col.prop(self, 'importTexNormal')
        col.prop(self, 'importTexEffect')

class import_mat_op(bpy.types.Operator, ImportHelper):
    bl_idname = "owm_importer.import_material"
    bl_label = "Import OWMAT"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".owmat"
    filter_glob = bpy.props.StringProperty(
        default="*.owmat",
        options={'HIDDEN'},
    )

    importTexNormal = BoolProperty(
        name="Import Normal Maps",
        description="Import Normal Textures",
        default=True,
    )

    importTexEffect = BoolProperty(
        name="Import Misc Maps",
        description="Import Misc Texutures (Effects, highlights)",
        default=True,
    )

    def menu_func(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'
        self.layout.operator(
            import_mat_op.bl_idname,
            text="Text Export Operator")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        import_owmat.read(self.filepath, '', self.importTexNormal, self.importTexNormal)
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label('Material')
        col.prop(self, 'importTexNormal')
        col.prop(self, 'importTexEffect')
        col.enabled = bpy.context.scene.render.engine != 'CYCLES'

class import_map_op(bpy.types.Operator, ImportHelper):
    bl_idname = "owm_importer.import_map"
    bl_label = "Import OWMAP"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".owmap"
    filter_glob = bpy.props.StringProperty(
        default="*.owmap",
        options={'HIDDEN'},
    )

    uvDisplX = bpy.props.IntProperty(
        name="X",
        description="Displace UV X axis",
        default=0,
    )

    uvDisplY = bpy.props.IntProperty(
        name="Y",
        description="Displace UV Y axis",
        default=0,
    )

    importNormals = BoolProperty(
        name="Import Normals",
        description="Import Custom Normals",
        default=True,
    )

    importColor = BoolProperty(
        name="Import Color",
        description="Import Custom Colors",
        default=True,
    )
    
    importObjects = BoolProperty(
        name="Import Objects",
        description="Import Map Objects",
        default=True,
    )

    importDetails = BoolProperty(
        name="Import Props",
        description="Import Map Props",
        default=True,
    )

    importLights = BoolProperty(
        name="Import Lights",
        description="Import Map Lights",
        default=True,
    )

    importPhysics = BoolProperty(
        name="Import Collision Model",
        description="Import Map Collision Model",
        default=False,
    )

    importMaterial = BoolProperty(
        name="Import Material",
        description="Import Referenced OWMAT",
        default=True,
    )
    
    importTexNormal = BoolProperty(
        name="Import Normal Maps",
        description="Import Normal Textures",
        default=True,
    )

    importTexEffect = BoolProperty(
        name="Import Misc Maps",
        description="Import Misc Texutures (Effects, highlights)",
        default=True,
    )

    importLampSun = BoolProperty(
        name="Import Sun lamps",
        description="Import lamps of type Sun",
        default=True,
    )

    importLampSpot = BoolProperty(
        name="Import Spot lamps",
        description="Import lamps of type Spot",
        default=True,
    )

    importLampPoint = BoolProperty(
        name="Import Point lamps",
        description="Import lamps of type Point",
        default=True,
    )

    multipleImportance = BoolProperty(
        name="Multiple Importance",
        default=False,
    )

    adjustLightValue = FloatProperty(
        name="Adjust Light Value",
        description="Multiply value (HSV) by this amount",
        default=1.0,
        step=0.1,
        min=0.0,
        max=1.0,
        precision=3
    )

    useLightStrength = BoolProperty(
        name="Use Light Strength",
        description="Use light strength data (Experimental)",
        default=True,
    )

    adjustLightStrength = FloatProperty(
        name="Adjust Light Strength",
        description="Multiply strength by this amount",
        default=1.0,
        step=1,
        min=0.0,
        precision=3
    )
    
    importRemoveCollision = BoolProperty(
        name="Remove Collision Models",
        description="Remove the collision models",
        default=True,
    )

    def menu_func(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'
        self.layout.operator(
            import_map_op.bl_idname,
            text="Text Export Operator")

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
            self.importTexNormal,
            self.importTexEffect,
            self.importColor
        )
        light_settings = owm_types.OWLightSettings(
            self.importLights, 
            self.multipleImportance,
            [self.importLampSun, self.importLampSpot, self.importLampPoint],
            [self.adjustLightValue, self.adjustLightStrength], 
            self.useLightStrength
        )
        import_owmap.read(settings, self.importObjects, self.importDetails, self.importPhysics, light_settings, self.importRemoveCollision)
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label('Mesh')
        col.prop(self, "importNormals")
        col.prop(self, 'importColor')
        col.prop(self, "importMaterial")
        
        sub = col.row()
        sub.label('UV')
        sub.prop(self, "uvDisplX")
        sub.prop(self, "uvDisplY")
        
        col = layout.column(align=True)
        col.label('Map')
        col.prop(self, "importObjects")
        col.prop(self, "importDetails")
        
        sub = col.row()
        sub.prop(self, "importPhysics")
        sub.enabled = self.importDetails
        
        col.prop(self, "importLights")
        col.prop(self, "importRemoveCollision")

        col = layout.column(align=True)
        col.label('Material')
        col.enabled = self.importMaterial
        col.prop(self, 'importTexNormal')
        col.prop(self, 'importTexEffect')

        col = layout.column(align=True)
        col.label('Lights')
        col.enabled = self.importLights
        col.prop(self, 'importLampSun')
        col.prop(self, 'importLampSpot')
        col.prop(self, 'importLampPoint')
        col.prop(self, 'adjustLightValue')
        col.prop(self, 'useLightStrength')
        col.prop(self, 'multipleImportance')
        col = col.column(align=False)
        col.enabled = self.useLightStrength
        col.prop(self, 'adjustLightStrength')

class import_ent_op(bpy.types.Operator, ImportHelper):
    bl_idname = "owm_importer.import_entity"
    bl_label = "Import OWENTITY"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    filter_glob = bpy.props.StringProperty(
        default="*.owentity",
        options={'HIDDEN'},
    )

    import_children = BoolProperty(
        name="Import Children",
        description="Import child entities",
        default=True,
    )

    uvDisplX = bpy.props.IntProperty(
        name="X",
        description="Displace UV X axis",
        default=0,
    )

    uvDisplY = bpy.props.IntProperty(
        name="Y",
        description="Displace UV Y axis",
        default=0,
    )

    autoIk = BoolProperty(
        name="AutoIK",
        description="Set AutoIK",
        default=True,
    )

    importNormals = BoolProperty(
        name="Import Normals",
        description="Import Custom Normals",
        default=True,
    )

    importNormals = BoolProperty(
        name="Import Color",
        description="Import Custom Color",
        default=True,
    )

    importEmpties = BoolProperty(
        name="Import Empties",
        description="Import Empty Objects",
        default=False,
    )

    importMaterial = BoolProperty(
        name="Import Material",
        description="Import Referenced OWMAT",
        default=True,
    )

    importSkeleton = BoolProperty(
        name="Import Skeleton",
        description="Import Bones",
        default=(not bpyhelper.IS_BLENDER280),
    )

    importTexNormal = BoolProperty(
        name="Import Normal Maps",
        description="Import Normal Textures",
        default=True,
    )

    importTexEffect = BoolProperty(
        name="Import Misc Maps",
        description="Import Misc Texutures (Effects, highlights)",
        default=True,
    )

    def menu_func(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'
        self.layout.operator(
            import_map_op.bl_idname,
            text="Text Export Operator")

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
            True, # self.importEmpties
            self.importMaterial,
            True, # self.importSkeleton
            self.importTexNormal,
            self.importTexEffect,
            self.importColor
        )
        import_owentity.read(settings, self.import_children)
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label('Entity')
        col.prop(self, "import_children")

        col = layout.column(align=True)
        col.label('Mesh')
        col.prop(self, "importNormals")
        col.prop(self, 'importColor')
        col.prop(self, "importMaterial")
        sub = col.row()
        sub.label('UV')
        sub.prop(self, "uvDisplX")
        sub.prop(self, "uvDisplY")

        col = layout.column(align=True)
        col.label('Armature')
        sub = col.row()
        sub.prop(self, "autoIk")
        sub.enabled = self.importSkeleton

        col = layout.column(align=True)
        col.enabled = self.importMaterial and bpy.context.scene.render.engine != 'CYCLES'
        col.label('Material')
        col.prop(self, 'importTexNormal')
        col.prop(self, 'importTexEffect')

class import_effect_op(bpy.types.Operator, ImportHelper):
    bl_idname = "owm_importer.import_effect"
    bl_label = "Import OWEFFECT / OWANIM"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".oweffect;.owanim"
    filter_glob = bpy.props.StringProperty(
        default="*.oweffect;*.owanim",
        options={'HIDDEN'},
    )

    import_dmce = BoolProperty(
        name="Import DMCE (Models)",
        description="Import DMCE",
        default=True,
    )

    import_cece = BoolProperty(
        name="Import CECE (Entity Control)",
        description="Import CECE",
        default=True,
    )

    import_nece = BoolProperty(
        name="Import NECE (Entities)",
        description="Import NECE",
        default=True,
    )

    import_svce = BoolProperty(
        name="Import SVCE (Voice) (EXPERIMENTAL)",
        description="Import SVCE. WARNING: CAN CRASH BLENDER",
        default=False,
    )

    svce_line_seed = bpy.props.IntProperty(
        name="SVCE Line seed",
        description="SVCE Line seed",
        default=-1,
        min=-1
    )

    svce_sound_seed = bpy.props.IntProperty(
        name="SVCE Sound seed",
        description="SVCE Sound seed",
        default=-1,
        min=-1
    )

    cleanup_hardpoints = BoolProperty(
        name="Cleanup Hardpoints",
        description="Remove unused hardpoints",
        default=True,
    )
    
    force_framerate = BoolProperty(
        name="Force Framerate",
        description="Force Framerate",
        default=False,
    )

    target_framerate = bpy.props.IntProperty(
        name="Target Framerate",
        description="Target Framerate",
        default=60,
        min=1
    )

    import_camera = BoolProperty(
        name="Create Camera",
        description="Create an estimation of the animation camera",
        default=False,
    )

    def menu_func(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'
        self.layout.operator(
            import_map_op.bl_idname,
            text="Text Export Operator")

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
            True,
            True
        )

        efct_settings = owm_types.OWEffectSettings(settings, self.filepath, self.force_framerate,
            self.target_framerate, self.import_dmce, self.import_cece, self.import_nece,
            self.import_svce, self.svce_line_seed, self.svce_sound_seed, self.import_camera,
            self.cleanup_hardpoints)

        import_oweffect.read(efct_settings)
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label('Effect')
        col.prop(self, "import_dmce")
        col.prop(self, "import_cece")
        col.prop(self, "import_nece")
        col.prop(self, "import_svce")
        svce_col = col.column(align=True)
        svce_col.enabled = self.import_svce
        svce_col.prop(self, "svce_line_seed")
        svce_col.prop(self, "svce_sound_seed")

        col.label('Animation')
        col.prop(self, 'import_camera')
        col.prop(self, "cleanup_hardpoints")
        col.prop(self, "force_framerate")
        col2 = layout.column(align=True)
        col2.enabled = self.force_framerate
        col2.prop(self, 'target_framerate')        

def mdlimp(self, context):
    self.layout.operator(
        import_mdl_op.bl_idname,
        text="OWMDL"
    )

def matimp(self, context):
    self.layout.operator(
        import_mat_op.bl_idname,
        text="OWMAT"
    )

def mapimp(self, context):
    self.layout.operator(
        import_map_op.bl_idname,
        text="OWMAP"
    )

def entity_import(self, context):
    self.layout.operator(
        import_ent_op.bl_idname,
        text="OWENTITY"
    )

def effect_import(self, context):
    self.layout.operator(
        import_effect_op.bl_idname,
        text="OWEFFECT / OWANIM"
    )

def register():
    bpy.types.INFO_MT_file_import.append(mdlimp)
    bpy.types.INFO_MT_file_import.append(matimp)
    bpy.types.INFO_MT_file_import.append(mapimp)
    bpy.types.INFO_MT_file_import.append(entity_import)
    bpy.types.INFO_MT_file_import.append(effect_import)

def unregister():
    bpy.types.INFO_MT_file_import.remove(mdlimp)
    bpy.types.INFO_MT_file_import.remove(matimp)
    bpy.types.INFO_MT_file_import.remove(mapimp)
    bpy.types.INFO_MT_file_import.remove(entity_import)
    bpy.types.INFO_MT_file_import.remove(effect_import)


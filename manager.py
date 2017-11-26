from . import import_owmap
from . import import_owentity
from . import import_owmdl
from . import import_owmat
from . import owm_types
from . import bpyhelper
import bpy
from bpy.props import StringProperty, BoolProperty
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
            self.importTexEffect
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
        col.enabled = self.importMaterial
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
            self.importTexEffect
        )
        import_owmap.read(settings, self.importObjects, self.importDetails, self.importPhysics, self.importLights, [self.importLampSun, self.importLampSpot, self.importLampPoint])
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label('Mesh')
        col.prop(self, "importNormals")
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

class import_ent_op(bpy.types.Operator, ImportHelper):
    bl_idname = "owm_importer.import_entity"
    bl_label = "Import OWENTITY"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".owmap"
    filter_glob = bpy.props.StringProperty(
        default="*.owentity",
        options={'HIDDEN'},
    )

    importChildren = BoolProperty(
        name="Import Children",
        description="Import child entities",
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
        import_owentity.read(settings, self.importChildren)
        # import_owmap.read(settings, self.importObjects, self.importDetails, self.importPhysics, self.importLights, [self.importLampSun, self.importLampSpot, self.importLampPoint])
        print('DONE')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label('Test')
        col.prop(self, "importChildren")

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

def entimp(self, context):
    self.layout.operator(
        import_ent_op.bl_idname,
        text="OWENTITY"
    )

def register():
    bpy.types.INFO_MT_file_import.append(mdlimp)
    bpy.types.INFO_MT_file_import.append(matimp)
    bpy.types.INFO_MT_file_import.append(mapimp)
    bpy.types.INFO_MT_file_import.append(entimp)

def unregister():
    bpy.types.INFO_MT_file_import.remove(mdlimp)
    bpy.types.INFO_MT_file_import.remove(matimp)
    bpy.types.INFO_MT_file_import.remove(mapimp)
    bpy.types.INFO_MT_file_import.remove(entimp)

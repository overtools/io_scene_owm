import bpy
from bpy.app.handlers import persistent


from . import ImportMaterialOperator
from . import ImportEntityOperator
from . import ImportMapOperator
from . import ImportModelOperator
from . import LibraryHandler
from . import UtilityOperators
from . import SettingTypes

class OvertoolsMenu(bpy.types.Menu):
    bl_idname = 'import_mesh_MT_overtools_menu'
    bl_label = "Select"

    def draw(self, context):
        self.layout.operator(ImportModelOperator.ImportOWMDL.bl_idname, text='Model (.owmdl)')
        self.layout.operator(ImportEntityOperator.ImportOWENTITY.bl_idname, text='Entity (.owentity)')
        self.layout.operator(ImportMapOperator.ImportOWMAP.bl_idname, text='Map (.owmap)')
        self.layout.operator(ImportMaterialOperator.ImportOWMAT.bl_idname, text='Material (.owmat)')

def overtoolsMenuDraw(self, context):
    self.layout.menu("import_mesh_MT_overtools_menu", text="Overtools")

classes = (
    # Setting props
    SettingTypes.OWMInternalSettings,
    SettingTypes.OWMapSettings,
    SettingTypes.OWEntitySettings,
    SettingTypes.OWModelSettings,
    #OWEffectSettings,
    SettingTypes.OWLightSettings,
    #Panel
    UtilityOperators.OWMUtilityPanel,
    #Operators
    LibraryHandler.OWMLoadOp,
    LibraryHandler.OWMSaveOp,
    LibraryHandler.OWMLoadJSONOp,
    UtilityOperators.OWMCleanupOp,
    UtilityOperators.OWMCleanupTexOp,
    #Importers
    OvertoolsMenu,
    ImportModelOperator.ImportOWMDL,
    ImportMaterialOperator.ImportOWMAT,
    ImportMapOperator.ImportOWMAP,
    ImportEntityOperator.ImportOWENTITY,
    # ImportOWEFFECT
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(overtoolsMenuDraw)
    # bpy.types.TOPBAR_MT_file_import.append(effect_import)
    bpy.types.Scene.owm_internal_settings = bpy.props.PointerProperty(type=SettingTypes.OWMInternalSettings)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(overtoolsMenuDraw)
    # bpy.types.TOPBAR_MT_file_import.remove(effect_import)
    bpy.types.Scene.owm_internal_settings = None

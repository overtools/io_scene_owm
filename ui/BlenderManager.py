import bpy
from . import ImportModelOperator
from . import ImportMaterialOperator
from . import ImportEntityOperator
from . import ImportAnimationOperator
from . import ImportMapOperator
from . import ImportMapWizard
from . import ImportSkinOperator
from . import UtilityOperators
from . import Preferences
from . import SettingTypes
from . import DatatoolLibHandler
from . import shader_library_operators
from . import filehandler_operators

class OvertoolsMenu(bpy.types.Menu):
    bl_idname = 'OWM_MT_overtools_menu'
    bl_label = "Select"

    def draw(self, context):
        self.layout.operator(ImportSkinOperator.ImportOWSkinWizard.bl_idname, text='Skin (wizard)')
        self.layout.operator(ImportMapWizard.ImportOWMapWizard.bl_idname, text='Map (wizard)')
        self.layout.operator(ImportModelOperator.ImportOWMDL.bl_idname, text='Model (.owmdl)')
        self.layout.operator(ImportEntityOperator.ImportOWENTITY.bl_idname, text='Entity (.owentity)')
        self.layout.operator(ImportMapOperator.ImportOWMAP.bl_idname, text='Map (.owmap)')
        self.layout.operator(ImportMaterialOperator.ImportOWMAT.bl_idname, text='Material (.owmat)')
        self.layout.operator(ImportAnimationOperator.ImportOWANIMCLIP.bl_idname, text='Animation (.owanimclip)')

def overtoolsMenuDraw(self, context):
    self.layout.menu("OWM_MT_overtools_menu", text="Overtools")


classes = (
    Preferences.OWMPreferences,
    # Setting props
    SettingTypes.OWModelSettings,
    SettingTypes.OWEntitySettings,
    SettingTypes.OWLightSettings,
    SettingTypes.OWMapSettings,
    #Panel
    UtilityOperators.OWMUtilityPanel,
    UtilityOperators.OWMModelLookPanel,
    #Menu
    OvertoolsMenu,
    #Operators
    shader_library_operators.OWMShaderLoadOp,
    shader_library_operators.OWMShaderSaveOp,
    UtilityOperators.OWMConnectAOOp,
    UtilityOperators.OWMDisconnectAOOp,
    UtilityOperators.OWMCleanupOp,
    UtilityOperators.OWMChangeModelLookOp,
    DatatoolLibHandler.OWMBuildTextureDB,
    DatatoolLibHandler.OWMFixTextures
)
classes_importers = (
    ImportModelOperator.ImportOWMDL,
    ImportMaterialOperator.ImportOWMAT,
    ImportEntityOperator.ImportOWENTITY,
    ImportMapOperator.ImportOWMAP,
    ImportAnimationOperator.ImportOWANIMCLIP,
    ImportMapWizard.ImportOWMapWizard,
    ImportSkinOperator.ImportOWSkinWizard,
    filehandler_operators.IO_FH_owmdl,
    filehandler_operators.IO_FH_owmat,
    filehandler_operators.IO_FH_owentity,
    filehandler_operators.IO_FH_owanimclip,
    filehandler_operators.IO_FH_owmap
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for cls in classes_importers:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(overtoolsMenuDraw)


def unregister():
    for cls in classes_importers:
        bpy.utils.unregister_class(cls)

    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(overtoolsMenuDraw)

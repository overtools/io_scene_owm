import bpy
from bpy.app.handlers import persistent


from . import ImportMaterialOperator
from . import ImportEntityOperator
from . import ImportMapOperator
from . import ImportModelOperator
from . import ImportSkinOperator
from . import LibraryHandler
from . import Preferences
from . import SettingTypes
from . import UtilityOperators
from . import ImportMapWizard
from . import ImportAnimationOperator
from . import DatatoolLibHandler

class OvertoolsMenu(bpy.types.Menu):
    bl_idname = 'OWM_MT_overtools_menu'
    bl_label = "Select"

    def draw(self, context):
        self.layout.operator(ImportSkinOperator.ImportOWSkin.bl_idname, text='Skin (wizard)')
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
    #OWEffectSettings,
    #Panel
    UtilityOperators.OWMUtilityPanel,
    UtilityOperators.OWMModelLookPanel,
    #Menu
    OvertoolsMenu,
    #Operators
    LibraryHandler.OWMLoadOp,
    LibraryHandler.OWMSaveOp,
    LibraryHandler.OWMLoadJSONOp,
    LibraryHandler.OWMConnectAOOp,
    LibraryHandler.OWMDisconnectAOOp,
    UtilityOperators.OWMCleanupOp,
    UtilityOperators.OWMCleanupTexOp,
    UtilityOperators.OWMChangeModelLookOp,
    DatatoolLibHandler.OWMBuildTextureDB,
    DatatoolLibHandler.OWMFixTextures,
    #Independent import
    ImportAnimationOperator.ImportOWANIMCLIP,
)
classes_importers = (
    ImportModelOperator.ImportOWMDL,
    ImportMaterialOperator.ImportOWMAT,
    ImportEntityOperator.ImportOWENTITY,
    ImportMapOperator.ImportOWMAP,
    ImportMapWizard.ImportOWMapWizard,
    ImportSkinOperator.ImportOWSkin
    # ImportOWEFFECT
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

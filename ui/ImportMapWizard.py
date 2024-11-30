from datetime import datetime

import bpy
from bpy.utils import smpte_from_seconds
import bpy.utils.previews

from . import LibraryHandler
from . import SettingTypes
from . import DatatoolLibUtil
from . import UIUtil
from ..importer import ImportMap
from ..readers.PathUtil import joinPath
from . import Preferences

MAPS = []
IDS = []
VARIANTS = []

class ImportOWMapWizard(bpy.types.Operator):
    bl_idname = 'import_mesh.overtools2_mapwiz'
    bl_label = 'Import Map Wizard'
    __doc__ = bl_label
    bl_options = {'UNDO'}

    def listMaps(self, context):
        global MAPS
        MAPS = DatatoolLibUtil.categoryList("Maps")
        return MAPS

    def listIDs(self, context):
        if self.map == "Select":
            return DatatoolLibUtil.DUMMY
        enum = DatatoolLibUtil.subCategoryList("Maps", self.map, True)
        IDS = enum
        return IDS

    def listVariants(self, context):
        if self.id == "Select":
            return DatatoolLibUtil.DUMMY
        global VARIANTS
        VARIANTS = DatatoolLibUtil.subCategoryList("Maps", joinPath(self.map, self.id), True, True, ".owmap")
        return VARIANTS

    def resetValues(self, context=None):
        ImportOWMapWizard.listIDs(self, None)
        self.id = "Select" if len(IDS) != 2 else IDS[1][0]
        self.variation = "Select"
        ImportOWMapWizard.resetVariation(self, None)
    
    def resetVariation(self, context=None):
        ImportOWMapWizard.listVariants(self, None)
        self.variation = "Select" if len(VARIANTS) != 2 else VARIANTS[1][0]

    modelSettings: bpy.props.PointerProperty(type=SettingTypes.OWModelSettings)

    mapSettings: bpy.props.PointerProperty(type=SettingTypes.OWMapSettings)

    entitySettings: bpy.props.PointerProperty(type=SettingTypes.OWEntitySettings)

    lightSettings: bpy.props.PointerProperty(type=SettingTypes.OWLightSettings)

    map: bpy.props.EnumProperty(items=listMaps, name="Map", update=resetValues)

    id: bpy.props.EnumProperty(items=listIDs, name="ID", update=resetVariation)
    
    variation: bpy.props.EnumProperty(items=listVariants, name="Variant")

    mouse:  bpy.props.BoolProperty(default=False)

    mousePos: bpy.props.IntVectorProperty(size=2, default=(0,0))

    @classmethod
    def poll(cls, context):
        if DatatoolLibUtil.isPathSet():
            if DatatoolLibUtil.categoryExists("Maps"):
                return True
            else:
                cls.poll_message_set('\'Maps\' folder not found.\nExtract some maps (extract-maps) or check the DataTool output path is set correctly in the addon preferences.')
                return False
        else:
            cls.poll_message_set('DataTool output path not set.\nTo use this wizard (not required), set the DataTool output path in the addon preferences.')
            return False

    def execute(self, context):
        if self.map == "Select":
            self.report({'ERROR'}, "No Map selected.")
            bpy.ops.import_mesh.overtools2_mapwiz('INVOKE_DEFAULT')
        elif self.id == "Select":
            self.report({'ERROR'}, "No ID selected.")
            bpy.ops.import_mesh.overtools2_mapwiz('INVOKE_DEFAULT')
        elif self.variation == "Select":
            self.report({'ERROR'}, "No Variation selected.")
            bpy.ops.import_mesh.overtools2_mapwiz('INVOKE_DEFAULT')
        else:
            t = datetime.now()
            ImportMap.init(joinPath(DatatoolLibUtil.getRoot(), "Maps", self.map, self.id, self.variation), self.mapSettings, self.modelSettings, self.lightSettings, self.entitySettings)
            UIUtil.log('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - t)))
        return {'FINISHED'}

    def invoke(self, context, event):
        # Defaults overrides
        self.modelSettings.importEmpties = False
        self.mousePos = (event.mouse_x, event.mouse_y)
        self.mouse = True
        context.window.cursor_warp(int(context.window.width/2), int(context.window.height/2) + 200)
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        if self.mouse:
            context.window.cursor_warp(*self.mousePos)
            self.mouse = False
        layout = self.layout

        rootCol = layout.column()
        topCol = rootCol.column()
        topCol.scale_y = 1.5
        topCol.ui_units_y = 5
        topCol.prop(self, 'map')
        if self.map != "Select":
            topCol.prop(self, 'id')
            if self.id != "Select":
                topCol.prop(self, 'variation')

        rootCol.label(text="Import Options")
        bottomCol = rootCol.row()
        col = bottomCol.column()
        SettingTypes.OWMapSettings.draw(self, self.mapSettings, col)
        
        col = bottomCol.column()

        SettingTypes.OWModelSettings.draw(self, self.modelSettings, col)
        SettingTypes.OWModelSettings.draw_armature(self, self.modelSettings, col, False)
        if Preferences.getPreferences().devMode:
            col2 = col.column()
            col2.enabled = self.modelSettings.importMaterial
            col2.prop(self.modelSettings, 'saveMaterialDB')

        entityAndLightsCol = bottomCol.column()
        
        entitySettingsLayout = entityAndLightsCol.column()
        entitySettingsLayout.enabled = self.mapSettings.importDetails
        SettingTypes.OWEntitySettings.draw(self, self.entitySettings, entitySettingsLayout)

        lightSettingsLayout = entityAndLightsCol.column()
        lightSettingsLayout.enabled = self.mapSettings.importLights
        SettingTypes.OWLightSettings.draw(self, self.lightSettings, lightSettingsLayout)
        
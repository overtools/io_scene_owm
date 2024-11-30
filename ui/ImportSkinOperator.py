from datetime import datetime

import bpy
from bpy.utils import smpte_from_seconds
import bpy.utils.previews

from . import LibraryHandler
from . import SettingTypes
from . import DatatoolLibUtil
from . import UIUtil
from ..importer import ImportEntity
from ..readers import PathUtil
from ..readers.PathUtil import joinPath

heroLabels = {"D.Va":"D.Va cheat sheet:|Gameplay3P: Pilot, Pistol|Showcase: Meka, Pilot Torso, Pilot, Pistol (Left)|HighlightIntro: Meka, Pilot Torso, Pilot, Pistol (Right)|Hero Gallery: Meka, Pilot Torso, Pilot"}
heroDefaults = {"D.Va": "Showcase"}


ICONS = {"loaded":{}}
HEROES = []
SKINS = []
VARIANTS = []
ENTITIES = []
VARIANTCACHE = {}


class ImportOWSkin(bpy.types.Operator):
    bl_idname = 'import_mesh.overtools2_skin'
    bl_label = 'Import Hero Skin'
    __doc__ = bl_label
    bl_options = {'UNDO'}

    def listHeroes(self, context):
        global HEROES
        HEROES = [hero for hero in DatatoolLibUtil.categoryList("Heroes") if DatatoolLibUtil.categoryExists(joinPath("Heroes",hero[0], "Skin")) or hero[0] == "Select"]
        return HEROES

    def listSkins(self, context):
        global SKINS
        enum = [("Select", "Select", "", 0)]
        if self.hero == "Select":
            return enum
        path = joinPath(self.hero, "Skin")
        skinCategories = DatatoolLibUtil.subCategoryList("Heroes", path)
        i = 1
        for category in skinCategories:
            skinQualities = DatatoolLibUtil.subCategoryList("Heroes", joinPath(path, category))
            if "Common" not in skinQualities and "Epic" not in skinQualities and "Rare" not in skinQualities and "Legendary" not in skinQualities:
                for skin in skinQualities:
                    enum.append((joinPath(path, category, skin), "{} ({})".format(skin, category), "{}".format(category), i))
                    i+=1
            else:
                for quality in skinQualities:
                    skins = DatatoolLibUtil.subCategoryList("Heroes", joinPath(path, category, quality))
                    for skin in skins:
                        enum.append((joinPath(path, category, quality, skin), "{} ({})".format(skin, category), "{}, {} Quality".format(category,quality), i))
                        i+=1
        SKINS = enum
        return enum

    def listEntities(self, context):
        global ENTITIES
        placeholder = [("Gameplay3P", "place holder so blender doesn't go insane", "")]
        if self.skin == "Select":
            return placeholder
        path = joinPath(self.skin, self.variant if self.mythic else "", "Entities")
        known = []
        unknown = []
        try:
            entities = DatatoolLibUtil.subCategoryList("Heroes", path)
            for entity in entities:
                if entity.startswith("0"):
                    unknown.append((entity,entity,""))
                else:
                    known.append((entity,entity,""))
        except:
            self.mythic = True
            return placeholder
        ENTITIES = known+unknown
        return ENTITIES

    def listMythicVariants(self, context):
        global VARIANTS,VARIANTCACHE,ICONS
        if self.skin not in ICONS:
            ICONS[self.skin] = bpy.utils.previews.new()
            ICONS["loaded"][self.skin] = {}
            
        VARIANTCACHE.setdefault(self.skin, DatatoolLibUtil.subCategoryList("Heroes", self.skin))
        enum = []
        i=0
        for variant in VARIANTCACHE[self.skin]:
            if variant == "Models" or variant == "Effects" or variant == "GUI" or variant == "Sound":
                continue
            if variant not in ICONS["loaded"]:
                iconPath = joinPath(DatatoolLibUtil.getRoot(), "Heroes", self.skin, variant, "Info.png")
                icon = ICONS[self.skin].load(variant, iconPath, 'IMAGE')
                ICONS["loaded"][variant] = int(icon.icon_id)

            enum.append((variant, variant, variant, ICONS["loaded"][variant], i))
            i+=1
        VARIANTS = enum
        return VARIANTS

    def resetSkin(self, context):
        if self.hero != "Select":
            self.mythic = False
            self.skin = "Select"
    
    def resetEntity(self, context):
        if self.skin != "Select":
            defaultEntity = heroDefaults.get(self.hero, "Gameplay3P")
            self.entity = defaultEntity
            # setting a second time helps mythics.. (first doesn't stick)
            self.entity = defaultEntity


    modelSettings: bpy.props.PointerProperty(type=SettingTypes.OWModelSettings)

    entitySettings: bpy.props.PointerProperty(type=SettingTypes.OWEntitySettings)

    hero: bpy.props.EnumProperty(items=listHeroes, name="Hero", update=resetSkin)

    skin: bpy.props.EnumProperty(items=listSkins, name="Skin", update=resetEntity)
    
    entity: bpy.props.EnumProperty(items=listEntities, name="Entity")

    mythic: bpy.props.BoolProperty(default=False)

    variant: bpy.props.EnumProperty(items=listMythicVariants, name="Mythic Variant")

    mouse:  bpy.props.BoolProperty(default=False)

    mousePos: bpy.props.IntVectorProperty(size=2, default=(0,0))

    @classmethod
    def poll(cls, context):
        if DatatoolLibUtil.isPathSet():
            if DatatoolLibUtil.categoryExists("Heroes"):
                return True
            else:
                cls.poll_message_set('\'Heroes\' folder not found.\nExtract some skins (extract-unlocks) or check the DataTool output path is set correctly in the addon preferences.')
                return False
        else:
            cls.poll_message_set('DataTool output path not set.\nTo use this wizard (not required), set the DataTool output path in the addon preferences.')
            return False

    def execute(self, context):
        self.modelSettings.importMatless = not self.mythic
        if self.hero == "Select":
            self.report({'ERROR'}, "No Hero selected.")
            bpy.ops.import_mesh.overtools2_skin('INVOKE_DEFAULT')
        elif self.skin == "Select":
            self.report({'ERROR'}, "No Skin selected.")
            bpy.ops.import_mesh.overtools2_skin('INVOKE_DEFAULT')
        else:
            t = datetime.now()
            skinName = PathUtil.nameFromPath(self.skin)
            name = "{} {} ({})".format(self.hero, skinName, self.entity)
            entityPath = joinPath(DatatoolLibUtil.getRoot(), "Heroes", self.skin,
                self.variant if self.mythic else "", "Entities",
                self.entity, self.entity+".owentity")
            ImportEntity.init(entityPath, self.modelSettings, self.entitySettings, name)
            UIUtil.log('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - t)))
        return {'FINISHED'}

    def invoke(self, context, event):
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
        topRow = rootCol.row()
        topRow.scale_y = 2
        topRow.ui_units_y = 7
        col = topRow.column()
        col.prop(self, 'hero')
        drawEnt = False
        if self.hero != "Select":
            col.prop(self, 'skin')
            if self.skin != "Select":
                if self.mythic:
                    topRow.ui_units_y = 10.5
                    split = col.split(factor=.235)
                    split.label(text="Mythic Variant")
                    split.template_icon_view(self, 'variant', show_labels=True, scale=2, scale_popup=5)
                    if self.variant != "0":
                        drawEnt = True
                else:
                    drawEnt = True

                if drawEnt:
                    col.prop(self, 'entity')
        
        bottomRow = rootCol.row()
        col = bottomRow.column()
        col.ui_units_x = .3
        col.label(text="Import Options")
        SettingTypes.OWModelSettings.draw(self, self.modelSettings, col)

        
        col = bottomRow.column()
        col.ui_units_x = .3
        col.separator(factor=3)
        SettingTypes.OWEntitySettings.draw(self, self.entitySettings, col)
        SettingTypes.OWModelSettings.draw_armature(self, self.modelSettings, col)

        col = bottomRow.column()
        col.ui_units_x = .6
        if drawEnt:
            if self.hero in heroLabels:
                for line in heroLabels[self.hero].split("|"):
                    col.label(text=line)

        
        
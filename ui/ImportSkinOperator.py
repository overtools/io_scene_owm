from datetime import datetime

import bpy
from bpy.utils import smpte_from_seconds
import bpy.utils.previews

from . import SettingTypes
from . import DatatoolLibUtil
from . import UIUtil
from ..importer import ImportEntity
from ..readers import PathUtil
from ..readers.PathUtil import joinPath

HERO_LABELS = {
    "D.Va": 
        "D.Va cheat sheet:|"
        "Gameplay3P: Pilot, Pistol|"
        "Showcase: Meka, Pilot Torso, Pilot, Pistol (Left)|"
        "HighlightIntro: Meka, Pilot Torso, Pilot, Pistol (Right)|"
        "Hero Gallery: Meka, Pilot Torso, Pilot"
}
HERO_DEFAULT_ENTITIES = {
    "D.Va": "Showcase"
}

class SkinWizardCache:
    HEROES = []
    SKINS = []
    ENTITIES = []

    VARIANTS = []
    LAST_VARIANTS_SKIN = ""

    VARIANT_ICONS = None

    _GENERIC_PLACEHOLDER = ("Select", "Select", "", 0)
    _ENTITY_PLACEHOLDER = ("Gameplay3P", "", "", 0)

    @classmethod
    def list_heroes(cls):
        cls.HEROES.clear()
        cls.HEROES.append(cls._GENERIC_PLACEHOLDER)

        for hero_tuple in DatatoolLibUtil.categoryList("Heroes"):
            if not DatatoolLibUtil.categoryExists(joinPath("Heroes", hero_tuple[0], "Skin")):
                continue
            cls.HEROES.append(hero_tuple)
        
        return cls.HEROES
    
    @classmethod
    def list_skins(cls, hero):
        cls.SKINS.clear()
        cls.SKINS.append(cls._GENERIC_PLACEHOLDER)

        if hero == "Select":
            return cls.SKINS
        
        skins_path = joinPath(hero, "Skin")
        index = 1
        for category in DatatoolLibUtil.subCategoryList("Heroes", skins_path):
            category_subfolder = DatatoolLibUtil.subCategoryList("Heroes", joinPath(skins_path, category))

            if "Common" not in category_subfolder and "Epic" not in category_subfolder and "Rare" not in category_subfolder and "Legendary" not in category_subfolder:
                for skin in category_subfolder:
                    cls.SKINS.append((joinPath(skins_path, category, skin), "{} ({})".format(skin, category), "{}".format(category), index))
                    index += 1
                continue
            
            for rarity in category_subfolder:
                skins = DatatoolLibUtil.subCategoryList("Heroes", joinPath(skins_path, category, rarity))
                for skin in skins:
                    cls.SKINS.append((joinPath(skins_path, category, rarity, skin), "{} ({})".format(skin, category), "{}, {} Quality".format(category,rarity), index))
                    index += 1
        return cls.SKINS
    
    @classmethod
    def list_mythic_variants(cls, skin, is_mythic):
        cls.VARIANTS.clear()

        if skin == "Select" or not is_mythic:
            return cls.VARIANTS

        # skin is actually a path.. to the skin from heroes root dir
        if skin == cls.LAST_VARIANTS_SKIN:
            # calculating this is very expensive
            return cls.VARIANTS

        variant_idx=0
        for variant in DatatoolLibUtil.subCategoryList("Heroes", skin):
            if variant == "Models" or variant == "Effects" or variant == "GUI" or variant == "Sound":
                continue

            icon_path = joinPath(DatatoolLibUtil.getRoot(), "Heroes", skin, variant, "Info.png")
            if icon_path not in cls.VARIANT_ICONS:
                cls.VARIANT_ICONS.load(icon_path, icon_path, 'IMAGE')

            cls.VARIANTS.append((variant, variant, variant, cls.VARIANT_ICONS[icon_path].icon_id, variant_idx))
            variant_idx+=1

        return cls.VARIANTS
    
    @classmethod
    def list_entities(cls, skin, variant, is_mythic):
        cls.ENTITIES.clear()

        if skin == "Select":
            cls.ENTITIES.append(cls._ENTITY_PLACEHOLDER)
            return cls.ENTITIES
        
        variant = variant if is_mythic else ""
        entities_path = joinPath(skin, variant, "Entities")

        named_entities = []
        unnamed_entities = []
        for entity_folder in DatatoolLibUtil.subCategoryList("Heroes", entities_path):
            if entity_folder.startswith("0"):
                unnamed_entities.append((entity_folder, entity_folder, ""))
            else:
                named_entities.append((entity_folder, entity_folder, ""))
        
        cls.ENTITIES.extend(named_entities)
        cls.ENTITIES.extend(unnamed_entities)
        return cls.ENTITIES
    
    @classmethod
    def clear(cls):
        cls.HEROES.clear()
        cls.SKINS.clear()
        cls.ENTITIES.clear()
        cls.LAST_VARIANTS_SKIN = ""
        cls.VARIANT_ICONS.clear()

    @classmethod
    def register(cls):
        cls.VARIANT_ICONS = bpy.utils.previews.new()

    @classmethod
    def unregister(cls):
        if cls.VARIANT_ICONS is not None:
            bpy.utils.previews.remove(cls.VARIANT_ICONS)

class ImportOWSkinWizard(bpy.types.Operator):
    bl_idname = 'import_mesh.overtools2_skin'
    bl_label = 'Import Hero Skin'
    __doc__ = bl_label
    bl_options = {'UNDO'}

    def list_heroes(self, context):
        return SkinWizardCache.list_heroes()

    def list_skins(self, context):
        return SkinWizardCache.list_skins(self.hero)
    
    def list_mythic_variants(self, context):
        return SkinWizardCache.list_mythic_variants(self.skin, self.is_mythic)

    def list_entities(self, context):
        return SkinWizardCache.list_entities(self.skin, self.mythic_variant, self.is_mythic)
    
    def on_hero_changed(self, context):
        if self.hero == "Select":
            return
        
        self.is_mythic = False
        self.skin = "Select"
    
    def on_skin_changed(self, context):
        if self.skin == "Select":
            return
        
        # needs to be before we touch self.entity
        # it triggers eval
        non_mythic_entities_path = joinPath("Heroes", self.skin, "Entities")
        self.is_mythic = not DatatoolLibUtil.categoryExists(non_mythic_entities_path)

        default_entity = HERO_DEFAULT_ENTITIES.get(self.hero, "Gameplay3P")
        self.entity = default_entity

    # importer settings
    modelSettings: bpy.props.PointerProperty(type=SettingTypes.OWModelSettings)
    entitySettings: bpy.props.PointerProperty(type=SettingTypes.OWEntitySettings)

    # selectors
    hero: bpy.props.EnumProperty(items=list_heroes, name="Hero", update=on_hero_changed)
    skin: bpy.props.EnumProperty(items=list_skins, name="Skin", update=on_skin_changed)
    mythic_variant: bpy.props.EnumProperty(items=list_mythic_variants, name="Mythic Variant")
    entity: bpy.props.EnumProperty(items=list_entities, name="Entity")

    # internal
    is_mythic: bpy.props.BoolProperty(default=False)
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
        if self.hero == "Select":
            self.report({'ERROR'}, "No Hero selected.")
            return {'FINISHED'}
        elif self.skin == "Select":
            self.report({'ERROR'}, "No Skin selected.")
            return {'FINISHED'}

        entity_path = joinPath(DatatoolLibUtil.getRoot(), "Heroes", self.skin,
            self.mythic_variant if self.is_mythic else "", "Entities",
            self.entity, self.entity+".owentity")
        
        skin_name = PathUtil.nameFromPath(self.skin)
        full_name = "{} {} ({})".format(self.hero, skin_name, self.entity)

        self.modelSettings.importMatless = not self.is_mythic

        start_time = datetime.now()
        ImportEntity.init(entity_path, self.modelSettings, self.entitySettings, full_name)
        UIUtil.log('Done. SMPTE: %s' % (smpte_from_seconds(datetime.now() - start_time)))

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
                if self.is_mythic:
                    topRow.ui_units_y = 10.5
                    split = col.split(factor=.235)
                    split.label(text="Mythic Variant")
                    split.template_icon_view(self, 'mythic_variant', show_labels=True, scale=2, scale_popup=5)
                    if self.mythic_variant != "0":
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
            if self.hero in HERO_LABELS:
                for line in HERO_LABELS[self.hero].split("|"):
                    col.label(text=line)

    @staticmethod
    def register():
        SkinWizardCache.register()

    @staticmethod
    def unregister():
        SkinWizardCache.unregister()

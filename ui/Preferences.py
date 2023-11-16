import bpy

def getPreferences():
    return bpy.context.preferences.addons[__package__.split(".")[0]].preferences

class OWMPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__.split(".")[0] # ¯\_(ツ)_/¯

    devMode: bpy.props.BoolProperty(
        name="Enable Developer Mode",
        default=False,
    )

    debugLogging: bpy.props.BoolProperty(
        name="Enable Debug Logging",
        default=False,
    )

    experimental: bpy.props.BoolProperty(
        name="Enable Experimental Features",
        default=False,
    )

    datatoolOutPath: bpy.props.StringProperty(
        name="Datatool output path",
        description="Path to the datatool output folder",
        subtype='DIR_PATH',
        default='')

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "datatoolOutPath")
        layout.separator()
        #row.prop(self, "experimental")
        layout.label(text="Developer Options (leave these alone if you don't know what you're doing)")
        row = layout.row()
        row.prop(self, "devMode")
        #row.prop(self, "debugLogging")
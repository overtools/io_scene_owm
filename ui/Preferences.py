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
        name="DataTool output path",
        description="Path to the DataTool output folder",
        subtype='DIR_PATH',
        default='')

    def draw(self, context):
        self.layout.prop(self, "datatoolOutPath")
        self.layout.label(text="(should be the root folder, not the \"Heroes\" or \"Maps\" folder created by DataTool)")
        
        developerOptionsBox = self.layout.box()
        developerOptionsBox.label(text="Developer Options:")
        developerOptionsBox.label(text="(leave these alone unless you know what you're doing)")
        #developerOptionsBox.prop(self, "experimental")
        developerOptionsBox.prop(self, "devMode")
        #developerOptionsBox.prop(self, "debugLogging")
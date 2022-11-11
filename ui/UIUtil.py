import bpy

def createPopup(title, label, icon='ERROR'):
    bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=" "+label), title = title, icon = icon)

def ow1FileError():
    createPopup("Unsupported file","Overwatch 1 exports are not supported")

def legacyFileError():
    createPopup("Phased out format", "Please re-export using the latest datatool")

def newerFileError():
    createPopup("Newer Unsupported file","File has a newer format than supported. Please update the addon.")

def fileOpenError():
    createPopup("Unable to open file","¯\_(ツ)_/¯")

def fileFormatError(extension):
    createPopup("Error reading file", "File format not recognized; This might not be an .{} file".format(extension))

def owmap20Warning():
    createPopup("Older map export detected", "Lights weren't imported")
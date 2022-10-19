from venv import create
import bpy

def createPopup(title, label, icon='ERROR'):
    bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=" "+label), title = title, icon = icon)

def legacyFileError():
    createPopup("Unsupported file","Overwatch 1 exports are not supported")

def fileOpenError():
    createPopup("Unable to open file","¯\_(ツ)_/¯")

def fileFormatError(extension):
    createPopup("Error reading file", "File format not recognized; This might not be an .{} file".format(extension))

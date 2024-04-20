import bpy
import inspect
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

def updateProgressbar(i, total):
    def drawProgress(header, context):
        header.layout.progress(factor = i/total, type = 'RING', text = "Loading models {}/{}".format(i, total))
    
    if bpy.app.version[0] >= 4:
        setStatus(drawProgress)

def setStatus(text):
    if bpy.app.version[0] >= 4:
        bpy.context.workspace.status_text_set(text)

def log(text):
    caller = inspect.stack()[1].filename.split("\\")[-1].replace(".py", "")
    print("[owm]", caller+":", text)

def consoleProgressBar(op, current, total, bar_length=20, caller=""):
    updateProgressbar(current, total)
    fraction = current / total

    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '

    ending = '\n' if current == total    else '\r'
    print(f'[owm] {caller}: {op} [{arrow}{padding}] {int(fraction*100)}%', end=ending)
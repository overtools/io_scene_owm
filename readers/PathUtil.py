import os.path
from enum import Enum

joinPath = os.path.join

scan = os.scandir

# this still should not be on me weirdmush
class AssetTypes(Enum):
    Model = ("Models",".owmdl", ".00C")
    Entity = ("Entities", ".owentity", "")
    Effect = ("Effects", ".oweffect", ".00D")
    ModelLook = ("ModelLooks", ".owmat", ".01A")

def buildAssetPath(startPath, relativeRoot, type, filename):
    folder, extension, origExtension = type.value
    return joinPath(startPath, relativeRoot, folder, filename if type != AssetTypes.ModelLook else "", filename.replace(origExtension, "")+extension)

def pathRoot(path):
    return os.path.split(path)[0]

def checkExistence(filename):
    return os.path.exists(normPath(filename))

def pathText(path):
    return os.path.splitext(path)[0]

def listPath(path):
    return os.listdir(normPath(path))

def nameFromPath(path):
    return os.path.splitext(os.path.basename(path))[0]

def makePathAbsolute(root, path):
    if not os.path.isabs(path):
        return normPath('%s/%s' % (root, path))
    return path

def normPath(path):
    return os.path.normpath(path.replace('\\', os.path.sep).replace('/', os.path.sep))

def isValidPath(path):
    return path is not None and len(path) > 4

from ..readers import PathUtil
from . import Preferences

DUMMY = [("Select", "Select", "", 0)]

def getRoot():
    return Preferences.getPreferences().datatoolOutPath

def isPathSet():
    return getRoot() != None and getRoot() != ""

def categoryPath(category):
    return PathUtil.normPath(PathUtil.joinPath(getRoot(), category))

def categoryExists(category):
    return PathUtil.checkExistence(categoryPath(category))

def categoryList(category):
    return enumDir(categoryPath(category))

def subCategoryList(category, sub, enum=False, file=False, fileFilter=None):
    dir = PathUtil.joinPath(categoryPath(category), sub)
    return enumDir(dir, file, fileFilter) if enum else [item.name for item in PathUtil.scan(dir) if item.is_dir()]

def enumDir(dir, file=False, fileFilter=None):
    enum = [("Select", "Select", "", 0)]
    i = 1
    with PathUtil.scan(dir) as items:
        for item in items:
            check = item.is_file if file else item.is_dir
            if check():
                displayName = item.name
                if fileFilter:
                    if fileFilter not in item.name:
                        continue
                    else:
                        displayName = item.name.replace(fileFilter, "")
                enum.append((item.name, displayName, "", i))
                i+=1
    return tuple(enum)
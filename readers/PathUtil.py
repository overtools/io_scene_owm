import os.path


def pathRoot(path):
    return os.path.split(path)[0]


def getModelPath(entPath, model):
    return normPath(os.path.dirname(os.path.dirname(os.path.dirname(entPath))) + '/Models/' + model + '/' + model.replace('.00C','') + '.owmdl')


def getEntPath(entPath, ent):
    return normPath(os.path.dirname(os.path.dirname(entPath)) + '/{}/{}.owentity'.format(ent, ent))


def getEffectPath(entPath, ent):
    return normPath(os.path.dirname(os.path.dirname(os.path.dirname(entPath))) + '/Effects/' + ent + '/' + ent.replace('.00D','') + '.oweffect')


def checkExistence(filename):
    return os.path.exists(filename)


def pathText(path):
    return os.path.splitext(path)[0]


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

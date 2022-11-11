from ..readers import PathUtil

class OWMFile:
    def __init__(self, path=None, GUID=None):
        self.GUID = GUID
        self.filepath = None
        if path:
            self.setPath(path)

    def __bool__(self):
        return self.filepath is not None

    def setPath(self, filepath):
        self.filepath = filepath
        if not self.GUID:
            self.GUID = PathUtil.nameFromPath(filepath)

    def __repr__(self):
        return '<{}>: GUID:{}, Path: {}'.format(__class__.__name__, self.GUID, self.filepath)
        
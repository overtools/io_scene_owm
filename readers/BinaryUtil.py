import struct
from io import BytesIO
from . import PathUtil
from ..ui import UIUtil

def compatibilityCheck(format, major, minor):
    def asFloat(major,minor):
        return float(str(major)+"."+str(minor))

    if major < 2:
        UIUtil.ow1FileError()
        return False

    if major > format.major:
        UIUtil.newerFileError()
        return False

    if asFloat(major,minor) < asFloat(*format.minimum):
        UIUtil.legacyFileError()
        return False
    
    return True

def openStream(filename, extension):
    filename = PathUtil.normPath(filename)
    if not filename.endswith(extension):
        UIUtil.fileFormatError(extension)
        return None
    stream = None
    try:
        with open(filename, 'rb') as f:
            stream = BinaryFile(f.read())
            stream.path = PathUtil.pathRoot(filename)
    except:
        UIUtil.fileOpenError()
        UIUtil.log("failed to open file {}".format(filename))
        return None
    return stream

class BinaryFile(BytesIO):
    def readString(self, absPaths=False):
        lb1 = struct.unpack('B', self.read(1))[0]
        lb2 = 0

        if lb1 > 128:
            lb2 = struct.unpack('B', self.read(1))[0]

        l = (lb1 % 128) + (lb2 * 128)
        if l == 0:
            return ''
        s = self.read(l)
        s = s.decode('utf8')

        if s == "null":
            return None
        if "\\" in s and absPaths:
            return PathUtil.makePathAbsolute(self.path, s)
        return s


    def readSingle(self, fmt):
        return list(struct.unpack(fmt, self.read(struct.calcsize(fmt))))

    def readClass(self, fmt, cls, absPath=False, flat=True):
        return cls(*self.readFmt(fmt, absPath, flat))

    def readClassArray(self, fmt, cls, count, absPath=False, flat=True):
        l = []
        for i in range(count):
            l.append(self.readClass(fmt, cls, absPath, flat))
        return l

    def readCoupledClass(self, mainFmt, mainCls, coupledFmt, coupledCls, before, mainFlat=False, coupledFlat=False):
        if before:
            coupledData = self.readFmt(coupledFmt, flat=coupledFlat)
        mainData = self.readFmt(mainFmt, flat=mainFlat, absPath=True)
        if not before:
            coupledData = self.readFmt(coupledFmt, flat=coupledFlat)
        return mainCls(*mainData, coupledCls(*coupledData))

    def readCoupledClassArray(self, mainFmt, mainCls, coupledFmt, coupledCls, before, count, mainFlat=False, coupledFlat=False):
        l = []
        for i in range(count):
            l.append(self.readCoupledClass(mainFmt, mainCls, coupledFmt, coupledCls, before, mainFlat, coupledFlat))
        return l

    def readFmt(self, fmts, absPath=False, flat=True):
        a = []
        for fmt in fmts:
            if fmt == str:
                a.append(self.readString(absPath))
            else:
                if flat:
                    a += self.readSingle(fmt)
                else:
                    a.append(self.readSingle(fmt))
        if len(a) == 1 and flat:
            return a[0]
        return a

    def readFmtArray(self, fmt, count):
        return tuple(struct.iter_unpack(fmt, self.read(struct.calcsize(fmt) * count)))

    def readFmtFlatArray(self, fmt, count):
        return list(struct.unpack(fmt * count, self.read(struct.calcsize(fmt) * count)))

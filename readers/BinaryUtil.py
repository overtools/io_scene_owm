import struct
from io import BytesIO
from . import PathUtil
from ..ui import UIUtil

def openStream(filename):
    filename = PathUtil.normPath(filename)
    stream = None
    try:
        with open(filename, 'rb') as f:
            stream = BytesIO(f.read())
    except:
        UIUtil.fileOpenError()
        return None
    return stream

def readString(file):
    lb1 = struct.unpack('B', file.read(1))[0]
    lb2 = 0

    if lb1 > 128:
        lb2 = struct.unpack('B', file.read(1))[0]

    l = (lb1 % 128) + (lb2 * 128)
    if l == 0:
        return ''
    s = file.read(l)
    s = s.decode('utf8')
    return s if s != "null" else None


def read(file, fmt):
    return list(struct.unpack(fmt, file.read(struct.calcsize(fmt))))


def readFmt(file, fmts):
    a = []
    for fmt in fmts:
        if fmt == str:
            a += [readString(file)]
        else:
            a += [read(file, fmt)]
    if len(a) == 1:
        return a[0]
    return a


def readFmtFlat(file, fmts):
    a = []
    for fmt in fmts:
        if fmt == str:
            a += [readString(file)]
        else:
            a += read(file, fmt)
    if len(a) == 1:
        return a[0]
    return a

def readFmtArray(file, fmt, count):
    return tuple(struct.iter_unpack(fmt, file.read(struct.calcsize(fmt) * count)))

def readFmtFlatArray(file, fmt, count):
    return list(struct.unpack(fmt * count, file.read(struct.calcsize(fmt) * count)))

import bz2
import gzip
import io
import urllib

from omnio import http, path, s3


_scheme_opens = {
    '': path._open,
    'file': path._open,
    'http': http._open,
    'https': http._open,
    's3': s3._open,
}


def open_(uri, mode='rb', encoding=None, errors=None,
          newline=None):

    # Allow all standard mode characters, leaving the responsibility
    # of supporting them or not to the scheme open functions.
    if not all(c in 'rwxatb+Ujz' for c in mode):
        msg = 'invalid mode: {}'.format(mode)
        raise ValueError(msg)

    if not (('r' in mode) ^ ('w' in mode) ^ ('x' in mode) ^ ('a' in mode)):
        msg = 'must have exactly one of create/read/write/append mode'
        raise ValueError(msg)

    if 'b' in mode and 't' in mode:
        msg = "can't have text and binary mode at once"
        raise ValueError(msg)

    if 'b' in mode and encoding is not None:
        msg = "binary mode doesn't take an encoding argument"
        raise ValueError(msg)

    if 'b' in mode and errors is not None:
        msg = "binary mode doesn't take an errors argument"
        raise ValueError(msg)

    if 'b' in mode and newline is not None:
        msg = "binary mode doesn't take an newline argument"
        raise ValueError(msg)

    if 'j' in mode and 'z' in mode:
        msg = "can't use more than one compression argument"
        raise ValueError(msg)

    parsed_uri = urllib.parse.urlparse(uri)
    scheme_open = _scheme_opens[parsed_uri.scheme]

    # Text encoding and compression are handled with wrapper
    # classes. We always do the underlying open in binary mode.
    rw_mode = mode
    for s in 'tbjz':
        rw_mode = rw_mode.replace(s, '')

    fd = scheme_open(uri, rw_mode + 'b')

    if 'j' in mode:
        fd = BZ2FileWrapper(fd, rw_mode)

    if 'z' in mode:
        fd = GzipFileWrapper(fd, rw_mode)

    if 't' in mode:
        fd = io.TextIOWrapper(fd, encoding=encoding, errors=errors,
                              newline=newline)

    return fd


class BZ2FileWrapper(bz2.BZ2File):
    def __init__(self, fd, mode):
        self._fileobj = fd
        super(BZ2FileWrapper, self).__init__(fd, mode=mode)

    def close(self):
        super(BZ2FileWrapper, self).close()
        self._fileobj.close()


class GzipFileWrapper(gzip.GzipFile):
    def __init__(self, fd, mode):
        self._fileobj = fd
        super(GzipFileWrapper, self).__init__(fileobj=fd, mode=mode)

    def close(self):
        super(GzipFileWrapper, self).close()
        self._fileobj.close()

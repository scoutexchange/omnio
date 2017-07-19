import gzip
import io
import urllib

from omnio import http, s3


_scheme_opens = {
    '': open,
    'file': open,
    'http': http.open_,
    'https': http.open_,
    's3': s3.open_,
    's3n': s3.open_,
    's3u': s3.open_,
}


class GzipFileWrapper(gzip.GzipFile):
    def __init__(self, fd, mode):
        self._fileobj = fd
        super(GzipFileWrapper, self).__init__(fileobj=fd, mode=mode)

    def close(self):
        super(GzipFileWrapper, self).close()
        self._fileobj.close()


def open_(uri, mode='r', buffering=-1, encoding=None, newline=None,
          closefd=None, opener=None):

    if not all(c in 'rwxatb+z' for c in mode):
        msg = 'invalid mode: {}'.format(mode)
        raise ValueError(msg)

    if not (('r' in mode) ^ ('w' in mode) ^ ('x' in mode) ^ ('a' in mode)):
        msg = 'must have exactly one of create/read/write/append mode'
        raise ValueError(msg)

    if 'b' in mode and 't' in mode:
        msg = "can't have text and binary mode at once"
        raise ValueError(msg)

    if 'b' in mode and encoding is not None:
        msg = "binary mode doesn't take an encodinqg argument"
        raise ValueError(msg)

    # We want to support the standard python file open interface,
    # but be clear that the following options aren't currently
    # supported. Some of them could be in the future.
    if buffering != -1:  # pragma: no cover
        raise NotImplementedError('buffering kwarg')
    if newline is not None:  # pragma: no cover
        raise NotImplementedError('newline kwarg')
    if closefd is not None:  # pragma: no cover
        raise NotImplementedError('closefd kwarg')
    if opener is not None:  # pragma: no cover
        raise NotImplementedError('opener kwarg')

    parsed_uri = urllib.parse.urlparse(uri)
    scheme_open = _scheme_opens[parsed_uri.scheme]

    # Text encoding and gzip compression are handled with wrapper
    # classes. Always do the underlying open in binary mode.
    fd_mode = mode.replace('t', '').replace('b', '').replace('z', '')
    fd = scheme_open(uri, fd_mode + 'b')

    if 'z' in mode:
        fd = GzipFileWrapper(fd, fd_mode)

    if 'b' not in mode:
        fd = io.TextIOWrapper(fd, encoding=encoding)

    return fd

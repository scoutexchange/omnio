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


def default_config():
    return {
        "file": {},
        "http": {"iter_content_chunk_size": 512},
        "s3": {
            "upload_part_size": 5 * 1024**2,
            "boto_client_config_args": [],
            "boto_client_config_kwargs": {},
        },
    }


def open_(uri, mode='rb', encoding=None, errors=None, newline=None, config=None):
    """
    Open URI and return a file-like stream.

    uri -- URI or local path. Supported URI schemes are `file`,
    `http`, and `s3`. Local paths may be specified by as ordinary path
    strings.

    mode -- Optional string that specifies the mode in which the
    file is opened. It defaults to 'rb' which means open for reading
    in binary mode. Supported mode characters are as follows:

    ========= =======================================================
    Character Meaning
    --------- -------------------------------------------------------
    'r'       open for reading (default)
    'w'       open for writing, truncating the file first
    'b'       binary mode (default)
    't'       text mode
    'z'       use gzip compression
    'j'       use bzip2 compression
    ========= =======================================================

    These characters can be composed into valid modes. Binary mode is
    always the default, so some mode specifications are equivalent.
    The complete list of supported modes are as follows:

    ============= ===================================================
    Mode          Meaning
    ------------- ---------------------------------------------------
    'r', 'rb'     read bytes
    'rt'          read and decode to unicode
    'rz', 'rbz'   read, decompressing gzip to bytes
    'rj', 'rbj'   read, decompressing bzip2 to bytes
    'rtz'         read, decompress gzip to bytes, decode to unicode
    'rtj'         read, decompress bzip2 to bytes, decode to unicode
    'w', 'wb'     write bytes
    'wt'          write unicode, encoding to bytes
    'wz', 'wbz'   write bytes, compress with gzip
    'wj', 'wbj'   write bytes, compress with bzip2
    'wtz'         write unicode, encode to bytes, compress with gzip
    'wtj'         write unicode, encode to bytes, compress with bzip2
    ========= =======================================================

    * Some keyword arguments may be applicable to only certain modes.
    For example, `encoding` only applies to 't' (text) modes.

    * Some schemes may not support some modes.  For example, the http
    scheme currently does not support any 'w' (write) modes

    Returns a file-like object whose type depends on the scheme and
    the mode.

    Usage examples:

    # Read from an HTTTP URI to unicode
    with omnio.open('http://example.com/example.txt', 'rt') as f:
        for line in f:
            print(line)


    # Write and compress with gzip a megabyte of random data to s3
    import os

    data = os.urandom(1024**2)
    with omnio.open('s3://my-bucket/my-key', 'wbz') as f:
        f.write(data)


    # Read a bzip2 compressed csv file into a list of data rows
    import csv

    with omnio.open('data/example_data.csv.bz2', 'rtj') as f:
        reader = csv.reader(f)
        data = list(reader)
    """

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

    if config is None:
        config = default_config()

    fd = scheme_open(uri, rw_mode + 'b', config)

    if 'j' in mode:
        fd = BZ2FileWrapper(fd, rw_mode)

    if 'z' in mode:
        fd = GzipFileWrapper(fd, rw_mode)

    if 't' in mode:
        fd = io.TextIOWrapper(fd, encoding=encoding, errors=errors, newline=newline)

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

import glob
import urllib


def _open(uri, mode, *, config=None):
    parsed_uri = urllib.parse.urlparse(uri)
    return open(parsed_uri.path, mode)


def _iglob(uri, *, recursive=False, config=None):
    parsed_uri = urllib.parse.urlparse(uri)
    yield from glob.iglob(parsed_uri.path, recursive=False)

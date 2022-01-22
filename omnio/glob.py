"""
Drop in replacement module for python's filename globbing utility


"""

import urllib

from . import path, s3
from .config import default_config

# make the escape function available so omnio.glob
# is a true drop in replacement for stdlib glob
from glob import escape

assert escape


# map uri schemes to the appropriate iglob functions
_scheme_iglobs = {
    '': path._iglob,
    'file': path._iglob,
    's3': s3._iglob,
}


def glob(uri, *, recursive=False, config=None):
    """
    Return a list of paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    If recursive is true, the pattern '**' will match any files and
    zero or more directories and subdirectories.
    """
    return list(iglob(uri, recursive=recursive, config=config))


def iglob(uri, *, recursive=False, config=None):
    """
    Return an iterator which yields the paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    If recursive is true, the pattern '**' will match any files and
    zero or more directories and subdirectories.
    """
    parsed_uri = urllib.parse.urlparse(uri)
    scheme_glob = _scheme_iglobs[parsed_uri.scheme]

    if config is None:
        config = default_config()

    yield from scheme_glob(uri, recursive=recursive, config=config)

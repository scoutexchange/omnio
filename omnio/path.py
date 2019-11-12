import os
import urllib


def _open(uri, mode, config):
    parsed_uri = urllib.parse.urlparse(uri)
    os.path.abspath(os.path.join(parsed_uri.netloc, parsed_uri.path))
    return open(parsed_uri.path, mode)

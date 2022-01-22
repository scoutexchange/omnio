import urllib


def _open(uri, mode, config):
    parsed_uri = urllib.parse.urlparse(uri)
    return open(parsed_uri.path, mode)

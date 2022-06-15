"""
This library provides the `omnio.open()` function with an interface
very similar to that of the built in Python `open` function.  The
difference is that while Python's `open` operates only on local
filesystem paths, `omnio` accepts URIs as well.

In addition, it supports compression and decompression of streams
with gzip or bz2.

It currently supports `file`, `http`, and `s3` URIs, though it may
be expanded to support additional schemes in the future.
"""

# Internally, we define the main open function as open_ to avoid
# shadowing the python built-in open(). However, the module API
# is designed to be semantically referenced as omnio.open().  So
# here we rejigger to make that work and look natural in the module
# help.
from omnio.lib import open_ as open, default_config

__all__ = ['open', 'default_config']
open.__name__ = 'open'

__version__ = '1.2.2'

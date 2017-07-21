# Internally, we define the main open function as open_ to avoid
# shadowing the python built-in open(). However, the module API
# is designed to be semantically referenced as omnio.open().  So
# here we rejigger to make that work and look natural in the module
# help.
from omnio.lib import open_ as open

__all__ = ['open']
open.__name__ = 'open'

__version__ = '1.0.0'

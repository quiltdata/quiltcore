
"""A Mapping is a generic container for associating key/value
pairs.

This class provides concrete generic implementations of all
methods except for __getitem__, __iter__, and __len__.

"""

from collections.abc import MutableMapping
from .root import Root

class Keyed(Root, MutableMapping):
  
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    
  def __getitem__(self, key):
    raise NotImplementedError
  
  def __iter__(self):
    raise NotImplementedError
  
  def __len__(self):
    return 1  # so not zero => None in assert
  
  def __setitem__(self, key, value):
    raise NotImplementedError
  
  def __delitem__(self, key):
    raise NotImplementedError

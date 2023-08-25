
"""A Mapping is a generic container for associating key/value
pairs.

This class provides concrete generic implementations of all
methods except for __getitem__, __iter__, and __len__.

"""

from collections.abc import Mapping

class Keyed(Mapping):
  pass

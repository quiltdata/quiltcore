from .udg.node import Node
from .udg.codec import Codec

class Factory(Node):

    def __init__(self, name: str, **kwargs):
        super().__init__(Codec(), name, self, **kwargs)

quilt = Factory('quilt')

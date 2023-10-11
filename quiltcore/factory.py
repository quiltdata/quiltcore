from .udg.codec import Codec
from .udg.node import Node


class Factory(Node):
    def __init__(self, name: str, **kwargs):
        super().__init__(Codec(), name, self, **kwargs)


quilt = Factory("quilt")

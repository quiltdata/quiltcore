import logging

from .node import Node


class Child(Node):
    def __init__(self, name: str, parent: Node, **kwargs):
        super().__init__(parent.cf, name, parent, **kwargs)
        logging.debug(f"Child.init: {self} <- {self.parent}")
        assert parent == self.parent

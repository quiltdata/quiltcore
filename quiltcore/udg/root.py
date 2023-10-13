from time import time

import quiltcore

from .types import Types


class Root(Types):
    """
    Base class for Universal Data Graph.
    Contains definitions and static methods.
    """

    @staticmethod
    def ClassFromName(name: str) -> type:
        """Return a class from a string."""
        return getattr(quiltcore, name)

    @staticmethod
    def Now() -> str:
        "Return integer timestamp."
        return str(int(time()))

    def __init__(self, **kwargs):
        self.args = kwargs
        self.class_name = self.__class__.__name__
        self.class_key = self.class_name.lower()
        self.args[self.class_key] = self

    def __eq__(self, other):
        return str(self) == str(other)

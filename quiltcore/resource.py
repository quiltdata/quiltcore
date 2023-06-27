import quiltcore

from pathlib import Path
from sys import modules
from typing_extensions import Self

from .config import CoreConfig

class CoreResource:

    @staticmethod
    def ClassFromName(name: str) -> type:
        """Return a class from a string."""
        return getattr(quiltcore, name)

    """Generic resource class."""
    def __init__(self, path: Path, parent: Self|None = None):
        self.config = CoreConfig()
        self.name = self.__class__.__name__
        rkey = f'resources/{self.name}'
        self.params = self.config.get(rkey) or {}
        print(f"params[{rkey}]: {self.params} <- {self.config.data['resources']}")
        self.path = path
        _child = self.param('child', 'CoreResource')
        print(f"child[{self.name}]: {_child}")
        self.klass = CoreResource.ClassFromName(_child)
        self.glob = self.param('glob', '*')

    def __repr__(self):
        return f"<{self.__class__} {self.path}>"
    
    def __str__(self):
        return str(self.path)
    
    def param(self, key: str, default: str) -> str:
        """Return a param."""
        return self.params[key] if key in self.params else default # type: ignore

    def child_params(self, key: str) -> Self:
        """Return the params for a child resource."""
        return self

    def child(self, path: Path, key: str = ''):
        """Return a child resource."""
        return self.klass(path, self.child_params(key))

    def list(self) -> list[Self]:
        """List all child resources."""
        gen = self.path.glob(self.glob)
        return [self.child(x) for x in gen]
    
    def get(self, key: str) -> Self:
        """Get a child resource by name."""
        path = self.path / key
        return self.child(path, key)

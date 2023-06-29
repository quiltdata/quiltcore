from __future__ import annotations

from pathlib import Path

import quiltcore
from typing_extensions import Self

from .config import CoreConfig


class CoreResource:
    @staticmethod
    def ClassFromName(name: str) -> type:
        """Return a class from a string."""
        return getattr(quiltcore, name)

    """Generic resource class."""

    def __init__(self, path: Path, **kwargs):
        self.cf = CoreConfig()
        self.name = self.__class__.__name__
        rkey = f"resources/{self.name}"
        self.params = self.cf.get_dict(rkey)
        self.path = path
        _child = self.param("child", "CoreResource")
        self.klass = CoreResource.ClassFromName(_child)
        self.glob = self.param("glob", "*")

    def __repr__(self):
        return f"<{self.__class__} {self.path}>"

    def __str__(self):
        return str(self.path)

    def param(self, key: str, default: str) -> str:
        """Return a param."""
        return self.params[key] if key in self.params else default  # type: ignore

    def child_args(self, key: str) -> dict:
        """Return the parameters for a child resource."""
        return {}

    def child(self, path: Path, key: str = ""):
        """Return a child resource."""
        return self.klass(path, **self.child_args(key))

    def child_path(self, key: str) -> Path:
        """Return the path for a child resource."""
        return self.path / key

    def list_gen(self):
        return self.path.glob(self.glob)

    def list(self) -> list[Self]:
        """List all child resources."""
        return [self.child(x) for x in self.list_gen()]

    def get(self, key: str) -> Self:
        """Get a child resource by name."""
        path = self.child_path(key)
        if not path.exists():
            raise KeyError(f"Key {key} not found in {self.path}")
        return self.child(path, key)

    def put(self, dest: Path) -> Path:
        """Put a resource into dest. Return the new path"""
        raise NotImplementedError

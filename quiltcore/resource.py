from __future__ import annotations

from pathlib import Path

import quiltcore
from typing import Generator
from tempfile import TemporaryDirectory

from .yaml.config import Config


class Resource:
    """
    Base class for all Quilt resources.
    Manages configuration and provides common methods.
    Subclasses override child* to customize get/list behavior
    """

    @staticmethod
    def TempGen(filename: str = "") -> Generator[Path, None, None]:
        """Return generator to a temporary directory."""
        with TemporaryDirectory() as tmpdirname:
                temp_path = Path(tmpdirname) / filename if len(filename) > 0 else Path(tmpdirname)
                yield temp_path

    @staticmethod
    def TempDir(filename: str = "") -> Path:
        for path in Resource.TempGen(filename):
            return path
        return Path(".")  # should never happen

    @staticmethod
    def ClassFromName(name: str) -> type:
        """Return a class from a string."""
        return getattr(quiltcore, name)

    def __init__(self, path: Path, **kwargs):
        self.cf = Config()
        self.class_name = self.__class__.__name__
        self.path = path
        self.setup_params()

    def __repr__(self):
        return f"<{self.class_name} {self.path}>"

    def __str__(self):
        return str(self.path)

    def param(self, key: str, default: str) -> str:
        """Return a param."""
        return self.params[key] if key in self.params else default  # type: ignore

    def setup_params(self):
        """Load Resource-specific params from config file."""
        self.params = self.cf.get_dict(f"resources/{self.class_name}")
        self.glob = self.param("glob", "*")
        _child = self.param("child", "Resource")
        self.klass = Resource.ClassFromName(_child)

    #
    # Private Methods for child resources
    #

    def child_args(self, key: str) -> dict:
        """Return the parameters for a child resource."""
        return {}

    def child(self, path: Path, key: str = ""):
        """Return a child resource."""
        return self.klass(path, **self.child_args(key))

    def child_path(self, key: str) -> Path:
        """Return the path for a child resource."""
        return self.path / key

    def child_list(self):
        """List/generator of valid children, based on self.glob"""
        return self.path.glob(self.glob)

    #
    # Public HTTP-like Methods
    #

    def list(self) -> list["Resource"]:
        """List all child resources."""
        return [self.child(x) for x in self.child_list()]

    def get(self, key: str, **kwargs) -> "Resource":
        """Get a child resource by name."""
        path = self.child_path(key)
        if not path.exists():
            raise KeyError(f"Key {key} not found in {self.path}")
        return self.child(path, key)

    def put(self, dest: Path, **kwargs) -> Path:
        """Copy contents of resource's path into _dest_."""
        dest.write_bytes(self.path.read_bytes())  # for binary files
        return dest
    
    def delete(self, key: str = "", **kwargs) -> None:
        """Delete a child resource by name."""
        pass

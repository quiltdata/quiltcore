from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import quiltcore

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
            temp_path = (
                Path(tmpdirname) / filename if len(filename) > 0 else Path(tmpdirname)
            )
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
    # Abstract HTTP Methods
    #

    def list(self, **kwargs) -> list["Resource"]:
        """List all child resources."""
        return []

    def get(self, key: str, **kwargs) -> "Resource":
        """Get a child resource by name."""
        return self

    def put(self, path: Path, **kwargs) -> Path:
        """Copy contents of resource's path into _path_."""
        path.write_bytes(self.path.read_bytes())  # for binary files
        return path

    def delete(self, key: str = "", **kwargs) -> None:
        """Delete a child resource by name."""
        pass

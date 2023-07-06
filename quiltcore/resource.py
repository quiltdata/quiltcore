from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from time import time
from typing import Generator

import quiltcore

from .yaml.config import Config


class Resource:
    """
    Base class for all Quilt resources.
    Manages configuration and provides common methods.
    Subclasses override child* to customize get/list behavior
    """

    DEFAULT_HASH_TYPE = "SHA256"
    KEY_GLOB = "glob"
    KEY_KEY = "_key"
    KEY_NAME = f"namespace.{KEY_KEY}"
    KEY_PATH = "_path"
    MANIFEST = "_manifest"
    TAG_DEFAULT = "latest"
    

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
    
    @staticmethod
    def Timestamp() -> str:
        "Return integer timestamp."
        return str(int(time()))

    def __init__(self, path: Path, **kwargs):
        self.path = path
        self.args = kwargs
        self.name = path.name
        self.class_name = self.__class__.__name__
        self.class_key = self.class_name.lower()
        self.args[self.class_key] = self
        key = kwargs.get(self.KEY_KEY, None)
        if key is not None:
            self.args[f"{self.class_key}.{self.KEY_KEY}"] = key
        self.cf = Config()
        self.setup_params()

    def __repr__(self):
        return f"<{self.class_name}({self.path}, {self.args})>"

    def __str__(self):
        return f"<{self.class_name}({self.path})>"
    
    def __eq__(self, other):
        return str(self) == str(other)

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
        """Get a child resource by key."""
        return self

    def patch(self, res: Resource, **kwargs) -> "Resource":
        """Update and return a child resource."""
        raise NotImplementedError

    def post(self, key: str, **kwargs) -> "Resource":
        """Create and return a child resource using key."""
        raise NotImplementedError

    def put(self, res: Resource, **kwargs) -> "Resource":
        """Insert/Replace and return a child resource."""
        raise NotImplementedError

    def delete(self, key: str, **kwargs) -> None:
        """Delete a child resource by name."""
        raise NotImplementedError

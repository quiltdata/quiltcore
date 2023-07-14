from __future__ import annotations

import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from time import time
from typing import Generator
from urllib.parse import parse_qs, quote, unquote, urlparse

import quiltcore
from upath import UPath

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
    KEY_VER = "versionId"
    KEY_S3VER = "version_id"
    MANIFEST = "_manifest"
    TAG_DEFAULT = "latest"
    UNQUOTED = "/:"
    LOCAL = "file://./"

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

    @staticmethod
    def AsPath(key: str) -> UPath:
        """Return a Path from a string."""
        if not isinstance(key, str):
            raise TypeError(f"[{key}]Expected str, got {type(key)}")
        return UPath(key, version_aware=True)

    @staticmethod
    def AsStr(object) -> str:
        """Return a string from a simple object."""
        if not isinstance(object, str):
            raise TypeError(f"Expected str, got {type(object)}:{object}")
        return object

    @staticmethod
    def GetVersion(uri: str) -> str:
        """Extract `versionId` from query."""
        query = urlparse(uri).query
        if not query:
            return ""
        qs = parse_qs(query)
        vlist = qs.get(Resource.KEY_VER)
        return vlist[0] if vlist else ""

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
        assert "s3:/udp" not in str(path)
        self._setup_params()

    def __repr__(self):
        return f"<{self.class_name}({self.path}, {self.args})>"

    def __str__(self):
        return f"<{self.class_name}({self.path})>"

    def __eq__(self, other):
        return str(self) == str(other)

    def param(self, key: str, default: str) -> str:
        """Return a param."""
        return self.params[key] if key in self.params else default  # type: ignore

    def _setup_params(self):
        """Load Resource-specific params from config file."""
        self.params = self.cf.get_dict(f"resources/{self.class_name}")
        self.glob = self.param("glob", "*")
        _child = self.param("child", "Resource")
        self.klass = Resource.ClassFromName(_child)

    #
    # Read Bytes/Text
    #

    def read_opts(self) -> dict:
        if self.KEY_VER in self.args:
            opts = {self.KEY_S3VER: self.args[self.KEY_VER]}
            logging.debug(f"read_opts: {opts}")
            return opts
        return {}

    def to_bytes(self) -> bytes:
        """Return bytes from path."""
        opts = self.read_opts()
        if len(opts) > 0:
            with self.path.open(mode="rb", **opts) as fi:
                return fi.read()
        return self.path.read_bytes()

    def to_text(self, strip=True) -> str:
        """Return text from path."""
        text = self.to_bytes().decode("utf-8")
        return text.strip() if strip else text

    #
    # URL Encoding of Physical Keys
    #

    def encoded(self) -> bool:
        """Return True if Resource keys should be encoded."""
        return len(self.cf.get_dict("quilt3/encoded")) > 0

    def encode(self, object) -> str:
        """Encode object as a string."""
        key = self.AsStr(object)
        return quote(key, safe=self.UNQUOTED) if self.encoded() else key

    def decode(self, object) -> str:
        """Decode object as a string."""
        key = self.AsStr(object)
        return unquote(key) if self.encoded() else key

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

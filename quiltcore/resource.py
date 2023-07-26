from __future__ import annotations

import logging
from pathlib import Path
from re import compile
from time import time
from urllib.parse import parse_qs, urlparse

import quiltcore
from upath import UPath

from .yaml.config import Config


class Resource:
    """
    Base class for all Quilt resources.
    Manages configuration and provides common methods.
    Subclasses override child* to customize get/list behavior
    """

    ARG_REG = "registry"
    ARG_MAN = "manifest"
    ARG_NS = "namespace"

    KEY_FRC = "force"
    KEY_GLOB = "glob"
    KEY_KEY = "_key"
    KEY_HSH = "hash"
    KEY_MAN = "_manifest"
    KEY_META = "meta"
    KEY_MH = "multihash"
    KEY_MSG = "message"
    KEY_NCP = "nocopy"
    KEY_NS = f"{ARG_NS}.{KEY_KEY}"
    KEY_PATH = "_path"
    KEY_S3VER = "version_id"
    KEY_SELF = "."
    KEY_SZ = "size"
    KEY_TAG = "tag"
    KEY_USER = "user_meta"
    KEY_UVER = "VersionId"
    KEY_VER = "versionId"

    TAG_DEFAULT = "latest"
    IS_LOCAL = compile(r"file:\/*")
    IS_REL = "./"
    IS_URI = ":/"

    @staticmethod
    def ClassFromName(name: str) -> type:
        """Return a class from a string."""
        return getattr(quiltcore, name)

    @staticmethod
    def Now() -> str:
        "Return integer timestamp."
        return str(int(time()))

    @classmethod
    def AsPath(cls, key: str) -> Path:
        """Return a Path from a string."""
        if not isinstance(key, str):
            raise TypeError(f"[{key}]Expected str, got {type(key)}")
        return UPath(key, version_aware=True)

    @classmethod
    def CheckPath(cls, path) -> Path:
        if not isinstance(path, Path):
            raise TypeError(f"[{path}]Expected Path, got {type(path)}")
        return path

    @classmethod
    def GetVersion(cls, uri: str) -> str:
        """Extract `versionId` from URI query string."""
        query = urlparse(uri).query
        if not query:
            return ""
        qs = parse_qs(query)
        vlist = qs.get(Resource.KEY_VER)
        return vlist[0] if vlist else ""

    @classmethod
    def FromURI(cls, uri: str) -> "Resource":
        path = cls.AsPath(uri)
        ver = cls.GetVersion(uri)
        opts = {cls.KEY_VER: ver} if len(ver) > 0 else {}
        return cls(path, **opts)

    def __init__(self, path: Path, **kwargs):
        self.path = self.CheckPath(path)
        self.args = kwargs
        self.name = path.name
        self.class_name = self.__class__.__name__
        self.class_key = self.class_name.lower()
        self.args[self.class_key] = self
        key = kwargs.get(self.KEY_KEY, None)
        if key is not None:
            self.args[f"{self.class_key}.{self.KEY_KEY}"] = key
        self.cf = Config()
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

    def put(self, res: Resource, **kwargs) -> "Resource":
        """Insert/Replace and return a child resource."""
        raise NotImplementedError

    def delete(self, key: str, **kwargs) -> None:
        """Delete a child resource by name."""
        raise NotImplementedError

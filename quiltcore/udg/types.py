import logging  # noqa: E402

from dataclasses import dataclass
from pathlib import Path
from re import compile
from sys import platform
from typing import Optional
from upath import UPath


@dataclass
class Hash3:
    type: str
    value: str


@dataclass
class Dict3:
    logical_key: str
    physical_keys: list[str]
    size: int
    hash: Hash3
    meta: Optional[dict] = None


@dataclass
class Dict4:
    name: str
    place: str
    size: int
    multihash: str
    metadata: Optional[dict]


List4 = list[Dict4]


Multihash = str


class Types:
    IS_LOCAL = compile(r"file:\/*")

    K_META = "meta"
    K_SIZE = "size"
    K_UVER = "VersionId"
    K_VER = "versionId"
    MH_DIG = "digest"
    MH_PRE = "prefix"
    T_HSH = "is_hash"
    T_LST = "is_list"
    T_OPT = "is_optional"
    T_QTD = "is_quoted"

    UNQUOTED = "/:?="
    URI_SPLIT = "://"

    @classmethod
    def AsStr(cls, object) -> str:
        """Return a string from a simple object."""
        if isinstance(object, UPath) and object.exists():
            versionId = cls.StatVersion(object)
            if versionId:
                logging.debug(f"AsStr.versionId: {versionId}")
                return f"{object}?{cls.K_VER}={versionId}"
        if isinstance(object, Path):
            object = str(object.as_posix())
        if not isinstance(object, str):
            raise TypeError(f"Expected str, got {type(object)}:{object}")
        return object

    @classmethod
    def AsPath(cls, key: str) -> UPath:
        """Return a Path from a string."""
        if not isinstance(key, str):
            raise TypeError(f"[{key}]Expected str, got {type(key)}")
        return UPath(key, version_aware=True).absolute()

    @staticmethod
    def OnWindows():
        return platform.startswith("win")

    @classmethod
    def StatVersion(cls, path: Path) -> str | None:
        if not path.exists():
            return None
        stat: dict = path.stat()  # type: ignore
        if isinstance(stat, dict):
            return stat.get(cls.K_UVER, None)
        if hasattr(stat, "cls.K_UVER"):
            return getattr(stat, cls.K_UVER)
        logging.warning(f"StatVersion: {path} -> {stat} has no {cls.K_UVER}")
        return None

    @classmethod
    def ToPath(cls, scheme: str, domain: str) -> Path:
        if scheme == "file":
            return cls.AsPath(domain)
        uri = f"{scheme}{cls.URI_SPLIT}{domain}"
        logging.debug(f"Domain.ToPath: {uri}")
        return cls.AsPath(uri)

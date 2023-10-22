import logging  # noqa: E402

from datetime import datetime
from dataclasses import dataclass, asdict
from json import dumps as json_dumps
from pathlib import Path
from re import compile
from sys import platform
from typing import Optional
from upath import UPath


class Types:
    HEADER_NAME = "."
    HEADER_V3 = "v0"
    HEADER_V4 = "v4"
    MULTIHASH = "1220"

    IS_LOCAL = compile(r"file:\/*")
    IS_WINDRIVE = compile(r"^([a-z])\\")

    K_JSON_FIELDS = ["info", "meta"]
    K_METADATA = "metadata"
    K_META_JSON = "meta.json"
    K_MESSAGE = "message"
    K_META = "meta"
    K_SIZE = "size"
    K_USER_META = "user_meta"
    K_UVER = "VersionId"
    K_VER = "versionId"
    K_VERSION = "version"
    MH_DIG = "digest"
    MH_PRE = "prefix"
    SIZE = 0
    T_HSH = "is_hash"
    T_LST = "is_list"
    T_OPT = "is_optional"
    T_QTD = "is_quoted"

    UNQUOTED = "/:?="
    URI_SPLIT = "://"

    @classmethod
    def AsString(cls, object) -> str:
        """Return a string from a simple object."""
        try:
            if isinstance(object, UPath) and object.exists():
                versionId = cls.StatVersion(object)
                if versionId:
                    logging.debug(f"AsString.versionId: {versionId}")
                    return f"{object}?{cls.K_VER}={versionId}"
        except Exception as e:
            logging.error(f"AsString.cannot stat: {object}\n{e}")
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
        # TODO: Fix Windows Relative Paths
        drives = cls.IS_WINDRIVE.match(key)
        if drives:
            key = key.replace(drives[0], drives[1] + ":")
        return UPath(key).absolute()  # , version_aware=True

    @staticmethod
    def RelativePath(path: Path, base: Path) -> Path:
        """Return a relative path, if inside base."""
        return path.relative_to(base) if base in path.parents else path

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
        logging.debug(f"StatVersion: {path} -> {stat} has no {cls.K_UVER}")
        return None

    @classmethod
    # Windows string: d\a\quiltcore\quiltcore\tests\example
    def ToPath(cls, scheme: str, domain: str) -> Path:
        logging.debug(f"Domain.ToPath: {scheme} {cls.URI_SPLIT} {domain}")
        if scheme == "file":
            return cls.AsPath(domain)
        uri = f"{scheme}{cls.URI_SPLIT}{domain}"
        logging.debug(f"Domain.ToPath: {uri}")
        return cls.AsPath(uri)


@dataclass
class DataDict:
    def to_dict(self) -> dict:
        raw_dict = asdict(self)
        for k, v in raw_dict.items():
            if isinstance(v, datetime):
                raw_dict[k] = str(v)
        return raw_dict


@dataclass
class Hash3(DataDict):
    type: str
    value: str


@dataclass
class Dict3(DataDict):
    logical_key: str
    physical_keys: list[str]
    size: int
    hash: Hash3
    meta: Optional[dict] = None
    workflow: Optional[str] = None


@dataclass
class Dict4(DataDict):
    name: str
    place: str
    size: int
    multihash: str
    info: dict  # was (system) metadata
    meta: dict  # was user_meta
    workflow: Optional[str] = None

    def to_parquet_dict(self) -> dict:
        map = self.to_dict()
        for field in Types.K_JSON_FIELDS:
            if field in map:
                json_field = f"{field}.json"
                map[json_field] = json_dumps(map[field], default=str)
                del map[field]
        return map


List4 = list[Dict4]


Multihash = str

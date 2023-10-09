from dataclasses import dataclass
from typing import Optional


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

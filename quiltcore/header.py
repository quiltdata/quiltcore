from datetime import datetime
from pathlib import Path

import pyarrow as pa  # type: ignore

from .resource_key import ResourceKey
from .udg.types import Dict4


class Header(ResourceKey):
    """
    Represents top-level metadata for a Manifest
    Attributes:

    * info: str
    * msg: str
    * user_meta: object

    """

    NAME = "."
    PLACE = "."
    SIZE = 0
    MULTIHASH = "Qm"

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.cols: list[str] = []
        self._setup_headers(kwargs["first"])

    #
    # Setup
    #

    def _setup_headers(self, first: dict):
        for header, default in self.headers.items():
            value = first.get(header, default)
            setattr(self, header, value)
            if header in first:
                self.cols.append(header)

    def drop(self, table) -> pa.Table:
        return table.drop(self.cols).slice(1)

    #
    # Output
    #

    def to_dict4(self) -> Dict4:
        return Dict4(
            name=self.NAME,
            place=self.PLACE,
            size=self.SIZE,
            multihash=self.MULTIHASH,
            metadata=self.headers,
        )

    def to_dict(self) -> dict:
        raw_dict = {k: getattr(self, k) for k in self.headers.keys()}
        return self.codec.encode_dates(raw_dict)

    def hashable_dict(self) -> dict:
        meta = self.to_dict()
        if hasattr(self, self.KEY_USER):
            user_meta = getattr(self, self.KEY_USER)
            for k, v in user_meta.items():
                if isinstance(v, datetime):
                    user_meta[k] = self.codec.encode_date(v)
            meta[self.KEY_USER] = user_meta
        return meta

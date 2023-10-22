from datetime import datetime

import pyarrow as pa  # type: ignore

from .codec import Codec
from .types import Dict4


class Header(Codec):
    """
    Represents top-level metadata for a Manifest, and convert to Dict4
    Attributes:

    * version: str
    * message: str
    * user_meta: object

    TODO: May be largely redundant, can simplify to just create Dict4

    """

    @classmethod
    def HeaderDict4(
        cls, message: str = "Updated", user_meta={}, version=Codec.HEADER_V4
    ) -> Dict4:
        return Dict4(
            name=cls.HEADER_NAME,
            place=cls.HEADER_NAME,
            size=cls.SIZE,
            multihash=cls.MULTIHASH,
            info={
                cls.K_VERSION: version,
                cls.K_MESSAGE: message,
            },
            meta=user_meta,
        )

    @classmethod
    def First(cls, message: str = "N/A") -> dict:
        return {
            cls.K_VERSION: cls.HEADER_V4,
            cls.K_MESSAGE: message,
        }

    @classmethod
    def FromMessage(cls, message: str = "N/A") -> "Header":
        first = cls.First(message)
        return cls(first)

    def __init__(self, first: dict, **kwargs):
        super().__init__(**kwargs)
        self.cols: list[str] = []
        self._setup_headers(first)

    #
    # Setup
    #

    def _setup_headers(self, first: dict):
        self.headers = self.get_dict("quilt3/headers")
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
        base = self.to_dict()
        return self.HeaderDict4(**base)

    def to_dict(self) -> dict:
        raw_dict = {k: getattr(self, k) for k in self.headers.keys()}
        return self.encode_dates(raw_dict)

    def hashable_dict(self) -> dict:
        meta = self.to_dict()
        if hasattr(self, self.K_USER_META):
            user_meta = getattr(self, self.K_USER_META)
            for k, v in user_meta.items():
                if isinstance(v, datetime):
                    user_meta[k] = self.encode_date(v)
            meta[self.K_USER_META] = user_meta
        return meta

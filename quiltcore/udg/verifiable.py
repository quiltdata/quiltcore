import logging
from json import JSONEncoder

from .codec import Codec
from .keyed import Keyed

Multihash = str


class Verifiable(Keyed):
    ENCODE = JSONEncoder(sort_keys=True, separators=(",", ":"), default=str).encode

    def __init__(self, codec: Codec, **kwargs):
        super().__init__(**kwargs)
        self.cf = codec

    #
    # Abstract methods
    #

    def hash(self) -> Multihash:
        raise NotImplementedError("subclass must override")

    def to_bytes(self) -> bytes:
        raise NotImplementedError("subclass must override")

    def to_hashable(self) -> dict:
        raise NotImplementedError("subclass must override")

    #
    # Hash creation
    #

    def digest(self, contents: bytes) -> Multihash:
        """Hash `contents` using the current codec."""
        return self.cf.digest(contents)

    def hash_quilt3(self) -> str:
        """Return the value portion of the legacy quilt3 hash."""
        mh = self.hash()
        hash_struct = self.cf.encode_hash(mh)
        return hash_struct["value"]

    def _hash_path(self) -> str:
        """Return the multihash of the source file."""
        return self.digest(self.to_bytes())

    #
    # Hash retreival
    #

    def hashable(self) -> bytes:
        source = self.to_hashable()
        return self.ENCODE(source).encode("utf-8")  # type: ignore

    def verify(self, contents: bytes) -> bool:
        """Verify that multihash digest of bytes match the current multihash"""
        digest = self.digest(contents)
        logging.debug(f"verify.digest: {digest}")
        return digest == self.hash()

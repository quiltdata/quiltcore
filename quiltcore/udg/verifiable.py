import logging
from json import JSONEncoder
from pathlib import Path

from .codec import Codec
from .keyed import Keyed

Multihash = str


class Verifiable(Keyed):
    ENCODE = JSONEncoder(sort_keys=True, separators=(",", ":"), default=str).encode

    def __init__(self, codec: Codec, **kwargs):
        super().__init__(**kwargs)
        self.cf = codec
        self._hash: Multihash|None = None

    #
    # Hashable Bytes
    #

    def hashable_dict(self) -> dict:
        return {}
    
    def hashable_path(self) -> Path|None:
        if hasattr(self, "path"):
            path = getattr(self, "path")
            assert isinstance(path, Path)
            if path.exists() and path.is_file():
                logging.debug(f"to_bytes.path: {path}")
                return path
        return None
            
    def hashable_values(self) -> str:
        """Concatenate the hashes of each Verifiable in values()."""
        hashes = [v.hash() for v in self.values() if isinstance(v, Verifiable)]
        return "".join(hashes)


    def to_bytes(self) -> bytes:
        """Return hashable bytes if present."""
        if path := self.hashable_path():
                return path.read_bytes()
        if values := self.hashable_values():
            return values.encode("utf-8")
        if source := self.hashable_dict():
            return self.ENCODE(source).encode("utf-8")  # type: ignore

        raise ValueError("No bytes to hash for {self}")

    #
    # Hash creation
    #

    def digest_bytes(self, input: bytes) -> Multihash:
        """Hash `input` bytes using the current codec."""
        return self.cf.digest(input)

    def _multihash_contents(self) -> Multihash:
        """Calculate the multihash for this object's bytes."""
        return self.digest_bytes(self.to_bytes())
    
    def hash(self) -> Multihash:
        """Return (or calculate) the multihash of the contents."""
        if self._hash is None or self.is_dirty():
            self._hash = self._multihash_contents()
        return self._hash

    def q3hash(self) -> str:
        """Return the value portion of the legacy quilt3 hash."""
        mh = self.hash()
        hash_struct = self.cf.encode_hash(mh)
        return hash_struct["value"]

    #
    # Hash retrieval
    #

    def hashable(self) -> bytes:
        source = self.hashable_dict()
        return self.ENCODE(source).encode("utf-8")  # type: ignore

    def verify(self, contents: bytes) -> bool:
        """Verify that multihash digest of bytes match the current multihash"""
        digest = self.digest_bytes(contents)
        logging.debug(f"verify.digest: {digest}")
        return digest == self.hash()

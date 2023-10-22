import logging
from pathlib import Path
from os import stat_result

from .codec import Codec, Dict4, Multihash
from .keyed import Keyed


class Verifiable(Keyed):
    DEFAULT_DICT: dict = {}

    @classmethod
    def UpdateDict4(cls, base: Dict4, path: Path) -> Dict4:
        """Update metadata for a relaxed file."""
        assert isinstance(base.info, dict)
        base.place = str(path)
        base.info["tombstone"] = False
        base.info["prior"] = base.multihash
        stat = path.stat()
        if isinstance(stat, stat_result):
            base.size = stat.st_size
            base.info["mode"] = stat.st_mode
            base.info["mtime"] = stat.st_mtime
            base.info["ctime"] = stat.st_ctime
        elif isinstance(stat, dict):
            # TODO: whitelist only the values we care about
            assert "size" in stat
            for key in stat.keys():  # type: ignore
                if key not in base.info:
                    base.info[key] = stat[key]
        else:
            logging.error(f"UpdateDict4: unknown stat type {stat} ->  {base}\n{path}")
        return base

    def __init__(self, codec: Codec, **kwargs):
        super().__init__(**kwargs)
        self.cf = codec
        self._hash: Multihash | None = None

    #
    # Hashable Bytes
    #

    def hashable_dict(self) -> dict:
        return self.DEFAULT_DICT

    def hashable_path(self) -> Path | None:
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
            return (
                path.read_bytes()
            )  # TODO: pth.open(version_id="B0zNSMELW__87yfYtZcfcdBw3qxHkFhm") as f
        if values := self.hashable_values():
            return values.encode("utf-8")
        if source := self.hashable_dict():
            return Codec.EncodeDict(source)  # type: ignore

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

    def dict4_from_path(self, path: Path) -> Dict4:
        base = Dict4(
            name=path.name,
            place="",
            size=0,
            multihash=self.digest_bytes(path.read_bytes()),
            info={},
            meta={},
        )
        return self.UpdateDict4(base, path)

    def hash(self) -> Multihash:
        """Return (or calculate) the multihash of the contents."""
        if self._hash is None or self.is_dirty():
            self._hash = self._multihash_contents()
        return self._hash

    def q3hash_from_hash(self, mh: Multihash) -> str:
        hash_struct = self.cf.encode_hash(mh)
        return hash_struct["value"]

    def q3hash(self) -> str:
        """Return the value portion of the legacy quilt3 hash."""
        return self.q3hash_from_hash(self.hash())

    #
    # Hash retrieval
    #

    def hashable(self) -> bytes:
        source = self.hashable_dict()
        return Codec.EncodeDict(source)

    def verify(self, contents: bytes) -> bool:
        """Verify that multihash digest of bytes match the current multihash"""
        digest = self.digest_bytes(contents)
        logging.debug(f"verify.digest: {digest}")
        return digest == self.hash()


class VerifyDict(Verifiable):
    def __init__(self, codec: Codec, hashable: dict, **kwargs):
        super().__init__(codec, **kwargs)
        self.dict = hashable

    def hashable_dict(self) -> dict:
        return self.dict

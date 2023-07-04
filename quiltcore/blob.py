
import logging
from multiformats import multihash
from pathlib import Path

from .manifest import Manifest
from .resource import Resource


class Blob(Resource):
    """Represents a single blob of data in a datastore."""

    MH_PREFIX_SHA256 = "1220"

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.parent = kwargs["parent"]
        self.row = kwargs["row"]
        if len(self.row) > 0:
            self.setup(self.row)
        
    def get_value(self, row:dict, key:str):
        value = row.get(key, None)
        if value:
            return value[0]
        if not hasattr(self, 'source') and not self.source:
            raise KeyError(f"Key {key} not found / derivable from {row}")
        print(f"Deriving {key} from {self.source}:\nrow={row}")
        if key == self.parent.kHash:
            bytes = self.source.read_bytes()
            return self.digest(bytes)
        if key == self.parent.kSize:
            return self.source.stat().st_size
        raise KeyError(f"Cannot derive {key} from {self.source}")
    
    def setup(self, row: dict):
        print(f"setup row:{row}")
        columns = self.cf.get_dict("schema/columns")
        for key, type in columns.items():
            print(f"setup key:{key} of type:{type}")
            value = self.get_value(row, key)
            if isinstance(type, list):
                value = value[0]
                key = key.rstrip("s")
            if type == "int64":
                value = int(value)
            print(f"Setting {key} to {value}")
            setattr(self, key, value)
            if key == self.parent.kPlace:
                self.source = Path(str(value))
            if key == self.parent.kHash:
                self.setup_hash(value)  # type: ignore

    #
    # Calculate and verify hash
    #

    def setup_hash(self, opt: dict):
        self.hash_value = opt["value"]
        hash_key = f'multihash/{opt["type"]}'
        self.hash_type = self.cf.get_str(hash_key)
        self.hash_digest = multihash.get(self.hash_type)

    def digest(self, bstring: bytes) -> str:
        digest = self.hash_digest.digest(bstring)
        hex = digest.hex()
        return hex.strip(Blob.MH_PREFIX_SHA256)

    def verify(self, bstring: bytes) -> bool:
        """Verify that bytes match the hash"""
        digest = self.digest(bstring)
        print(digest)
        print(self.hash_value)
        return digest == self.hash_value

    #
    # Convenience Methods
    #

    def name(self):
        return self.row[self.parent.kName]  # type: ignore

    def place(self):
        return self.source

from pathlib import Path

from multiformats import multihash

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

    def setup(self, row: dict):
        columns = self.cf.get_dict("schema/columns")
        for key, type in columns.items():
            value = row[key][0]
            if isinstance(value, list):
                value = value[0]
                key = key.rstrip("s")
            if type == "int64":
                value = int(value)
            setattr(self, key, value)
            if key == "hash":
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
        return self.row[self.parent.name_col]  # type: ignore

    def place(self):
        return self.row[self.parent.place_col]  # type: ignore

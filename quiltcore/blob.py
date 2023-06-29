from pathlib import Path

from multiformats import multihash

from .manifest import CoreManifest
from .resource import CoreResource


class CoreBlob(CoreResource):
    """Storage for dereferenced Names"""

    MH_PREFIX = "1220"

    @staticmethod
    def FromKeyInManifest(key: str, manifest: CoreManifest) -> "CoreBlob":
        path = manifest.child_path(key)
        row = manifest.child_row(key)
        return CoreBlob(path, parent=manifest, row=row)

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

    def setup_hash(self, opt: dict):
        self.hash_value = opt["value"]
        hash_key = f'multihash/{opt["type"]}'
        self.hash_type = self.cf.get_str(hash_key)
        self.hash_digest = multihash.get(self.hash_type)

    def digest(self, bstring: bytes) -> str:
        digest = self.hash_digest.digest(bstring)
        hex = digest.hex()
        return hex.strip(CoreBlob.MH_PREFIX)

    def name(self):
        return self.row[self.parent.name_col]  # type: ignore

    def location(self):
        return self.row[self.parent.loc_col]  # type: ignore

    def put(self, dest: Path) -> Path:
        """Put a resource into dest. Return the new path"""
        dest.write_bytes(self.path.read_bytes())  # for binary files
        return dest

    def verify(self, bstring: bytes) -> bool:
        """Verify that bytes match the hash"""
        digest = self.digest(bstring)
        print(digest)
        print(self.hash_value)
        return digest == self.hash_value

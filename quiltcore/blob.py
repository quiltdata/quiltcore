from pathlib import Path

from .manifest import CoreManifest
from .resource import CoreResource

class CoreBlob(CoreResource):
    """Storage for dereferenced Names"""

    @staticmethod
    def FromKeyInManifest(key: str, manifest: CoreManifest) -> "CoreBlob":
        path = manifest.child_path(key)
        row = manifest.child_row(key)
        return CoreBlob(path, manifest, row)

    def __init__(self, path: Path, manifest: CoreManifest, row: dict = {}):
        super().__init__(path, manifest)
        self.row = row
        if len(row) > 0:
            self.setup(row)

    def setup(self, row: dict):
        columns = self.get_dict("schema/columns")
        for key, type in columns.items():
            value = row[key][0]
            print(f"key: {key}, value: {value}, type: {type}")
            if isinstance(value, list):
                value = value[0]
                key = key.rstrip('s')
            if type == "int64":
                value = int(value)
            setattr(self, key, value)

    def name(self):
        return self.row[self.parent.name_col]  # type: ignore
    
    def location(self):
        return self.row[self.parent.loc_col]  # type: ignore


    def put(self, dest: Path) -> Path:
        """Put a resource into dest. Return the new path"""
        dest.write_bytes(self.path.read_bytes()) #for binary files
        return dest

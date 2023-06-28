from pathlib import Path

from .resource import CoreResource


class CoreBlob(CoreResource):

    """Storage for dereferenced Names"""

    def __init__(self, value: Path, parent: CoreResource):
        super().__init__(value)

    def put(self, dest: Path) -> Path:
        """Put a resource into dest. Return the new path"""
        dest.write_bytes(self.path.read_bytes()) #for binary files
        return dest

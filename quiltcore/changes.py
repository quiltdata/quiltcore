from pathlib import Path

from .resource import Resource
from .manifest import Manifest


class Changes(Resource):
    """
    Track Changes to a new or existing Manifest using 'put' and 'delete'
    Use 'get' to return the new revision

    Optional: track changes to a directory?
    """

    MANIFEST_FILE = "manifest.json"
    MANIFEST_KEY = "manifest"

    @staticmethod
    def ScratchFile() -> Path:
        return Changes.TempDir(Changes.MANIFEST_FILE)

    def __init__(self, **kwargs):
        path = Changes.ScratchFile()
        super().__init__(path, **kwargs)
        self.manifest = kwargs.get(Changes.MANIFEST_KEY)

    def put(self, dest: Path, **kwargs) -> Path:
        """Add path."""
        dest.write_bytes(self.path.read_bytes())  # for binary files
        return dest
    
    def delete(self, key: str = "", **kwargs) -> None:
        """Delete a child resource by name."""
        pass

    def get(self, key: str, **kwargs) -> Manifest:
        """Get a child resource by name."""
        path = self.child_path(key)
        if not path.exists():
            raise KeyError(f"Key {key} not found in {self.path}")
        return self.child(path, key)


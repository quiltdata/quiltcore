from pathlib import Path

from .delta import Delta
from .manifest import Manifest
from .resource import Resource


class Changes(Resource):
    """
    Track Changes to a new or existing Manifest
    Add a file: put(path, action="add", key="filename.txt", prefix="./")
    Use 'get' and 'list' to return the Deltas

    Optional: track changes to a directory?
    """

    MANIFEST_FILE = "manifest.json"
    MANIFEST_KEY = "manifest"

    @staticmethod
    def ScratchFile() -> Path:
        return Changes.TempDir(Changes.MANIFEST_FILE)
    
    @staticmethod
    def GetCache(path: Path) -> Path:
        if not path:
            return Changes.ScratchFile()
        if path.exists() and path.is_dir():
            return path / Changes.MANIFEST_FILE
        return path

    def __init__(self, path = None, **kwargs):
        cache = Changes.GetCache(path)
        super().__init__(cache, **kwargs)
        self.manifest = kwargs.get(Changes.MANIFEST_KEY)
        self.deltas = {}

    def put(self, src: Path, **kwargs) -> Path:
        """
        Create and track a Delta for this source Path. 
        Options: 
        * action: add [default], rm
        * key: defaults to filename
        * prefix: pre-pended to key if non-empty
.
        """
        delta = Delta(src, **kwargs)
        self.deltas[delta.key] = delta
        return delta.path
    
    def delete(self, key: str = "", **kwargs) -> None:
        """ Delete the key from this change set """
        if key in self.deltas:
            del self.deltas[key]
            return
        raise KeyError(f"Key {key} not found in {self.deltas}")

    def get_delta(self, key: str, **kwargs) -> Delta:
        """
        Get a child resource by name.
        Q: Is this at all useful?
        Why not use get(message) to return a Manifest?
        """
        if key in self.deltas:
            return self.deltas[key]
        raise KeyError(f"Key {key} not found in {self.deltas}")
    
    def list_deltas(self, **kwargs) -> list[Resource]:
        """
        List child Deltas.
        Q: Does anyone care?
        Why not return this info as a String instead?
        """
        return list(self.deltas.values())
    
    #
    # Create new Manifest
    # 1. Get list of paths and keys (merge with `manifest`, if any)
    # 2. Create Blobs for each path ("row=")
    # 3. 


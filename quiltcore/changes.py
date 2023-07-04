from pathlib import Path
from yaml import dump

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

    @staticmethod
    def GetManifest(args: dict) -> Manifest:
        if Changes.MANIFEST_KEY in args:
            return args[Changes.MANIFEST_KEY]
        path = Changes.ScratchFile()
        return Manifest(path)   

    def __init__(self, path = None, **kwargs):
        cache = Changes.GetCache(path)
        super().__init__(cache, **kwargs)
        self.manifest = Changes.GetManifest(kwargs)
        self.kName = self.manifest.kName
        self.kPlaces = self.manifest.kPlaces
        self.deltas = {}

    def __str__(self):
        return dump(self.to_dict())

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.deltas.items()}
    
    #
    # Mutate Changes
    #
    
    def put(self, path: Path, **kwargs) -> Path:
        """
        Create and track a Delta for this source Path. 
        Options: 
        * action: add [default], rm
        * key: defaults to filename
        * prefix: pre-pended to key if non-empty
.
        """
        delta = Delta(path, **kwargs)
        self.deltas[delta.key] = delta
        return delta.path
    
    def delete(self, key: str = "", **kwargs) -> None:
        """ Delete the key from this change set """
        if key in self.deltas:
            del self.deltas[key]
            return
        raise KeyError(f"Key {key} not found in {self.deltas}")
    
    #
    # Create Blob for each Delta

    def get_delta(self, key: str, **kwargs) -> Delta:
        """ Return a Delta by key. Raise KeyError if not found. """
        if key in self.deltas:
            return self.deltas[key]
        raise KeyError(f"Key {key} not found in {self.deltas}")

    def child_path(self, key: str) -> Path:
        """Return the Path for a child resource."""
        delta = self.get_delta(key)
        return delta.path

    def child_args(self, key: str) -> dict:
        """Return the parameters for a child resource."""
        path = self.child_path(key)

        return {
            "parent": self.manifest,
            "row": {
                self.kName: [key],
                self.kPlaces: [[str(path)]],
            }
        }
    
    
    def list_deltas(self, **kwargs) -> list[Resource]:
        """
        List child Deltas.
        Q: Does anyone care?
        Why not return this info as a String instead?
        """
        return list(self.deltas.values())

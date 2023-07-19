from pathlib import Path

from yaml import dump

from .resource_key import ResourceKey


class Delta(ResourceKey):
    """
    A single change to a Manifest
    Use 'get' to return the new revision

    Optional: track changes to a directory?
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self._setup(kwargs)

    def _setup(self, args: dict):
        self.action = args.get("action", "add")
        self.name = args.get("name", self.path.name)
        self.prefix = args.get("prefix")
        if self.prefix:
            ppath = self.AsPath(self.prefix) / self.name
            self.name = str(ppath.as_posix())

    def __repr__(self):
        return super().__repr__()

    def __str__(self):
        return dump(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "name": self.name,
            "path": self.path,
            "prefix": self.prefix,
        }
    
    def to_row(self, path: Path) -> dict:
        return {
            self.kName: self.name,
            self.KEY_PATH: path
        }
    
    def to_rows(self, path: Path) -> list[dict]:
        return [self.to_row(path)]

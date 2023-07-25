from pathlib import Path

from yaml import dump

from .resource_key import ResourceKey


class Delta(ResourceKey):
    """
    A single change to a Manifest
    Use 'get' to return the new revision

    Optional: track changes to a directory?
    """

    KEY_ACT = "action"
    KEY_ADD = "add"
    KEY_NAM = "name"
    KEY_PRE = "prefix"
    KEY_RM = "rm"

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self._setup(kwargs)

    def _setup(self, args: dict):
        self.action = args.get(self.KEY_ACT, self.KEY_ADD)
        self.name = args.get(self.KEY_NAM, self.path.name)
        self.prefix = args.get(self.KEY_PRE)
        if self.prefix:
            ppath = self.AsPath(self.prefix) / self.name
            self.name = str(ppath.as_posix())

    def prefixed(self, path: Path) -> str:
        relative = path.relative_to(self.path)
        if self.prefix:
            relative = self.AsPath(self.prefix) / relative
        return str(relative)
        
    def __str__(self):
        return dump(self.to_dict())

    def to_dict(self) -> dict:
        return {
            self.KEY_ACT: self.action,
            self.cf.K_NAM: self.name,
            self.cf.K_PLC: str(self.path),
        }

    def to_dicts(self) -> list[dict]:
        if not self.path.is_dir():
            return [self.to_dict()]
        result = []
        for obj in self.path.rglob("*"):
            row = {
                self.KEY_ACT: self.action,
                self.cf.K_NAM: self.prefixed(obj),
                self.cf.K_PLC: str(obj),
                #self.KEY_PATH: obj,
            }
            result.append(row)
        return result

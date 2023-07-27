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

    #
    # Abstract Methods for child resources
    #

    def _child_names(self, **kwargs) -> list[str]:
        """Return names of each child resource."""
        if self.path.is_dir():
            return [str(obj) for obj in self.path.rglob("*")]
        return [str(self.path)]

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        path = self.AsPath(key)
        name = self.prefixed(path) if self.path.is_dir() else self.name
        args: dict = {
            self.cf.K_NAM: name,
            self.cf.K_PLC: key,
        }
        if self.action == self.KEY_RM:
            args[self.KEY_META] = {self.KEY_RM: True}
        elif not path.exists():
            raise ValueError(f"Missing path: {path}")
        return args

    #
    # Legacy Constructors
    #

    def to_dict(self) -> dict:
        return {
            self.KEY_ACT: self.action,
            self.cf.K_NAM: self.name,
            self.cf.K_PLC: str(self.path),
        }


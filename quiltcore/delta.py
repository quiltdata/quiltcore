from pathlib import Path

from .resource import Resource


class Delta(Resource):
    """
    A single change to a Manifest
    Use 'get' to return the new revision

    Optional: track changes to a directory?
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.setup(kwargs)
        self.args = kwargs

    def setup(self, args: dict):
        self.action = args.get("action", "add")
        self.key = args.get("key", self.path.name)
        self.prefix = args.get("prefix")
        if self.prefix:
            ppath =  Path(self.prefix) / self.key
            self.key = str(ppath.as_posix())
    
    def __repr__(self):
        return super().__repr__() + f": {self.args}"
    
    def __str__(self):
        return f"{self.action}[{self.key}] {self.path}"
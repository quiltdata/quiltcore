from pathlib import Path

from .resource import CoreResource
from .values import CoreValues


class CoreRegistry(CoreResource):
    """
    Registry of Names and parent of Values
    `list` and `get` return CoreName with parent of CoreValues
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        base = path / self.cf.get_path("dirs/config")
        self.path = base / self.cf.get_path("dirs/names")
        values = base / self.cf.get_path("dirs/values")
        self.values = CoreValues(values, self)

    def child_args(self, key: str) -> dict:
        return {"values": self.values}

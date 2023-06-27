from pathlib import Path

from .resource import CoreResource
from .values import CoreValues


class CoreRegistry(CoreResource):
    """
    Registry of Names and parent of Values
    `list` and `get` return CoreName with parent of CoreValues
    """

    def __init__(self, path: Path):
        super().__init__(path)
        base = path / self.get_path("dirs/config")
        self.path = base / self.get_path("dirs/names")
        values = base / self.get_path("dirs/values")
        self.values = CoreValues(values, self)

    def parent(self, key: str):
        return self.values

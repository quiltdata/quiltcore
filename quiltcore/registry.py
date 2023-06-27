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
        base = path / self.config.path("dirs/config")
        self.path = base / self.config.path("dirs/names")
        values = base / self.config.path("dirs/values")
        self.values = CoreValues(values, self)

    def parent(self, key: str):
        return self.values

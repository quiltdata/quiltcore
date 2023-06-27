from pathlib import Path
from .resource import CoreResource
from .values import CoreValues

class CoreRegistry(CoreResource):
    """Registry of Names and parent of Values"""

    def __init__(self, path: Path):
        super().__init__(path)
        base = path / self.config.path('dirs/config')
        self.path = base / self.config.path('dirs/names')
        values = base / self.config.path('dirs/values')
        self.values = CoreValues(values, self)

    def child_params(self, key: str) -> CoreValues:
        return self.values

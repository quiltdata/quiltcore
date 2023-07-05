from __future__ import annotations

from pathlib import Path
from upath import UPath

from .resource import Resource


class ResourceKey(Resource):
    """
    Get/List child resources by key in Manifest
    """
    MANIFEST = "_manifest"

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.kPath = "path"

    #
    # Abstract Methods for child resources
    #

    def child_names(self, **kwargs) -> list[str]:
        """Return names of each child resource."""
        return []

    def child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        return {}

    #
    # Concrete Methods for child resources
    #

    def child_path(self, key: str) -> Path:
        """Return the Path for a child resource."""
        row = self.child_dict(key)
        place = row[self.kPath]
        return UPath(place)

    def child(self, key: str, **kwargs):
        """Return a child resource."""
        path = self.child_path(key, **kwargs)
        if self.MANIFEST not in kwargs:
            kwargs[self.MANIFEST] = self
        return self.klass(path, **kwargs)

    #
    # Concrete HTTP Methods
    #

    def get(self, key: str, **kwargs) -> "Resource":
        """Get a child resource by name."""
        return self.child(key, **kwargs)

    def list(self, **kwargs) -> list[Resource]:
        """List all child resources by name."""
        return [self.child(key, **kwargs) for key in self.child_names(**kwargs)]


from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .resource import Resource
from .udg.keyed import Keyed


class ResourcePath(Resource, Keyed):
    """
    Path-based list and get.
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.glob = self.param(self.KEY_GLOB, "*")

    #
    # Private Methods for Path-based child resources
    #

    def _child_args(self, key: str) -> dict:
        """Return the kwargs for a child resource."""
        return {}

    def child(self, path: Path, key: str = ""):
        """Return a child resource."""
        args = self._child_args(key)
        args[self.KEY_KEY] = key
        merged = {**self.args, **args}
        self.CheckPath(path)
        return self.klass(path, **merged)

    def _child_path(self, key: str, **kwargs) -> Path:
        """Return the path for a child resource."""
        return self.path / key

    def _child_list(self) -> list[Path]:
        """List/generator of valid child paths; defaults to self.glob"""
        return sorted(self.path.glob(self.glob))

    #
    # Public HTTP-like Methods
    #

    def list(self, **kwargs) -> list[Resource]:
        """List all child resources."""
        return [self.child(x) for x in self._child_list()]

    def mapping(self, **kwargs) -> dict[str, Resource]:
        """Return a mapping of child resources."""
        return {x.name: x for x in self.list()}

    def __len__(self) -> int:
        """Return the number of child resources."""
        return len(self._child_list())

    def __iter__(self) -> Iterator[str]:
        """Iterate over child resources."""
        return self.mapping().keys().__iter__()

    def __getitem__(self, key: str) -> Resource:
        """Get a child resource by name."""
        return self.getResource(key)  # type: ignore

    def getResource(self, key: str, **kwargs) -> Resource:
        """Get a child resource by name."""
        path = self._child_path(key, **kwargs)
        if not path.exists():
            if not kwargs.get(self.KEY_FRC, False):
                raise KeyError(f"Key {key} not found in {self.path}")
            path.mkdir(parents=True)
        return self.child(path, key)

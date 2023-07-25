from __future__ import annotations

from pathlib import Path

from .resource import Resource


class ResourcePath(Resource):
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

    def _child_path(self, key: str) -> Path:
        """Return the path for a child resource."""
        return self.path / key

    def _child_list(self) -> list[Path]:
        """List/generator of valid child paths; defaults to self.glob"""
        return sorted(self.path.glob(self.glob))

    #
    # Public HTTP-like Methods
    #

    def list(self, **kwargs) -> list["Resource"]:
        """List all child resources."""
        return [self.child(x) for x in self._child_list()]

    def get(self, key: str, **kwargs) -> "Resource":
        """Get a child resource by name."""
        path = self._child_path(key)
        if not path.exists():
            raise KeyError(f"Key {key} not found in {self.path}")
        return self.child(path, key)

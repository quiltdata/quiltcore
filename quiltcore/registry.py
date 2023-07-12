from pathlib import Path

from .manifest import Manifest
from .resource import Resource
from .resource_path import ResourcePath


class Registry(ResourcePath):
    """
    Top-level Resource reperesenting a Quilt Registry.
    Defines core paths containing Namespaces and Manifests.
    `list` and `get` return Namespace objects
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.root = path
        self.base = self._setup_dir(path, "quilt3/dirs/config")
        self.path = self._setup_dir(self.base, "quilt3/dirs/names")
        self.manifests = self._setup_dir(self.base, "quilt3/dirs/manifests")

    def _setup_dir(self, path: Path, key: str) -> Path:
        """Form dir and create if it does not exist."""
        dir = path / self.cf.get_path(key)
        if not dir.exists():
            dir.mkdir(parents=True, exist_ok=True)
        return dir

    def _child_args(self, key: str) -> dict:
        return {"manifests": self.manifests}

    def put(self, res: Resource, **kwargs) -> "Resource":
        """Link manifest into namespace"""
        if not isinstance(res, Manifest):
            raise TypeError(f"Expected Manifest, got {type(res)}")
        hash = res.hash()
        name = kwargs[self.KEY_NAME]
        name_dir = self.path / name
        name_dir.mkdir(parents=True, exist_ok=True)

        tag = self.Timestamp()
        tag_file = name_dir / tag
        tag_file.write_text(hash)

        latest_file = name_dir / self.TAG_DEFAULT
        latest_file.unlink(missing_ok=True)
        latest_file.write_text(hash)

        return res

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

    DIR_PREFIX = "quilt3/dirs/"

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.root = path
        self.base = self._setup_dir(path, "config")
        self.path = self._setup_dir(self.base, "names")
        self.manifests = self._setup_dir(self.base, "manifests")
        self.stage = self._setup_dir(self.base, "stage")

    def _setup_dir(self, path: Path, key: str) -> Path:
        """Form dir and create if it does not exist."""

        dir = path / self.cf.get_path(self.DIR_PREFIX + key)
        if not dir.exists():
            dir.mkdir(parents=True, exist_ok=True)
        return dir

    def _child_args(self, key: str) -> dict:
        return {self.KEY_MAN: self.manifests}

    def put(self, res: Resource, **kwargs) -> "Resource":
        """Link manifest into namespace"""
        if not isinstance(res, Manifest):
            raise TypeError(f"Expected Manifest, got {type(res)}")
        hash = res.hash_quilt3()
        name = kwargs[self.KEY_NS]
        name_dir = self.path / name
        name_dir.mkdir(parents=True, exist_ok=True)

        tag = self.Now()
        tag_file = name_dir / tag
        tag_file.write_text(hash)

        latest_file = name_dir / self.TAG_DEFAULT
        latest_file.unlink(missing_ok=True)
        latest_file.write_text(hash)

        res.args[self.KEY_TAG] = tag
        return res

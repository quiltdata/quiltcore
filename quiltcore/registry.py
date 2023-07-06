from pathlib import Path

from .resource_path import ResourcePath


class Registry(ResourcePath):
    """
    Top-level Resource reperesenting a Quilt Registry.
    Defines core paths containing Namespaces and Manifests.
    `list` and `get` return Namespace objects
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        base = path / self.cf.get_path("quilt3/dirs/config")
        self.path = base / self.cf.get_path("quilt3/dirs/names")
        self.manifests = base / self.cf.get_path("quilt3/dirs/manifests")

    def child_args(self, key: str) -> dict:
        return {"manifests": self.manifests}

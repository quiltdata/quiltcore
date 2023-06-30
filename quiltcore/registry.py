from pathlib import Path

from .resource import Resource


class Registry(Resource):
    """
    Top-level Resource reperesenting a Quilt Registry.
    Defines core paths containing Namespaces and Manifests.
    `list` and `get` return Namespace objects
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        base = path / self.cf.get_path("dirs/config")
        self.path = base / self.cf.get_path("dirs/names")
        self.versions = base / self.cf.get_path("dirs/versions")

    def child_args(self, key: str) -> dict:
        return {"versions": self.versions}

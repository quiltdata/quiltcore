from .config import Config


class Spec(Config):
    """Manage quiltspec parameters"""

    CONFIG_FILE = "quiltspec.yaml"
    K_PKG = "config"

    def __init__(self, name=None, update=None) -> None:
        super().__init__()
        self.name = name
        self.update = update

    def pkg(self, key: str) -> str:
        _pkg = self.get_dict(self.K_PKG)
        return _pkg.get(key, "<missing>")

    # Configuration

    def registry(self) -> str:
        return self.pkg("registry")

    def namespace(self) -> str:
        return self.name or self.pkg("namespace")

    def hash(self) -> str:
        return self.pkg("hash")

    def tag(self) -> str:
        return str(self.pkg("tag"))

    # Contents

    def files(self) -> dict:
        _files = self.get_dict("files")
        update = self.pkg("update")
        for key in _files:
            if key in update and self.update:
                _files[key] = self.update
        return _files

    def metadata(self, key="_package") -> dict:
        return self.get_dict(f"metadata/{key}")

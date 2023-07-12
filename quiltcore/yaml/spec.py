from pathlib import Path

from .config import Config


class Spec(Config):
    CONFIG_FILE = "quiltspec.yaml"
    K_PKG = "config"

    def __init__(self) -> None:
        super().__init__()

    def pkg(self, key: str) -> str:
        _pkg = self.get_dict(self.K_PKG)
        print(f"pkg: {_pkg.keys()}")
        return _pkg.get(key, "<missing>")

    # Configuration

    def registry(self) -> str:
        return self.pkg("registry")

    def namespace(self) -> str:
        return self.pkg("namespace")

    def hash(self) -> str:
        return self.pkg("hash")
    
    # Contents

    def files(self) -> dict:
        return self.get_dict("files")

    def metadata(self) -> dict:
        return self.get_dict("metadata")

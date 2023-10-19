from .config import Config
from .udi import UDI


class Spec(Config):
    """Manage quiltspec parameters"""

    CONFIG_FILE = "quiltspec.yaml"

    def __init__(self, name=None, update=None) -> None:
        super().__init__()
        self.name = name
        self.update = update

    def udi(self) -> UDI:
        udi_string = self.pkg("udi")
        return UDI.FromUri(udi_string)

    def udi_new(self) -> UDI:
        udi_string = f"quilt+{self.registry()}#package={self.name}"
        return UDI.FromUri(udi_string)

    def pkg(self, key: str) -> str:
        _pkg = self.get_dict(self.K_CFG)
        return _pkg.get(key, "<missing>")

    # Configuration

    def registry(self) -> str:
        return self.pkg("registry")

    def namespace(self) -> str:
        return self.name or self.pkg("namespace")

    def hash(self) -> str:
        return self.pkg(self.K_HASH)

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

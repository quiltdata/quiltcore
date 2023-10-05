import logging
from un_yaml import UnConf  # type: ignore
from upath import UPath


class Data(UnConf):
    DATA_FILE = "data.yaml"

    def __init__(self, path: UPath) -> None:
        assert path.exists() and path.is_dir()
        super().__init__(path / self.DATA_FILE)

    def save(self):
        self.path.touch(exist_ok=True)
        super().save()

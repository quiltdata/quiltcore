from un_yaml import UnYaml  # type: ignore
from upath import UPath


class Config(UnYaml):
    CONFIG_FILE = "quiltcore.yaml"
    K_MAP = "map"
    K_NAM = "name"
    K_PLC = "place"
    K_HSH = "hash"

    @classmethod
    def DefaultConfig(cls) -> dict:
        return UnYaml.LoadYaml(cls.CONFIG_FILE, __package__)

    def __init__(self, yaml_data: dict = {}) -> None:
        data = yaml_data if len(yaml_data) > 0 else self.DefaultConfig()
        super().__init__(data)

    def get_str(self, key: str, default="") -> str:
        return super().get(key) or default

    def get_path(self, key: str) -> UPath:
        str_path = self.get_str(key, ".")
        return UPath(str_path)

    def get_bool(self, key: str) -> bool:
        return self.get(key) or False

    def get_dict(self, key: str) -> dict:
        return self.get(key) or {}

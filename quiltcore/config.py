from un_yaml import UnYaml  # type: ignore


class CoreConfig(UnYaml):
    CONFIG_FILE = "config.yaml"

    @classmethod
    def DefaultConfig(cls) -> dict:
        return UnYaml.LoadYaml(cls.CONFIG_FILE, __package__)

    def __init__(self, yaml_data: dict = {}) -> None:
        data = yaml_data if len(yaml_data) > 0 else CoreConfig.DefaultConfig()
        super().__init__(data)

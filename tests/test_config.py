from quiltcore import CoreConfig


def test_config():
    cfg = CoreConfig()
    assert cfg
    assert cfg.get("config_dir") == ".quilt"

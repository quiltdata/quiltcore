from quiltcore import CoreConfig

def test_config():
    cfg = CoreConfig()
    assert cfg
    assert cfg.get("root") == ".quilt"
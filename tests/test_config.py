from quiltcore import Config


def test_config():
    cfg = Config()
    assert cfg
    assert cfg.get("quilt3/dirs/config") == ".quilt"

from quiltcore import Config, Decoder, Hash3


def test_cf_config():
    cfg = Config()
    assert cfg
    assert cfg.get("quilt3/dirs/config") == ".quilt"


def test_cf_decoder():
    codec = Decoder()
    assert isinstance(codec.coding, dict)


def test_cf_hash():
    codec = Decoder()
    ht = codec.config("hash_type")
    assert ht == "SHA256"

    mh = codec.get_dict("multihash")
    assert mh
    assert codec.MH_DIG in mh
    assert codec.MH_PRE in mh

    assert mh[codec.MH_PRE][ht] == "1220"
    assert codec.hash_config(codec.MH_DIG)[ht] == "sha2-256"
    assert codec.digester()
    mhash = codec.digest(b"Hello World")
    assert mhash

    prefixes = codec.hash_config(codec.MH_PRE)
    assert isinstance(prefixes, dict)
    hash_struct = codec.encode_hash(mhash)
    assert isinstance(hash_struct, dict)
    assert hash_struct["type"] == ht
    assert hash_struct["value"] == mhash.removeprefix("1220")
    hash_data = Hash3(**hash_struct)
    assert codec.decode_hash(hash_data) == mhash

    codec.check_opts({codec.T_HSH: True})
    assert codec.encode_value(mhash) == hash_struct
    assert codec.decode_value(hash_struct) == mhash


def test_cf_encode():
    codec = Decoder()

    TEST_STR = "file://READ ME.md"
    codec.check_opts({})
    assert codec.encode_value(TEST_STR) == TEST_STR

    codec.check_opts({codec.T_QTD: True})
    result = codec.encode_value(TEST_STR)
    assert result != TEST_STR
    assert isinstance(result, str)

    codec.check_opts({codec.T_LST: True})
    assert codec.encode_value(TEST_STR) == [TEST_STR]

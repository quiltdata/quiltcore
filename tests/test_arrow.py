from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore
import pyarrow.parquet as pq  # type: ignore
import pytest  # noqa: F401

from quiltcore import Table3, Table4, Dict4

from .conftest import TEST_MAN, TEST_PARQUET

test_file = "tests/test.parquet"


def test_arrow_pandas():
    df = pd.DataFrame(
        {
            "one": [-1, np.nan, 2.5],
            "two": ["foo", "bar", "baz"],
            "three": [True, False, True],
        },
        index=list("abc"),
    )  # type: ignore
    table = pa.Table.from_pandas(df)
    assert table
    with TemporaryDirectory() as tmpdirname:
        f = Path(tmpdirname) / "test.parquet"
        fn = str(f)
        pq.write_table(table, fn)
        table2 = pq.read_table(fn)
        assert table.equals(table2)


def test_arrow_json():
    s3, path = pa.fs.FileSystem.from_uri(TEST_MAN)
    assert s3
    assert path
    assert "packages" in str(path)
    with s3.open_input_stream(path) as f:
        table = pj.read_json(f)
        assert table


def test_arrow_table():
    path = Table3.AsPath(TEST_MAN)
    table = Table3(path)
    body = table.body
    assert body.num_rows == 1
    schema = body.schema
    assert schema
    columns = table.codec.get_dict("quilt3/schema")
    for key in columns:
        assert key in schema.names

    col = table.names()
    assert col
    assert len(col) == 2
    assert col[0] == Table3.HEADER_NAME
    assert col[1] == "ONLYME.md"


def test_arrow_table3():
    path = Table3.AsPath(TEST_MAN)
    assert path.exists()
    table3 = Table3(path)
    assert table3
    assert "pyarrow.Table" in str(table3)
    assert len(table3) == 2
    assert "ONLYME.md" in table3

    assert Table3.HEADER_NAME in table3
    head = table3[Table3.HEADER_NAME]
    assert isinstance(head, Dict4)
    assert head.info[Table3.K_VERSION] == "v0"
    assert "ONLYME" in head.info[Table3.K_MESSAGE]
    assert head.meta["Author"] == "Ernest"


def test_arrow_table4():
    path = Table3.AsPath(TEST_PARQUET)
    assert path.exists()
    table4 = Table4(path)
    assert table4
    assert "Table4" in repr(table4)
    assert len(table4) == 2
    assert "ONLYME.md" in table4
    assert Table4.HEADER_NAME in table4
    head = table4[Table4.HEADER_NAME]
    assert isinstance(head, Dict4)
    assert head.info[Table4.K_VERSION] == "v4"
    assert "ONLYME" in head.info[Table4.K_MESSAGE]


def test_arrow_relax():
    path3 = Table3.AsPath(TEST_MAN)
    assert path3.exists()
    table3 = Table3(path3)
    assert table3
    with TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        pout = root / "test"
        list4 = table3.relax(root)
        ppout = Table4.ParquetPath(pout)
        print(f"pout: {pout} ppout: {ppout}")
        assert pout.parent == ppout.parent
        assert ppout.name.startswith(Table4.MULTIHASH)
        assert ppout.name.endswith(Table4.EXT4)
        p4out = Table4.WriteParquet(list4, pout)
        assert p4out == ppout

        table4 = Table4(ppout)
        assert table4
        meta = table4.head.info
        assert meta
        assert meta["version"] == "v2"
        assert "ONLYME.md" in table4.keys()
        entry = table4["ONLYME.md"]
        assert entry
        assert entry.name == "ONLYME.md"

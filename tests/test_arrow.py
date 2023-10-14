from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore
import pyarrow.parquet as pq  # type: ignore
import pytest  # noqa: F401

from quiltcore import Resource, Table3, Table4

from .conftest import TEST_MAN

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


def test_arrow_s3():
    s3, path = pa.fs.FileSystem.from_uri(TEST_MAN)
    assert s3
    assert path
    assert "packages" in str(path)
    with s3.open_input_stream(path) as f:
        table = pj.read_json(f)
        assert table


def test_arrow_table():
    path = Resource.AsPath(TEST_MAN)
    table = Table3(path)
    assert isinstance(table, Table3)
    head = table.head
    assert head.version == "v0"  # type: ignore
    assert len(head.message) > 0  # type: ignore
    assert len(head.user_meta) > 0  # type: ignore
    assert head.user_meta["Author"] == "Ernest"  # type: ignore

    body = table.body
    assert body.num_rows == 1
    schema = body.schema
    assert schema
    columns = table.codec.get_dict("quilt3/schema")
    for key in columns:
        assert key in schema.names

    col = table.names()
    assert col
    assert col[0] == "ONLYME.md"


def test_arrow_relax():
    path = Resource.AsPath(TEST_MAN)
    assert path.exists()
    table = Table3(path)
    with TemporaryDirectory() as tmpdirname:
        f = Path(tmpdirname)
        pout = f / "test.parquet"
        list4 = table.relax(f)
        Table4.Write4(list4, pout)
        table4 = Table4(pout)
        meta = table4.head.metadata
        assert meta
        assert meta["version"] == "v4"
        assert "ONLYME.md" in table4.keys()
        entry = table4["ONLYME.md"]
        assert entry

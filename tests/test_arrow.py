from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore
import pyarrow.parquet as pq  # type: ignore
from pytest import mark
from quiltcore import Table

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


@mark.skip("Need to understand Arrow schema")
def test_arrow_schema():
    path = Table.AsPath(TEST_MAN)
    table = Table(path)
    yaml_schema = table.cf.get_dict("quilt3/schema")
    assert yaml_schema
    schema = pa.schema(yaml_schema)
    assert schema


def test_arrow_table():
    path = Table.AsPath(TEST_MAN)
    table = Table(path)
    assert table
    head = table.head
    assert head
    assert head.version == "v0"  # type: ignore
    assert len(head.message) > 0  # type: ignore
    assert len(head.user_meta) > 0  # type: ignore
    assert head.user_meta["Author"] == "Ernest"  # type: ignore

    body = table.body
    assert body
    assert body.num_rows == 1
    schema = body.schema
    assert schema
    columns = table.cf.get_dict("quilt3/columns")
    for key in columns:
        assert key in schema.names
    cn = schema.names[0]
    col = body.column(cn)
    assert col
    assert col[0].as_py() == "ONLYME.md"

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore
import pyarrow.parquet as pq  # type: ignore
import pytest

test_file = "tests/test.parquet"


def test_arrow_pandas():
    df = pd.DataFrame(
        {
            "one": [-1, np.nan, 2.5],
            "two": ["foo", "bar", "baz"],
            "three": [True, False, True],
        },
        index=list("abc"),
    )
    table = pa.Table.from_pandas(df)
    assert table
    with TemporaryDirectory() as tmpdirname:
        f = Path(tmpdirname) / "test.parquet"
        fn = str(f)
        assert "/tmp" in fn
        pq.write_table(table, fn)
        table2 = pq.read_table(fn)
        assert table.equals(table2)


def test_arrow_s3():
    S3_URI = (
        "s3://quilt-example/.quilt/packages/"
        + "00004ceff627cc6679fec2c9d55e16614dc055695fc2e4c85f02c0845bfda12f"
    )
    s3, path = pa.fs.FileSystem.from_uri(S3_URI)
    assert s3
    assert path
    assert "packages" in str(path)
    with s3.open_input_stream(path) as f:
        table = pj.read_json(f)
        assert table
        print(table.schema)
        assert True

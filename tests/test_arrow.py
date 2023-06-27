from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore
import pyarrow.parquet as pq  # type: ignore

from .conftest import TEST_TABLE

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
        pq.write_table(table, fn)
        table2 = pq.read_table(fn)
        assert table.equals(table2)


def test_arrow_s3():
    s3, path = pa.fs.FileSystem.from_uri(TEST_TABLE)
    assert s3
    assert path
    assert "packages" in str(path)
    with s3.open_input_stream(path) as f:
        table = pj.read_json(f)
        assert table
        print(table.schema)
        assert True

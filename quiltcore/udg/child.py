import logging

from pathlib import Path

from .node import Node
from .types import Dict3, Dict4, List4
from .tabular import Tabular


class Child(Node):
    def __init__(self, name: str, parent: Node, **kwargs):
        super().__init__(parent.cf, name, parent, **kwargs)
        logging.debug(f"Child.init: {self} <- {self.parent}")
        assert parent == self.parent
        self.headers = self.cf.get_dict("quilt3/headers")

    def dict4_to_header(self, dict4) -> dict:
        raw_dict = {}
        for k in self.headers.keys():
            if hasattr(dict4, k):
                raw_dict[k] = getattr(dict4, k)
        return self.cf.encode_dates(raw_dict)

    def dict4_to_dict3(self, dict4: Dict4) -> Dict3:
        if not hasattr(dict4, "path"):
            path = self.AsPath(dict4.place)
            setattr(dict4, "path", path)
        result = self.encode_date_dicts(dict4)
        assert isinstance(result, Dict4)
        return self.cf.encode_dict4(result)

    def encode_date_dicts(self, base: Dict4):
        for key in self.K_JSON_FIELDS:
            value = getattr(base, key)
            if value:
                new_value = self.cf.encode_dates(value)
                setattr(base, key, new_value)
            return base

    def save_manifest(self, list4: List4, path: Path, writeJSON=True) -> Path:
        assert list4, "save_manifest: list4 is empty; cannot save to {path}}"
        parquet_path = Tabular.WriteParquet(list4, path)
        if writeJSON:
            head4 = list4.pop()
            list3: list[Dict3] = [self.dict4_to_dict3(dict4) for dict4 in list4]
            head = self.dict4_to_header(head4)
            Tabular.WriteJSON(head, list3, path)
        return parquet_path if parquet_path.exists() else path

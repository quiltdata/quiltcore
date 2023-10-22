import logging

from pathlib import Path

from .header import Header
from .node import Node
from .types import Dict3, Dict4, List4
from .tabular import Tabular


class Child(Node):
    def __init__(self, name: str, parent: Node, **kwargs):
        super().__init__(parent.cf, name, parent, **kwargs)
        logging.debug(f"Child.init: {self} <- {self.parent}")
        assert parent == self.parent, f"Child.init: {parent} != {self.parent}"

    def dict4_to_meta3(self, dict4: Dict4) -> dict:
        meta = dict4.info
        meta[self.K_USER_META] = dict4.meta
        return self.cf.encode_dates(meta)

    def dict4_to_dict3(self, dict4: Dict4) -> Dict3:
        if not hasattr(dict4, "path"):
            path = self.AsPath(dict4.place)
            setattr(dict4, "path", path)
        result = self.encode_date_dicts(dict4)
        assert isinstance(result, Dict4), f"dict4_to_dict3: {result} is not a Dict4"
        dict3 = self.cf.encode_dict4(result)
        return dict3

    def encode_date_dicts(self, base: Dict4):
        for key in self.K_JSON_FIELDS:
            value = getattr(base, key)
            if value:
                new_value = self.cf.encode_dates(value)
                setattr(base, key, new_value)
            return base

    def save_manifest(self, list4: List4, path: Path, msg="", writeJSON=True) -> Path:
        print(f"save_manifest: {list4} to {path}")
        assert list4, "save_manifest: list4 is empty; cannot save to {path}}"
        parquet_path = Tabular.WriteParquet(list4, path)
        if writeJSON:
            if msg:
                head4 = Header.HeaderDict4(msg)
            else:
                header = [dict4 for dict4 in list4 if dict4.name == Tabular.HEADER_NAME]
                print(f"save_manifest.header: {header}")
                if not header:
                    raise ValueError(f"save_manifest: no header in {list4}")
                else:
                    head4 = header[0]
                    print(f"save_manifest.head4: {head4}")
                    list4.remove(head4)
            print(f"save_manifest.head4: {head4}")
            meta3 = self.dict4_to_meta3(head4)
            print(f"save_manifest.meta3: {meta3}")
            body3: list[Dict3] = [self.dict4_to_dict3(dict4) for dict4 in list4]
            print(f"save_manifest.body3: {body3}")
            Tabular.WriteJSON(meta3, body3, path)
        return parquet_path

import logging
from typing import Any

from un_yaml import UnConf  # type: ignore
from pathlib import Path


class Data(UnConf):
    DATA_FILE = "data.yaml"
    DEFAULTS = {
        "app": DATA_FILE,
        "app_version": "0.1.0",
        "doc": "quiltcore",
        "doc_version": "0.1.0",
    }

    def __init__(self, path: Path) -> None:
        assert path.exists() and path.is_dir()
        super().__init__(path / self.DATA_FILE, **self.DEFAULTS)

    def save(self):
        self.path.touch(exist_ok=True)
        super().save()

    def put_list(self, *values):
        parent = self.data
        keys = list(values)
        value = keys.pop()
        tail = keys.pop()
        for child in keys:
            logging.debug(f"child: {child} parent: {parent}")
            if child not in parent:
                parent[child] = {}
            parent = parent[child]
            logging.debug(f"+parent: {parent}")
        parent[tail] = value

    def get_list(self, *keys):
        parent = self.data
        for child in keys:
            if child not in parent:
                return None
            parent = parent[child]
        return parent

    def set(self, prefix: str, uri: str, action: str, value: Any):
        self.put_list(prefix, uri, action, value)
        self.save()

    def folder2uri(self, folder: str) -> str:
        uri_dict = self.data.get(folder) or {}
        return list(uri_dict.keys())[-1] if uri_dict else ""

    def uri2folder(self, uri: str) -> str | None:
        for folder, uri_dict in self.data.items():
            if uri in uri_dict:
                return folder
        return None

from pathlib import Path

from .delta import Delta
from .header import Header
from .resource_key import ResourceKey


class Builder(ResourceKey):
    """
    Create Entry resources for each row
    Calculate the hash
    Write a new manifest file
    Return the path
    """

    def __init__(self, path: Path, head: Header, rows: list[dict], **kwargs):
        super().__init__(path, **kwargs)
        self.head = head
        self.keystore = {row[Delta.K_NAM]: row for row in rows} # type: ignore

    def _child_names(self, **kwargs) -> list[str]:
        """Return names of each child resource."""
        return list(self.keystore.keys())

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        return self.keystore[key]

    def manifest_path(self) -> Path:
        return self.path / self.calc_hash(self.head)

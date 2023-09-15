from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .udg.codec import Dict4
from .udg.verifiable import Verifiable

class ChangeOp(Enum):
    ADD = "add"
    KEEP = "keep"
    MOVE = "move"
    REMOVE = "remove"
    REPLACE = "replace"

@dataclass
class Change:
    """
    A single change to a Manifest
    Creates one or more Entries
    """

    operation: ChangeOp = ChangeOp.ADD
    path: Path | None = None
    dict4: Dict4 | None = None
    meta: dict = field(default_factory=dict)
    prefix: str | None = None

    def logical_key(self, path: Path) -> str:
        assert self.path is not None
        relative = path.relative_to(self.path)
        return str(relative)
    
    def _dict4(self, path: Path, parent: Verifiable) -> Dict4:
        assert self.dict4 is None
        assert path is not None
        return parent.to_dict4(path)

    def to_dict4s(self, parent: Verifiable) -> list[Dict4]:
        if self.operation == ChangeOp.REMOVE:
            return []

        if self.operation == ChangeOp.ADD:
            assert self.path is not None
            if self.path.is_file():
                return [self._dict4(self.path, parent)]
            return [self._dict4(p, parent) for p in self.path.iterdir()]

        assert self.dict4 is not None
        if self.operation == ChangeOp.MOVE:
            if self.path is not None:
                self.dict4.place = str(self.path)

        return [self.dict4]

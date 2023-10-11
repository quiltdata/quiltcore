from __future__ import annotations

import logging
from pathlib import Path

from .codec import Codec
from .verifiable import Verifiable


class Node(Verifiable):
    """
    Base class for all Nodes.

    Contains:
    - name
    - parent
    - path
    - type
    - children
    """

    DEFAULT_PATH = Path(".")

    def __init__(self, codec: Codec, name: str, parent: "Node" | None, **kwargs):
        super().__init__(codec, **kwargs)
        self.name = name
        self.parent = parent
        self.path = self.extend_parent_path(name)
        self.type = f"{self.cf.info('app')}.{self.class_key}"
        self._setup()

    def __repr__(self):
        name = f"{self.name}:{self.parent_name()}"
        return f"<{self.class_name}({name}, {self.args})@{self.path}>"

    def __str__(self):
        return f"<{self.class_name}({self.name})>"

    def check_parent(self) -> Node | None:
        if hasattr(self, "parent"):
            if parent := getattr(self, "parent") is not None:
                assert isinstance(parent, Node)
                return parent
        return None

    def set_dirty(self, state: bool = True):
        super().set_dirty(state)
        if parent := self.check_parent() is not None:
            assert isinstance(parent, Node)
            parent.set_dirty(state)

    def extend_parent_path(self, key: str) -> Path:
        if self.parent is not None and hasattr(self.parent, "path"):
            root = self.parent.path / key
            return root
        return self.DEFAULT_PATH

    def parent_name(self) -> str:
        return self.parent.name if self.parent is not None else "None"

    def param(self, key: str, default: str) -> str:
        """Return a param."""
        return self.params[key] if key in self.params else default  # type: ignore

    def _setup(self):
        """Load Node-specific params from config file."""
        self.params = self.cf.get_dict(f"resources/{self.class_name}")
        self._child_class = self.param("child", self.class_name)
        if self._child_class == self.class_name:
            raise ValueError(f"No child class found for: {self.class_name}")

    def make_child(self, name: str, **kwargs) -> Node:
        logging.debug(f"Node.make_child: {self._child_class}({name}) <- {self}")
        klass = self.ClassFromName(self._child_class)
        merged = {**self.args, **kwargs}
        return klass(name, self, **merged)

    def _get(self, key: str) -> Node:
        """Return child Node for a key."""
        return self.make_child(key)

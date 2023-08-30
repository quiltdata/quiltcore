from __future__ import annotations

import logging


from .codec import Codec
from .verifiable import Verifiable


class Node(Verifiable):
    def __init__(self, codec: Codec, name: str, parent: "Node" | None, **kwargs):
        super().__init__(codec, **kwargs)
        self.name = name
        self.parent = parent or self
        self.type = f"{self.cf.info('app')}.{self.class_key}"
        logging.debug(f"Node.init: {repr(self)}")
        self._setup()

    def __repr__(self):
        return f"<{self.class_name}({self.name}.{self.parent.name}, {self.args})>"

    def __str__(self):
        return f"<{self.class_name}({self.name})>"

    def param(self, key: str, default: str) -> str:
        """Return a param."""
        return self.params[key] if key in self.params else default  # type: ignore

    def _setup(self):
        """Load Node-specific params from config file."""
        self.params = self.cf.get_dict(f"resources/{self.class_name}")
        self._child_class = self.param("child", self.class_name)

    def make_child(self, name: str, **kwargs) -> Node:
        klass = self.ClassFromName(self._child_class)
        merged = {**self.args, **kwargs}
        return klass(name, self, **merged)

    def __getitem__(self, key: str) -> Node:
        """Return a Node."""
        return self.make_child(key)

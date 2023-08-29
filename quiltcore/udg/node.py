from __future__ import annotations

import logging

from typing_extensions import Self

from .verifiable import Verifiable
from .codec import Codec

class Node(Verifiable):

    def __init__(self, codec: Codec, name: str, parent: Self, **kwargs):
        super().__init__(codec, **kwargs)
        self.name = name
        self.parent = parent
        self.type = f"{self.cf.info('app')}.{self.class_key}"
        logging.debug(f"Node.init: {repr(self)}")
        self.param_setup()

    def __repr__(self):
        return f"<{self.class_name}({self.name}.{self.parent.name}, {self.args})>"

    def __str__(self):
        return f"<{self.class_name}({self.name})>"

    def param(self, key: str, default: str) -> str:
        """Return a param."""
        return self.params[key] if key in self.params else default  # type: ignore

    def param_setup(self):
        """Load Node-specific params from config file."""
        self.params = self.cf.get_dict(f"resources/{self.class_name}")
        _child = self.param("child", self.class_name)
        self.klass = self.ClassFromName(_child)


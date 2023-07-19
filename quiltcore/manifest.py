import logging
from pathlib import Path

import pyarrow as pa  # type: ignore
import pyarrow.compute as pc  # type: ignore
import pyarrow.json as pj  # type: ignore

from .header import Header
from .resource_key import ResourceKey
from .table import Table


class Manifest(ResourceKey):
    """
    In-memory representation of a serialized package manifest.
    list/get returns Entry with Path to the Place data actually lives
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.decoded = False
        try:
            self.table = Table(path, **kwargs)
            self.head = self.table.head
        except FileNotFoundError:
            logging.warning(f"Manifest not found: {path}")
        self.name_key = "name" if self.encoded() else self.kName
        self.places_key = "places" if self.encoded() else self.kPlaces
        self._setup_hash()

    #
    # Hash functions
    #

    def source_hash(self) -> str:
        """
        Return the hash of the contents.
        """
        return self.name

    def calc_multihash(self) -> str:
        hashable = self.head.hashable()
        for entry in self.list():
            hashable += entry.hashable()  # type: ignore
        return self.digest(hashable)

    def calc_hash(self) -> str:
        """
        Return the hash of the manifest.
        """
        return self.calc_multihash().removeprefix(self.DEFAULT_MH_PREFIX)

    #
    # Private Methods for child resources
    #

    def _child_names(self, **kwargs) -> list[str]:
        """List all child resource names."""
        return self.table.column(self.name_key)

    def _child_place(self, places, root="") -> str:
        """Return the place for a child resource."""
        place = places[0] if isinstance(places, list) else places
        if place.startswith(self.LOCAL):
            stem = place.replace(self.LOCAL, "")
            if len(root) == 0:
                registry = self.args.get("registry")
                logging.debug(f"_child_place.registry: {registry} for ->\n\t{self.args.keys()}")
                if registry:
                    root = registry.root
                    logging.debug(f"_child_place.root: {root}")
            place = Path(root) / stem
        return str(place)

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        # TODO: cache to avoid continually re-calcluating
        row = self.table.filter(self.name_key, key)
        places = row[self.places_key][0]
        place = self._child_place(places)
        row[self.KEY_PATH] = place
        v = self.GetVersion(place)
        if len(v) > 0:
            row[self.KEY_VER] = v
        return row

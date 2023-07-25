import logging
from pathlib import Path


from .resource_key import ResourceKey
from .table import Table
from .yaml.decoder import asdict


class Manifest(ResourceKey):
    """
    In-memory representation of a serialized package manifest.
    list/get returns Entry with Path to the Place data actually lives
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        try:
            self.table = Table(path, **kwargs)
            self.head = self.table.head
        except FileNotFoundError:
            logging.warning(f"Manifest not found: {path}")

    #
    # Hash functions
    #

    def hash_quilt3(self) -> str:
        """Legacy quilt3 hash of the contents."""
        return self.name

    #
    # Private Methods for child resources
    #

    def _child_names(self, **kwargs) -> list[str]:
        """List all child resource names."""
        return self.table.names()

    def _child_place(self, place: str) -> str:
        if not self.IS_REL in place:
            return place
        if self.IS_LOCAL.match(place) != None:
            place = self.IS_LOCAL.sub("", place)
        if not self.ARG_REG in self.args:
            raise KeyError(f"No registry root available in {self.args.keys()}")
        reg = self.args[self.ARG_REG]
        path = reg.root / place
        logging.debug(f"{place} -> {path} [{path.absolute()}]")
        return str(path) # .as_uri()

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        row = self.table.get_row4(key)
        place = row.place
        drow = asdict(row)
        drow[self.codec.K_PLC] = self._child_place(place)
        v = self.GetVersion(place)
        if len(v) > 0:
            drow[self.KEY_VER] = v
        return drow

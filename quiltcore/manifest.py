import logging
from pathlib import Path

import pyarrow as pa  # type: ignore
import pyarrow.compute as pc  # type: ignore
import pyarrow.json as pj  # type: ignore

from .resource_key import ResourceKey


class Manifest(ResourceKey):
    """
    In-memory representation of a serialized package manifest.
    list/get returns Entry with Path to the Place data actually lives
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.decoded = False
        try:
            self.body = self._setup_table()
        except FileNotFoundError:
            logging.warning(f"Manifest not found: {path}")
        self.name_key = "name" if self.decoded else self.kName
        self.places_key = "places" if self.decoded else self.kPlaces

    def hash(self) -> str:
        return self.name

    #
    # Parse Table
    #

    def header_keys(self) -> list[str]:
        headers = self.cf.get_dict("quilt3/headers")
        return list(headers.keys())

    def header_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.cols}

    def _setup_table(self) -> pa.Table:
        """
        Read the manifest into a pyarrow Table.
        Extract header values into attributes.
        Return the Table without header row and columns
        """
        with self.path.open(mode="rb") as fi:
            self.table = pj.read_json(fi)
        first = self.table.take([0]).to_pydict()
        self.cols = []
        for header in self.header_keys():
            if header in first:
                self.cols.append(header)
                setattr(self, header, first[header][0])
        body = self.table.drop_columns(self.cols).slice(1)
        return self.decode_table(body)

    def decode_table(self, body: pa.Table) -> pa.Table:
        """
        URL-Decode appropriate columns of the manifest.
        """
        encoded = self.cf.get_dict("quilt3/encoded")
        for old_col, new_col in encoded.items():
            self.decoded = True
            if old_col in body.column_names:
                body = body.append_column(
                    new_col,
                    self.decode_item(body.column(old_col)),
                )

        return body

    def decode_item(self, item):
        item_type = type(item)
        if isinstance(item, str):
            return self.decode(item)
        if isinstance(item, list):
            return [self.decode_item(item[0])]
        if isinstance(item, pa.ChunkedArray):
            return pa.chunked_array([self.decode_item(chunk) for chunk in item.chunks])
        if issubclass(item_type, pa.Array):
            return [self.decode_item(chunk) for chunk in item.to_pylist()]
        raise TypeError(f"Unexpected type: {item_type}")

    #
    # Private Methods for child resources
    #

    def _child_names(self, **kwargs) -> list[str]:
        """List all child resources."""
        names = self.body.column(self.name_key).to_pylist()
        return names
    
    def _child_place(self, places, root="") -> str:
        """Return the place for a child resource."""
        place = places[0] if isinstance(places, list) else places
        if place.startswith(self.LOCAL):
            stem = place.replace(self.LOCAL, "")
            if len(root) == 0:
                registry = self.args.get("registry")
                print(f"_child_place.registry: {registry} for ->\n\t{self.args.keys()}")
                if registry:
                    root = registry.root
                    logging.debug(f"_child_place.root: {root}")
            place = Path(root) / stem
        return str(place)

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        # TODO: cache to avoid continually re-calcluating
        rows = self.body.filter(pc.field(self.name_key) == key)
        if rows.num_rows == 0:
            raise KeyError(f"Key [{key}] not found in {self.name_key} of {self.path}")
        row = rows.to_pydict()
        places = row[self.places_key][0]
        place = self._child_place(places)
        row[self.KEY_PATH] = place
        v = self.GetVersion(place)
        if len(v) > 0:
            row[self.KEY_VER] = v
        return row

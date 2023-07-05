from __future__ import annotations

from pathlib import Path

from upath import UPath

from .resource import Resource


class ResourceKey(Resource):
    """
    Get/List child resources by key in Manifest
    """

    DEFAULT_HASH_TYPE = "SHA256"
    MANIFEST = "_manifest"

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.defaultHash = self.cf.get_str("quilt3/hash_type", self.DEFAULT_HASH_TYPE)
        self.kHash = self.cf.get_str("quilt3/hash", "hash")
        self.kMeta = self.cf.get_str("quilt3/meta", "meta")
        self.kName = self.cf.get_str("quilt3/name", "logical_key")
        self.kPath = "path"
        self.kPlaces = self.cf.get_str("quilt3/places", "physical_keys")
        self.kSize = self.cf.get_str("quilt3/size", "size")

    #
    # Abstract Methods for child resources
    #

    def child_names(self, **kwargs) -> list[str]:
        """Return names of each child resource."""
        return []

    def child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        return {}

    #
    # Concrete Methods for child resources
    #

    def key_path(self, key: str, args: dict = {}) -> Path:
        """Return the Path for a child resource."""
        if self.kPath not in args:
            raise KeyError(f"Missing {self.kPath} in {args.keys()}")
        place = args[self.kPath]
        return UPath(place)

    def child(self, key: str, **kwargs):
        """Return a child resource."""
        args = self.child_dict(key)
        path = self.key_path(key, args)
        merged = {**self.args, **args}
        if self.kPath in merged:
            del merged[self.kPath]
        return self.klass(path, **merged)

    #
    # Concrete HTTP Methods
    #

    def get(self, key: str, **kwargs) -> "Resource":
        """Get a child resource by name."""
        return self.child(key, **kwargs)

    def list(self, **kwargs) -> list[Resource]:
        """List all child resources by name."""
        return [self.child(key, **kwargs) for key in self.child_names(**kwargs)]

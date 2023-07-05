from pathlib import Path
from upath import UPath

from .entry import Entry
from .manifest import Manifest
from .namespace import Namespace
from .registry import Registry
from .resource import Resource
from .resource_key import ResourceKey


class Volume(ResourceKey):
    """
    Top-level Resource reperesenting a logical unit of storage
    with a single type of filesystem or blob storage
    and its own Registry
    """
    ERR_REQUIRE_REGISTRY = "Volume.get requires registry keyword argument"
    KEY_MH = "multihash"
    KEY_HSH = "hash"
    KEY_TAG = "tag"
    KEY_SELF = "."
    MH_PREFIX = Entry.MH_PREFIX["SHA256"]

    @staticmethod
    def FromURI(uri: str, **kwargs) -> "Volume":
        """Create a Volume from a URI"""
        path = UPath(uri)
        return Volume(path, **kwargs)

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.registry = Registry(path, **self.args)
        self.uri = self.path.as_uri()
        self.keystore: dict[str,dict] = {
            self.KEY_SELF: self.args,
        }

    def is_local(self) -> bool:
        return self.uri.startswith("file://")
    
    def child_names(self, **kwargs) -> list[str]:
        """Return names of each child resource."""
        names = list(self.keystore.keys())
        names.remove(self.KEY_SELF)
        return names
    
#
# Concrete Resource methods
#

    def delete(self, key: str, **kwargs) -> None:
        """Delete the key from this keystore"""
        if key in self.keystore:
            del self.keystore[key]
            return
        raise KeyError(f"Key {key} not found in {self.keystore.keys()}")

    def list(self, **kwargs) -> list["Resource"]:
        """List all child resources."""
        return [self.get(x) for x in self.child_names()]

    def get(self, key: str, **kwargs) -> "Resource":
        """
        Return and keystore manifest for Namespace `key`

        * hash
        * multihash
        * tag [default: latest]
        """
        if key in self.keystore:
            opts = self.keystore[key]
            print(f"Volume.get({key}) opts: {opts.keys()}")
            return opts["Manifest"]

        manifest = self.get_manifest(key, **kwargs)
        args = manifest.args.copy()
        args[self.kPath] = manifest.path
        self.keystore[key] = args
        return manifest
    
#
# get helpers
#

    def get_manifest(self, key: str, **kwargs) -> "Resource":
        """
        Create manifest for Namespace `key` and `kwargs`
        """
        opts: dict[str,str] = kwargs
        hash = self.get_hash(opts)
        if len(hash) > 0:
            return Manifest(self.registry.versions / hash, **self.args)

        tag = opts.get(self.KEY_TAG, Namespace.TAG_DEFAULT)
        name = self.registry.get(key)
        return name.get(tag)        

    def get_hash(self, opts: dict[str,str]) -> str:
        if self.KEY_HSH in opts:
            return opts[self.KEY_HSH]
        if self.KEY_MH in opts:
            mh = opts[self.KEY_MH]
            return mh.strip(self.MH_PREFIX)
        return ""
    



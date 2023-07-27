import logging
from pathlib import Path

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

    @staticmethod
    def FromURI(uri: str, **kwargs) -> "Volume":
        """Create a Volume from a URI"""
        path = Volume.AsPath(uri)
        return Volume(path, **kwargs)

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.registry = Registry(path, **self.args)
        self.uri = str(self.path)
        self.pkgcache: dict[str, dict] = {
            self.KEY_SELF: self.args,
        }

    #
    # Helper Methods
    #

    def is_local(self) -> bool:
        return self.uri.startswith("file://") or "://" not in self.uri

    def _child_names(self, **kwargs) -> list[str]:
        """Return names of each child resource."""
        names = list(self.pkgcache.keys())
        names.remove(self.KEY_SELF)
        return [n.split(":")[0].split("@")[0] for n in names]

    def _man_path(self, hash: str) -> Path:
        """Return path to a manifest"""
        return self.registry.manifests / hash

    def _stage_path(self, hash: str) -> Path:
        """Return path to a manifest"""
        return self.registry.stage / hash

    #
    # List/Delete vs keycache
    #

    def delete(self, key: str, **kwargs) -> None:
        """Delete the key from this keycache"""
        for pkg in self.pkgcache:
            if key in pkg:
                del self.pkgcache[pkg]
                logging.debug(f"Deleted {pkg} from {self.pkgcache.keys()}")
                return
        raise KeyError(f"Key {key} not found in {self.pkgcache.keys()}")

    def list(self, **kwargs) -> list["Resource"]:
        """List all child resources."""
        return [self.get(x) for x in self._child_names()]

    #
    # GET and helpers - return a Manfiest
    #

    def get(self, key: str, **kwargs) -> "Resource":
        """
        Return and keycache manifest for Namespace `key`

        * hash
        * multihash
        * tag [default: latest]
        """
        pkg = self.get_pkg_name(key, **kwargs)
        if pkg in self.pkgcache:
            opts = self.pkgcache[pkg]
            return opts["manifest"]

        manifest = self.get_manifest(key, **kwargs)
        args = manifest.args.copy()
        args[self.KEY_PATH] = manifest.path
        self.pkgcache[pkg] = args
        return manifest

    def read_manifest(self, hash: str) -> Manifest:
        """Read a manifest from the registry"""
        paths = [self._stage_path(hash), self._man_path(hash)]
        for path in paths:
            if path.exists():
                return Manifest(path, **self.args)
        raise FileNotFoundError(f"Manifest not found: {hash}\n\tin: {paths}")

    def get_pkg_name(self, key: str, **kwargs) -> str:
        opts: dict[str, str] = kwargs
        hash = opts.get(self.KEY_HSH, "")
        tag = opts.get(self.KEY_TAG, self.TAG_DEFAULT)
        if hash:
            return f"{key}@{hash}"
        if tag:
            return f"{key}:{tag}"
        return key

    def get_manifest(self, key: str, **kwargs) -> "Resource":
        """
        Get or Create manifest for Namespace `key` and `kwargs`
        """
        opts: dict[str, str] = kwargs
        hash = opts.get(self.KEY_HSH, "")
        tag = opts.get(self.KEY_TAG, self.TAG_DEFAULT)
        if len(hash) == 0:
            name = self.registry.get(key)
            if not isinstance(name, Namespace):
                raise TypeError(f"Volume.get requires a Namespace, not {type(name)}")
            hash = name.hash(tag)
            name.get(tag)
        return self.read_manifest(hash)

    #
    # PUT and helpers - upload a Manfiest or other resource
    #
    # - PUT Entry: copies individual file onto Volume (TBD)
    # - PUT Manifest:
    #   - copies necessary Entries onto Volume (unless --nocopy and non-local)
    #   - calculates hash and creates Namespaced folders
    #   - copies Manifest onto Volume
    #
    #  OPTS:
    #  - namespace_key="PKG/NAME": namespace to register manifest
    #  - force=True: overwrite any existing manifest
    #  - nocopy=True: do not copy any files onto new Volume (just copy manifest)

    def put(self, res: Resource, **kwargs) -> "Resource":
        """Insert/Replace and return a child resource."""
        logging.debug(f"Volume.put: {res} [{kwargs}]]")
        if not isinstance(res, Manifest):
            raise TypeError(f"Volume.put requires a Manifest, not {type(res)}")
        man: Manifest = res
        hash = man.hash_quilt3()
        stage_path = self._stage_path(hash)
        Manifest.WriteToPath(man.head, man.list(), stage_path)  # type: ignore

        new_path = self._man_path(hash)
        if new_path.exists() and not kwargs.get(self.KEY_FRC, False):
            raise FileExistsError(f"Manifest {new_path} already exists")

        ns_name = (
            kwargs.get(self.KEY_NS)
            or man.args.get(self.KEY_NS)
            or f"unknown/{self.Now()}"
        )
        kwargs[self.KEY_NS] = ns_name
        if self.KEY_META in kwargs:
            man.head.user_meta = kwargs[self.KEY_META]
        if self.KEY_MSG in kwargs:
            man.head.message = kwargs[self.KEY_MSG]

        if not kwargs.get(self.KEY_NCP, False):
            man = self.translate_manifest(man, new_path, ns_name)
        self.registry.put(man, **kwargs)
        return man

    def translate_manifest(self, man: ResourceKey, path: Path, name: str) -> Manifest:
        """Translate entries from manifest into this Volume"""
        dest = str(self.path / name)
        entries = [entry.get(dest) for entry in man.list()]
        Manifest.WriteToPath(man.head, entries, path)  # type: ignore
        return Manifest(path, **self.args)

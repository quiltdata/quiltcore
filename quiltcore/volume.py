import logging
from pathlib import Path

from jsonlines import Writer  # type: ignore

from .entry import Entry
from .header import Header
from .manifest import Manifest
from .namespace import Namespace
from .registry import Registry
from .resource import Resource
from .resource_key import ResourceKey
from .yaml.codec import asdict


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

    @staticmethod
    def WriteManifest(head: Header, entries: list[Entry], path: Path) -> None:
        """Write manifest contents to _path_"""
        logging.debug(f"WriteManifest: {path}")
        rows = [entry.to_row3() for entry in entries]  # type: ignore
        with path.open(mode="wb") as fo:
            with Writer(fo) as writer:
                writer.write(head.to_dict())
                for row in rows:
                    writer.write(asdict(row))

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.registry = Registry(path, **self.args)
        self.uri = str(self.path)
        self.keycache: dict[str, dict] = {
            self.KEY_SELF: self.args,
        }

    def is_local(self) -> bool:
        return self.uri.startswith("file://") or "://" not in self.uri

    def _child_names(self, **kwargs) -> list[str]:
        """Return names of each child resource."""
        names = list(self.keycache.keys())
        names.remove(self.KEY_SELF)
        return names

    #
    # List/Delete vs keycache
    #

    def delete(self, key: str, **kwargs) -> None:
        """Delete the key from this keycache"""
        if key in self.keycache:
            del self.keycache[key]
            logging.debug(f"Deleted {key} from {self.keycache.keys()}")
            return
        raise KeyError(f"Key {key} not found in {self.keycache.keys()}")

    def list(self, **kwargs) -> list["Resource"]:
        """List all child resources."""
        return [self.get(x) for x in self._child_names()]

    #
    # GET and helpers - return a Manfiest
    #

    def get(self, key: str, **kwargs) -> "Resource":
        """
        TODO: cache the manifest by hash, not package name
        Return and keycache manifest for Namespace `key`

        * hash
        * multihash
        * tag [default: latest]
        """
        if key in self.keycache:
            opts = self.keycache[key]
            return opts["manifest"]

        manifest = self.get_manifest(key, **kwargs)
        args = manifest.args.copy()
        args[self.KEY_PATH] = manifest.path
        self.keycache[key] = args
        return manifest
    
    def read_manifest(self, hash: str) -> Manifest:
        """Read a manifest from the registry"""
        path = self.registry.manifests / hash
        print(f"read_manifest: {path}")
        return Manifest(path, **self.args)

    def get_manifest(self, key: str, **kwargs) -> "Resource":
        """
        Get or Create manifest for Namespace `key` and `kwargs`
        """
        opts: dict[str, str] = kwargs
        hash = opts.get(self.KEY_HSH, "")
        if len(hash) == 0:
            tag = opts.get(self.KEY_TAG, self.TAG_DEFAULT)
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
    #  - pkg="PKG/NAME": namespace to register manifest
    #  - force=True: overwrite any existing manifest

    # TODO: add --nocopy option
    def put(self, res: Resource, **kwargs) -> "Resource":
        """Insert/Replace and return a child resource."""
        logging.debug(f"Volume.put: {res} [{kwargs}]]")
        if not isinstance(res, Manifest):
            raise TypeError(f"Volume.put requires a Manifest, not {type(res)}")
        man: Manifest = res
        hash = man.hash_quilt3()
        stage_path = self.registry.stage / hash
        self.WriteManifest(man.head, man.list(), stage_path)  # type: ignore

        new_path = self.registry.manifests / hash
        if new_path.exists() and not kwargs.get(self.KEY_FRC, False):
            raise FileExistsError(f"Manifest {new_path} already exists")

        ns_name = (
            kwargs.get(self.KEY_NS)
            or man.args.get(self.KEY_NS)
            or f"unknown/{self.Now()}"
        )
        kwargs[self.KEY_NS] = ns_name

        ns_name = self.write_entries(man, new_path, ns_name)
        man2 = Manifest(new_path, **self.args)
        self.registry.put(man2, **kwargs)
        return man2

    def write_entries(self, man: ResourceKey, path: Path, name: str) -> str:
        """Write entries to a manifest"""
        dest = str(self.path / name)
        entries = [entry.get(dest) for entry in man.list()]
        self.WriteManifest(man.head, entries, path)  # type: ignore
        return name

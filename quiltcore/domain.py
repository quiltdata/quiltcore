import datetime
import logging
import os

from pathlib import Path
from upath import UPath

from .builder import FolderBuilder
from .factory import quilt
from .manifest import Manifest
from .udg.folder import Folder
from .udg.node import Node
from .config.data import Data
from .config.udi import UDI


class Domain(Folder):
    K_MUTABLE = "mutable"
    K_NOCOPY = "no_copy"
    K_NEWOK = "new_ok"
    K_PACKAGE = "package"
    K_REMOTE = "remote"
    TAG_DEFAULT = "latest"
    URI_SPLIT = "://"

    @classmethod
    def FromURI(cls, registry_uri: str) -> "Domain":
        """Return a domain from a URI."""
        scheme, domain = registry_uri.split(cls.URI_SPLIT)
        logging.debug(
            f"Domain.FromURI: {scheme} {cls.URI_SPLIT} {domain} -> {registry_uri}"
        )
        return quilt[scheme][domain]

    @classmethod
    def FromLocalPath(cls, path: Path) -> "Domain":
        """Return a domain from a local path."""
        domain = cls.AsString(path)
        return quilt["file"][domain]

    @classmethod
    def FindStore(cls, next: Node) -> Path:
        """Return the datastore path."""
        parent = next.parent
        if parent is None:
            raise ValueError("No parent for {self}")
        if isinstance(parent, Domain):
            return parent.store
        return cls.FindStore(parent)

    @classmethod
    def GetRemoteManifest(cls, udi: UDI) -> Manifest:
        """Return the manifest for the UDI."""
        domain = cls.FromURI(udi.registry)
        namespace = domain[udi.package]
        assert namespace is not None, f"Namespace not found for: {udi}"
        tag = udi.attrs.get(udi.K_TAG, cls.TAG_DEFAULT)
        manifest = namespace[tag]
        assert manifest is not None, f"Manifest not found for tag[{tag}]: {udi}"
        return manifest

    @staticmethod
    def TimeStamp() -> str:
        """Return a timestamp."""
        return datetime.datetime.now().isoformat()

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        self.store = self.cf.ToPath(self.parent_name(), name)
        assert self.store.exists(), f"Domain store does not exist: {self.store}"
        logging.debug(f"Domain.store: {self.store}")
        self.base = self._setup_dir(self.store, "config")
        self.path = self._setup_dir(self.base, "names")
        self.remotes = self._setup_dir(self.base, "remotes")
        self.is_mutable = kwargs.get(self.K_MUTABLE, True)
        self.data_yaml = Data(self.store)

    #
    # Descriptors
    #

    def get_uri(self) -> str:
        """Return the URI for this domain."""
        return self.store.as_uri()

    def get_udi_string(self, package_name: str = "", ppath: str = "") -> str:
        udi = f"quilt+{self.get_uri()}"
        if package_name:
            udi += f"#package={package_name}"
            if ppath:
                udi += f"&path={ppath}"
        return udi

    def get_udi(self, package_name: str = "", ppath: str = "") -> UDI:
        """Return the UDI for this domain."""
        udi_string = self.get_udi_string(package_name, ppath)
        return UDI.FromUri(udi_string)

    #
    # Pull
    #

    def package_path(self, pkg_name: str) -> Path:
        """Return the path for this package."""
        folder = self.store / pkg_name
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def pull(self, udi: UDI, install_folder: UPath | None = None, **kwargs):
        """Pull resource at the UDI into the domain at path."""
        assert self.is_mutable, "Can not pull into read-only Domain"
        install_dir = install_folder or self.package_path(udi.package)
        install_dir.mkdir(parents=True, exist_ok=True)
        self._track_lineage("pull", udi, install_dir, **kwargs)
        try:
            manifest = self.GetRemoteManifest(udi)
            namespace = self[udi.package]
            assert namespace is not None
            no_copy = kwargs.get(self.K_NOCOPY, False)
            namespace.pull(manifest, install_dir, no_copy=no_copy)
        except ValueError as e:
            msg = f"Domain.pull.failed[{e}]: {udi}"
            if not kwargs.get(self.K_NEWOK, False):
                raise ValueError(msg)
            logging.warning(msg)

        return install_dir

    def _status(self, attrs: dict, **kwargs) -> dict:
        """Return the status dictionary for this UDI event."""
        status = {
            "timestamp": self.TimeStamp(),
            "user": os.environ.get("USER", "unknown"),
            **attrs,
            **kwargs,
        }
        return status

    def _track_lineage(self, action, udi: UDI, path: Path, **kwargs):
        """Store the UDI in the domain."""
        opts = self._status(udi.attrs, **kwargs)
        logging.debug(f"Domain._track_lineage: {action} {udi} {path} {opts}")
        uri = udi.uri
        assert uri and isinstance(uri, str)
        folder = str(path)
        # TODO: store hash and other udi attributes
        self.data_yaml.set(folder, uri, action, opts)
        self.data_yaml.save()
        return folder

    #
    # Push
    #

    def _message(self, attrs) -> str:
        """Return the message for this push."""
        status = self._status(attrs)
        return str(status)

    def folder2udi(self, path: Path) -> UDI | None:
        """Return the URI for this path."""
        uri = self.data_yaml.folder2uri(str(path))
        return UDI.FromUri(uri)

    def get_pkg_name(self, path: Path, **kwargs) -> str:
        pkg = kwargs.get(self.K_PACKAGE, None)
        if not pkg:
            udi = self.folder2udi(path)
            assert udi is not None, f"UDI not found for: {path}"
            pkg = udi.package
        return pkg

    def get_remote_udi(self, path: Path, **kwargs) -> UDI:
        """Return the UDI for this path."""
        udi = kwargs.get(self.K_REMOTE, None)
        if not udi:
            udi = self.folder2udi(path)
            assert udi is not None, f"UDI not found for: {path}"
        return udi

    def build(self, path: Path, **kwargs) -> FolderBuilder:
        """Writes manifest for folder into `package` namespace."""
        builder = FolderBuilder(path, self)
        assert builder.path == path
        msg = kwargs.get(self.K_MESSAGE, self._message(kwargs))
        meta = kwargs.get(self.K_META, {})
        builder.commit(msg, meta)
        return builder

    def commit(self, path: Path, **kwargs):
        """Writes manifest for folder into `package` namespace."""
        builder = self.build(path, **kwargs)

        pkg = self.get_pkg_name(path, **kwargs)
        udi = self.get_udi(pkg)
        self._track_lineage("commit", udi, path, **kwargs)
        namespace = self[pkg]
        assert namespace is not None, f"Namespace not found for: {pkg}"
        return namespace.put(builder.list4(), builder.q3hash(), **kwargs)

    def push(self, folder: Path, **kwargs):
        """
        `push` is actually syntactic sugar for:

        1. Find the local UDI (manifest) associated with the local folder
        2. Find the explicit or implicit remote UDI for this folder
        3. Create or find the remote Domain for that UDI
        4. Tell the remote Domain to pull data (manifest and files)
           from the local Domain
        """
        local_udi = self.folder2udi(folder)
        assert local_udi is not None, f"UDI not found for: {folder}"
        remote_udi = self.get_remote_udi(folder, **kwargs)
        self._track_lineage("push", remote_udi, folder, **kwargs)
        assert remote_udi is not None, f"UDI not found for: {folder}"
        remote = self.FromURI(remote_udi.registry)
        remote.pull(local_udi, **kwargs)
        return remote

import datetime
import logging
import os

from pathlib import Path
from upath import UPath

from .builder2 import FolderBuilder
from .factory import quilt
from .manifest2 import Manifest2
from .udg.folder import Folder
from .udg.node import Node
from .udg.types import List4
from .yaml.data import Data
from .yaml.udi import UDI


class Domain(Folder):
    K_MUTABLE = "mutable"
    K_NOCOPY = "no_copy"
    K_NEWOK = "new_ok"
    K_PACKAGE = "package"
    URI_SPLIT = "://"

    @classmethod
    def FromURI(cls, uri):
        """Return a domain from a URI."""
        scheme, path = uri.split(cls.URI_SPLIT)
        logging.debug(f"Domain.FromURI: {scheme} {cls.URI_SPLIT} {path} -> {uri}")
        return quilt[scheme][path]

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
    def GetRemoteManifest(cls, udi: UDI) -> Manifest2:
        """Return the manifest for the UDI."""
        domain = cls.FromURI(udi.registry)
        namespace = domain.get(udi.package)
        tag = udi.attrs.get(udi.K_TAG, namespace.TAG_DEFAULT)
        manifest = namespace.get(tag)
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
        self.is_mutable = kwargs.get(self.K_MUTABLE, False)
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
        assert install_dir.is_dir(), f"install_dir not a directory: {install_dir}"
        self._track_lineage("pull", udi, install_dir, **kwargs)
        try:
            remote = self.GetRemoteManifest(udi)
            namespace = self.get(udi.package)
            assert namespace is not None
            no_copy = kwargs.get(self.K_NOCOPY, False)
            namespace.pull(remote, install_dir, no_copy=no_copy)
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

    def folder2udi(self, path: Path) -> UDI:
        """Return the URI for this path."""
        uri = self.data_yaml.folder2uri(str(path))
        assert uri, f"URI not found for path: {path}"
        return UDI.FromUri(uri)

    def to_list4(self, path: Path, glob=Folder.DEFAULT_GLOB) -> List4:
        """Generate to_dict4 for each file in path matching glob."""
        return [self.dict4_from_path(file) for file in path.rglob(glob)]

    def commit(self, path: Path, **kwargs):
        """Writes manifest for folder into `package` namespace."""
        builder = FolderBuilder(path, self)
        msg = kwargs.get(self.K_MESSAGE, self._message(kwargs))
        builder.commit(msg, {})

        pkg = kwargs.get(self.K_PACKAGE, None)
        if not pkg:
            udi = self.folder2udi(path)
            assert udi is not None, f"UDI not found for: {path}"
            pkg = udi.package

        namespace = self.get(pkg)
        assert namespace is not None, f"Namespace not found for: {pkg}"
        return builder.save_to(namespace, **kwargs)

    def push(self, path: Path, **kwargs):
        """
        `push` is actually syntactic sugar for:

        1. Find the Domain associated with the local folder
        2. Find the remote UDI associated with that folder
        3. Create or find the remote Domain for that UDI
        4. Tell the remote Domain to pull data (manifest and files)
           from the local Domain
        """
        remote_udi = self.folder2udi(path)
        remote = self.FromURI(remote_udi.registry)
        local_udi = self.get_udi(remote_udi.package)
        print(f"remote.pull({local_udi}, **kwargs)")
        return remote

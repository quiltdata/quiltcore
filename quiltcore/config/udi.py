# Create Universal Data Identifier from UnURI attributes
import logging

from un_yaml import UnUri  # type: ignore

from yaml.representer import SafeRepresenter


def default_representer(dumper, data):
    # Alternatively, use repr() instead str():
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))


SafeRepresenter.add_representer(None, default_representer)  # type: ignore


class UDI:
    """
    Create and manage Quilt Resources from UnURI attrs.
    """

    PREFIX = "quilt+"
    K_BKT = UnUri.K_HOST
    K_DIR = "dir"
    K_FILE = "file"
    K_FORCE = "force"
    K_FAIL = "fallible"
    K_LOCAL = "localhost"
    K_REG = "registry"

    # Fragments
    K_PKG = "package"
    K_PTH = "path"
    K_PRP = "property"
    K_CAT = "catalog"
    FRAG_KEYS = [K_PRP, K_PTH, K_PKG]

    # Decomposed Package Name
    SEP_HASH = "@"
    SEP_TAG = ":"
    SEP_PKG = "/"
    K_HASH = "_hash"
    K_TAG = "_tag"
    K_VER = "_version"
    K_PATHS = "_uri_paths"
    SEP = {K_HASH: SEP_HASH, K_TAG: SEP_TAG, K_PKG: SEP_PKG}
    K_PKG_NAME = "_package_name"
    K_PKG_PRE = "_package_prefix"
    K_PKG_SUF = "_package_suffix"

    @classmethod
    def FromUnUri(cls, un: UnUri) -> "UDI":
        return cls(un.attrs)

    @classmethod
    def FromUri(cls, uri: str) -> "UDI":
        un = UnUri(uri)
        return cls.FromUnUri(un)

    @staticmethod
    def AttrsFromUri(uri: str) -> dict:
        un = UnUri(uri)
        return un.attrs

    def __init__(self, attrs: dict):
        """
        Set local variables and additional attributes.

        >>> reg = "s3://quilt-example"
        >>> pkg = "examples/wellplates"
        >>> pkg_full = f"{pkg}:latest"
        >>> path = "README.md"
        >>> uri = f"{UDI.PREFIX}{reg}#package={pkg_full}&path={path}"
        >>> attrs = UnUri(uri).attrs
        >>> quilt = UDI(attrs)
        >>> quilt.uri == uri
        True
        >>> quilt.registry == reg
        True
        >>> quilt.package == pkg
        True
        >>> quilt.attrs[UDI.K_PKG] == pkg_full
        True
        >>> quilt.attrs[UDI.K_PKG_NAME]
        'examples/wellplates'
        >>> quilt.attrs[UDI.K_PKG_PRE]
        'examples'
        >>> quilt.attrs[UDI.K_PKG_SUF]
        'wellplates'
        >>> quilt.attrs[UDI.K_PTH] == path
        True
        """
        self.attrs = attrs
        self.uri = attrs.get(UnUri.K_URI)
        self.package = self.parse_package()
        self.registry = self.parse_registry()

    def __repr__(self):
        return f"UDI({self.uri})"

    def __str__(self):
        return self.uri

    def __eq__(self, other: object):
        if not isinstance(other, UDI):
            return NotImplemented
        return self.registry == other.registry and self.package == other.package

    def parse_registry(self) -> str:
        prot = self.attrs.get(UnUri.K_PROT, self.K_FILE)
        host = self.attrs.get(UnUri.K_HOST, self.K_LOCAL)
        path = ""
        logging.debug(f"parse_registry: {prot} {host} [{path}]")

        if self.K_PATHS in self.attrs and self.attrs[self.K_PATHS][0]:
            path = "/" + "/".join(self.attrs[self.K_PATHS])
        if host == self.K_LOCAL:
            host = ""

        return f"{prot}://{host}{path}"

    def full_package(self) -> str | bool:
        return self.attrs.get(UDI.K_PKG) or False

    def split_package(self, key) -> str | bool:
        sep = UDI.SEP[key]
        pkg = self.full_package()
        if isinstance(pkg, str) and sep in pkg:
            s = pkg.split(sep)
            self.attrs[key] = s[1]
            return s[0]
        return False

    def parse_package(self) -> str:
        package = (
            self.split_package(UDI.K_HASH)
            or self.split_package(UDI.K_TAG)
            or self.full_package()
        )
        sep = UDI.SEP[UDI.K_PKG]
        if not isinstance(package, str) or sep not in package:
            return ""

        split = package.split(sep)
        self.attrs[UDI.K_PKG_NAME] = package
        self.attrs[UDI.K_PKG_PRE] = split[0]
        self.attrs[UDI.K_PKG_SUF] = split[1]
        return package

    def has_package(self) -> bool:
        return UDI.SEP[UDI.K_PKG] in self.package if self.package else False

import logging
import pyarrow as pa  # type: ignore
import pyarrow.compute as pc  # type: ignore

from json import JSONEncoder
from datetime import datetime
from urllib.parse import quote, unquote

from multiformats import multihash
from typing_extensions import Any

from ..config.config import Config
from .types import Dict3, Dict4, Hash3, Multihash, Types


class Codec(Config, Types):
    """
    Manage manifest encode/decode

    Design Principles:

    1. Keep the native arrow table as it is
    2. decode quilt3 manifest format into quilt3 schema
    3. encode quilt4 schema into quilt3 manifest format

    Column Mappings

    quilt3        | quiltcore
    -------------------------
    logical_key   | name
    physical_keys | place
    size          | size
    hash          | multihash
    meta          | info
    meta.user_meta| meta
    """

    ENCODE = JSONEncoder(sort_keys=True, separators=(",", ":"), default=str).encode

    @classmethod
    def EncodeDict(cls, source: dict) -> bytes:
        return cls.ENCODE(source).encode("utf-8")

    def __init__(self, scheme="quilt3") -> None:
        super().__init__()
        self.scheme = scheme
        self.coding = self.config()
        self.name_col = None
        self.this_opts: dict = {}

    #
    # Helper Methods
    #

    def check(self, key: str) -> bool:
        return True if self.this_opts.get(key, False) else False

    def check_opts(self, opts: dict) -> dict:
        self.this_opts = opts if len(opts) > 0 else self.this_opts
        return self.this_opts

    def config(self, value="schema") -> dict:
        """Return a dict of values to encode, and their mappings."""
        return self.get_dict(f"{self.scheme}/{value}")

    #
    # Table Operations
    #

    def decode_list(self, item, opts={}) -> list[str]:
        """decode and convert to a list"""
        result = self.decode_item(item, opts)
        if isinstance(result, list):
            return result
        if hasattr(result, "to_pylist"):
            return result.to_pylist()  # type: ignore
        raise TypeError(f"Expected list, got {type(result)}: {result}")

    def decode_names(self, body: pa.Table) -> pa.Table:
        """Return table with decoded names (also cached)."""
        source = self.config(self.K_MAP)[self.K_NAM]
        opts = self.coding.get(source, {})
        input = body.column(source)
        new_col = [self.decode_list(input, opts)]
        with_names = body.append_column(self.K_NAM, new_col)
        self.name_col = with_names.column(self.K_NAM)
        return with_names

    def index_name(self, name: str) -> int:
        """Return the row index for a column name."""
        return pc.index(self.name_col, name)

    #
    # Hash Methods
    #

    def hash_config(self, key: str):
        """return multihash configuration dictionary for this key"""
        mh_config = self.get_dict("multihash")
        logging.debug(f"hash_config[{key}]: {mh_config}")
        return mh_config[key]

    def digester(self, hash_type=None):
        """return method for calculating digests"""
        ht = hash_type or self.config("hash_type")
        digest_type = self.hash_config(self.MH_DIG)[ht]
        return multihash.get(digest_type)

    def digest(self, bstring: bytes) -> Multihash:
        """return multihash digest as hex"""
        digester = self.digester()
        return digester.digest(bstring).hex()

    def decode_q3hash(self, q3hash: str) -> Multihash:
        hash_type = self.config("hash_type")
        prefix = self.hash_config(self.MH_PRE)[hash_type]
        return prefix + q3hash

    def decode_hash(self, hash_data: Hash3) -> Multihash:
        """convert quilt3 hash_struct into multihash string"""
        hash_type = hash_data.type
        prefix = self.hash_config(self.MH_PRE)[hash_type]
        return prefix + hash_data.value

    def encode_hash(self, mhash: Multihash) -> dict:
        """Encode multihash string into a quilt3 hash_struct."""
        prefixes = self.hash_config(self.MH_PRE)
        prefix = mhash[0:4]
        if prefix not in prefixes.values():
            raise ValueError(f"Prefix[{prefix}] not in [{prefixes}]: {mhash}")
        keys = [key for key, value in prefixes.items() if value == prefix]
        hash3 = Hash3(type=keys[0], value=mhash.removeprefix(prefix))
        return hash3.to_dict()

    #
    # Encoder Methods
    #

    def encode_hashable(self, obj: Dict4) -> dict:
        if not obj.multihash or not obj.size:
            raise ValueError(f"Missing hash or size: {obj}")
        hashable = {
            self.config("map")["name"]: obj.name,
            self.K_HASH: self.encode_hash(obj.multihash),
            self.K_SIZE: obj.size,
        }
        hashable[self.K_META] = obj.info  # or {}
        return hashable

    def encode_dict4(self, obj: Dict4) -> Dict3:
        """Encode Dict4 attributes into Dict3 for a manifest row."""
        row: dict[str, Any] = {}
        for key3, opts in self.coding.items():
            self.check_opts(opts)
            key4 = opts[self.K_NAM]
            logging.debug(f"encode[{key3}]: {key4} -> {opts}")
            if key4 == self.K_PLC:
                key4 = "path"
            if hasattr(obj, key4):
                value = getattr(obj, key4)
                row[key3] = self.encode_value(value, opts)
        logging.debug(f"encode: {obj} -> {row}")
        d3 = Dict3(**row)
        return d3

    def encode_dates(self, values: dict) -> dict:
        """format dates for quilt3 metadata"""
        for key, value in values.items():
            if hasattr(value, "strftime"):
                values[key] = self.encode_date(value)
            elif isinstance(value, dict):
                values[key] = self.encode_dates(value)
        return values

    def encode_date(self, value, opts={}) -> str:
        """format date for quilt3 metadata"""
        if not hasattr(value, "strftime"):
            raise ValueError(f"Value {value} not formattable")
        fmt = self.get_str("quilt3/format/datetime", "%Y-%m-%d")
        return value.strftime(fmt)

    def encode_value(self, value, opts={}):
        """encode value based on this_opt"""
        self.check_opts(opts)
        if self.check(self.T_HSH):
            if not isinstance(value, str):
                raise TypeError(f"Expected str, got {type(value)}: {value}")
            value = self.encode_hash(value)

        if isinstance(value, datetime):
            value = self.encode_date(value)
        if self.check(self.T_QTD):
            value = self.AsString(value)
            value = quote(value, safe=self.UNQUOTED)

        if self.check(self.T_LST):
            value = [value]

        return value

    #
    # Decoder Methods
    #

    def decode_dict3(self, row: Dict3) -> Dict4:
        """Return a dict of decoded values."""
        decoded: dict[str, Any] = {self.K_META: {}}
        for key, value in row.to_dict().items():
            opts = self.coding.get(key, {})
            name = opts.get(self.K_NAM, key)
            decoded[name] = self.decode_value(value, opts)
        if decoded["info"] and self.K_USER_META in decoded["info"]:
            decoded["meta"] = decoded["info"][self.K_USER_META]
            del decoded["info"][self.K_USER_META]
        return Dict4(**decoded)

    def decode_item(self, item, opts={}):
        """decode scalar or compound item"""
        item_type = type(item)
        if isinstance(item, str):
            return self.decode_value(item, opts)
        if isinstance(item, list):
            return [self.decode_item(item[0], opts)]
        if isinstance(item, pa.ChunkedArray):
            decoded = [self.decode_item(chunk, opts) for chunk in item.chunks]
            return pa.chunked_array(decoded)
        if issubclass(item_type, pa.Array):
            return [self.decode_item(chunk, opts) for chunk in item.to_pylist()]
        raise TypeError(f"Unexpected type: {item_type}")

    def decode_value(self, value, opts={}):
        """Decode a single value from quilt3 manifest into quiltcore schema."""
        self.check_opts(opts)
        if self.check(self.T_LST):
            if isinstance(value, list):
                value = value[0]
            else:
                raise TypeError(f"Expected list, got {type(value)}: {value}")

        if self.check(self.T_QTD):
            value = self.AsString(value)
            value = unquote(value)

        if self.check(self.T_HSH):
            if not isinstance(value, dict):
                raise TypeError(f"Expected dict, got {type(value)}: {value}")
            value3 = Hash3(**value)
            value = self.decode_hash(value3)

        return value

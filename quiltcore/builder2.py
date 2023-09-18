import logging

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .change import Change, ChangeOp, Dict4
from .manifest2 import Manifest2
from .udg.keyed import Keyed


class Builder2(Keyed):
    """
    Create with a Manifest2, and optional `relax` flag.
    Update using:
    - `build[key] = Path` 
    - `build[key].meta = dict`
    - `del build[key]`
    Automatically infers Add (new), Replace (exist), or Move (relax)
    """

    def __init__(self, manifest: Manifest2|None = None, relax: bool =False, **kwargs):
        super().__init__(**kwargs)
        self.message = self.head_hash = None
        self.manifest = self._setup_manifest(manifest) # TODO: run lazily

    def _setup_manifest(self, manifest) -> Manifest2|None:
        # FIXME: how do I know if a Path has been modified
        if manifest is None:
            return None
        assert isinstance(manifest, Manifest2)
        self.message = manifest.head.message
        self.head_hash = manifest.head.q3hash()
        for key, dict4 in manifest.items():
            if not key in self._cache:
                self._change(ChangeOp.KEEP, key, dict4.path, dict4)
        return manifest
        
    def _change(self,
                op: ChangeOp,
                key: str,
                path: Path|None = None,
                dict4: Dict4|None = None
        ):
        if path is not None:
            assert path.exists(), "If Path is provided, must already exist"
        change = Change(op, path, dict4)
        if key in self._cache and op == ChangeOp.ADD and self._cache[key].op != ChangeOp.REMOVE:
            raise KeyError(f"Key {key} already exists: {change}")
        self._cache[key] = change
        return self

    def __setitem__(self, key, path: Path):
        if key not in self._cache:
            self._change(ChangeOp.ADD, key, path)
        else:
            change = self._cache[key]
            self._change(ChangeOp.REPLACE, key, path, change.dict4)
        
    def __delitem__(self, key):
        assert key in self.manifest
        self._change(ChangeOp.REMOVE, key)

    def append(self, path: Path):
        assert path.exists()
        self._change(ChangeOp.ADD, path.name, path)
        return self
    
    def replace(self, path: Path):
        assert path.exists()
        self._change(ChangeOp.REPLACE, path.name, path)
        return self
    
    #
    # Results
    #

    def commit(self, message: str, name: str) -> Manifest2:
        """
        Collect Entries
        """
        assert self.manifest is not None
        return self.manifest

    def same_scheme(self, path, install_folder) -> bool:
        return False

    def relax(self, man_folder: Path, install_folder: Path, schemeCopy: bool = False):
        """Clone the manifest, relaxing its keys into the install_folder."""
        assert self.message is not None
        assert self.manifest is not None
        assert man_folder.exists()
        install_folder.mkdir(parents=True, exist_ok=True)

        for key, dict4 in self.manifest.items():
            if schemeCopy or not self.same_scheme(dict4.path, install_folder):
                new_path = install_folder / key
                new_path.write_bytes(dict4.to_bytes())
                self._change(ChangeOp.MOVE, key, new_path, dict4)
        return self.commit(self.message, self.manifest.name)
    
    def to_dict4s(self) -> list[Dict4]:
            # reduce to a list of Dict4s          
            result = []
            for change in self.values():
                result += change.to_dict4s(self)
            return result
    


    def _hash_manifest(self) -> str:
        hashable = b""
        if hasattr(self, "head"):
            self.head.hashable()  # type: ignore
        for dict4 in self.items():
            hashable += dict4.hashable()  # type: ignore
        assert self.manifest is not None
        return self.manifest.digest_bytes(hashable)

    

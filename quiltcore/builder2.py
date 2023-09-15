import logging

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .change import Change, ChangeOp
from .entry2 import Entry2
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
        self.manifest = self._setup_manifest(manifest)

    def _setup_manifest(self, manifest) -> Manifest2|None:
        # TODO: run lazily before commit, only for empty keys
        if manifest is None:
            return None
        assert isinstance(manifest, Manifest2)
        self.message = manifest.head.message
        self.head_hash = manifest.head.q3hash()
        for key, entry in manifest.items():
            self._change(ChangeOp.KEEP, key, entry.path, entry)
        return manifest
        
    def _change(self,
                op: ChangeOp,
                key: str,
                path: Path|None = None,
                entry: Entry2|None = None
        ):
        if path is not None:
            assert path.exists(), "If Path is provided, must already exist"
        self._cache[key] = Change(op, path, entry)
        return self

    def __setitem__(self, key, path: Path):
        if key not in self._cache:
            self._change(ChangeOp.ADD, key, path)
        else:
            change = self._cache[key]
            self._change(ChangeOp.REPLACE, key, path, change.entry)
        
    def __delitem__(self, key):
        assert key in self.manifest
        self._change(ChangeOp.REMOVE, key)
    
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
        assert self.manifest is not None
        assert man_folder.exists()
        install_folder.mkdir(parents=True, exist_ok=True)

        for key, entry in self.manifest.items():
            if schemeCopy or not self.same_scheme(entry.path, install_folder):
                new_path = install_folder / key
                new_path.write_bytes(entry.to_bytes())
                self._change(ChangeOp.MOVE, key, new_path, entry)

        return self.commit(self.manifest.head.message, self.manifest.name)
    
    def _entries(self) -> list[Entry2]:
        return [change.entry for change in self.values() if change.entry is not None]


    def _hash_manifest(self) -> str:
        hashable = b""
        if hasattr(self, "head"):
            self.head.hashable()  # type: ignore
        for entry in self.items():
            hashable += entry.hashable()  # type: ignore
        assert self.manifest is not None
        return self.manifest.digest_bytes(hashable)

    

from pathlib import Path

from .resource import CoreResource


class CoreBlob(CoreResource):

    """Storage for dereferenced Names"""

    def __init__(self, value: Path, parent: CoreResource):
        super().__init__(value)

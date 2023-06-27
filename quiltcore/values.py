from pathlib import Path

from .resource import CoreResource


class CoreValues(CoreResource):

    """Storage for dereferenced Names"""

    def __init__(self, values: Path, parent: CoreResource):
        super().__init__(values)

"""Fossil Image"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True)
class Image:
    """Raw Disk Image"""

    path: Path

    @property
    def size(self) -> int:
        """Image size"""
        return self.path.stat().st_size

    @property
    def name(self) -> str:
        """Image name"""
        return self.path.name

"""Fossil Partition"""

from collections.abc import Iterator
from dataclasses import dataclass

from generaptor.concept import OperatingSystem

from .image import Image

OS_PART_TYPE_MAPPING = {
    OperatingSystem.LINUX: 'Linux (0x83)',
    OperatingSystem.WINDOWS: 'NTFS / exFAT (0x07)',
}


@dataclass(kw_only=True)
class Partition:
    """Partition"""

    size: int
    offset: int
    description: str
    image: Image


PartitionIterator = Iterator[Partition]

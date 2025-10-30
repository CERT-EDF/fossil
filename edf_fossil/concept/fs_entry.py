"""Fossil File System Entry"""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import PurePosixPath

from .partition import Partition


@dataclass(kw_only=True)
class FSEntry:
    """File System Entry"""

    path: PurePosixPath
    inode: str
    deleted: bool
    directory: bool
    partition: Partition


FSEntryIterator = Iterator[FSEntry]

"""Command module"""

from .collect import setup_cmd as setup_collect
from .digest import setup_cmd as setup_digest
from .fs_entries import setup_cmd as setup_fs_entries
from .partitions import setup_cmd as setup_partitions

_COMMANDS = (
    setup_collect,
    setup_digest,
    setup_fs_entries,
    setup_partitions,
)


def setup_commands(cmd):
    """Setup commands"""
    for setup_cmd in _COMMANDS:
        setup_cmd(cmd)

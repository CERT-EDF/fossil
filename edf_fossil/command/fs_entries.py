"""fs_entries command"""

from csv import writer
from sys import stdout

from generaptor.concept import OperatingSystem

from ..concept import OS_PART_TYPE_MAPPING, Image
from ..helper.logging import get_logger
from ..helper.tsk import TheSleuthKit

_LOGGER = get_logger('command.fs_entries')


def _cmd_fs_entries(args):
    tsk = TheSleuthKit(
        cache=args.cache, image_is_partition=args.image_is_partition
    )
    image = Image(path=args.image)
    csv_w = writer(stdout)
    csv_w.writerow(['image', 'partition.offset', 'inode', 'path'])
    opsystem = OperatingSystem(args.opsystem)
    part_type = OS_PART_TYPE_MAPPING[opsystem]
    for partition in tsk.partitions(image):
        _LOGGER.info("processing %s", partition)
        if not args.image_is_partition and partition.description != part_type:
            continue
        for fs_entry in tsk.fs_entries(partition):
            if fs_entry.deleted and not args.deleted:
                continue
            if fs_entry.directory and not args.directories:
                continue
            csv_w.writerow(
                [
                    image.name,
                    str(partition.offset),
                    str(fs_entry.inode),
                    str(fs_entry.path),
                ]
            )


def setup_cmd(cmd):
    """Setup fs_entries command"""
    fs_entries = cmd.add_parser('fs_entries')
    fs_entries.add_argument(
        '--deleted',
        action='store_true',
        help="include deleted file",
    )
    fs_entries.add_argument(
        '--directories',
        action='store_true',
        help="include directories",
    )
    fs_entries.set_defaults(func=_cmd_fs_entries)

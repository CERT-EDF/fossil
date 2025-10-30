"""digest command"""

from csv import QUOTE_MINIMAL, writer
from datetime import datetime
from sys import stdout

from generaptor.concept import OperatingSystem

from ..concept import OS_PART_TYPE_MAPPING, Image
from ..helper.logging import get_logger
from ..helper.tsk import TheSleuthKit, fs_entry_data_digests

_LOGGER = get_logger('command.digest')


def _cmd_digest(args):
    tsk = TheSleuthKit(
        cache=args.cache, image_is_partition=args.image_is_partition
    )
    image = Image(path=args.image)
    csv_w = writer(stdout, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
    csv_w.writerow(
        [
            'image',
            'partition.offset',
            'md5',
            'sha1',
            'sha256',
            'sha512',
            'inode',
            'path',
        ]
    )
    opsystem = OperatingSystem(args.opsystem)
    part_type = OS_PART_TYPE_MAPPING[opsystem]
    for partition in tsk.partitions(image):
        _LOGGER.info("processing %s", partition)
        if not args.image_is_partition and partition.description != part_type:
            continue
        _LOGGER.info("hashing records data from %s", partition)
        count = 0
        start = datetime.now()
        for fs_entry in tsk.fs_entries(partition):
            if fs_entry.deleted and not args.deleted:
                continue
            if fs_entry.directory:
                continue
            digests = fs_entry_data_digests(tsk, fs_entry)
            if not digests:
                _LOGGER.warning(
                    "digests computation failed: %s", fs_entry.path
                )
                continue
            count += 1
            csv_w.writerow(
                [
                    image.name,
                    str(partition.offset),
                    digests['md5'],
                    digests['sha1'],
                    digests['sha256'],
                    digests['sha512'],
                    str(fs_entry.inode),
                    str(fs_entry.path),
                ]
            )
        duration = datetime.now() - start
        _LOGGER.info("done hashing %d records, took %s", count, duration)


def setup_cmd(cmd):
    """Setup digest command"""
    digest = cmd.add_parser('digest')
    digest.add_argument(
        '--deleted',
        action='store_true',
        help="include deleted file (prone to extraction errors)",
    )
    digest.set_defaults(func=_cmd_digest)

"""partitions command"""

from csv import QUOTE_MINIMAL, writer
from sys import stdout

from generaptor.concept import OperatingSystem

from ..concept import OS_PART_TYPE_MAPPING, Image
from ..helper.logging import get_logger
from ..helper.tsk import TheSleuthKit

_LOGGER = get_logger('command.partitions')


def _cmd_partitions(args):
    tsk = TheSleuthKit(
        cache=args.cache, image_is_partition=args.image_is_partition
    )
    image = Image(path=args.image)
    csv_w = writer(stdout, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
    csv_w.writerow(['image', 'partition.offset'])
    opsystem = OperatingSystem(args.opsystem)
    part_type = OS_PART_TYPE_MAPPING[opsystem]
    for partition in tsk.partitions(image):
        _LOGGER.info("processing %s", partition)
        if not args.image_is_partition and partition.description != part_type:
            continue
        csv_w.writerow([image.name, str(partition.offset)])


def setup_cmd(cmd):
    """Setup partitions command"""
    partitions = cmd.add_parser('partitions')
    partitions.set_defaults(func=_cmd_partitions)

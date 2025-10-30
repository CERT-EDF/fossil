"""collect command"""

from pathlib import Path, PurePosixPath, PureWindowsPath

from generaptor.concept import (
    Cache,
    Config,
    OperatingSystem,
    RuleSet,
    get_profile_mapping,
    get_ruleset_from_targets,
)

from ..concept import OS_PART_TYPE_MAPPING, Image, Partition
from ..helper.logging import get_logger
from ..helper.regexp import Pattern, glob2re
from ..helper.tsk import TheSleuthKit, fs_entry_data_extract

_LOGGER = get_logger('command.collect')


def _select_rules(
    custom: bool,
    profile: str,
    opsystem: OperatingSystem,
) -> RuleSet | None:
    cache = Cache()
    config = Config()
    profile_mapping = get_profile_mapping(cache, config, opsystem)
    profile = profile_mapping.get(profile)
    if not custom and not profile:
        _LOGGER.error("profile not found: %s", profile)
        return None
    return get_ruleset_from_targets(
        cache, config, profile.targets if profile else [], opsystem
    )


def _patterns_from_rule_set(
    rule_set: RuleSet,
    opsystem: OperatingSystem,
) -> list[Pattern]:
    case_insensitive = opsystem == OperatingSystem.WINDOWS
    path_cls = PureWindowsPath if case_insensitive else PurePosixPath
    return [
        glob2re(path_cls(rule.glob), case_insensitive)
        for rule in rule_set.rules.values()
    ]


def _extract_from_partition(
    tsk: TheSleuthKit,
    partition: Partition,
    patterns: list[Pattern],
    output_directory: Path,
):
    for fs_entry in tsk.fs_entries(partition):
        if fs_entry.directory:
            continue
        if any(pattern.fullmatch(str(fs_entry.path)) for pattern in patterns):
            size = fs_entry_data_extract(tsk, fs_entry, output_directory)
            if size < 0:
                _LOGGER.warning("extraction failed for %s", fs_entry.path)
                continue
            _LOGGER.info("extracted %s (%d bytes)", fs_entry.path, size)


def _cmd_collect(args):
    tsk = TheSleuthKit(
        cache=args.cache, image_is_partition=args.image_is_partition
    )
    image = Image(path=args.image)
    opsystem = OperatingSystem(args.opsystem)
    rule_set = _select_rules(
        args.custom,
        args.profile,
        opsystem,
    )
    if not rule_set:
        return
    patterns = _patterns_from_rule_set(rule_set, opsystem)
    part_type = OS_PART_TYPE_MAPPING[opsystem]
    for partition in tsk.partitions(image):
        _LOGGER.info("processing %s", partition)
        if not args.image_is_partition and partition.description != part_type:
            continue
        _extract_from_partition(
            tsk, partition, patterns, args.output_directory
        )


def setup_cmd(cmd):
    """Setup collect command"""
    collect = cmd.add_parser('collect')
    collect.add_argument(
        '--custom',
        '-c',
        action='store_true',
        help="enable collector targets customization (interactive)",
    )
    collect.add_argument(
        '--profile',
        default='default',
        help="use given profile (non interactive)",
    )
    collect.add_argument(
        '--output-directory',
        '-o',
        type=Path,
        default=Path('extracted'),
        help="set output directory",
    )
    collect.set_defaults(func=_cmd_collect)

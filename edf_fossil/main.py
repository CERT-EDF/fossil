"""Fossil Application"""

from argparse import ArgumentParser
from pathlib import Path

from generaptor.concept import OperatingSystem

from .__version__ import version
from .command import setup_commands
from .helper.logging import get_logger

_LOGGER = get_logger('main')


def _parse_args():
    parser = ArgumentParser(description="dissect raw disk images")
    parser.add_argument(
        '--cache', type=Path, default=Path('.fossil'), help="cache directory"
    )
    parser.add_argument(
        '--image-is-partition',
        action='store_true',
        help="given image is a raw partition",
    )
    parser.add_argument(
        'opsystem',
        choices=[item.value for item in OperatingSystem],
        help="operating system",
    )
    parser.add_argument('image', type=Path, help="image to dissect")
    cmd = parser.add_subparsers(dest='cmd')
    cmd.required = True
    setup_commands(cmd)
    return parser.parse_args()


def app():
    """Application entry point"""
    _LOGGER.info("Fossil v%s", version)
    args = _parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print()
        _LOGGER.warning("operation canceled by user.")


if __name__ == '__main__':
    app()

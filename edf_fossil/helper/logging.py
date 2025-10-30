"""Fossil Logging Helper"""

from logging import basicConfig, getLogger
from os import getenv

from rich.console import Console
from rich.logging import RichHandler

DEBUG = int(getenv('FOSSIL_DEBUG', '0'))

"""Setup logging facility"""
basicConfig(
    level='DEBUG' if DEBUG else 'INFO',
    format="(%(name)s): %(message)s",
    datefmt="[%Y-%m-%dT%H:%M:%S]",
    handlers=[RichHandler(console=Console(stderr=True), show_path=False)],
    force=True,
)


def get_logger(name: str, root: str = 'fossil'):
    """Retrieve logger for given name"""
    return getLogger('.'.join([root, name]))

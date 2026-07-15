"""The Sleuth Kit interface"""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from subprocess import DEVNULL, PIPE, CalledProcessError, Popen, run

from ..concept.fs_entry import FSEntry, FSEntryIterator
from ..concept.image import Image
from ..concept.partition import Partition, PartitionIterator
from .hashing import Digests
from .logging import get_logger
from .regexp import MatchIterator, Pattern, regexp

_LOGGER = get_logger('helper.tsk')
FLS_PATTERN = regexp(
    r'(?P<type>[^\s]+)\s+(?P<deleted>\*\s+)?(?P<inode>[^:\(]+)[^\s]+\s+(?P<path>.*)'
)
MMLS_PATTERN = regexp(
    r'\d+:\s+\d+:\d+\s+(?P<offset>\d+)\s+\d+\s+(?P<size>\d+)\s*(?P<description>.*)'
)


def _read_and_match(cache: Path, pattern: Pattern) -> MatchIterator:
    out = cache.parent / f'{cache.name}.out'
    with out.open('rb') as outf:
        for line in outf:
            try:
                line = line.decode('utf-8')
            except UnicodeDecodeError:
                _LOGGER.warning("cannot decode as utf-8: %s", line)
                continue
            line = line.strip()
            match = pattern.fullmatch(line)
            if not match:
                continue
            yield match


def _exec(cache: Path, argv: list[str], pattern: Pattern) -> MatchIterator:
    out = cache.parent / f'{cache.name}.out'
    err = cache.parent / f'{cache.name}.err'
    cache.parent.mkdir(parents=True, exist_ok=True)
    if err.is_file():
        _LOGGER.error("using %s.err => %s", cache, err.read_bytes())
        return
    if out.is_file():
        _LOGGER.info("using %s.out", cache)
        yield from _read_and_match(cache, pattern)
        return
    with out.open('wb') as outf:
        with err.open('wb') as errf:
            try:
                _LOGGER.info("running %s", argv)
                run(argv, check=True, stdout=outf, stderr=errf)
            except CalledProcessError:
                errf.flush()
                _LOGGER.error(
                    "subprocess failed with error: %s", err.read_bytes()
                )
                return
    err.unlink()
    yield from _read_and_match(cache, pattern)


@dataclass(kw_only=True)
class TheSleuthKit:
    cache: Path
    image_is_partition: bool

    def partitions(self, image: Image) -> PartitionIterator:
        """Enumerate image partitions using mmls"""
        if self.image_is_partition:
            yield Partition(
                size=image.size,
                offset=0,
                description='',
                image=image,
            )
            return
        argv = ['mmls', str(image.path)]
        cache = self.cache / image.name / 'mmls'
        for match in _exec(cache, argv, MMLS_PATTERN):
            yield Partition(
                size=int(match.group('size')),
                offset=int(match.group('offset')),
                description=match.group('description'),
                image=image,
            )

    def fs_entries(self, partition: Partition) -> FSEntryIterator:
        """Enumerate partition file system entries using fls"""
        argv = [
            'fls',
            '-rpo',
            str(partition.offset),
            str(partition.image.path),
        ]
        cache = (
            self.cache / partition.image.name / str(partition.offset) / 'fls'
        )
        for match in _exec(cache, argv, FLS_PATTERN):
            if match.group('type') == 'V/V':
                continue
            yield FSEntry(
                path=PurePosixPath(match.group('path')),
                inode=match.group('inode'),
                deleted=bool(match.group('deleted')),
                directory=(match.group('type').endswith('/d')),
                partition=partition,
            )

    def fs_entry_data(self, fs_entry: FSEntry) -> Iterator[bytes]:
        """Extract fs entry data"""
        argv = [
            'icat',
            '-o',
            str(fs_entry.partition.offset),
            str(fs_entry.partition.image.path),
            str(fs_entry.inode),
        ]
        with Popen(argv, stdout=PIPE, stderr=DEVNULL) as process:
            # consume output in chunks while the process is running
            while process.poll() is None:
                data = process.stdout.read(64 * 1024)
                if not data:
                    continue
                yield data
            # consume remaining output after process termination
            data = process.stdout.read()
            if data:
                yield data
            # check for a non-zero return code before exiting
            if process.returncode != 0:
                _LOGGER.warning(
                    "icat failed with code %d for %s",
                    process.returncode,
                    fs_entry,
                )
                raise RuntimeError


def fs_entry_data_digests(
    tsk: TheSleuthKit, fs_entry: FSEntry
) -> Digests | None:
    """Compute digests of file system entry data"""
    digests = Digests()
    try:
        for data in tsk.fs_entry_data(fs_entry):
            digests.update(data)
    except (CalledProcessError, RuntimeError):
        return None
    digests.finalize()
    return digests


def fs_entry_data_extract(
    tsk: TheSleuthKit,
    fs_entry: FSEntry,
    output_directory: Path,
) -> int:
    """Extract filesystem record data to file"""
    if fs_entry.directory:
        raise ValueError("cannot extract a directory")
    output_filepath = (
        output_directory
        / str(fs_entry.partition.image.name)
        / str(fs_entry.partition.offset)
        / Path(fs_entry.path)
    )
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    with output_filepath.open('wb') as fobj:
        try:
            for data in tsk.fs_entry_data(fs_entry):
                fobj.write(data)
        except (CalledProcessError, RuntimeError):
            return -1
        fobj.flush()
    return output_filepath.stat().st_size

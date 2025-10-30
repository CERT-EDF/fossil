"""Regular expression helper"""

from collections.abc import Iterator
from pathlib import PurePath
from re import Match, Pattern
from re import compile as regexp

GLOB_STAR = regexp(r'(?<!\\)\*')
GLOB_QMARK = regexp(r'(?<!\\)\?')
GLOB_CLASS = regexp(r'(?<!\\)\[!')
GLOB_LIMITED = regexp(r'\*\*(?P<limit>\d+)')


MatchIterator = Iterator[Match]


def glob2re(glob: PurePath, case_insensitive: bool) -> Pattern:
    """This function attempts to convert a glob pattern to a regexp pattern"""
    parts = glob.parts
    pattern = []
    for index, part in enumerate(parts):
        match = GLOB_LIMITED.fullmatch(part)
        if match:
            limit = match.group('limit')
            pattern.append(f'([^/]*(/|$)){{,{limit}}}')
            continue
        if part == '**':
            pattern.append('([^/]*(/|$))*')
            continue
        for char in '#$&+-.^|~':
            part = part.replace(char, f'\\{char}')
        part = GLOB_CLASS.sub('[^', part)
        part = GLOB_QMARK.sub('.', part)
        part = GLOB_STAR.sub('.*', part)
        pattern.append(part)
        if index + 1 < len(parts):
            pattern.append('/')
    if case_insensitive:
        pattern.insert(0, '(?i)')
    return regexp(''.join(pattern))

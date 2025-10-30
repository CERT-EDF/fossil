"""Hashing helper"""

from dataclasses import dataclass, field

from cryptography.hazmat.primitives.hashes import (
    MD5,
    SHA1,
    SHA256,
    SHA512,
    Hash,
)


def _hashes_factory():
    return {
        'md5': Hash(MD5()),
        'sha1': Hash(SHA1()),
        'sha256': Hash(SHA256()),
        'sha512': Hash(SHA512()),
    }


@dataclass
class Digests:
    """Compute several digest at the same time"""

    _mda_map: dict[str, Hash] = field(default_factory=_hashes_factory)
    digests: dict[str, str] = field(default_factory=dict)

    def update(self, data: bytes):
        """Feed data to underlying message digest algorithms"""
        for mda in self._mda_map.values():
            mda.update(data)

    def finalize(self):
        """Finalize digest computation"""
        self.digests.update(
            {name: mda.finalize().hex() for name, mda in self._mda_map.items()}
        )

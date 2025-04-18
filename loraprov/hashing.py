"""
loraprov.hashing
~~~~~~~~~~~~~~~~

Tiny wrapper around :pymod:`hashlib` that streams the file so even multi‑GB
weights hash in constant memory.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Union


def sha256(path: Union[str, Path], chunk_size: int = 8192) -> str:
    """Return the lowercase hex SHA‑256 digest of *path*.

    Parameters
    ----------
    path
        File to hash.
    chunk_size
        How many bytes to read per iteration. 8 KiB is usually optimal.

    Examples
    --------
    >>> from loraprov.hashing import sha256
    >>> sha256("model.safetensors")
    '6efa0b42c7…'
    """
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

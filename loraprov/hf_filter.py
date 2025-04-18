"""
loraprov.hf_filter
~~~~~~~~~~~~~~~~~~

Git‑LFS *clean* filter that invokes loraprov.verify before push.

Usage (one‑time per repo)
-------------------------
git config filter.loraprov-clean.clean "python -m loraprov.hf_filter clean %f"
git config filter.loraprov-clean.smudge cat
echo "*.safetensors filter=loraprov-clean" >> .gitattributes
"""

from __future__ import annotations

import sys
from pathlib import Path

from .core import verify

MODE_CLEAN = "clean"  # invoked before files enter git‑LFS objects


def _abort(msg: str):
    sys.stderr.write(f"[loraprov] {msg}\n")
    sys.exit(1)


def main():
    if len(sys.argv) < 3:
        _abort("Usage: python -m loraprov.hf_filter clean <file>")

    mode, file_path = sys.argv[1], sys.argv[2]
    if mode != MODE_CLEAN:
        _abort(f"Unknown mode {mode}")

    ok, msg = verify(Path(file_path))
    if not ok:
        _abort(msg)
    # success → print original file path for LFS pipeline
    print(file_path)


if __name__ == "__main__":
    main()

"""
loraprov.keycli
~~~~~~~~~~~~~~~

Persistent Ed25519 key management for signing / verification.

• Keys live under  {home}/.loraprov/keys/{name}.key
• Public keys are returned as lowercase hex for easy JSON embedding.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Tuple

import nacl.signing  # type: ignore


def _loraprov_home() -> Path:
    # Allow override for tests:  set env LORAPROV_HOME="C:/tmp"
    return Path(os.environ.get("LORAPROV_HOME", Path.home() / ".loraprov")).expanduser()


class KeyManager:
    """Simple file‑based Ed25519 key storage."""

    def __init__(self) -> None:
        self.keys_dir = _loraprov_home() / "keys"
        self.keys_dir.mkdir(parents=True, exist_ok=True)

    # ---------- public API ---------- #
    def generate(self, name: str, overwrite: bool = False) -> str:
        """Generate a key named *name* and return its public key hex."""
        path = self._key_path(name)
        if path.exists() and not overwrite:
            raise FileExistsError(f"Key '{name}' already exists at {path}")
        signing_key = nacl.signing.SigningKey.generate()
        path.write_bytes(signing_key.encode())
        return signing_key.verify_key.encode().hex()

    def load(self, name: str) -> Tuple[nacl.signing.SigningKey, str]:
        """Return (signing_key, public_key_hex)."""
        path = self._key_path(name)
        if not path.exists():
            raise FileNotFoundError(f"Key '{name}' not found in {self.keys_dir}")
        signing_key = nacl.signing.SigningKey(path.read_bytes())
        return signing_key, signing_key.verify_key.encode().hex()

    def list(self) -> Dict[str, str]:
        """Return {key_name: public_key_hex} for all stored keys."""
        out: Dict[str, str] = {}
        for file in self.keys_dir.glob("*.key"):
            name = file.stem
            sk = nacl.signing.SigningKey(file.read_bytes())
            out[name] = sk.verify_key.encode().hex()
        return out

    # ---------- helpers ---------- #
    def _key_path(self, name: str) -> Path:
        if any(c in name for c in r"\/"):
            raise ValueError("Key name must not contain path separators")
        return self.keys_dir / f"{name}.key"

"""
loraprov.core
~~~~~~~~~~~~~

Detached‑signature format:

sig‑file = <adapter_path>.sig  (JSON)

{
  "sig": "<hex‑encoded ed25519 signature>",
  "payload": {
    "adapter_sha256": "…",
    "parent_sha256": "…",
    "license": "MIT",
    "created_at": "2025‑04‑17T00:00:00Z",
    "author_pubkey": "<hex 32‑byte>",
    "tool_version": "0.1.0"
  }
}
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional, Tuple

import nacl.signing  # type: ignore

from .hashing import sha256
from .keycli import KeyManager

TOOL_VERSION = "0.1.0"


# ---------- public API ---------- #
def sign(
    adapter_path: str | Path,
    *,
    parent_sha: str,
    license: str,
    key_name: str = "default",
    key_manager: Optional[KeyManager] = None,
) -> Path:
    """Create `<adapter>.sig` and return its path."""
    adapter_path = Path(adapter_path)
    if not adapter_path.exists():
        raise FileNotFoundError(adapter_path)
    km = key_manager or KeyManager()
    sk, author_pubkey = km.load(key_name)

    payload = {
        "adapter_sha256": sha256(adapter_path),
        "parent_sha256": parent_sha,
        "license": license,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "author_pubkey": author_pubkey,
        "tool_version": TOOL_VERSION,
    }

    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    sig_hex = sk.sign(payload_json).signature.hex()  # detached signature

    sig_obj = {"sig": sig_hex, "payload": payload}
    sig_path = adapter_path.with_suffix(adapter_path.suffix + ".sig")
    sig_path.write_text(json.dumps(sig_obj, indent=2))
    return sig_path


def verify(
    adapter_path: str | Path,
    *,
    sig_path: Path | None = None,
    policy: str = "default",
) -> Tuple[bool, str]:
    """Return (ok, message). *policy* placeholder for future rules."""
    adapter_path = Path(adapter_path)
    if sig_path is None:
        sig_path = adapter_path.with_suffix(adapter_path.suffix + ".sig")
    if not sig_path.exists():
        return False, f"signature file {sig_path} not found"

    sig_obj = json.loads(sig_path.read_text())
    sig_hex = sig_obj["sig"]
    payload = sig_obj["payload"]

    # 1. adapter hash match
    actual_sha = sha256(adapter_path)
    if payload["adapter_sha256"] != actual_sha:
        return False, "adapter_sha256 mismatch (file tampered?)"

    # 2. author signature verification
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    try:
        vk = nacl.signing.VerifyKey(bytes.fromhex(payload["author_pubkey"]))
        vk.verify(payload_json, bytes.fromhex(sig_hex))
    except Exception as exc:
        return False, f"invalid signature: {exc}"

    # 3. TODO: implement policy checks
    if policy != "default":
        return False, f"unknown policy {policy}"

    return True, "signature valid"

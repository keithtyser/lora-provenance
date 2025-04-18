import tempfile
from pathlib import Path

from loraprov.core import sign, verify
from loraprov.keycli import KeyManager


def _tmp_home():
    return tempfile.TemporaryDirectory().name  # helper for isolation


def test_sign_and_verify_roundtrip(tmp_path: Path, monkeypatch):
    # isolate ~/.loraprov
    monkeypatch.setenv("LORAPROV_HOME", str(tmp_path))
    km = KeyManager()
    km.generate("alice")

    # create dummy adapter
    adapter = tmp_path / "adapter.bin"
    adapter.write_bytes(b"hello world")

    sig_file = sign(adapter, parent_sha="abcd1234", license="MIT", key_name="alice")
    assert sig_file.exists()

    ok, msg = verify(adapter)
    assert ok, msg


def test_verify_detects_tamper(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("LORAPROV_HOME", str(tmp_path))
    km = KeyManager()
    km.generate("bob")

    adapter = tmp_path / "adapter.bin"
    adapter.write_bytes(b"data")
    sign(adapter, parent_sha="zz", license="MIT", key_name="bob")

    # tamper with adapter
    adapter.write_bytes(b"evil")

    ok, msg = verify(adapter)
    assert not ok
    assert "mismatch" in msg

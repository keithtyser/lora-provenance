import subprocess
import sys

from loraprov.core import sign
from loraprov.keycli import KeyManager


def test_filter_blocks_unsigned(monkeypatch, tmp_path):
    monkeypatch.setenv("LORAPROV_HOME", str(tmp_path / "home"))
    km = KeyManager()
    km.generate("k")

    adapter = tmp_path / "a.bin"
    adapter.write_bytes(b"hi")
    # unsigned
    proc = subprocess.run(
        [sys.executable, "-m", "loraprov.hf_filter", "clean", str(adapter)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0

    # sign and expect pass
    sign(adapter, parent_sha="x", license="MIT", key_name="k")
    proc = subprocess.run(
        [sys.executable, "-m", "loraprov.hf_filter", "clean", str(adapter)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0

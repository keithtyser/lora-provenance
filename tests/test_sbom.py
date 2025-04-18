from pathlib import Path

from loraprov.keycli import KeyManager
from loraprov.core import sign
from loraprov.sbom import export_cyclonedx


def test_sbom_export(tmp_path: Path, monkeypatch):
    # isolate ~/.loraprov
    monkeypatch.setenv("LORAPROV_HOME", str(tmp_path / "home"))

    # prepare key and signed adapter
    km = KeyManager()
    km.generate("alice")
    adapter = tmp_path / "a.bin"
    adapter.write_bytes(b"hello")
    sign(adapter, parent_sha="deadbeef", license="MIT", key_name="alice")

    # export SBOM
    sbom_out = tmp_path / "sbom.json"
    export_cyclonedx(adapter, sbom_out)

    # assertions
    data = sbom_out.read_text()
    assert '"bomFormat":' in data or '"components"' in data  # basic sanity

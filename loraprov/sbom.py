"""
loraprov.sbom
~~~~~~~~~~~~~

Lightweight CycloneDX SBOM exporter (JSON v1.4).

We intentionally avoid the `cyclonedx-python-lib` dependency to keep
loraprov minimal.  The SBOM includes only the fields enterprises care about:
hash, license, and provenance metadata.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from .core import verify


def export_cyclonedx(adapter: Path, out: Path):
    ok, msg = verify(adapter)
    if not ok:
        raise RuntimeError(f"Cannot export SBOM: {msg}")

    sig_obj = json.loads((adapter.with_suffix(adapter.suffix + ".sig")).read_text())
    p = sig_obj["payload"]

    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tools": [
                {"vendor": "loraprov", "name": "loraprov", "version": p["tool_version"]}
            ],
        },
        "components": [
            {
                "type": "library",
                "name": adapter.name,
                "version": p["parent_sha256"][:12],
                "hashes": [{"alg": "SHA-256", "content": p["adapter_sha256"]}],
                "licenses": [{"license": {"id": p["license"]}}],
            }
        ],
    }

    out.write_text(json.dumps(bom, indent=2))

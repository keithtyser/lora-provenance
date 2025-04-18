from pathlib import Path
import hashlib
import tempfile

from loraprov.hashing import sha256


def test_sha256_matches_reference():
    data = b"lora-provenance"
    # Create a temp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        expected = hashlib.sha256(data).hexdigest()
        assert sha256(Path(tmp.name)) == expected

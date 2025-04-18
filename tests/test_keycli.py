import os
import tempfile

from loraprov.keycli import KeyManager


def test_generate_load_list():
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["LORAPROV_HOME"] = tmp  # isolate test home
        km = KeyManager()

        pub1 = km.generate("alice")
        assert len(pub1) == 64  # hex‑encoded 32‑byte key
        assert "alice" in km.list()

        sk, pub1b = km.load("alice")
        assert pub1b == pub1
        message = b"hello"
        signature = sk.sign(message)
        # Verify succeeds with stored public key
        verify_key = km.load("alice")[0].verify_key
        verify_key.verify(signature)

"""One-time device possession proofs, shared with the authenticated claim endpoint."""
import hashlib
import hmac
import os
import secrets
from pathlib import Path
import threading

KEY_PATH = Path(os.getenv("DEVICE_CLAIM_KEY_PATH", "/var/lib/ad-agent/claim-key"))
_lock = threading.Lock()


def get_proof() -> str:
    with _lock:
        try:
            return KEY_PATH.read_text().strip()
        except OSError:
            KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
            key = secrets.token_urlsafe(48)
            temporary = KEY_PATH.with_suffix(".tmp")
            temporary.write_text(key)
            os.chmod(temporary, 0o600)
            os.replace(temporary, KEY_PATH)
            return key


def make_claim_payload(device_id: str) -> tuple[str, str]:
    proof = hmac.new(get_proof().encode(), device_id.encode(), hashlib.sha256).hexdigest()
    return proof, proof


def claim_established() -> None:
    with _lock:
        KEY_PATH.unlink(missing_ok=True)

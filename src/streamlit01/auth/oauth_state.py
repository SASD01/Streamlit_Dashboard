import base64
import hashlib
import hmac
import json
import secrets
import time

from streamlit01.config import get_microsoft_auth_settings


def generate_oauth_state() -> str:
    payload = {
        "nonce": secrets.token_urlsafe(16),
        "exp": int(time.time()) + 600,
    }

    data = base64.urlsafe_b64encode(
        json.dumps(payload).encode("utf-8")
    ).decode("utf-8")

    signature = _sign(data)

    return f"{data}.{signature}"


def is_valid_oauth_state(state: str) -> bool:
    try:
        data, signature = state.split(".")
    except ValueError:
        return False

    if not hmac.compare_digest(signature, _sign(data)):
        return False

    try:
        payload_bytes = base64.urlsafe_b64decode(data.encode("utf-8"))
        payload = json.loads(payload_bytes)
    except Exception:
        return False

    exp = payload.get("exp", 0)

    return int(exp) > int(time.time())


def _sign(data: str) -> str:
    secret = get_microsoft_auth_settings().state_secret

    return hmac.new(
        secret.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
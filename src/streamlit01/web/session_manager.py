import base64
import binascii
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta, timezone

import streamlit as st
from streamlit_cookies_controller import CookieController

from streamlit01.config import get_microsoft_auth_settings

AUTH_COOKIE_NAME = "portal_auth"
_AUTH_COOKIE_CONTROLLER_KEY = "portal_auth_cookie_controller"
_AUTH_SESSION_TTL = timedelta(days=7)


def get_current_user_id() -> uuid.UUID:
    return uuid.UUID(st.session_state.user_id)


def get_cookie_controller() -> CookieController:
    return CookieController(key=_AUTH_COOKIE_CONTROLLER_KEY)


def init_session_state() -> None:
    defaults = {
        "auth_state": None,
        "user_id": None,
        "user_email": None,
        "user_name": None,
        "allowed_pages": [],
        "auth_error": None,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def is_authenticated() -> bool:
    return st.session_state.get("user_id") is not None


def get_allowed_pages() -> list[dict[str, str]]:
    return st.session_state.get("allowed_pages", [])


def set_authenticated_user(
    user_id: str,
    email: str,
    name: str,
    allowed_pages: list[dict[str, str]],
    cookies: CookieController,
) -> None:
    settings = get_microsoft_auth_settings()
    token = _create_auth_token(user_id, settings.state_secret)
    cookies.set(
        AUTH_COOKIE_NAME,
        token,
        expires=datetime.now(timezone.utc) + _AUTH_SESSION_TTL,
        secure=settings.redirect_uri.startswith("https://"),
        same_site="strict",
    )

    st.session_state.user_id = user_id
    st.session_state.user_email = email
    st.session_state.user_name = name
    st.session_state.allowed_pages = allowed_pages
    st.session_state.auth_error = None


def clear_auth(cookies: CookieController) -> None:
    """Clear authentication data and the browser's auth cookie."""
    if cookies.get(AUTH_COOKIE_NAME) is not None:
        cookies.remove(AUTH_COOKIE_NAME)

    for key in (
        "auth_state",
        "user_id",
        "user_email",
        "user_name",
        "allowed_pages",
        "auth_error",
    ):
        st.session_state.pop(key, None)


def get_user_id_from_auth_token(token: object) -> uuid.UUID | None:
    if not isinstance(token, str) or len(token) > 2048:
        return None

    try:
        encoded_payload, signature = token.split(".", maxsplit=1)
    except ValueError:
        return None

    secret = get_microsoft_auth_settings().state_secret
    expected_signature = _sign(encoded_payload, secret)
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        payload_bytes = base64.b64decode(
            encoded_payload + "=" * (-len(encoded_payload) % 4),
            altchars=b"-_",
            validate=True,
        )
        payload = json.loads(payload_bytes)
        expiration = int(payload["exp"])
        user_id = uuid.UUID(payload["sub"])
    except (
        binascii.Error,
        KeyError,
        TypeError,
        ValueError,
        UnicodeDecodeError,
    ):
        return None

    if expiration <= int(datetime.now(timezone.utc).timestamp()):
        return None

    return user_id


def _create_auth_token(user_id: str, secret: str) -> str:
    payload = json.dumps(
        {
            "sub": user_id,
            "exp": int(
                (datetime.now(timezone.utc) + _AUTH_SESSION_TTL).timestamp()
            ),
        },
        separators=(",", ":"),
    ).encode("utf-8")
    encoded_payload = (
        base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    )

    return f"{encoded_payload}.{_sign(encoded_payload, secret)}"


def _sign(value: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        value.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
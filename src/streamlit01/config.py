import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

_RESERVED_MSAL_SCOPES = {
    "offline_access",
    "openid",
    "profile",
}


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")

    if not url:
        raise RuntimeError("DATABASE_URL environment variable is required.")

    return _normalize_database_url(url)


def _normalize_database_url(url: str) -> str:
    schemes = {
        "postgresql+psycopg2://": "postgresql+psycopg://",
        "postgresql+psycopg://": "postgresql+psycopg://",
        "postgresql://": "postgresql+psycopg://",
        "postgres://": "postgresql+psycopg://",
    }

    for old_scheme, new_scheme in schemes.items():
        if url.startswith(old_scheme):
            return url.replace(old_scheme, new_scheme, 1)

    raise ValueError("Unsupported DATABASE_URL scheme.")


@dataclass(frozen=True)
class MicrosoftAuthSettings:
    tenant_id: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: tuple[str, ...]
    state_secret: str


def get_microsoft_auth_settings() -> MicrosoftAuthSettings:
    tenant_id = _require_env("AZURE_TENANT_ID")
    client_id = _require_env("AZURE_CLIENT_ID")
    client_secret = _require_env("AZURE_CLIENT_SECRET")
    redirect_uri = _require_env("AZURE_REDIRECT_URI")

    scopes_env = os.getenv(
        "AZURE_SCOPES",
        "email,User.Read",
    )

    scopes = tuple(
        scope.strip()
        for scope in scopes_env.split(",")
        if scope.strip() and scope.strip() not in _RESERVED_MSAL_SCOPES
    )

    if not scopes:
        scopes = ("User.Read",)

    state_secret = os.getenv("AUTH_STATE_SECRET") or client_secret

    return MicrosoftAuthSettings(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes,
        state_secret=state_secret,
    )


def _require_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"{name} environment variable is required.")

    return value
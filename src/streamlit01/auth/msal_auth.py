from dataclasses import dataclass

import msal

from streamlit01.config import (
    MicrosoftAuthSettings,
    get_microsoft_auth_settings,
)


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    object_id: str
    email: str
    display_name: str


class MicrosoftAuthService:
    def __init__(self, settings: MicrosoftAuthSettings | None = None) -> None:
        self._settings = settings or get_microsoft_auth_settings()

    def _build_client(self) -> msal.ConfidentialClientApplication:
        authority = (
            "https://login.microsoftonline.com/"
            f"{self._settings.tenant_id}"
        )

        return msal.ConfidentialClientApplication(
            client_id=self._settings.client_id,
            client_credential=self._settings.client_secret,
            authority=authority,
        )

    def get_login_url(self, state: str) -> str:
        client = self._build_client()

        result = client.get_authorization_request_url(
            scopes=list(self._settings.scopes),
            redirect_uri=self._settings.redirect_uri,
            state=state,
        )

        if isinstance(result, tuple):
            return result[0]

        return result

    def exchange_code(self, code: str) -> AuthenticatedPrincipal:
        client = self._build_client()

        result = client.acquire_token_by_authorization_code(
            code,
            scopes=list(self._settings.scopes),
            redirect_uri=self._settings.redirect_uri,
        )

        if "error" in result:
            description = result.get(
                "error_description",
                "Unknown Microsoft authentication error.",
            )
            raise RuntimeError(description)

        claims = result.get("id_token_claims", {})

        return self._map_claims(claims)

    def _map_claims(
        self,
        claims: dict[str, object],
    ) -> AuthenticatedPrincipal:
        object_id = str(claims.get("oid", ""))

        email = str(
            claims.get("email")
            or claims.get("preferred_username")
            or ""
        )

        display_name = str(claims.get("name") or email)

        if not object_id:
            raise RuntimeError("Microsoft token does not contain oid.")

        if not email:
            raise RuntimeError(
                "Microsoft token does not contain email "
                "or preferred_username."
            )

        return AuthenticatedPrincipal(
            object_id=object_id,
            email=email,
            display_name=display_name,
        )
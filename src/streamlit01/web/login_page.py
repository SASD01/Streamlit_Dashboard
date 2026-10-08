import base64
from html import escape
from pathlib import Path

import streamlit as st

LOGO_PATH = Path(__file__).resolve().parents[1] / "assets" / "LOGIS_LOGO.png"

_MICROSOFT_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" '
    'viewBox="0 0 21 21" aria-hidden="true">'
    '<path fill="#f25022" d="M1 1h9v9H1z"/>'
    '<path fill="#7fba00" d="M11 1h9v9h-9z"/>'
    '<path fill="#00a4ef" d="M1 11h9v9H1z"/>'
    '<path fill="#ffb900" d="M11 11h9v9h-9z"/>'
    "</svg>"
)

_CSS = """
<style>
#MainMenu, footer { visibility: hidden; }
section[data-testid="stSidebar"],
button[data-testid="stSidebarCollapsedControl"] { display: none; }

div[data-testid="stMainBlockContainer"] {
    padding-top: .5rem !important;
    padding-bottom: .5rem !important;
}

.login-hero {
    box-sizing: border-box;
    width: 100%;
    min-height: calc(100vh - 5rem);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center !important;
    padding: 1rem !important;
}

.login-error {
    color: #b42318;
    margin: 0 auto 1rem !important;
}

.login-logo {
    display: block;
    width: min(220px, 28vw, 20vh);
    height: auto;
    margin: 0 auto 1.5rem !important;
}

.login-title {
    font-size: 2.1rem !important;
    font-weight: 700 !important;
    margin: 0 auto 1.5rem auto !important;
}

.login-subtitle {
    color: #555 !important;
    max-width: 620px;
    line-height: 1.6;
    margin: 0 auto clamp(1.25rem, 4vh, 2.25rem) auto !important;
}

a.ms-button,
a.ms-button:visited,
a.ms-button:hover,
a.ms-button:active {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: .6rem;
    background: #000 !important;
    color: #fff !important;
    border-radius: 8px;
    padding: .9rem 2.2rem !important;
    font-weight: 600 !important;
    text-decoration: none !important;
}

a.ms-button span {
    color: #fff !important;
    text-decoration: none !important;
}

.login-footer {
    color: #9aa5b1 !important;
    font-size: .85rem !important;
    margin-top: clamp(1.5rem, 4vh, 2.5rem) !important;
}

@media (max-height: 600px) {
    .login-hero {
        min-height: calc(100vh - 4rem);
        padding: .5rem !important;
    }

    .login-logo {
        width: min(160px, 18vh);
        margin-bottom: .75rem !important;
    }

    .login-title { font-size: 1.7rem !important; }
    .login-subtitle { margin-bottom: 1rem !important; }
    .login-footer { margin-top: 1rem !important; }
}
</style>
"""


@st.cache_data
def _logo_base64() -> str:
    return base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")


def render_login_page(
    login_url: str,
    error_message: str | None = None,
) -> None:
    logo_html = ""

    if LOGO_PATH.exists():
        logo_html = (
            '<img class="login-logo" '
            f'src="data:image/png;base64,{_logo_base64()}" '
            'alt="Logo Logistic">'
        )

    safe_url = escape(login_url, quote=True)
    error_html = ""
    if error_message:
        error_html = (
            '<div class="login-error" role="alert">'
            f"{escape(error_message)}"
            "</div>"
        )

    st.html(
        f"""{_CSS}
        <div class="login-hero">
            {error_html}
            {logo_html}
            <div class="login-title">
                Bienvenido al Dashboard de Logistic
            </div>
            <p class="login-subtitle">
                Inicia sesión para consultar la información de tus archivos.
                Conoce el estado, los detalles, y las versiones de tus
                archivos cargados a SharePoint.
            </p>
            <a class="ms-button" href="{safe_url}" target="_self">
                {_MICROSOFT_SVG}
                <span>Iniciar Sesión con Microsoft</span>
                <span aria-hidden="true">→</span>
            </a>
            <div class="login-footer">
                © 2026 Logistic Services And Solutions S.A.S
            </div>
        </div>
        """
    )
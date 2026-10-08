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

.login-hero {
    width: 100%;
    text-align: center !important;
    padding: 5rem 1rem 2rem !important;
}

.login-logo {
    display: block;
    width: 240px;
    margin: 0 auto 3.5rem auto !important;
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
    margin: 0 auto 4.5rem auto !important;
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
    margin-top: 6rem !important;
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
    if error_message:
        st.error(error_message)

    st.markdown(_CSS, unsafe_allow_html=True)

    logo_html = ""

    if LOGO_PATH.exists():
        logo_html = (
            '<img class="login-logo" '
            f'src="data:image/png;base64,{_logo_base64()}" '
            'alt="Logo Logistic">'
        )

    safe_url = escape(login_url, quote=True)

    st.markdown(
        f"""
        <div class="login-hero">
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
        """,
        unsafe_allow_html=True,
    )
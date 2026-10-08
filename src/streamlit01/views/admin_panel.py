import streamlit as st

from streamlit01.web.admin import (
    render_roles_section,
    render_users_section,
)
from streamlit01.web.guard import require_page_permission

_ADMIN_CSS = """
<style>
button[kind="primaryButton"] {
    background-color: var(--primary-color) !important;
    border-color: var(--primary-color) !important;
}

button[kind="primaryButton"]:hover {
    filter: brightness(0.92);
}

[data-testid="stTabBar"] button[aria-selected="true"],
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary-color) !important;
}

[data-testid="stTabBar"] button[aria-selected="true"]::after,
div[data-baseweb="tab-highlight"] {
    background-color: var(--primary-color) !important;
}

[data-testid="stMultiSelect"] [data-baseweb="tag"],
[data-testid="stMultiSelect"] [data-testid="stTag"] {
    background-color: var(--secondary-background-color) !important;
    border-color: var(--secondary-background-color) !important;
}

[data-testid="stMultiSelect"] [data-baseweb="tag"] span,
[data-testid="stMultiSelect"] [data-testid="stTag"] span {
    color: var(--text-color) !important;
}

[data-testid="stMultiSelect"] [data-baseweb="tag"] svg,
[data-testid="stMultiSelect"] [data-testid="stTag"] svg {
    fill: var(--text-color) !important;
}
</style>
"""

require_page_permission("admin_panel")

st.markdown(_ADMIN_CSS, unsafe_allow_html=True)

st.title("Panel de administración")
st.caption(
    "Los cambios de permisos se aplican cuando el usuario "
    "vuelve a iniciar sesión."
)

users_tab, roles_tab = st.tabs(
    ["Usuarios", "Roles y permisos"]
)

with users_tab:
    render_users_section()

with roles_tab:
    render_roles_section()
import streamlit as st

from streamlit01.web.session_manager import (
    init_session_state,
    is_authenticated,
)


def require_page_permission(page_key: str) -> None:
    init_session_state()

    if not is_authenticated():
        st.warning("Debes iniciar sesión para ver esta página.")
        st.stop()

    allowed_pages = st.session_state.get("allowed_pages", [])

    allowed_keys = {
        item.get("key")
        for item in allowed_pages
    }

    if page_key not in allowed_keys:
        st.error("No tienes permisos para ver esta página.")
        st.stop()
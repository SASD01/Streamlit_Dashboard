import streamlit as st

from streamlit01.web.session_manager import (
    clear_auth,
    get_allowed_pages,
)

_PAGE_PATHS = {
    "alert_control_dashboard": "views/alert_control_dashboard.py",
    "calls_dashboard": "views/calls_dashboard.py",
    "reimbursements_dashboard": "views/reimbursements_dashboard.py",
    "pre_operationals_dashboard": "views/pre_operationals_dashboard.py",
    "fuels_dashboard": "views/fuels_dashboard.py",
    "admin_panel": "views/admin_panel.py",
}


def render_navigation() -> None:
    _render_sidebar()

    allowed_pages = get_allowed_pages()
    pages = _build_pages(allowed_pages)

    if not pages:
        st.title("Sin acceso")
        st.info(
            "Tu usuario no tiene páginas asignadas. "
            "Contacta al administrador."
        )
        return

    navigation = st.navigation(pages)
    navigation.run()


def _build_pages(
    allowed_pages: list[dict[str, str]],
) -> list:
    pages = []

    for item in allowed_pages:
        page_key = item.get("key")
        title = item.get("title", page_key)
        path = _PAGE_PATHS.get(page_key)

        if path:
            pages.append(
                st.Page(
                    path,
                    title=title,
                    url_path=page_key,
                )
            )

    return pages


def _render_sidebar() -> None:
    with st.sidebar:
        st.write(f"Usuario: {st.session_state.get('user_name')}")

        if st.button("Cerrar sesión"):
            clear_auth()
            st.query_params.clear()
            st.rerun()
import streamlit as st

from streamlit01.auth import (
    MicrosoftAuthService,
    generate_oauth_state,
    is_valid_oauth_state,
)
from streamlit01.db.session import get_session
from streamlit01.services import UserService
from streamlit01.web.login_page import render_login_page
from streamlit01.web.session_manager import (
    is_authenticated,
    set_authenticated_user,
)


def handle_authentication() -> None:
    if is_authenticated():
        return

    _process_oauth_callback()

    if is_authenticated():
        return

    _render_login_page()


def _process_oauth_callback() -> None:
    code = st.query_params.get("code")
    state = st.query_params.get("state")

    if not code:
        return

    if not state or not is_valid_oauth_state(state):
        st.session_state.auth_error = "Estado de autenticación inválido."
        st.query_params.clear()
        return

    try:
        auth_service = MicrosoftAuthService()
        principal = auth_service.exchange_code(code)

        with get_session() as session:
            user_service = UserService(session)

            user = user_service.get_or_create_user(
                ms_object_id=principal.object_id,
                email=principal.email,
                full_name=principal.display_name,
            )

            pages = user_service.get_allowed_pages(user.id)

            allowed_pages = [
                {"key": page.page_key, "title": page.display_name}
                for page in pages
            ]

        set_authenticated_user(
            user_id=str(user.id),
            email=principal.email,
            name=principal.display_name,
            allowed_pages=allowed_pages,
        )

    except Exception as exc:
        st.session_state.auth_error = str(exc)

    finally:
        st.query_params.clear()
        st.session_state.auth_state = None


def _render_login_page() -> None:
    state = generate_oauth_state()
    auth_service = MicrosoftAuthService()
    login_url = auth_service.get_login_url(state)

    render_login_page(
        login_url=login_url,
        error_message=st.session_state.get("auth_error"),
    )
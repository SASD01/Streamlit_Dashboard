import streamlit as st
from streamlit_cookies_controller import CookieController

from streamlit01.auth import (
    MicrosoftAuthService,
    generate_oauth_state,
    is_valid_oauth_state,
)
from streamlit01.db.session import get_session
from streamlit01.repositories.user_repository import UserRepository
from streamlit01.services import UserService
from streamlit01.web.login_page import render_login_page
from streamlit01.web.session_manager import (
    AUTH_COOKIE_NAME,
    get_user_id_from_auth_token,
    is_authenticated,
    set_authenticated_user,
)


def handle_authentication(cookies: CookieController) -> None:
    if is_authenticated():
        return

    _restore_authenticated_user(cookies)

    if is_authenticated():
        return

    _process_oauth_callback(cookies)

    if is_authenticated():
        return

    _render_login_page()


def _restore_authenticated_user(cookies: CookieController) -> None:
    token = cookies.get(AUTH_COOKIE_NAME)
    user_id = get_user_id_from_auth_token(token)

    if user_id is None:
        if token is not None:
            cookies.remove(AUTH_COOKIE_NAME)
        return

    with get_session() as session:
        user = UserRepository(session).get_by_id(user_id)
        if user is None or not user.is_active:
            cookies.remove(AUTH_COOKIE_NAME)
            return

        pages = UserService(session).get_allowed_pages(user_id)
        allowed_pages = [
            {"key": page.page_key, "title": page.display_name}
            for page in pages
        ]

    set_authenticated_user(
        user_id=str(user.id),
        email=user.email,
        name=user.full_name,
        allowed_pages=allowed_pages,
        cookies=cookies,
    )


def _process_oauth_callback(cookies: CookieController) -> None:
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
            cookies=cookies,
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
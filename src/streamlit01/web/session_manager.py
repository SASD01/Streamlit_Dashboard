import streamlit as st


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
) -> None:
    st.session_state.user_id = user_id
    st.session_state.user_email = email
    st.session_state.user_name = name
    st.session_state.allowed_pages = allowed_pages
    st.session_state.auth_error = None


def clear_auth() -> None:
    """Clear the complete Streamlit session when the user logs out."""
    st.session_state.clear()
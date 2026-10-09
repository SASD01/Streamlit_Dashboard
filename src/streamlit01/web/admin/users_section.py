import uuid
import streamlit as st
from streamlit01.db.role import Role
from streamlit01.db.session import get_session
from streamlit01.db.user import User
from streamlit01.services import AdminActionError, AdminService
from streamlit01.web.session_manager import get_current_user_id


def render_users_section() -> None:
    actor_id = get_current_user_id()
    search = st.text_input("Buscar", placeholder="Nombre o correo")

    with get_session() as session:
        service = AdminService(session, actor_id)
        users = service.list_users(search or None)
        all_roles = service.list_roles()

    if not users:
        st.info("No se encontraron usuarios.")
        return

    for user in users:
        _render_user(actor_id, user, all_roles)


def _render_user(actor_id: uuid.UUID, user: User, all_roles: list[Role]) -> None:
    status = "-" if user.is_active else "x"

    with st.expander(f"{status} {user.full_name} · {user.email}"):
        with get_session() as session:
            service = AdminService(session, actor_id)
            current = [r.name for r in service.get_user_roles(user.id)]

        selected = st.multiselect(
            "Roles",
            [r.name for r in all_roles],
            current,
            key=f"roles_{user.id}",
        )

        if user.is_active:
            action_label, new_state = "Desactivar usuario", False
        else:
            action_label, new_state = "Activar usuario", True

        save_col, action_col = st.columns(2)

        with save_col:
            saved = st.button("Guardar roles", key=f"save_{user.id}", width="stretch")

        with action_col:
            toggled = st.button(action_label, key=f"toggle_{user.id}", width="stretch")

        if saved:
            _save_roles(actor_id, user.id, all_roles, current, selected)

        if toggled:
            _set_active(actor_id, user.id, new_state)


def _save_roles(actor_id: uuid.UUID, user_id: uuid.UUID, all_roles: list[Role], current: list[str], selected: list[str]) -> None:
    by_name = {r.name: r.id for r in all_roles}

    try:
        with get_session() as session:
            service = AdminService(session, actor_id)

            for name in set(selected) - set(current):
                service.assign_role(user_id, by_name[name])

            for name in set(current) - set(selected):
                service.remove_role(user_id, by_name[name])

        st.success("Roles actualizados.")
        st.rerun()
    except AdminActionError as exc:
        st.error(str(exc))


def _set_active(actor_id: uuid.UUID, user_id: uuid.UUID, is_active: bool) -> None:
    try:
        with get_session() as session:
            AdminService(session, actor_id).set_user_active(user_id, is_active)

        st.success("Estado actualizado.")
        st.rerun()
    except AdminActionError as exc:
        st.error(str(exc))
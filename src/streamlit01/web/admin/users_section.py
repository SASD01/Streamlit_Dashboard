import uuid

import streamlit as st

from streamlit01.db.role import Role
from streamlit01.db.session import get_session
from streamlit01.db.user import User
from streamlit01.services import AdminActionError, AdminService


def render_users_section() -> None:
    actor_id = uuid.UUID(st.session_state.user_id)
    search = st.text_input("Buscar", placeholder="Nombre o correo")

    with get_session() as session:
        service = AdminService(session)
        users = service.list_users(search or None)
        all_roles = service.list_roles()

    if not users:
        st.info("No se encontraron usuarios.")
        return

    for user in users:
        _render_user(actor_id, user, all_roles)


def _render_user(
    actor_id: uuid.UUID,
    user: User,
    all_roles: list[Role],
) -> None:
    status = "-" if user.is_active else "x"

    with st.expander(f"{status} {user.full_name} · {user.email}"):
        with get_session() as session:
            current = [
                role.name
                for role in AdminService(session).get_user_roles(user.id)
            ]

        role_names = [role.name for role in all_roles]

        selected = st.multiselect(
            "Roles",
            role_names,
            current,
            key=f"roles_{user.id}",
        )

        if user.is_active:
            action_label, new_state = "Desactivar usuario", False
        else:
            action_label, new_state = "Activar usuario", True

        save_column, action_column = st.columns(2)
        with save_column:
            if st.button(
                "Guardar roles",
                key=f"save_{user.id}",
                width="stretch",
            ):
                _save_roles(actor_id, user.id, all_roles, current, selected)

        with action_column:
            if st.button(
                action_label,
                key=f"toggle_{user.id}",
                width="stretch",
            ):
                _set_active(actor_id, user.id, new_state)


def _save_roles(
    actor_id: uuid.UUID,
    user_id: uuid.UUID,
    all_roles: list[Role],
    current: list[str],
    selected: list[str],
) -> None:
    by_name = {role.name: role.id for role in all_roles}

    try:
        with get_session() as session:
            service = AdminService(session)

            for name in set(selected) - set(current):
                service.assign_role(actor_id, user_id, by_name[name])

            for name in set(current) - set(selected):
                service.remove_role(actor_id, user_id, by_name[name])

        st.success("Roles actualizados.")
        st.rerun()
    except AdminActionError as exc:
        st.error(str(exc))


def _set_active(
    actor_id: uuid.UUID,
    user_id: uuid.UUID,
    is_active: bool,
) -> None:
    try:
        with get_session() as session:
            service = AdminService(session)
            service.set_user_active(actor_id, user_id, is_active)

        st.success("Estado actualizado.")
        st.rerun()
    except AdminActionError as exc:
        st.error(str(exc))
import uuid

import streamlit as st

from streamlit01.db.session import get_session
from streamlit01.services import AdminActionError, AdminService


def render_role_create_form(actor_id: uuid.UUID) -> None:
    with st.expander("Crear nuevo rol"):
        with st.form("create_role_form", clear_on_submit=True):
            name = st.text_input(
                "Nombre del rol",
                placeholder="ej: analyst, finance_manager",
            )
            description = st.text_input(
                "Descripción (opcional)",
                placeholder="ej: Read-only analytics role",
            )
            submitted = st.form_submit_button("Crear rol", type="primary")

        if submitted:
            _create_role(actor_id, name.strip(), description.strip() or None)


def _create_role(actor_id: uuid.UUID, name: str, description: str | None) -> None:
    if not name:
        st.error("El nombre del rol es obligatorio.")
        return

    try:
        with get_session() as session:
            AdminService(session, actor_id).create_role(name, description)

        st.success(f"Rol '{name}' creado. Asígnale páginas abajo.")
        st.rerun()
    except AdminActionError as exc:
        st.error(str(exc))
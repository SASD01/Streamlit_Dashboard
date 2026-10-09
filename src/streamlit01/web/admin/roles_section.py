import uuid

import streamlit as st

from streamlit01.db.page import Page
from streamlit01.db.session import get_session
from streamlit01.repositories.page_repository import PageRepository
from streamlit01.services import AdminActionError, AdminService
from streamlit01.web.admin.role_create_form import render_role_create_form
from streamlit01.web.session_manager import get_current_user_id


def render_roles_section() -> None:
    actor_id = get_current_user_id()

    render_role_create_form(actor_id)

    with get_session() as session:
        service = AdminService(session, actor_id)
        roles = service.list_roles()
        all_pages = PageRepository(session).list_all()

    if not roles:
        st.info("No hay roles registrados.")
        return

    role_ids = {role.name: role.id for role in roles}
    role_name = st.selectbox("Rol", options=list(role_ids.keys()))
    role_id = role_ids[role_name]

    with get_session() as session:
        service = AdminService(session, actor_id)
        assigned = service.get_role_pages(role_id)

    assigned_keys = {page.page_key for page in assigned}
    labels = {page.page_key: page.display_name for page in all_pages}
    page_keys = list(labels.keys())

    selected = st.multiselect(
        "Páginas del rol",
        options=page_keys,
        default=sorted(assigned_keys, key=page_keys.index),
        format_func=lambda key: labels[key],
        key=f"pages_{role_id}",
    )

    if role_name == "admin":
        st.caption(
            "Protección activa: el rol admin siempre debe conservar "
            "la página admin_panel."
        )

    if st.button("Guardar permisos", type="primary"):
        _save_pages(actor_id, role_id, all_pages, selected)


def _save_pages(actor_id: uuid.UUID, role_id: uuid.UUID, all_pages: list[Page], selected: list[str]) -> None:
    page_ids = [p.id for p in all_pages if p.page_key in selected]

    try:
        with get_session() as session:
            AdminService(session, actor_id).update_role_pages(role_id, page_ids)

        st.success(
            "Permisos actualizados. Se aplicarán al próximo "
            "inicio de sesión de cada usuario."
        )
        st.rerun()
    except AdminActionError as exc:
        st.error(str(exc))
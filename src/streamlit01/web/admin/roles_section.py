import streamlit as st

from streamlit01.db.session import get_session
from streamlit01.repositories.page_repository import PageRepository
from streamlit01.services import AdminActionError, AdminService


def render_roles_section() -> None:
    with get_session() as session:
        service = AdminService(session)
        roles = service.list_roles()
        all_pages = PageRepository(session).list_all()

    if not roles:
        st.info("No hay roles registrados.")
        return

    role_ids = {role.name: role.id for role in roles}
    role_name = st.selectbox("Rol", options=list(role_ids.keys()))
    role_id = role_ids[role_name]

    with get_session() as session:
        assigned = AdminService(session).get_role_pages(role_id)

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
        page_ids = [
            page.id for page in all_pages if page.page_key in selected
        ]

        try:
            with get_session() as session:
                AdminService(session).update_role_pages(role_id, page_ids)

            st.success(
                "Permisos actualizados. Se aplicarán al próximo "
                "inicio de sesión de cada usuario."
            )
            st.rerun()
        except AdminActionError as exc:
            st.error(str(exc))
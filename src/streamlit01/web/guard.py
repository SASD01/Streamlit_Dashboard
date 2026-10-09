import re
import uuid

import streamlit as st
from sqlalchemy.orm import Session

from streamlit01.repositories.page_repository import PageRepository
from streamlit01.repositories.role_repository import RoleRepository
from streamlit01.repositories.user_admin_repository import UserAdminRepository
from streamlit01.repositories.user_repository import UserRepository
from streamlit01.web.session_manager import init_session_state, is_authenticated

ADMIN_ROLE = "admin"
ADMIN_PAGE_KEY = "admin_panel"
RESERVED_ROLE_NAMES = {"admin", "guest"}
ROLE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class AdminActionError(Exception):
    """Operación de administración no permitida."""


def require_page_permission(page_key: str) -> None:
    init_session_state()

    if not is_authenticated():
        st.warning("Debes iniciar sesión para ver esta página.")
        st.stop()

    allowed = st.session_state.get("allowed_pages", [])
    allowed_keys = {item.get("key") for item in allowed}

    if page_key not in allowed_keys:
        st.error("No tienes permisos para ver esta página.")
        st.stop()


def require_admin_actor(session: Session, actor_id: uuid.UUID) -> None:
    users = UserRepository(session)
    actor = users.get_by_id(actor_id)

    if actor is None or not actor.is_active:
        raise AdminActionError("Sesión no autorizada.")

    if ADMIN_ROLE not in users.get_role_names(actor_id):
        raise AdminActionError("Se requiere rol admin para esta operación.")


def validate_new_role_name(session: Session, name: str) -> None:
    if not ROLE_NAME_PATTERN.match(name):
        raise AdminActionError(
            "Nombre de rol inválido: use minúsculas, números o guiones bajos."
        )

    if name in RESERVED_ROLE_NAMES:
        raise AdminActionError(f"El nombre '{name}' está reservado.")

    if RoleRepository(session).get_by_name(name) is not None:
        raise AdminActionError(f"El rol '{name}' ya existe.")


def guard_admin_role_removal(session: Session, actor_id: uuid.UUID, user_id: uuid.UUID) -> None:
    if user_id == actor_id:
        raise AdminActionError("No puedes quitarte tu propio rol admin.")

    if UserAdminRepository(session).count_active_with_role(ADMIN_ROLE) <= 1:
        raise AdminActionError("Debe quedar al menos un admin activo.")


def guard_deactivation(session: Session, actor_id: uuid.UUID, user_id: uuid.UUID) -> None:
    if user_id == actor_id:
        raise AdminActionError("No puedes desactivar tu propio usuario.")

    users = UserRepository(session)
    is_admin = ADMIN_ROLE in users.get_role_names(user_id)

    if is_admin and UserAdminRepository(session).count_active_with_role(ADMIN_ROLE) <= 1:
        raise AdminActionError("Debe quedar al menos un admin activo.")


def guard_admin_pages(session: Session, page_ids: list[uuid.UUID]) -> None:
    admin_page = PageRepository(session).get_by_key(ADMIN_PAGE_KEY)

    if admin_page is not None and admin_page.id not in page_ids:
        raise AdminActionError("El rol admin debe conservar admin_panel.")
import uuid

from sqlalchemy.orm import Session

from streamlit01.db.page import Page
from streamlit01.db.role import Role
from streamlit01.db.user import User
from streamlit01.repositories.page_repository import PageRepository
from streamlit01.repositories.role_repository import RoleRepository
from streamlit01.repositories.user_admin_repository import UserAdminRepository
from streamlit01.repositories.user_repository import UserRepository

ADMIN_ROLE = "admin"
ADMIN_PAGE_KEY = "admin_panel"


class AdminActionError(Exception):
    """Operación de administración no permitida."""


class AdminService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._user_admin = UserAdminRepository(session)
        self._roles = RoleRepository(session)
        self._pages = PageRepository(session)

    def list_users(self, search: str | None = None) -> list[User]:
        return self._user_admin.list_users(search)

    def list_roles(self) -> list[Role]:
        return self._roles.list_all()

    def get_user_roles(self, user_id: uuid.UUID) -> list[Role]:
        return self._users.get_roles(user_id)

    def get_role_pages(self, role_id: uuid.UUID) -> list[Page]:
        return self._roles.get_pages(role_id)

    def assign_role(
        self, actor_id: uuid.UUID, user_id: uuid.UUID, role_id: uuid.UUID,
    ) -> None:
        self._users.assign_role(user_id, role_id, assigned_by=actor_id)
        self._session.commit()

    def remove_role(
        self, actor_id: uuid.UUID, user_id: uuid.UUID, role_id: uuid.UUID,
    ) -> None:
        role = self._roles.get_by_id(role_id)
        if role is None:
            raise AdminActionError("Rol no encontrado.")
        if role.name == ADMIN_ROLE:
            self._guard_admin_role_removal(actor_id, user_id)
        self._users.remove_role(user_id, role_id)
        self._session.commit()

    def set_user_active(
        self, actor_id: uuid.UUID, user_id: uuid.UUID, is_active: bool,
    ) -> None:
        if not is_active:
            self._guard_deactivation(actor_id, user_id)
        self._user_admin.set_active(user_id, is_active)
        self._session.commit()

    def update_role_pages(
        self, role_id: uuid.UUID, page_ids: list[uuid.UUID],
    ) -> None:
        role = self._roles.get_by_id(role_id)
        if role is None:
            raise AdminActionError("Rol no encontrado.")
        if role.name == ADMIN_ROLE:
            self._guard_admin_pages(page_ids)
        self._roles.set_pages(role_id, page_ids)
        self._session.commit()

    def _guard_admin_role_removal(
        self, actor_id: uuid.UUID, user_id: uuid.UUID,
    ) -> None:
        if user_id == actor_id:
            raise AdminActionError("No puedes quitarte tu propio rol admin.")
        if self._user_admin.count_active_with_role(ADMIN_ROLE) <= 1:
            raise AdminActionError("Debe quedar al menos un admin activo.")

    def _guard_deactivation(self, actor_id: uuid.UUID, user_id: uuid.UUID) -> None:
        if user_id == actor_id:
            raise AdminActionError("No puedes desactivar tu propio usuario.")
        has_admin = ADMIN_ROLE in self._users.get_role_names(user_id)
        if has_admin and self._user_admin.count_active_with_role(ADMIN_ROLE) <= 1:
            raise AdminActionError("Debe quedar al menos un admin activo.")

    def _guard_admin_pages(self, page_ids: list[uuid.UUID]) -> None:
        admin_page = self._pages.get_by_key(ADMIN_PAGE_KEY)
        if admin_page is not None and admin_page.id not in page_ids:
            raise AdminActionError("El rol admin debe conservar admin_panel.")
import uuid

from sqlalchemy.orm import Session

from streamlit01.db.page import Page
from streamlit01.db.role import Role
from streamlit01.db.user import User
from streamlit01.repositories.page_repository import PageRepository
from streamlit01.repositories.role_repository import RoleRepository
from streamlit01.repositories.user_admin_repository import UserAdminRepository
from streamlit01.repositories.user_repository import UserRepository
from streamlit01.web import guard


class AdminService:
    def __init__(self, session: Session, actor_id: uuid.UUID) -> None:
        self._session = session
        self._actor_id = actor_id
        self._users = UserRepository(session)
        self._user_admin = UserAdminRepository(session)
        self._roles = RoleRepository(session)
        self._pages = PageRepository(session)

    def list_users(self, search: str | None = None) -> list[User]:
        self._require_admin()
        return self._user_admin.list_users(search)

    def list_roles(self) -> list[Role]:
        self._require_admin()
        return self._roles.list_all()

    def get_user_roles(self, user_id: uuid.UUID) -> list[Role]:
        self._require_admin()
        return self._users.get_roles(user_id)

    def get_role_pages(self, role_id: uuid.UUID) -> list[Page]:
        self._require_admin()
        return self._roles.get_pages(role_id)

    def create_role(self, name: str, description: str | None = None) -> Role:
        self._require_admin()
        guard.validate_new_role_name(self._session, name)
        role = self._roles.create(name=name, description=description)
        self._session.commit()
        return role

    def assign_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        self._require_admin()
        self._users.assign_role(user_id, role_id, assigned_by=self._actor_id)
        self._session.commit()

    def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        self._require_admin()
        role = self._roles.get_by_id(role_id)

        if role is None:
            raise guard.AdminActionError("Rol no encontrado.")

        if role.name == guard.ADMIN_ROLE:
            guard.guard_admin_role_removal(self._session, self._actor_id, user_id)

        self._users.remove_role(user_id, role_id)
        self._session.commit()

    def set_user_active(self, user_id: uuid.UUID, is_active: bool) -> None:
        self._require_admin()

        if not is_active:
            guard.guard_deactivation(self._session, self._actor_id, user_id)

        self._user_admin.set_active(user_id, is_active)
        self._session.commit()

    def update_role_pages(self, role_id: uuid.UUID, page_ids: list[uuid.UUID]) -> None:
        self._require_admin()
        role = self._roles.get_by_id(role_id)

        if role is None:
            raise guard.AdminActionError("Rol no encontrado.")

        if role.name == guard.ADMIN_ROLE:
            guard.guard_admin_pages(self._session, page_ids)

        self._roles.set_pages(role_id, page_ids)
        self._session.commit()

    def _require_admin(self) -> None:
        guard.require_admin_actor(self._session, self._actor_id)
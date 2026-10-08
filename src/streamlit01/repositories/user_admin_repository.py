import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from streamlit01.db.associations import user_roles
from streamlit01.db.role import Role
from streamlit01.db.user import User


class UserAdminRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_users(self, search: str | None = None) -> list[User]:
        stmt = select(User).order_by(User.full_name)

        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                User.full_name.ilike(pattern)
                | User.email.ilike(pattern)
            )

        return list(self._session.scalars(stmt).all())

    def set_active(self, user_id: uuid.UUID, is_active: bool) -> None:
        user = self._session.get(User, user_id)

        if user is not None:
            user.is_active = is_active

    def count_active_with_role(self, role_name: str) -> int:
        stmt = (
            select(User.id)
            .join(user_roles, user_roles.c.user_id == User.id)
            .join(Role, Role.id == user_roles.c.role_id)
            .where(
                User.is_active.is_(True),
                Role.name == role_name,
            )
            .distinct()
        )

        return len(self._session.scalars(stmt).all())
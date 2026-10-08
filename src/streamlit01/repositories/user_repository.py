import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from streamlit01.db.associations import role_pages, user_roles
from streamlit01.db.page import Page
from streamlit01.db.role import Role
from streamlit01.db.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_microsoft_object_id(self, object_id: str) -> User | None:
        stmt = select(User).where(User.microsoft_object_id == object_id)
        return self._session.scalar(stmt)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._session.scalar(stmt)

    def create(
        self,
        *,
        microsoft_object_id: str,
        email: str,
        full_name: str,
        is_active: bool = True,
    ) -> User:
        user = User(
            microsoft_object_id=microsoft_object_id,
            email=email,
            full_name=full_name,
            is_active=is_active,
        )

        self._session.add(user)
        self._session.flush()

        return user

    def assign_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        assigned_by: uuid.UUID | None = None,
    ) -> None:
        stmt = select(user_roles.c.user_id).where(
            user_roles.c.user_id == user_id,
            user_roles.c.role_id == role_id,
        )

        exists = self._session.execute(stmt).first() is not None

        if not exists:
            insert_stmt = user_roles.insert().values(
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by,
            )

            self._session.execute(insert_stmt)

    def get_roles(self, user_id: uuid.UUID) -> list[Role]:
        stmt = (
            select(Role)
            .join(user_roles, Role.id == user_roles.c.role_id)
            .where(user_roles.c.user_id == user_id)
            .order_by(Role.name)
        )

        return list(self._session.scalars(stmt).all())

    def get_allowed_pages(self, user_id: uuid.UUID) -> list[Page]:
        stmt = (
            select(Page)
            .join(role_pages, Page.id == role_pages.c.page_id)
            .join(user_roles, role_pages.c.role_id == user_roles.c.role_id)
            .join(User, User.id == user_roles.c.user_id)
            .where(
                user_roles.c.user_id == user_id,
                User.is_active.is_(True),
                Page.is_active.is_(True),
            )
            .order_by(Page.sort_order)
            .distinct()
        )

        return list(self._session.scalars(stmt).all())
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from streamlit01.db.associations import role_pages
from streamlit01.db.page import Page
from streamlit01.db.role import Role


class RoleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        return self._session.scalar(stmt)

    def get_by_id(self, role_id: uuid.UUID) -> Role | None:
        stmt = select(Role).where(Role.id == role_id)
        return self._session.scalar(stmt)

    def list_all(self) -> list[Role]:
        stmt = select(Role).order_by(Role.name)
        return list(self._session.scalars(stmt).all())

    def create(self, *, name: str, description: str | None = None) -> Role:
        role = Role(name=name, description=description)
        self._session.add(role)
        self._session.flush()
        return role

    def get_pages(self, role_id: uuid.UUID) -> list[Page]:
        stmt = (
            select(Page)
            .join(role_pages, Page.id == role_pages.c.page_id)
            .where(role_pages.c.role_id == role_id)
            .order_by(Page.sort_order)
        )
        return list(self._session.scalars(stmt).all())

    def add_page(self, role_id: uuid.UUID, page_id: uuid.UUID) -> None:
        stmt = select(role_pages.c.role_id).where(
            role_pages.c.role_id == role_id,
            role_pages.c.page_id == page_id,
        )
        if self._session.execute(stmt).first() is None:
            self._session.execute(
                role_pages.insert().values(
                    role_id=role_id,
                    page_id=page_id,
                )
            )

    def remove_page(self, role_id: uuid.UUID, page_id: uuid.UUID) -> None:
        stmt = role_pages.delete().where(
            role_pages.c.role_id == role_id,
            role_pages.c.page_id == page_id,
        )
        self._session.execute(stmt)

    def set_pages(self, role_id: uuid.UUID, page_ids: list[uuid.UUID]) -> None:
        self._session.execute(
            role_pages.delete().where(role_pages.c.role_id == role_id)
        )

        for page_id in page_ids:
            self._session.execute(
                role_pages.insert().values(
                    role_id=role_id,
                    page_id=page_id,
                )
            )
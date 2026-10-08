from sqlalchemy import select
from sqlalchemy.orm import Session

from streamlit01.db.page import Page


class PageRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_key(self, page_key: str) -> Page | None:
        stmt = select(Page).where(Page.page_key == page_key)
        return self._session.scalar(stmt)

    def list_all(self) -> list[Page]:
        stmt = select(Page).order_by(Page.sort_order)
        return list(self._session.scalars(stmt).all())

    def list_active(self) -> list[Page]:
        stmt = (
            select(Page)
            .where(Page.is_active.is_(True))
            .order_by(Page.sort_order)
        )
        return list(self._session.scalars(stmt).all())

    def create(
        self,
        *,
        page_key: str,
        display_name: str,
        description: str | None = None,
        sort_order: int = 0,
        is_active: bool = True,
    ) -> Page:
        page = Page(
            page_key=page_key,
            display_name=display_name,
            description=description,
            sort_order=sort_order,
            is_active=is_active,
        )

        self._session.add(page)
        self._session.flush()

        return page
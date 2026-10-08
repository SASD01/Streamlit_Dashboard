import uuid

from sqlalchemy.orm import Session

from streamlit01.db.page import Page
from streamlit01.db.user import User
from streamlit01.repositories.role_repository import RoleRepository
from streamlit01.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._user_repo = UserRepository(session)
        self._role_repo = RoleRepository(session)

    def get_or_create_user(
        self,
        ms_object_id: str,
        email: str,
        full_name: str,
    ) -> User:
        user = self._user_repo.get_by_microsoft_object_id(ms_object_id)

        if user is not None:
            return user

        return self._create_and_provision_user(ms_object_id, email, full_name)

    def _create_and_provision_user(
        self,
        ms_object_id: str,
        email: str,
        full_name: str,
    ) -> User:
        user = self._user_repo.create(
            microsoft_object_id=ms_object_id,
            email=email,
            full_name=full_name,
        )

        guest_role = self._role_repo.get_by_name("guest")

        if guest_role is not None:
            self._user_repo.assign_role(user.id, guest_role.id)

        self._session.commit()

        self._session.refresh(user)
        return user

    def get_allowed_pages(self, user_id: uuid.UUID) -> list[Page]:
        return self._user_repo.get_allowed_pages(user_id)
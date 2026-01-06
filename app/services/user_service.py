from typing import Optional
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import verify_password


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.repo.get_by_email(email)

    async def get_user_by_id(self, user_id):
        return await self.repo.get_by_id(user_id)

    async def create_user(self, user_in: UserCreate) -> User:
        return await self.repo.create(user_in)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

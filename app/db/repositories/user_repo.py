from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower().strip()).first()

    def create_user(
        self,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            full_name=full_name,
            is_superuser=is_superuser,
        )
        return self.create(user)

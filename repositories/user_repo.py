from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from models.user import User, Role


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def get_role_by_name(self, name: str) -> Optional[Role]:
        return self.db.execute(
            select(Role).where(Role.name == name)
        ).scalar_one_or_none()

    def create(self, full_name: str, email: str,
               password_hash: str, role_id: UUID,
               phone: Optional[str] = None) -> User:
        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            role_id=role_id,
            phone=phone
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_login(self, user: User) -> None:
        from datetime import datetime
        user.last_login = datetime.utcnow()
        self.db.commit()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

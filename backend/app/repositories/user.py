import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import User

class UserRepository:
    def create(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_uid(self, db: Session, uid: uuid.UUID) -> User:
        return db.query(User).filter(User.id == uid, User.is_deleted == False).first()

    def get_all(self, db: Session) -> list[User]:
        return db.query(User).filter(User.is_deleted == False).all()

    def get_by_email(self, db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email, User.is_deleted == False).first()

    def update(self, db: Session, uid: uuid.UUID, data: dict) -> User:
        user = self.get_by_uid(db, uid)
        if user:
            for k, v in data.items():
                setattr(user, k, v)
            db.commit()
            db.refresh(user)
        return user

    def soft_delete(self, db: Session, uid: uuid.UUID) -> bool:
        user = self.get_by_uid(db, uid)
        if user:
            user.is_deleted = True
            user.deleted_at = datetime.utcnow()
            # Also soft delete member associated if any
            if user.member:
                user.member.is_deleted = True
                user.member.deleted_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def search(self, db: Session, query: str) -> list[User]:
        return db.query(User).filter(
            User.is_deleted == False,
            User.email.ilike(f"%{query}%")
        ).all()

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Member, User

class MemberRepository:
    def create(self, db: Session, member: Member) -> Member:
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    def get_by_uid(self, db: Session, uid: uuid.UUID) -> Member:
        return db.query(Member).filter(Member.id == uid, Member.is_deleted == False).first()

    def get_all(self, db: Session) -> list[Member]:
        return db.query(Member).filter(Member.is_deleted == False).all()

    def get_by_user_id(self, db: Session, user_id: uuid.UUID) -> Member:
        return db.query(Member).filter(Member.user_id == user_id, Member.is_deleted == False).first()

    def get_by_membership_number(self, db: Session, membership_number: str) -> Member:
        return db.query(Member).filter(Member.membership_number == membership_number, Member.is_deleted == False).first()

    def get_by_email(self, db: Session, email: str) -> Member:
        return db.query(Member).join(User).filter(User.email == email, Member.is_deleted == False).first()

    def update(self, db: Session, uid: uuid.UUID, data: dict) -> Member:
        member = self.get_by_uid(db, uid)
        if member:
            for k, v in data.items():
                setattr(member, k, v)
            db.commit()
            db.refresh(member)
        return member

    def soft_delete(self, db: Session, uid: uuid.UUID) -> bool:
        member = self.get_by_uid(db, uid)
        if member:
            member.is_deleted = True
            member.deleted_at = datetime.utcnow()
            
            # Also soft delete user login
            if member.user:
                member.user.is_deleted = True
                member.user.deleted_at = datetime.utcnow()
                
            db.commit()
            return True
        return False

    def search(self, db: Session, query: str) -> list[Member]:
        return db.query(Member).join(User).filter(
            Member.is_deleted == False,
            (Member.first_name.ilike(f"%{query}%") |
             Member.last_name.ilike(f"%{query}%") |
             Member.membership_number.ilike(f"%{query}%") |
             User.email.ilike(f"%{query}%"))
        ).all()

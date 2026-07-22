import uuid
from sqlalchemy.orm import Session
from app.repositories.member import MemberRepository
from app.repositories.user import UserRepository
from app.models.models import Member, User
from app.schemas.schemas import MemberCreate, MemberUpdate
from app.core.security import get_password_hash
from fastapi import HTTPException, status

class MemberService:
    def __init__(self):
        self.member_repo = MemberRepository()
        self.user_repo = UserRepository()

    def get_members(self, db: Session) -> list[Member]:
        return self.member_repo.get_all(db)

    def search_members(self, db: Session, query: str) -> list[Member]:
        return self.member_repo.search(db, query)

    def get_member_by_id(self, db: Session, member_id: uuid.UUID) -> Member:
        member = self.member_repo.get_by_uid(db, member_id)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        return member

    def get_member_by_email(self, db: Session, email: str) -> Member:
        member = self.member_repo.get_by_email(db, email)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member with this email not found")
        return member

    def create_member(self, db: Session, member_in: MemberCreate) -> Member:
        existing_user = self.user_repo.get_by_email(db, member_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {member_in.email} already exists."
            )

        try:
            user = User(
                email=member_in.email,
                hashed_password=get_password_hash(member_in.password),
                role="Member",
                is_active=True
            )
            db.add(user)
            db.flush()

            membership_no = f"MEM-{datetime_year()}-{str(uuid.uuid4())[:8].upper()}"

            member = Member(
                user_id=user.id,
                first_name=member_in.first_name,
                last_name=member_in.last_name,
                phone=member_in.phone,
                membership_number=membership_no,
                is_active=True
            )
            created_member = self.member_repo.create(db, member)
            return created_member
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not register member: {e}"
            )

    def update_member(self, db: Session, member_id: uuid.UUID, member_in: MemberUpdate) -> Member:
        member = self.get_member_by_id(db, member_id)
        update_data = member_in.dict(exclude_unset=True)
        return self.member_repo.update(db, member_id, update_data)

    def delete_member(self, db: Session, member_id: uuid.UUID) -> bool:
        member = self.get_member_by_id(db, member_id)
        
        from app.models.models import Loan
        active_loans_count = db.query(Loan).filter(
            Loan.member_id == member.id,
            Loan.status.in_(["Active", "Overdue"]),
            Loan.is_deleted == False
        ).count()
        
        if active_loans_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete member: {active_loans_count} active loans exist."
            )
            
        return self.member_repo.soft_delete(db, member_id)

def datetime_year() -> int:
    from datetime import datetime
    return datetime.utcnow().year

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Loan, Book, Member, User

class LoanRepository:
    def create(self, db: Session, loan: Loan) -> Loan:
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan

    def get_by_uid(self, db: Session, uid: uuid.UUID) -> Loan:
        return db.query(Loan).filter(Loan.id == uid, Loan.is_deleted == False).first()

    def get_all(self, db: Session) -> list[Loan]:
        return db.query(Loan).filter(Loan.is_deleted == False).order_by(Loan.borrow_date.desc()).all()

    def update(self, db: Session, uid: uuid.UUID, data: dict) -> Loan:
        loan = self.get_by_uid(db, uid)
        if loan:
            for k, v in data.items():
                setattr(loan, k, v)
            db.commit()
            db.refresh(loan)
        return loan

    def soft_delete(self, db: Session, uid: uuid.UUID) -> bool:
        loan = self.get_by_uid(db, uid)
        if loan:
            loan.is_deleted = True
            loan.deleted_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def search(self, db: Session, query: str) -> list[Loan]:
        return db.query(Loan).join(Book).join(Member).join(User).filter(
            Loan.is_deleted == False,
            (Book.title.ilike(f"%{query}%") |
             Book.isbn.ilike(f"%{query}%") |
             Member.first_name.ilike(f"%{query}%") |
             Member.last_name.ilike(f"%{query}%") |
             User.email.ilike(f"%{query}%") |
             Loan.status.ilike(f"%{query}%"))
        ).order_by(Loan.borrow_date.desc()).all()

    def get_active_loans_by_member(self, db: Session, member_id: uuid.UUID) -> list[Loan]:
        return db.query(Loan).filter(
            Loan.member_id == member_id,
            Loan.status.in_(["Active", "Overdue"]),
            Loan.is_deleted == False
        ).all()

    def get_active_loan_by_book_and_member(self, db: Session, book_id: uuid.UUID, member_id: uuid.UUID) -> Loan:
        return db.query(Loan).filter(
            Loan.book_id == book_id,
            Loan.member_id == member_id,
            Loan.status.in_(["Active", "Overdue"]),
            Loan.is_deleted == False
        ).first()

    def get_overdue_loans(self, db: Session) -> list[Loan]:
        return db.query(Loan).filter(
            Loan.due_date < datetime.utcnow(),
            Loan.status == "Active",
            Loan.is_deleted == False
        ).all()
        
    def get_loans_by_member(self, db: Session, member_id: uuid.UUID) -> list[Loan]:
        return db.query(Loan).filter(
            Loan.member_id == member_id,
            Loan.is_deleted == False
        ).order_by(Loan.borrow_date.desc()).all()

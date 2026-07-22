import uuid
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.repositories.loan import LoanRepository
from app.repositories.book import BookRepository
from app.repositories.member import MemberRepository
from app.models.models import Loan, Book, Member
from app.schemas.schemas import LoanCreate
from app.core.config import settings
from fastapi import HTTPException, status
import redis

# Establish redis client for notifications
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

class LoanService:
    def __init__(self):
        self.loan_repo = LoanRepository()
        self.book_repo = BookRepository()
        self.member_repo = MemberRepository()

    def get_loans(self, db: Session) -> list[Loan]:
        return self.loan_repo.get_all(db)

    def search_loans(self, db: Session, query: str) -> list[Loan]:
        return self.loan_repo.search(db, query)

    def get_loans_by_member_email(self, db: Session, email: str) -> list[Loan]:
        member = self.member_repo.get_by_email(db, email)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        return self.loan_repo.get_loans_by_member(db, member.id)

    def borrow_book(self, db: Session, loan_in: LoanCreate) -> Loan:
        member = self.member_repo.get_by_email(db, loan_in.member_email)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not registered")
        if not member.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member account is inactive")

        book = self.book_repo.get_by_isbn(db, loan_in.isbn)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        if book.available_copies <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book has no copies available")

        existing = self.loan_repo.get_active_loan_by_book_and_member(db, book.id, member.id)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book already borrowed by this member")

        try:
            borrow_date = datetime.utcnow()
            due_date = borrow_date + timedelta(days=loan_in.days)
            
            loan = Loan(
                book_id=book.id,
                member_id=member.id,
                borrow_date=borrow_date,
                due_date=due_date,
                status="Active"
            )
            created_loan = self.loan_repo.create(db, loan)
            
            book.available_copies -= 1
            db.commit()
            
            self._publish_notification(
                type="borrow",
                message=f"{member.first_name} borrowed '{book.title}'",
                book_title=book.title,
                member_name=f"{member.first_name} {member.last_name}"
            )
            
            return created_loan
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not complete checkout: {e}"
            )

    def return_book(self, db: Session, member_email: str, isbn: str) -> Loan:
        member = self.member_repo.get_by_email(db, member_email)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not registered")

        book = self.book_repo.get_by_isbn(db, isbn)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        loan = self.loan_repo.get_active_loan_by_book_and_member(db, book.id, member.id)
        if not loan:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active loan found for this book and member")

        try:
            loan.return_date = datetime.utcnow()
            loan.status = "Returned"
            
            book.available_copies += 1
            db.commit()
            
            self._publish_notification(
                type="return",
                message=f"{member.first_name} returned '{book.title}'",
                book_title=book.title,
                member_name=f"{member.first_name} {member.last_name}"
            )
            
            return loan
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not return book: {e}"
            )

    def check_overdue_loans(self, db: Session) -> list[Loan]:
        overdue_loans = self.loan_repo.get_overdue_loans(db)
        updated_any = False
        for loan in overdue_loans:
            loan.status = "Overdue"
            updated_any = True
            self._publish_notification(
                type="overdue",
                message=f"Loan for '{loan.book.title}' is OVERDUE (Member: {loan.member.user.email})",
                book_title=loan.book.title,
                member_name=f"{loan.member.first_name} {loan.member.last_name}"
            )
        if updated_any:
            db.commit()
        return overdue_loans

    def _publish_notification(self, type: str, message: str, book_title: str, member_name: str):
        event = {
            "type": type,
            "message": message,
            "book_title": book_title,
            "member_name": member_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        try:
            redis_client.publish("notifications", json.dumps(event))
        except Exception as e:
            print(f"Failed to publish notification to Redis: {e}")

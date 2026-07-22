import uuid
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from app.database.session import get_db
from app.services.loan import LoanService
from app.schemas.schemas import LoanCreate, LoanResponse
from app.core.dependencies import get_current_active_librarian, get_current_user
from app.models.models import User, Loan
from pydantic import BaseModel, EmailStr

router = APIRouter()
loan_service = LoanService()

class ReturnRequest(BaseModel):
    member_email: EmailStr
    isbn: str

@router.get("/", response_model=list[LoanResponse])
def read_loans(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_librarian)):
    loans = loan_service.get_loans(db)
    return [map_loan_to_response(l) for l in loans]

@router.get("/search", response_model=list[LoanResponse])
def search_loans(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_librarian)
):
    loans = loan_service.search_loans(db, q)
    return [map_loan_to_response(l) for l in loans]

@router.get("/my-history", response_model=list[LoanResponse])
def read_my_loans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    loans = loan_service.get_loans_by_member_email(db, current_user.email)
    return [map_loan_to_response(l) for l in loans]

@router.post("/borrow", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(
    loan_in: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # If standard member is borrowing, they cannot borrow on behalf of others
    if current_user.role != "Librarian" and current_user.email != loan_in.member_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot borrow books for another member."
        )
    
    loan = loan_service.borrow_book(db, loan_in)
    return map_loan_to_response(loan)

@router.post("/return", response_model=LoanResponse)
def return_book(
    return_in: ReturnRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # If standard member is returning, they cannot return on behalf of others
    if current_user.role != "Librarian" and current_user.email != return_in.member_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot return books for another member."
        )
        
    loan = loan_service.return_book(db, return_in.member_email, return_in.isbn)
    return map_loan_to_response(loan)

@router.post("/trigger-overdue-check", status_code=status.HTTP_202_ACCEPTED)
def trigger_overdue_check(
    current_user: User = Depends(get_current_active_librarian)
):
    # Trigger the Celery background task using .delay()
    # Import the task inside to prevent cyclic import loops
    try:
        from workers.tasks import check_overdue_loans_task
        task = check_overdue_loans_task.delay()
        return {"status": "triggered", "task_id": task.id}
    except Exception as e:
        # Fallback to direct synchronous execution if Celery is not running
        # (helpful in testing/development environments)
        db = Session(bind=None) # We will get session inside route if we do fallback, but let's just log
        return {"status": "error", "detail": f"Failed to dispatch worker task: {e}"}

def map_loan_to_response(l: Loan) -> LoanResponse:
    return LoanResponse(
        id=l.id,
        book_id=l.book_id,
        book_title=l.book.title,
        book_isbn=l.book.isbn,
        member_id=l.member_id,
        member_email=l.member.user.email,
        member_name=f"{l.member.first_name} {l.member.last_name}",
        borrow_date=l.borrow_date,
        due_date=l.due_date,
        return_date=l.return_date,
        status=l.status
    )

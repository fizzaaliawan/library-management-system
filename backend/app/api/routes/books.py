import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.book import BookService
from app.schemas.schemas import BookCreate, BookUpdate, BookResponse
from app.core.dependencies import get_current_active_librarian, get_current_user
from app.models.models import User

router = APIRouter()
book_service = BookService()

@router.get("/", response_model=list[BookResponse])
def read_books(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return book_service.get_books(db)

@router.get("/search", response_model=list[BookResponse])
def search_books(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return book_service.search_books(db, q)

@router.get("/{book_id}", response_model=BookResponse)
def read_book(book_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return book_service.get_book_by_id(db, book_id)

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_librarian)
):
    return book_service.create_book(db, book_in)

@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: uuid.UUID,
    book_in: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_librarian)
):
    return book_service.update_book(db, book_id, book_in)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_librarian)
):
    book_service.delete_book(db, book_id)
    return None

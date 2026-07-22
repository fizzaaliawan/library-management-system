import uuid
from sqlalchemy.orm import Session
from app.repositories.book import BookRepository
from app.models.models import Book
from app.schemas.schemas import BookCreate, BookUpdate
from fastapi import HTTPException, status

class BookService:
    def __init__(self):
        self.book_repo = BookRepository()

    def get_books(self, db: Session) -> list[Book]:
        return self.book_repo.get_all(db)

    def search_books(self, db: Session, query: str) -> list[Book]:
        return self.book_repo.search(db, query)

    def get_book_by_id(self, db: Session, book_id: uuid.UUID) -> Book:
        book = self.book_repo.get_by_uid(db, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        return book

    def create_book(self, db: Session, book_in: BookCreate) -> Book:
        existing = self.book_repo.get_by_isbn(db, book_in.isbn)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN {book_in.isbn} already exists."
            )
        
        book = Book(
            title=book_in.title,
            author=book_in.author,
            isbn=book_in.isbn,
            genre=book_in.genre,
            total_copies=book_in.total_copies,
            available_copies=book_in.total_copies
        )
        return self.book_repo.create(db, book)

    def update_book(self, db: Session, book_id: uuid.UUID, book_in: BookUpdate) -> Book:
        book = self.get_book_by_id(db, book_id)
        
        update_data = book_in.dict(exclude_unset=True)
        
        if "total_copies" in update_data:
            borrowed_copies = book.total_copies - book.available_copies
            if update_data["total_copies"] < borrowed_copies:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot reduce total copies to {update_data['total_copies']} because {borrowed_copies} are currently borrowed."
                )
            book.total_copies = update_data["total_copies"]
            book.available_copies = book.total_copies - borrowed_copies
            del update_data["total_copies"]

        return self.book_repo.update(db, book_id, update_data)

    def delete_book(self, db: Session, book_id: uuid.UUID) -> bool:
        book = self.get_book_by_id(db, book_id)
        
        from app.models.models import Loan
        active_loans_count = db.query(Loan).filter(
            Loan.book_id == book.id,
            Loan.status.in_(["Active", "Overdue"]),
            Loan.is_deleted == False
        ).count()
        
        if active_loans_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete book: {active_loans_count} active loans exist."
            )
            
        return self.book_repo.soft_delete(db, book_id)

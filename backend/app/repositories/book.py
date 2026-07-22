import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Book

class BookRepository:
    def create(self, db: Session, book: Book) -> Book:
        db.add(book)
        db.commit()
        db.refresh(book)
        return book

    def get_by_uid(self, db: Session, uid: uuid.UUID) -> Book:
        return db.query(Book).filter(Book.id == uid, Book.is_deleted == False).first()

    def get_all(self, db: Session) -> list[Book]:
        return db.query(Book).filter(Book.is_deleted == False).all()

    def get_by_isbn(self, db: Session, isbn: str) -> Book:
        return db.query(Book).filter(Book.isbn == isbn, Book.is_deleted == False).first()

    def update(self, db: Session, uid: uuid.UUID, data: dict) -> Book:
        book = self.get_by_uid(db, uid)
        if book:
            for k, v in data.items():
                setattr(book, k, v)
            db.commit()
            db.refresh(book)
        return book

    def soft_delete(self, db: Session, uid: uuid.UUID) -> bool:
        book = self.get_by_uid(db, uid)
        if book:
            book.is_deleted = True
            book.deleted_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def search(self, db: Session, query: str) -> list[Book]:
        return db.query(Book).filter(
            Book.is_deleted == False,
            (Book.title.ilike(f"%{query}%") |
             Book.author.ilike(f"%{query}%") |
             Book.isbn.ilike(f"%{query}%") |
             Book.genre.ilike(f"%{query}%"))
        ).all()

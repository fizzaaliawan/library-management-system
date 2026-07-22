from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import uuid

# ==================== TOKEN / AUTH SCHEMAS ====================

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ==================== USER SCHEMAS ====================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "Member"  # "Librarian" or "Member"

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== MEMBER SCHEMAS ====================

class MemberCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

class MemberUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class MemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    membership_number: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== BOOK SCHEMAS ====================

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    genre: Optional[str] = None
    total_copies: int = Field(default=1, ge=1)

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    total_copies: Optional[int] = Field(default=None, ge=1)

class BookResponse(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    isbn: str
    genre: Optional[str]
    total_copies: int
    available_copies: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== LOAN SCHEMAS ====================

class LoanCreate(BaseModel):
    member_email: EmailStr
    isbn: str
    days: int = Field(default=14, ge=1)

class LoanResponse(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    book_title: str
    book_isbn: str
    member_id: uuid.UUID
    member_email: str
    member_name: str
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    status: str

    class Config:
        from_attributes = True

from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.models.models import User
from app.schemas.schemas import UserCreate, UserLogin, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta

class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def authenticate_user(self, db: Session, login_in: UserLogin) -> User:
        user = self.user_repo.get_by_email(db, login_in.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(login_in.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        return user

    def signup_user(self, db: Session, user_in: UserCreate) -> User:
        existing = self.user_repo.get_by_email(db, user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {user_in.email} already exists."
            )
        
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            is_active=True
        )
        return self.user_repo.create(db, user)
        


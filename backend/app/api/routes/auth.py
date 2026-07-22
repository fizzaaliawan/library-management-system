from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.user import UserService
from app.schemas.schemas import UserCreate, Token, UserResponse, UserLogin
from app.core.security import create_access_token
from app.core.dependencies import get_current_user
from app.models.models import User
from pydantic import EmailStr

router = APIRouter()
user_service = UserService()

@router.post("/signup", response_model=UserResponse)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    return user_service.signup_user(db, user_in)

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    # Convert standard form login request to UserLogin schema
    login_in = UserLogin(email=form_data.username, password=form_data.password)
    user = user_service.authenticate_user(db, login_in)
    
    access_token = create_access_token(subject=user.email)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "email": user.email
    }

@router.post("/login-json", response_model=Token)
def login_json(login_in: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, login_in)
    access_token = create_access_token(subject=user.email)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "email": user.email
    }
@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

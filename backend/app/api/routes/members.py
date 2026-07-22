import uuid
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.member import MemberService
from app.schemas.schemas import MemberCreate, MemberUpdate, MemberResponse
from app.core.dependencies import get_current_active_librarian, get_current_user
from app.models.models import User

router = APIRouter()
member_service = MemberService()

@router.get("/", response_model=list[MemberResponse])
def read_members(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_librarian)):
    members = member_service.get_members(db)
    # Populate the response schemas email property from Joined User entity
    return [map_member_to_response(m) for m in members]

@router.get("/search", response_model=list[MemberResponse])
def search_members(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_librarian)
):
    members = member_service.search_members(db, q)
    return [map_member_to_response(m) for m in members]

@router.get("/{member_id}", response_model=MemberResponse)
def read_member(
    member_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    member = member_service.get_member_by_id(db, member_id)
    if current_user.role != "Librarian" and member.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return map_member_to_response(member)

@router.get("/by-email/{email}", response_model=MemberResponse)
def read_member_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    member = member_service.get_member_by_email(db, email)
    if current_user.role != "Librarian" and member.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return map_member_to_response(member)

@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    member_in: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_librarian)
):
    member = member_service.create_member(db, member_in)
    return map_member_to_response(member)

@router.put("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: uuid.UUID,
    member_in: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    member = member_service.get_member_by_id(db, member_id)
    if current_user.role != "Librarian" and member.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    updated_member = member_service.update_member(db, member_id, member_in)
    return map_member_to_response(updated_member)

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_librarian)
):
    member_service.delete_member(db, member_id)
    return None

def map_member_to_response(m) -> MemberResponse:
    # Quick utility to resolve lazy User fields for API
    return MemberResponse(
        id=m.id,
        user_id=m.user_id,
        email=m.user.email,
        first_name=m.first_name,
        last_name=m.last_name,
        phone=m.phone,
        membership_number=m.membership_number,
        is_active=m.is_active,
        created_at=m.created_at
    )

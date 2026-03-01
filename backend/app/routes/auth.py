# backend/app/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import UserRegister, UserResponse
from app.database import get_db
from app.models.user import User
from app.utils.password import hash_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register_user(data: UserRegister, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password)
    )

    # Save
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Users
from app.schemas.user import UserCreate, UserLogin, Token, PasswordReset
from app.api.auth.auth import (
    create_access_token,
    get_current_user,
    get_current_super_admin,
    get_current_restaurant_owner,
    authenticate_user,
    send_password_reset_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(Users).filter(Users.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password and create user
    hashed_password = get_password_hash(user_in.password)
    user = Users(
        email=user_in.email,
        password_hash=hashed_password,
        full_name=user_in.full_name,
        role=user_in.role,
        restaurant_id=user_in.restaurant_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(
    form_data: UserLogin = Body(...),
    db: Session = Depends(get_db),
):
    """Login user and return JWT token."""
    user = authenticate_user(form_data.email, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Refresh JWT access token."""
    user = get_current_user(token, db)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout():
    """Logout user (invalidate token on client side)."""
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
def forgot_password(
    email: str = Body(...),
    db: Session = Depends(get_db),
):
    """Initiate password reset process."""
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If an account with this email exists, a reset link has been sent"}
    
    reset_token = create_access_token(data={"sub": str(user.id)})
    send_password_reset_email(email, reset_token)
    return {"message": "If an account with this email exists, a reset link has been sent"}


@router.post("/reset-password")
def reset_password(
    password_data: PasswordReset,
    db: Session = Depends(get_db),
):
    """Reset password with token."""
    user = db.query(Users).filter(Users.id == password_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    return {"message": "Password has been reset successfully"}
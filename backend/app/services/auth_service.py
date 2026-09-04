from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.core.security import verify_password
from app.schemas.auth import LoginRequest, LoginResponse

def authenticate_user(session: Session, request: LoginRequest) -> LoginResponse:
    """
    Authenticate a user by username and password.
    Returns a safe LoginResponse without leaking sensitive details.
    """
    try:
        stmt = select(User).where(User.username == request.username)
        user = session.scalars(stmt).first()

        if not user:
            return LoginResponse(success=False, message="Invalid username or password")

        if not user.password_hash:
            return LoginResponse(success=False, message="Invalid username or password")

        if not verify_password(request.password, user.password_hash):
            return LoginResponse(success=False, message="Invalid username or password")

        return LoginResponse(success=True, message="Authentication successful", user_id=user.id)
    except Exception as e:
        # In a real app, we would log the exception here.
        # For security, we never expose internal database errors to the client.
        return LoginResponse(success=False, message="Authentication failed due to an internal error")



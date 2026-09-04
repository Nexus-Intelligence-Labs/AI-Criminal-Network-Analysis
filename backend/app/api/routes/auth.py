from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.auth import LoginRequest, LoginResponse
from app.services import auth_service

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, session: Session = Depends(get_db_session)):
    """
    Authenticate a user using their username and password.
    Returns a safe response without exposing hashes or passwords.
    """
    result = auth_service.authenticate_user(session, request)
    
    if not result.success:
        # Return 401 Unauthorized for failed authentication
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return result



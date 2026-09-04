from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.audit_service import log_event, LOGIN_SUCCESS, LOGIN_FAILURE


def authenticate_user(session: Session, request: LoginRequest) -> LoginResponse:
    """
    Authenticate a user by username and password.
    Returns a safe LoginResponse without leaking sensitive details.
    """
    try:
        stmt = select(User).where(User.username == request.username)
        user = session.scalars(stmt).first()

        if not user:
            # Generic failure — do not reveal whether the username exists.
            log_event(
                session,
                LOGIN_FAILURE,
                actor=None,
                details={"reason": "invalid_credentials"},
            )
            return LoginResponse(success=False, message="Invalid username or password")

        if not user.password_hash:
            # Generic failure — do not reveal that the account has no hash.
            log_event(
                session,
                LOGIN_FAILURE,
                actor=None,
                details={"reason": "invalid_credentials"},
            )
            return LoginResponse(success=False, message="Invalid username or password")

        if not verify_password(request.password, user.password_hash):
            # Generic failure — do not reveal whether the password was wrong.
            log_event(
                session,
                LOGIN_FAILURE,
                actor=None,
                details={"reason": "invalid_credentials"},
            )
            return LoginResponse(success=False, message="Invalid username or password")

        # Generate JWT token using the application's configured JWT settings
        access_token = create_access_token(subject=user.id)

        # Successful authentication — record the authenticated actor.
        log_event(
            session,
            LOGIN_SUCCESS,
            actor=str(user.id),
            details={
                "username": user.username,
                "user_id": user.id,
            },
        )

        return LoginResponse(
            success=True,
            message="Authentication successful",
            user_id=user.id,
            access_token=access_token,
            token_type="bearer"
        )
    except Exception:
        # Safe, generic audit event — no exception text, no credentials, no
        # internal details.  The audit service itself never raises.
        log_event(
            session,
            LOGIN_FAILURE,
            actor=None,
            details={"reason": "internal_error"},
        )
        # In a real app, we would log the exception here.
        # For security, we never expose internal database errors to the client.
        return LoginResponse(success=False, message="Authentication failed due to an internal error")

"""FastAPI dependencies for authentication and role-based authorization.

Stage 5 — current user dependency:

    Authorization: Bearer <JWT>
        ↓
    HTTPBearer extracts the bearer credentials
        ↓
    app.core.security.verify_token cryptographically validates the JWT
        ↓
    validated ``sub`` claim is parsed as the user's stable database ID
        ↓
    PostgreSQL User lookup via the project's get_db_session
        ↓
    authenticated User ORM object is injected into the endpoint

Every authentication failure raises a uniform ``401`` with a generic message
and a ``WWW-Authenticate: Bearer`` challenge.  No JWT decoding internals,
PyJWT exceptions, or database details are ever exposed to the client.

Stage 6 — role-based authorization:

    ``require_role("admin")``      →  single allowed role
    ``require_roles("admin", "investigator")``  →  multiple allowed roles

The authorization dependencies build on :func:`get_current_user`, so they
enforce 401 when the caller is not authenticated and 403 when an
authenticated user lacks the required role.  Role decisions never come from
request body / query / path input.
"""

from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import InvalidTokenError, verify_token
from app.db.session import get_db_session
from app.models.user import User

# auto_error=False so a missing/invalid Authorization header is handled by
# this module and always returned as 401 (never FastAPI's default 403).
bearer_scheme = HTTPBearer(auto_error=False)

# Default role when the User record has no role attribute.  The User model
# currently does not persist a role column; the repository has no established
# migration strategy, so a persistent role field is not introduced here.
DEFAULT_USER_ROLE = "investigator"

# Canonical role vocabulary for the platform.  Kept intentionally small:
# no granular permissions matrix.
UserRole = str


def _authentication_error() -> HTTPException:
    """Return the uniform 401 response for any authentication failure."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    db: Session = Depends(get_db_session),
) -> User:
    """Resolve the authenticated User from the verified JWT bearer token.

    The authenticated identity is taken from the validated JWT ``sub`` claim
    only — never from the request body, query string, or path parameters.

    Raises:
        HTTPException: 401 when the token is missing, malformed, invalid,
            expired, missing a valid ``sub``, or references a user that no
            longer exists.
    """
    if credentials is None:
        raise _authentication_error()

    token = credentials.credentials.strip()
    if not token:
        raise _authentication_error()

    try:
        payload = verify_token(token)
    except InvalidTokenError:
        raise _authentication_error()

    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub.isdigit():
        raise _authentication_error()

    user_id = int(sub)

    stmt = select(User).where(User.id == user_id)
    user = db.scalars(stmt).first()
    if user is None:
        # A valid JWT pointing at a deleted user is an authentication failure,
        # not a 404 — and it must not reveal whether the user used to exist.
        raise _authentication_error()

    return user


def get_user_role(user: User) -> str:
    """Return the authorization role for an authenticated user.

    The current SQLAlchemy ``User`` model does not persist a role column and
    the repository has no established migration strategy, so role storage is
    not added to the database in this stage.  When a ``role`` attribute is
    present on the instance (e.g. a future mapped column, or a value assigned
    in tests) it is used; otherwise the default platform role is returned.

    Note:
        Persistent role storage remains a documented architectural dependency.

    Args:
        user: The authenticated User object.

    Returns:
        The resolved role string.
    """
    role = getattr(user, "role", None)
    if role:
        return str(role)
    return DEFAULT_USER_ROLE


def require_role(required_role: str) -> Callable[..., User]:
    """Build an authorization dependency requiring a single role.

    Example::

        @router.get("/admin")
        def admin_panel(current_user: User = Depends(require_role("admin"))):
            ...
    """
    return require_roles(required_role)


def require_roles(*allowed_roles: str) -> Callable[..., User]:
    """Build an authorization dependency allowing one of the given roles.

    Example::

        @router.get("/cases")
        def list_cases(
            current_user: User = Depends(require_roles("admin", "investigator")),
        ):
            ...

    The returned dependency first authenticates via :func:`get_current_user`
    (any auth failure → 401), then verifies the authenticated user's role is
    one of ``allowed_roles`` (otherwise → 403).
    """

    def role_guard(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if get_user_role(current_user) not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_guard


__all__ = [
    "get_current_user",
    "get_user_role",
    "require_role",
    "require_roles",
    "DEFAULT_USER_ROLE",
]
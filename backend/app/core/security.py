"""Security utilities: password hashing (Argon2) and JWT access tokens.

This module provides the password hashing foundation and JWT creation/verification
for the security layer. It is intentionally infrastructure-free: no database,
no FastAPI.

Usage::

    from app.core.security import hash_password, verify_password
    from app.core.security import create_access_token, verify_token

    hashed = hash_password("supersecret")
    ok = verify_password("supersecret", hashed)   # True

    token = create_access_token(subject=user.id)
    payload = verify_token(token)                  # {"sub": "1", "exp": ...}
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import get_settings

# Module-level hasher instance — shared, stateless, thread-safe.
# Using Argon2 exclusively as mandated by the security roadmap.
_hasher: PasswordHash = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2.

    Args:
        password: The plaintext password to hash.

    Returns:
        An Argon2 password hash string (never the original plaintext).

    Note:
        The same password hashed twice will produce different hashes due to
        random salting. Use :func:`verify_password` to validate a password
        against a stored hash.
    """
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored Argon2 hash.

    Args:
        password: The plaintext password to check.
        password_hash: The previously hashed password to compare against.

    Returns:
        ``True`` if the password matches the hash, ``False`` otherwise.
    """
    return _hasher.verify(password, password_hash)


class InvalidTokenError(Exception):
    """Raised when a JWT is invalid, expired, malformed, or missing required claims."""
    pass


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token using the application's JWT settings.

    Args:
        subject: The stable identifier for the user (e.g., user ID).
        expires_delta: Optional expiration timedelta. Defaults to the
            configured ``jwt_access_token_expire_minutes``.

    Returns:
        A signed JWT string containing ``sub``, ``exp``, and ``iat`` claims.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    to_encode = {"sub": str(subject), "iat": now}

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT access token using the application's JWT settings.

    Args:
        token: The JWT string to verify.

    Returns:
        The decoded token payload containing the claims.

    Raises:
        InvalidTokenError: If the token is invalid, expired, or missing the 'sub' claim.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if "sub" not in payload:
            raise InvalidTokenError("Token missing 'sub' claim")
        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")

"""Password hashing utilities using Argon2 via pwdlib.

This module provides the password hashing foundation for the security layer.
It is intentionally infrastructure-free: no database, no FastAPI, no JWT.

Usage::

    from app.core.security import hash_password, verify_password

    hashed = hash_password("supersecret")
    ok = verify_password("supersecret", hashed)   # True
    bad = verify_password("wrongpass", hashed)     # False
"""

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

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



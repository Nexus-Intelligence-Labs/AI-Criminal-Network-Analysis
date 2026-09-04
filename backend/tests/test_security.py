"""Unit tests for the password hashing foundation (Stage 1) and JWT (Stage 4).

These tests are intentionally isolated from all infrastructure:
no PostgreSQL, no Neo4j, no Docker, no FastAPI required.
"""

import pytest
import jwt
from datetime import datetime, timedelta, timezone

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    InvalidTokenError,
)
from app.core.config import get_settings


class TestHashPassword:
    """Tests for hash_password()."""

    def test_returns_string(self) -> None:
        """hash_password must return a str."""
        result = hash_password("mysecretpassword")
        assert isinstance(result, str)

    def test_hash_is_not_plaintext(self) -> None:
        """The returned hash must never equal the original plaintext."""
        password = "mysecretpassword"
        result = hash_password(password)
        assert result != password

    def test_different_hashes_for_same_password(self) -> None:
        """Hashing the same password twice should produce different hashes
        because Argon2 uses a unique random salt each time."""
        password = "mysecretpassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2


class TestVerifyPassword:
    """Tests for verify_password()."""

    def test_correct_password_returns_true(self) -> None:
        """verify_password must return True for the correct password."""
        password = "correctpassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_wrong_password_returns_false(self) -> None:
        """verify_password must return False for an incorrect password."""
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_empty_string_does_not_match_non_empty_hash(self) -> None:
        """An empty string must not verify against a hash of a real password."""
        hashed = hash_password("realpassword")
        assert verify_password("", hashed) is False

    def test_plaintext_does_not_match_different_password_hash(self) -> None:
        """A password must not verify against a hash of a completely different
        password."""
        hash_a = hash_password("passwordA")
        assert verify_password("passwordB", hash_a) is False


class TestJWT:
    """Tests for JWT access token creation and verification."""

    def test_valid_token_can_be_created(self) -> None:
        """A valid token can be created and is a string."""
        token = create_access_token(subject=123)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_decodes_correctly(self) -> None:
        """Token decodes correctly with the configured secret and algorithm."""
        token = create_access_token(subject=123)
        payload = verify_token(token)
        assert isinstance(payload, dict)

    def test_subject_is_preserved(self) -> None:
        """Subject is preserved as a string in the token payload."""
        token = create_access_token(subject=123)
        payload = verify_token(token)
        assert payload["sub"] == "123"

    def test_exp_exists(self) -> None:
        """Token payload contains an 'exp' claim."""
        token = create_access_token(subject=123)
        payload = verify_token(token)
        assert "exp" in payload

    def test_invalid_signature_rejected(self) -> None:
        """Token signed with wrong secret is rejected."""
        settings = get_settings()
        token = create_access_token(subject=123)
        # Tamper with the token by re-signing with a different secret
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        tampered = jwt.encode(payload, "wrongsecret", algorithm=settings.jwt_algorithm)
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            verify_token(tampered)

    def test_malformed_token_rejected(self) -> None:
        """Malformed token string is rejected."""
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            verify_token("not.a.jwt")

    def test_expired_token_rejected(self) -> None:
        """Expired JWT is rejected."""
        token = create_access_token(subject=123, expires_delta=timedelta(seconds=-10))
        with pytest.raises(InvalidTokenError, match="Token has expired"):
            verify_token(token)

    def test_missing_sub_rejected(self) -> None:
        """Token without 'sub' claim is rejected."""
        settings = get_settings()
        token = jwt.encode(
            {"exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        with pytest.raises(InvalidTokenError, match="missing 'sub'"):
            verify_token(token)

    def test_password_absent_from_payload(self) -> None:
        """Password must not be a JWT claim."""
        token = create_access_token(subject=123)
        payload = verify_token(token)
        assert "password" not in payload

    def test_password_hash_absent_from_payload(self) -> None:
        """password_hash must not be a JWT claim."""
        token = create_access_token(subject=123)
        payload = verify_token(token)
        assert "password_hash" not in payload

    def test_algorithm_controlled_by_server_configuration(self) -> None:
        """The allowed algorithm comes from trusted application configuration."""
        settings = get_settings()
        assert settings.jwt_algorithm == "HS256"
        # A token signed with a different algorithm must be rejected
        token = jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
            settings.jwt_secret,
            algorithm="HS512",
        )
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            verify_token(token)

"""Unit tests for the password hashing foundation (Stage 1).

These tests are intentionally isolated from all infrastructure:
no PostgreSQL, no Neo4j, no Docker, no FastAPI, no JWT required.
"""

import pytest

from app.core.security import hash_password, verify_password


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

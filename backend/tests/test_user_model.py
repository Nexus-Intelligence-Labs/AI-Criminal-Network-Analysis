"""Unit tests for the User model security fields (Stage 2).

These tests verify the User model can represent a securely authenticated user.
They are intentionally isolated from infrastructure: no live PostgreSQL, no
Neo4j, no Docker, no FastAPI, no JWT required.

SQLAlchemy models are pure Python dataclasses at instantiation time — they do
not require a database connection to be constructed and inspected in tests.
"""

from datetime import datetime

from app.core.security import hash_password
from app.models.user import User


class TestUserModelFields:
    """Verify the User model structure after Stage 2."""

    def test_user_has_password_hash_field(self) -> None:
        """User model must expose a password_hash attribute."""
        assert hasattr(User, "password_hash")

    def test_user_has_existing_id_field(self) -> None:
        """Existing id field must still be present."""
        assert hasattr(User, "id")

    def test_user_has_existing_username_field(self) -> None:
        """Existing username field must still be present."""
        assert hasattr(User, "username")

    def test_user_has_existing_created_at_field(self) -> None:
        """Existing created_at field must still be present."""
        assert hasattr(User, "created_at")

    def test_user_does_not_have_plaintext_password_field(self) -> None:
        """User model must NOT expose a plaintext password column."""
        # Protects against accidentally adding a 'password' column.
        assert not hasattr(User, "password") or "password_hash" not in str(
            getattr(User, "password", "")
        )
        # More direct check: 'password' as a mapped column name must not exist.
        column_names = {col.key for col in User.__table__.columns}
        assert "password" not in column_names

    def test_password_hash_column_exists_in_table(self) -> None:
        """password_hash must be a real column in the users table metadata."""
        column_names = {col.key for col in User.__table__.columns}
        assert "password_hash" in column_names

    def test_password_hash_column_is_nullable(self) -> None:
        """password_hash must be nullable (existing rows have no hash yet)."""
        col = User.__table__.columns["password_hash"]
        assert col.nullable is True

    def test_password_hash_column_length(self) -> None:
        """password_hash column must be at least 200 chars to hold Argon2 output."""
        col = User.__table__.columns["password_hash"]
        assert col.type.length >= 200


class TestUserModelInstantiation:
    """Verify User instances can be created with a password hash."""

    def test_user_can_be_instantiated_with_password_hash(self) -> None:
        """A User instance can hold a password hash produced by hash_password()."""
        hashed = hash_password("secretpassword")
        user = User(username="analyst01", password_hash=hashed)
        assert user.password_hash == hashed

    def test_stored_value_is_not_plaintext(self) -> None:
        """The value stored in password_hash must not equal the original password."""
        plaintext = "secretpassword"
        hashed = hash_password(plaintext)
        user = User(username="analyst01", password_hash=hashed)
        assert user.password_hash != plaintext

    def test_user_without_hash_is_valid_python_object(self) -> None:
        """A User with no password_hash (None) must be constructable — existing
        rows in the DB do not yet have a hash."""
        user = User(username="legacy_user")
        assert user.password_hash is None

    def test_existing_fields_still_work(self) -> None:
        """id, username, and created_at must continue to function normally."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        user = User(id=1, username="analyst01", created_at=now)
        assert user.id == 1
        assert user.username == "analyst01"
        assert user.created_at == now

    def test_correct_password_verifies_against_stored_hash(self) -> None:
        """A password verified against its own hash must succeed — simulates the
        future login check without requiring a live database."""
        from app.core.security import verify_password

        plaintext = "correctpassword"
        user = User(username="analyst01", password_hash=hash_password(plaintext))
        assert verify_password(plaintext, user.password_hash) is True

    def test_wrong_password_does_not_verify_against_stored_hash(self) -> None:
        """A wrong password verified against the stored hash must fail."""
        from app.core.security import verify_password

        user = User(username="analyst01", password_hash=hash_password("correctpassword"))
        assert verify_password("wrongpassword", user.password_hash) is False

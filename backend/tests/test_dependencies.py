"""Stage 5 tests — current authenticated user dependency.

Covers the reusable Bearer-token authentication dependency in
``app.api.dependencies.get_current_user``.

Each test exercises the dependency directly (unit style) or through a minimal
FastAPI app (FastAPI dependency integration).  No live PostgreSQL/Neo4j is
required — the SQLAlchemy session and the user lookup are mocked.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_db_returning(user: User | None) -> MagicMock:
    """Build a Mock session whose scalars(...).first() returns *user*."""
    mock_db = MagicMock()
    mock_db.scalars.return_value.first.return_value = user
    return mock_db


def _override_db(user: User | None):
    """Return a dependency-override generator for get_db_session."""
    mock_db = _mock_db_returning(user)

    def _gen():
        yield mock_db

    return _gen


def _bearer(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _make_user(user_id: int = 1, username: str = "testuser") -> User:
    return User(
        id=user_id,
        username=username,
        password_hash="not-a-real-argon2-hash",
    )


def _token_with_sub(sub) -> str:
    """Create a signed token carrying an arbitrary sub claim."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": sub,
            "iat": now,
            "exp": now + timedelta(minutes=30),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def _token_without_sub() -> str:
    """Create a signed token that is missing the sub claim entirely."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "iat": now,
            "exp": now + timedelta(minutes=30),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def _make_test_app() -> FastAPI:
    test_app = FastAPI()

    @test_app.get("/whoami")
    def whoami(current_user: User = Depends(get_current_user)) -> dict:
        return {"id": current_user.id, "username": current_user.username}

    @test_app.get("/compare")
    def compare(user_id: int, current_user: User = Depends(get_current_user)) -> dict:
        # user_id is client-supplied and must NOT influence authentication.
        return {
            "requested_id": user_id,
            "authenticated_id": current_user.id,
        }

    return test_app


# ---------------------------------------------------------------------------
# Unit tests — direct dependency calls
# ---------------------------------------------------------------------------


class TestGetCurrentUserUnit:
    def test_valid_bearer_token_returns_current_user(self) -> None:
        token = create_access_token(subject=42)
        user = _make_user(user_id=42, username="agent42")
        db = _mock_db_returning(user)

        result = get_current_user(credentials=_bearer(token), db=db)

        assert result is user
        assert result.id == 42
        assert result.username == "agent42"

    def test_missing_credentials_returns_401(self) -> None:
        db = _mock_db_returning(_make_user())

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=None, db=db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"

    def test_empty_bearer_token_returns_401(self) -> None:
        db = _mock_db_returning(_make_user())

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=_bearer(" "), db=db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"

    def test_invalid_jwt_returns_401(self) -> None:
        db = _mock_db_returning(_make_user())

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=_bearer("not.a.jwt"), db=db)

        assert exc_info.value.status_code == 401

    def test_expired_jwt_returns_401(self) -> None:
        token = create_access_token(subject=1, expires_delta=timedelta(seconds=-10))
        db = _mock_db_returning(_make_user())

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=_bearer(token), db=db)

        assert exc_info.value.status_code == 401

    def test_invalid_signature_returns_401(self) -> None:
        settings = get_settings()
        payload = {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
        token = jwt.encode(payload, "totally-wrong-secret", algorithm=settings.jwt_algorithm)
        db = _mock_db_returning(_make_user())

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=_bearer(token), db=db)

        assert exc_info.value.status_code == 401

    def test_missing_sub_returns_401(self) -> None:
        token = _token_without_sub()
        db = _mock_db_returning(_make_user())

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=_bearer(token), db=db)

        assert exc_info.value.status_code == 401

    def test_malformed_sub_returns_401(self) -> None:
        token = _token_with_sub("not-a-number")
        db = _mock_db_returning(_make_user())

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=_bearer(token), db=db)

        assert exc_info.value.status_code == 401

    def test_empty_sub_returns_401(self) -> None:
        token = _token_with_sub("")
        db = _mock_db_returning(_make_user())

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=_bearer(token), db=db)

        assert exc_info.value.status_code == 401

    def test_user_not_found_returns_401(self) -> None:
        token = create_access_token(subject=999)
        db = _mock_db_returning(None)

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=_bearer(token), db=db)

        assert exc_info.value.status_code == 401

    def test_nonexistent_user_message_is_generic(self) -> None:
        """The 401 body must not reveal whether the user used to exist."""
        token = create_access_token(subject=999)
        db = _mock_db_returning(None)

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=_bearer(token), db=db)

        assert exc_info.value.detail == "Could not validate credentials"

    def test_password_and_password_hash_never_leak(self) -> None:
        token = create_access_token(subject=7)
        user = _make_user(user_id=7)
        db = _mock_db_returning(user)

        result = get_current_user(credentials=_bearer(token), db=db)

        assert not hasattr(result, "password")
        assert result.password_hash is not None


# ---------------------------------------------------------------------------
# Integration tests — through FastAPI dependency injection
# ---------------------------------------------------------------------------


class TestGetCurrentUserIntegration:
    def test_valid_bearer_token_returns_user(self) -> None:
        test_app = _make_test_app()
        user = _make_user(user_id=11, username="integration")
        test_app.dependency_overrides[get_db_session] = _override_db(user)
        client = TestClient(test_app)

        token = create_access_token(subject=11)
        resp = client.get(
            "/whoami",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        assert resp.json() == {"id": 11, "username": "integration"}

    def test_missing_authorization_header_returns_401(self) -> None:
        test_app = _make_test_app()
        test_app.dependency_overrides[get_db_session] = _override_db(_make_user())
        client = TestClient(test_app)

        resp = client.get("/whoami")

        assert resp.status_code == 401
        assert resp.headers.get("WWW-Authenticate") == "Bearer"

    def test_malformed_authorization_header_returns_401(self) -> None:
        test_app = _make_test_app()
        test_app.dependency_overrides[get_db_session] = _override_db(_make_user())
        client = TestClient(test_app)

        resp = client.get(
            "/whoami",
            headers={"Authorization": "Bearer token extra words"},
        )

        assert resp.status_code == 401

    def test_wrong_scheme_returns_401(self) -> None:
        test_app = _make_test_app()
        test_app.dependency_overrides[get_db_session] = _override_db(_make_user())
        client = TestClient(test_app)

        resp = client.get(
            "/whoami",
            headers={"Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="},
        )

        assert resp.status_code == 401

    def test_invalid_jwt_returns_401(self) -> None:
        test_app = _make_test_app()
        test_app.dependency_overrides[get_db_session] = _override_db(_make_user())
        client = TestClient(test_app)

        resp = client.get(
            "/whoami",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )

        assert resp.status_code == 401

    def test_expired_jwt_returns_401(self) -> None:
        token = create_access_token(subject=1, expires_delta=timedelta(seconds=-10))
        test_app = _make_test_app()
        test_app.dependency_overrides[get_db_session] = _override_db(_make_user())
        client = TestClient(test_app)

        resp = client.get(
            "/whoami",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 401

    def test_jwt_referencing_non_existent_user_returns_401(self) -> None:
        token = create_access_token(subject=999)
        test_app = _make_test_app()
        test_app.dependency_overrides[get_db_session] = _override_db(None)
        client = TestClient(test_app)

        resp = client.get(
            "/whoami",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 401

    def test_identity_comes_from_jwt_subject_not_request_input(self) -> None:
        test_app = _make_test_app()
        user = _make_user(user_id=5, username="trusted-user")
        test_app.dependency_overrides[get_db_session] = _override_db(user)
        client = TestClient(test_app)

        token = create_access_token(subject=5)
        resp = client.get(
            "/compare?user_id=999",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        assert resp.json() == {"requested_id": 999, "authenticated_id": 5}

    def test_user_id_path_parameter_does_not_override_identity(self) -> None:
        """Client-supplied path parameters never replace the JWT subject."""
        test_app = FastAPI()

        @test_app.get("/users/{user_id}")
        def user_detail(user_id: int, current_user: User = Depends(get_current_user)) -> dict:
            return {"path_user_id": user_id, "authenticated_id": current_user.id}

        user = _make_user(user_id=3)
        test_app.dependency_overrides[get_db_session] = _override_db(user)
        client = TestClient(test_app)

        token = create_access_token(subject=3)
        resp = client.get(
            "/users/777",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        assert resp.json() == {"path_user_id": 777, "authenticated_id": 3}
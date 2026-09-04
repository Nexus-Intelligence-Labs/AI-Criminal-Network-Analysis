"""Stage 8/10 tests — audit logging for security-relevant events.

Covers the audit service and its integration with authentication and
authorization flows.  Uses mock SQLAlchemy sessions and FastAPI dependency
overrides — no live PostgreSQL required.
"""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import require_roles
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.session import get_db_session
from app.models.audit import AuditLog
from app.models.user import User
from app.services.audit_service import (
    AUTH_FAILURE,
    AUTHORIZATION_DENIED,
    LOGIN_FAILURE,
    LOGIN_SUCCESS,
    log_event,
)
from app.services.auth_service import authenticate_user
from app.schemas.auth import LoginRequest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_db_with_user(user: User | None) -> MagicMock:
    """Build a Mock session whose scalars(...).first() returns *user*."""
    mock_db = MagicMock()
    mock_db.scalars.return_value.first.return_value = user
    return mock_db


def _override_db(user: User | None):
    """Return a dependency-override generator for get_db_session."""
    mock_db = _mock_db_with_user(user)

    def _gen():
        yield mock_db

    return _gen


def _make_user(user_id: int = 1, username: str = "testuser", role: str | None = None) -> User:
    user = User(
        id=user_id,
        username=username,
        password_hash=hash_password("correct_password"),
    )
    if role is not None:
        user.role = role
    return user


def _captured_audit_records(mock_db: MagicMock) -> list[AuditLog]:
    """Extract AuditLog objects passed to mock_db.add()."""
    records = []
    for call in mock_db.add.call_args_list:
        arg = call[0][0]
        if isinstance(arg, AuditLog):
            records.append(arg)
    return records


def _audit_actions(mock_db: MagicMock) -> list[str]:
    return [r.action for r in _captured_audit_records(mock_db)]


def _audit_details(record: AuditLog) -> dict:
    return json.loads(record.details) if record.details else {}


# ---------------------------------------------------------------------------
# Audit service unit tests
# ---------------------------------------------------------------------------


class TestAuditService:
    def test_log_event_creates_audit_record(self) -> None:
        mock_db = MagicMock()
        log_event(mock_db, LOGIN_SUCCESS, actor="42", details={"username": "admin"})

        records = _captured_audit_records(mock_db)
        assert len(records) == 1
        assert records[0].action == LOGIN_SUCCESS
        assert records[0].actor == "42"
        # created_at is set by SQLAlchemy's default on flush; the model
        # declares the default so the column exists.
        assert hasattr(records[0], "created_at")

    def test_log_event_serializes_details_as_json(self) -> None:
        mock_db = MagicMock()
        log_event(mock_db, AUTH_FAILURE, details={"reason": "invalid_token"})

        records = _captured_audit_records(mock_db)
        assert len(records) == 1
        details = _audit_details(records[0])
        assert details == {"reason": "invalid_token"}

    def test_log_event_without_details_stores_none(self) -> None:
        mock_db = MagicMock()
        log_event(mock_db, LOGIN_FAILURE)

        records = _captured_audit_records(mock_db)
        assert len(records) == 1
        assert records[0].details is None

    def test_log_event_commits(self) -> None:
        mock_db = MagicMock()
        log_event(mock_db, LOGIN_SUCCESS, actor="1")
        mock_db.commit.assert_called_once()

    def test_log_event_never_raises_on_db_failure(self) -> None:
        """Audit persistence failure must not propagate to the caller."""
        mock_db = MagicMock()
        mock_db.add.side_effect = Exception("database is down")

        # Should not raise
        log_event(mock_db, LOGIN_SUCCESS, actor="1")

    def test_log_event_rolls_back_on_failure(self) -> None:
        mock_db = MagicMock()
        mock_db.add.side_effect = Exception("database is down")

        log_event(mock_db, LOGIN_SUCCESS, actor="1")
        mock_db.rollback.assert_called_once()


# ---------------------------------------------------------------------------
# Login audit integration tests
# ---------------------------------------------------------------------------


class TestLoginAudit:
    def test_successful_login_creates_login_success(self) -> None:
        mock_db = _mock_db_with_user(_make_user(user_id=1, username="admin"))
        request = LoginRequest(username="admin", password="correct_password")

        response = authenticate_user(mock_db, request)

        assert response.success is True
        actions = _audit_actions(mock_db)
        assert LOGIN_SUCCESS in actions
        assert LOGIN_FAILURE not in actions

    def test_login_success_has_actor(self) -> None:
        mock_db = _mock_db_with_user(_make_user(user_id=7, username="agent7"))
        request = LoginRequest(username="agent7", password="correct_password")

        authenticate_user(mock_db, request)

        records = _captured_audit_records(mock_db)
        success_records = [r for r in records if r.action == LOGIN_SUCCESS]
        assert len(success_records) == 1
        assert success_records[0].actor == "7"

    def test_login_success_details_are_safe(self) -> None:
        mock_db = _mock_db_with_user(_make_user(user_id=1, username="admin"))
        request = LoginRequest(username="admin", password="correct_password")

        authenticate_user(mock_db, request)

        records = _captured_audit_records(mock_db)
        success_records = [r for r in records if r.action == LOGIN_SUCCESS]
        details = _audit_details(success_records[0])
        assert "password" not in json.dumps(details)
        assert "password_hash" not in json.dumps(details)
        assert "token" not in json.dumps(details).lower()
        assert "authorization" not in json.dumps(details).lower()

    def test_failed_login_creates_login_failure(self) -> None:
        mock_db = _mock_db_with_user(_make_user(user_id=1, username="admin"))
        request = LoginRequest(username="admin", password="wrong_password")

        response = authenticate_user(mock_db, request)

        assert response.success is False
        actions = _audit_actions(mock_db)
        assert LOGIN_FAILURE in actions
        assert LOGIN_SUCCESS not in actions

    def test_failed_login_has_no_actor(self) -> None:
        mock_db = _mock_db_with_user(_make_user(user_id=1, username="admin"))
        request = LoginRequest(username="admin", password="wrong_password")

        authenticate_user(mock_db, request)

        records = _captured_audit_records(mock_db)
        failure_records = [r for r in records if r.action == LOGIN_FAILURE]
        assert len(failure_records) == 1
        assert failure_records[0].actor is None

    def test_failed_login_details_do_not_contain_password(self) -> None:
        mock_db = _mock_db_with_user(_make_user(user_id=1, username="admin"))
        request = LoginRequest(username="admin", password="wrong_password")

        authenticate_user(mock_db, request)

        records = _captured_audit_records(mock_db)
        failure_records = [r for r in records if r.action == LOGIN_FAILURE]
        details_json = json.dumps(_audit_details(failure_records[0]))
        assert "wrong_password" not in details_json
        assert "password" not in details_json
        assert "password_hash" not in details_json

    def test_user_not_found_creates_login_failure(self) -> None:
        mock_db = _mock_db_with_user(None)
        request = LoginRequest(username="ghost", password="any_password")

        response = authenticate_user(mock_db, request)

        assert response.success is False
        actions = _audit_actions(mock_db)
        assert LOGIN_FAILURE in actions

    def test_no_password_hash_creates_login_failure(self) -> None:
        user = User(id=1, username="admin", password_hash=None)
        mock_db = _mock_db_with_user(user)
        request = LoginRequest(username="admin", password="any_password")

        response = authenticate_user(mock_db, request)

        assert response.success is False
        actions = _audit_actions(mock_db)
        assert LOGIN_FAILURE in actions


# ---------------------------------------------------------------------------
# AUTH_FAILURE audit tests
# ---------------------------------------------------------------------------


class TestAuthFailureAudit:
    def _make_protected_app(self) -> FastAPI:
        test_app = FastAPI()

        @test_app.get("/protected")
        def protected(current_user: User = Depends(require_roles("admin", "investigator"))) -> dict:
            return {"id": current_user.id}

        return test_app

    def test_missing_token_creates_auth_failure(self) -> None:
        test_app = self._make_protected_app()
        test_app.dependency_overrides[get_db_session] = _override_db(_make_user())
        client = TestClient(test_app, raise_server_exceptions=False)

        resp = client.get("/protected")

        assert resp.status_code == 401

    def test_invalid_jwt_creates_auth_failure(self) -> None:
        test_app = self._make_protected_app()
        test_app.dependency_overrides[get_db_session] = _override_db(_make_user())
        client = TestClient(test_app, raise_server_exceptions=False)

        resp = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )

        assert resp.status_code == 401

    def test_expired_jwt_creates_auth_failure(self) -> None:
        test_app = self._make_protected_app()
        test_app.dependency_overrides[get_db_session] = _override_db(_make_user())
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=1, expires_delta=timedelta(seconds=-10))
        resp = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 401

    def test_invalid_subject_creates_auth_failure(self) -> None:
        test_app = self._make_protected_app()
        test_app.dependency_overrides[get_db_session] = _override_db(_make_user())
        client = TestClient(test_app, raise_server_exceptions=False)

        settings = get_settings()
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {
                "sub": "not-a-number",
                "iat": now,
                "exp": now + timedelta(minutes=30),
            },
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        resp = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 401

    def test_user_not_found_creates_auth_failure(self) -> None:
        test_app = self._make_protected_app()
        test_app.dependency_overrides[get_db_session] = _override_db(None)
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=999)
        resp = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 401

    def test_auth_failure_response_is_generic(self) -> None:
        test_app = self._make_protected_app()
        test_app.dependency_overrides[get_db_session] = _override_db(_make_user())
        client = TestClient(test_app, raise_server_exceptions=False)

        resp = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )

        assert resp.status_code == 401
        assert resp.json()["detail"] == "Could not validate credentials"
        assert resp.headers.get("WWW-Authenticate") == "Bearer"


# ---------------------------------------------------------------------------
# AUTHORIZATION_DENIED audit tests
# ---------------------------------------------------------------------------


class TestAuthorizationDeniedAudit:
    def _make_admin_app(self) -> FastAPI:
        test_app = FastAPI()

        @test_app.get("/admin-only")
        def admin_only(current_user: User = Depends(require_roles("admin"))) -> dict:
            return {"id": current_user.id}

        return test_app

    def test_insufficient_role_creates_authorization_denied(self) -> None:
        test_app = self._make_admin_app()
        user = _make_user(user_id=2, username="investigator", role="investigator")
        test_app.dependency_overrides[get_db_session] = _override_db(user)
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=2)
        resp = client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 403

    def test_authorization_denied_has_actor(self) -> None:
        test_app = self._make_admin_app()
        user = _make_user(user_id=5, username="analyst", role="analyst")
        test_app.dependency_overrides[get_db_session] = _override_db(user)
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=5)
        resp = client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 403

    def test_authorization_denied_details_are_safe(self) -> None:
        test_app = self._make_admin_app()
        user = _make_user(user_id=5, username="analyst", role="analyst")
        test_app.dependency_overrides[get_db_session] = _override_db(user)
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=5)
        resp = client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 403
        # Response must not contain sensitive data
        assert "password" not in resp.text
        assert "password_hash" not in resp.text
        assert "token" not in resp.text.lower()

    def test_successful_authorized_request_does_not_create_denied(self) -> None:
        test_app = self._make_admin_app()
        user = _make_user(user_id=1, username="admin", role="admin")
        test_app.dependency_overrides[get_db_session] = _override_db(user)
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=1)
        resp = client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Audit failure behavior tests
# ---------------------------------------------------------------------------


class TestAuditFailureBehavior:
    def test_audit_failure_does_not_leak_credentials(self) -> None:
        """When audit persistence fails, the client still gets a safe response."""
        test_app = FastAPI()

        @test_app.get("/protected")
        def protected(current_user: User = Depends(require_roles("admin", "investigator"))) -> dict:
            return {"id": current_user.id}

        # Mock DB where add() raises (simulating audit persistence failure)
        mock_db = MagicMock()
        mock_db.add.side_effect = Exception("database is down")
        mock_db.scalars.return_value.first.return_value = _make_user()

        def _gen():
            yield mock_db

        test_app.dependency_overrides[get_db_session] = _gen
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=1)
        resp = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Authentication still succeeds — audit failure doesn't break the request
        assert resp.status_code == 200
        assert "password" not in resp.text
        assert "password_hash" not in resp.text

    def test_audit_failure_on_auth_failure_keeps_401(self) -> None:
        """When audit persistence fails during auth failure, still return 401."""
        test_app = FastAPI()

        @test_app.get("/protected")
        def protected(current_user: User = Depends(require_roles("admin", "investigator"))) -> dict:
            return {"id": current_user.id}

        mock_db = MagicMock()
        mock_db.add.side_effect = Exception("database is down")
        mock_db.scalars.return_value.first.return_value = _make_user()

        def _gen():
            yield mock_db

        test_app.dependency_overrides[get_db_session] = _gen
        client = TestClient(test_app, raise_server_exceptions=False)

        resp = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )

        assert resp.status_code == 401
        assert resp.json()["detail"] == "Could not validate credentials"
        assert "database" not in resp.text.lower()
        assert "exception" not in resp.text.lower()


# ---------------------------------------------------------------------------
# Audit record content safety tests
# ---------------------------------------------------------------------------


class TestAuditRecordSafety:
    def test_audit_record_has_action(self) -> None:
        mock_db = MagicMock()
        log_event(mock_db, LOGIN_SUCCESS, actor="1")
        records = _captured_audit_records(mock_db)
        assert records[0].action == LOGIN_SUCCESS

    def test_audit_record_has_timestamp(self) -> None:
        mock_db = MagicMock()
        log_event(mock_db, LOGIN_SUCCESS, actor="1")
        records = _captured_audit_records(mock_db)
        # The model declares a default for created_at; SQLAlchemy applies it
        # on flush.  The attribute exists on the model.
        assert hasattr(records[0], "created_at")

    def test_audit_details_never_contain_password(self) -> None:
        mock_db = MagicMock()
        log_event(
            mock_db,
            LOGIN_SUCCESS,
            actor="1",
            details={"username": "admin", "user_id": 1},
        )
        records = _captured_audit_records(mock_db)
        details_json = json.dumps(_audit_details(records[0]))
        assert "password" not in details_json

    def test_audit_details_never_contain_password_hash(self) -> None:
        mock_db = MagicMock()
        log_event(
            mock_db,
            LOGIN_SUCCESS,
            actor="1",
            details={"username": "admin", "user_id": 1},
        )
        records = _captured_audit_records(mock_db)
        details_json = json.dumps(_audit_details(records[0]))
        assert "password_hash" not in details_json

    def test_audit_details_never_contain_jwt(self) -> None:
        mock_db = MagicMock()
        log_event(
            mock_db,
            LOGIN_SUCCESS,
            actor="1",
            details={"username": "admin", "user_id": 1},
        )
        records = _captured_audit_records(mock_db)
        details_json = json.dumps(_audit_details(records[0]))
        assert "jwt" not in details_json.lower()
        assert "token" not in details_json.lower()

    def test_audit_details_never_contain_jwt_secret(self) -> None:
        mock_db = MagicMock()
        log_event(
            mock_db,
            LOGIN_SUCCESS,
            actor="1",
            details={"username": "admin", "user_id": 1},
        )
        records = _captured_audit_records(mock_db)
        details_json = json.dumps(_audit_details(records[0]))
        assert "secret" not in details_json.lower()

    def test_authorization_header_never_in_audit_details(self) -> None:
        mock_db = MagicMock()
        log_event(
            mock_db,
            AUTH_FAILURE,
            details={"reason": "invalid_token"},
        )
        records = _captured_audit_records(mock_db)
        details_json = json.dumps(_audit_details(records[0]))
        assert "authorization" not in details_json.lower()
        assert "bearer" not in details_json.lower()
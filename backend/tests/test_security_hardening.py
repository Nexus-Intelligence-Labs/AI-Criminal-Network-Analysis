"""Stage 9/10 tests — security hardening and configuration validation.

Covers:
- JWT configuration validation (secret, algorithm, expiration)
- JWT security guarantees (signature, expiration, subject, algorithm control)
- Sensitive data regression (no passwords, hashes, secrets in responses)
- 401 vs 403 distinction stability
- Public endpoint regression
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import require_roles
from app.core.config import (
    ALLOWED_JWT_ALGORITHMS,
    INSECURE_PLACEHOLDER_SECRETS,
    MAX_JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    Settings,
)
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    hash_password,
    verify_token,
)
from app.db.session import get_db_session
from app.models.user import User
from app.services.auth_service import authenticate_user
from app.schemas.auth import LoginRequest


# ---------------------------------------------------------------------------
# Configuration validation tests
# ---------------------------------------------------------------------------


class TestJWTConfigValidation:
    def test_empty_jwt_secret_rejected(self) -> None:
        with pytest.raises(ValueError, match="JWT_SECRET must not be empty"):
            Settings(jwt_secret="", app_env="development")

    def test_whitespace_jwt_secret_rejected(self) -> None:
        with pytest.raises(ValueError, match="JWT_SECRET must not be empty"):
            Settings(jwt_secret="   ", app_env="development")

    def test_short_jwt_secret_rejected(self) -> None:
        with pytest.raises(ValueError, match="JWT_SECRET must be at least 32 bytes"):
            Settings(jwt_secret="a" * 31, app_env="development")

    def test_32_byte_jwt_secret_accepted(self) -> None:
        secret = "a" * 32
        settings = Settings(jwt_secret=secret, app_env="development")
        assert settings.jwt_secret == secret

    def test_placeholder_secret_rejected_in_production(self) -> None:
        with pytest.raises(ValueError, match="insecure placeholder"):
            Settings(
                jwt_secret="change_me_to_a_longer_production_secret",
                app_env="production",
            )

    def test_placeholder_secret_allowed_in_development(self) -> None:
        # Development may use a placeholder; production must not.
        secret = "change_me_to_a_longer_production_secret"
        settings = Settings(jwt_secret=secret, app_env="development")
        assert settings.jwt_secret == secret

    def test_invalid_algorithm_rejected(self) -> None:
        with pytest.raises(ValueError, match="JWT_ALGORITHM"):
            Settings(jwt_secret="test-secret-32-bytes-long!!!!!!!", jwt_algorithm="HS512")

    def test_valid_algorithm_accepted(self) -> None:
        settings = Settings(jwt_secret="test-secret-32-bytes-long!!!!!!!", jwt_algorithm="HS256")
        assert settings.jwt_algorithm == "HS256"

    def test_negative_expiration_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be positive"):
            Settings(
                jwt_secret="test-secret-32-bytes-long!!!!!!!",
                jwt_access_token_expire_minutes=-5,
            )

    def test_zero_expiration_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be positive"):
            Settings(
                jwt_secret="test-secret-32-bytes-long!!!!!!!",
                jwt_access_token_expire_minutes=0,
            )

    def test_absurdly_large_expiration_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not exceed"):
            Settings(
                jwt_secret="test-secret-32-bytes-long!!!!!!!",
                jwt_access_token_expire_minutes=MAX_JWT_ACCESS_TOKEN_EXPIRE_MINUTES + 1,
            )

    def test_reasonable_expiration_accepted(self) -> None:
        settings = Settings(
            jwt_secret="test-secret-32-bytes-long!!!!!!!",
            jwt_access_token_expire_minutes=30,
        )
        assert settings.jwt_access_token_expire_minutes == 30

    def test_allowed_algorithms_contains_hs256(self) -> None:
        assert "HS256" in ALLOWED_JWT_ALGORITHMS

    def test_placeholder_secrets_are_known(self) -> None:
        assert "change_me" in INSECURE_PLACEHOLDER_SECRETS


# ---------------------------------------------------------------------------
# JWT security guarantee tests
# ---------------------------------------------------------------------------


class TestJWTSecurityGuarantees:
    def test_signature_verification_enabled(self) -> None:
        """A token signed with a different secret must be rejected."""
        settings = Settings(jwt_secret="test-secret-32-bytes-long!!!!!!!")
        tampered = jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
            "wrong-secret-32-bytes-long!!",
            algorithm="HS256",
        )
        with pytest.raises(InvalidTokenError):
            verify_token(tampered)

    def test_expiration_enforced(self) -> None:
        token = create_access_token(subject=1, expires_delta=timedelta(seconds=-10))
        with pytest.raises(InvalidTokenError):
            verify_token(token)

    def test_subject_required(self) -> None:
        settings = Settings(jwt_secret="test-secret-32-bytes-long!!!!!!!")
        token = jwt.encode(
            {"exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
            settings.jwt_secret,
            algorithm="HS256",
        )
        with pytest.raises(InvalidTokenError):
            verify_token(token)

    def test_server_controls_algorithm(self) -> None:
        """A token signed with a non-allowed algorithm must be rejected."""
        settings = Settings(jwt_secret="test-secret-32-bytes-long!!!!!!!")
        token = jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
            settings.jwt_secret,
            algorithm="HS512",
        )
        with pytest.raises(InvalidTokenError):
            verify_token(token)

    def test_no_sensitive_claims_in_jwt(self) -> None:
        token = create_access_token(subject=1)
        payload = verify_token(token)
        assert "password" not in payload
        assert "password_hash" not in payload
        assert "email" not in payload
        assert "phone" not in payload
        assert "role" not in payload


# ---------------------------------------------------------------------------
# Sensitive data regression tests
# ---------------------------------------------------------------------------


class TestSensitiveDataRegression:
    def test_internal_login_error_is_audited_without_details(self) -> None:
        mock_db = MagicMock()
        mock_db.scalars.side_effect = RuntimeError("database details")
        request = LoginRequest(username="admin", password="correct_password")

        with patch("app.services.auth_service.log_event") as audit_log:
            response = authenticate_user(mock_db, request)

        assert response.success is False
        assert response.message == "Authentication failed due to an internal error"
        audit_log.assert_called_once_with(
            mock_db,
            "LOGIN_FAILURE",
            actor=None,
            details={"reason": "internal_error"},
        )

    def test_login_response_has_no_password(self) -> None:
        mock_db = MagicMock()
        user = User(id=1, username="admin", password_hash=hash_password("correct_password"))
        mock_db.scalars.return_value.first.return_value = user

        request = LoginRequest(username="admin", password="correct_password")
        response = authenticate_user(mock_db, request)

        assert response.success is True
        assert "password" not in response.model_dump()
        assert "password_hash" not in response.model_dump()

    def test_login_response_has_no_jwt_secret(self) -> None:
        mock_db = MagicMock()
        user = User(id=1, username="admin", password_hash=hash_password("correct_password"))
        mock_db.scalars.return_value.first.return_value = user

        request = LoginRequest(username="admin", password="correct_password")
        response = authenticate_user(mock_db, request)

        assert response.success is True
        response_json = str(response.model_dump())
        assert "jwt_secret" not in response_json.lower()
        assert "secret" not in response_json.lower()

    def test_auth_failure_response_has_no_internal_details(self) -> None:
        test_app = FastAPI()

        @test_app.get("/protected")
        def protected(current_user: User = Depends(require_roles("admin", "investigator"))) -> dict:
            return {"id": current_user.id}

        mock_db = MagicMock()
        mock_db.scalars.return_value.first.return_value = None

        def _gen():
            yield mock_db

        test_app.dependency_overrides[get_db_session] = _gen
        client = TestClient(test_app, raise_server_exceptions=False)

        resp = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )

        assert resp.status_code == 401
        assert "invalid_token" not in resp.text
        assert "expired" not in resp.text
        assert "signature" not in resp.text
        assert "secret" not in resp.text.lower()
        assert "jwt" not in resp.text.lower()


# ---------------------------------------------------------------------------
# 401 vs 403 distinction tests
# ---------------------------------------------------------------------------


class TestStatusDistinction:
    def _make_app(self) -> FastAPI:
        test_app = FastAPI()

        @test_app.get("/admin-only")
        def admin_only(current_user: User = Depends(require_roles("admin"))) -> dict:
            return {"id": current_user.id}

        return test_app

    def _make_admin_user(self, user_id: int = 1) -> User:
        user = User(id=user_id, username="admin", password_hash="hash")
        user.role = "admin"
        return user

    def _make_investigator_user(self, user_id: int = 2) -> User:
        user = User(id=user_id, username="investigator", password_hash="hash")
        user.role = "investigator"
        return user

    def _override(self, user: User | None):
        mock_db = MagicMock()
        mock_db.scalars.return_value.first.return_value = user

        def _gen():
            yield mock_db

        return _gen

    def test_no_token_returns_401(self) -> None:
        test_app = self._make_app()
        test_app.dependency_overrides[get_db_session] = self._override(
            self._make_admin_user()
        )
        client = TestClient(test_app, raise_server_exceptions=False)

        resp = client.get("/admin-only")

        assert resp.status_code == 401

    def test_invalid_token_returns_401(self) -> None:
        test_app = self._make_app()
        test_app.dependency_overrides[get_db_session] = self._override(
            self._make_admin_user()
        )
        client = TestClient(test_app, raise_server_exceptions=False)

        resp = client.get(
            "/admin-only",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )

        assert resp.status_code == 401

    def test_expired_token_returns_401(self) -> None:
        test_app = self._make_app()
        test_app.dependency_overrides[get_db_session] = self._override(
            self._make_admin_user()
        )
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=1, expires_delta=timedelta(seconds=-10))
        resp = client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 401

    def test_user_missing_returns_401(self) -> None:
        test_app = self._make_app()
        test_app.dependency_overrides[get_db_session] = self._override(None)
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=999)
        resp = client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 401

    def test_insufficient_role_returns_403(self) -> None:
        test_app = self._make_app()
        test_app.dependency_overrides[get_db_session] = self._override(
            self._make_investigator_user()
        )
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=2)
        resp = client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 403

    def test_sufficient_role_succeeds(self) -> None:
        test_app = self._make_app()
        test_app.dependency_overrides[get_db_session] = self._override(
            self._make_admin_user()
        )
        client = TestClient(test_app, raise_server_exceptions=False)

        token = create_access_token(subject=1)
        resp = client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Public endpoint regression tests
# ---------------------------------------------------------------------------


class TestPublicEndpointRegression:
    def test_health_remains_public(self) -> None:
        from app.main import app

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/health")

        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_login_remains_public(self) -> None:
        from app.main import app

        mock_db = MagicMock()
        mock_db.scalars.return_value.first.return_value = None

        def _gen():
            yield mock_db

        app.dependency_overrides[get_db_session] = _gen
        client = TestClient(app, raise_server_exceptions=False)

        resp = client.post(
            "/api/auth/login",
            json={"username": "ghost", "password": "wrong"},
        )

        assert resp.status_code == 401  # auth failure, not protection
        app.dependency_overrides.clear()
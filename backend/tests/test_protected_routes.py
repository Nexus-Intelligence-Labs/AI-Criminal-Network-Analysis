"""Stage 7 tests — protected API endpoint integration.

Verifies that application data endpoints require a valid Bearer JWT while the
health and login endpoints remain public.
"""

from datetime import timedelta
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.models.user import User


# Protected route inventory covered here.  Each stub returns the same dict,
# and the route is exercised through the real API router.


USER = User(
    id=1,
    username="testuser",
    password_hash="not-a-real-argon2-hash",
)


def _override_db(user: User | None):
    mock_db = MagicMock()
    mock_db.scalars.return_value.first.return_value = user

    def _gen():
        yield mock_db

    return _gen


def _valid_token(user_id: int = 1) -> str:
    return create_access_token(subject=user_id)


PROTECTED_GET_ENDPOINTS = [
    "/api/entities/",
    "/api/relationships/",
    "/api/search/",
    "/api/alerts/",
    "/api/cases/",
    "/api/timelines/",
    "/api/evidence/",
    "/api/analytics/",
]

GRAPH_GET_ENDPOINTS = [
    "/api/graph/1",
    "/api/graph/neighbors/2",
    "/api/graph/shortest-path?source=1&target=2",
]


class TestProtectedRoutes:
    def setup_method(self):
        app.dependency_overrides.clear()

    def test_all_protected_endpoints_require_auth(self):
        """Every protected endpoint returns 401 without a Bearer token."""
        for endpoint in PROTECTED_GET_ENDPOINTS + GRAPH_GET_ENDPOINTS:
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(endpoint)
            assert resp.status_code == 401, (
                f"{endpoint} should require authentication; got {resp.status_code}"
            )

    def test_all_protected_endpoints_reject_invalid_jwt(self):
        """Every protected endpoint returns 401 with an invalid JWT."""
        for endpoint in PROTECTED_GET_ENDPOINTS + GRAPH_GET_ENDPOINTS:
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                endpoint,
                headers={"Authorization": "Bearer invalid.jwt.token"},
            )
            assert resp.status_code == 401, (
                f"{endpoint} should reject invalid JWT; got {resp.status_code}"
            )

    def test_all_protected_endpoints_accept_valid_jwt(self):
        """Every protected endpoint proceeds past authentication with a valid JWT."""
        app.dependency_overrides[get_db_session] = _override_db(USER)
        client = TestClient(app, raise_server_exceptions=False)

        token = _valid_token()
        for endpoint in PROTECTED_GET_ENDPOINTS:
            resp = client.get(
                endpoint,
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200, (
                f"{endpoint} should succeed with a valid JWT; got {resp.status_code}"
            )

    def test_graph_endpoints_accept_valid_jwt(self):
        """Graph endpoints proceed past authentication (service may still fail)."""
        app.dependency_overrides[get_db_session] = _override_db(USER)
        client = TestClient(app, raise_server_exceptions=False)

        for endpoint in GRAPH_GET_ENDPOINTS:
            resp = client.get(
                endpoint,
                headers={"Authorization": f"Bearer {_valid_token()}"},
            )
            # 401/403 would mean auth failed.  Any other status proves the
            # request passed the authentication gate and reached the service.
            assert resp.status_code not in (401, 403), (
                f"{endpoint} should proceed past auth; got {resp.status_code}"
            )

    def test_expired_jwt_rejected_on_protected_routes(self):
        client = TestClient(app, raise_server_exceptions=False)
        token = create_access_token(subject=1, expires_delta=timedelta(seconds=-10))

        resp = client.get(
            "/api/entities/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 401


class TestPublicRoutes:
    def setup_method(self):
        app.dependency_overrides.clear()

    def test_login_remains_public(self):
        """POST /api/auth/login is reachable without any credentials."""
        app.dependency_overrides[get_db_session] = _override_db(None)
        client = TestClient(app, raise_server_exceptions=False)

        resp = client.post(
            "/api/auth/login",
            json={"username": "ghost", "password": "wrong"},
        )

        assert resp.status_code == 401  # authentication failure, not protection

    def test_health_remains_public(self):
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/health")

        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
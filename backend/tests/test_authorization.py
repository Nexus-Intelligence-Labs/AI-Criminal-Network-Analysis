"""Stage 6 tests — role-based authorization dependency.

Covers ``app.api.dependencies.require_role`` / ``require_roles``.

The current User model does NOT persist a role column and the repository has
no established database migration strategy, so role storage is not added to
the schema in this stage.  The authorization abstraction is tested by setting
a ``role`` attribute on User instances in tests (simulating a future mapped
column or an equivalent server-side source), with the default role applied
when no role is present.

No live PostgreSQL/Neo4j is required — the SQLAlchemy session and the User
lookup are mocked.
"""

from typing import Callable
from unittest.mock import MagicMock

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import (
    DEFAULT_USER_ROLE,
    get_user_role,
    require_role,
    require_roles,
)
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_user_with_role(user_id: int, role: str | None) -> User:
    user = User(
        id=user_id,
        username=f"user{user_id}",
        password_hash="not-a-real-argon2-hash",
    )
    if role is not None:
        user.role = role
    return user


def _override_db_with_user(user: User | None):
    mock_db = MagicMock()
    mock_db.scalars.return_value.first.return_value = user

    def _gen():
        yield mock_db

    return _gen


def _app_with_guard(guard: Callable) -> FastAPI:
    test_app = FastAPI()

    @test_app.get("/guarded")
    def guarded(current_user: User = Depends(guard)) -> dict:
        return {"id": current_user.id}

    return test_app


def _get_client_for_user(user: User | None) -> TestClient:
    """Return a client whose db lookup returns *user* for any valid JWT."""
    test_app = _app_with_guard(require_roles("admin", "investigator"))
    test_app.dependency_overrides[get_db_session] = _override_db_with_user(user)
    return TestClient(test_app)


# ---------------------------------------------------------------------------
# get_user_role unit tests
# ---------------------------------------------------------------------------


class TestGetUserRole:
    def test_role_attribute_is_used_when_present(self) -> None:
        user = _make_user_with_role(user_id=1, role="admin")
        assert get_user_role(user) == "admin"

    def test_default_role_when_no_role_attribute(self) -> None:
        user = _make_user_with_role(user_id=1, role=None)
        assert get_user_role(user) == DEFAULT_USER_ROLE

    def test_role_is_always_returned_as_string(self) -> None:
        user = _make_user_with_role(user_id=1, role="analyst")
        assert isinstance(get_user_role(user), str)


# ---------------------------------------------------------------------------
# Authorization dependency tests
# ---------------------------------------------------------------------------


class TestRequireRoles:
    """Role-bearing users against role-restricted guards."""

    def test_authorized_role_succeeds(self) -> None:
        test_app = _app_with_guard(require_role("admin"))
        user = _make_user_with_role(user_id=1, role="admin")
        test_app.dependency_overrides[get_db_session] = _override_db_with_user(user)
        client = TestClient(test_app)

        token = create_access_token(subject=1)
        resp = client.get("/guarded", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        assert resp.json() == {"id": 1}

    def test_unauthorized_role_returns_403(self) -> None:
        test_app = _app_with_guard(require_role("admin"))
        user = _make_user_with_role(user_id=2, role="investigator")
        test_app.dependency_overrides[get_db_session] = _override_db_with_user(user)
        client = TestClient(test_app)

        token = create_access_token(subject=2)
        resp = client.get("/guarded", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 403
        assert resp.json()["detail"] == "Insufficient permissions"

    def test_unauthenticated_request_returns_401_before_role_check(self) -> None:
        test_app = _app_with_guard(require_role("admin"))
        user = _make_user_with_role(user_id=5, role="admin")
        test_app.dependency_overrides[get_db_session] = _override_db_with_user(user)
        client = TestClient(test_app)

        resp = client.get("/guarded")  # no Authorization header

        assert resp.status_code == 401

    def test_multiple_allowed_roles_succeed(self) -> None:
        for role in ("admin", "investigator"):
            test_app = _app_with_guard(require_roles("admin", "investigator"))
            user = _make_user_with_role(user_id=10, role=role)
            test_app.dependency_overrides[get_db_session] = _override_db_with_user(user)
            client = TestClient(test_app)

            token = create_access_token(subject=10)
            resp = client.get("/guarded", headers={"Authorization": f"Bearer {token}"})

            assert resp.status_code == 200

    def test_role_check_depends_on_authenticated_user(self) -> None:
        """The role comes from the server-side user record, never the request."""
        test_app = _app_with_guard(require_roles("admin"))

        # Client sends a role in the query string and a user_id in the body,
        # but the server-side user has role=investigator, so access is denied.
        user = _make_user_with_role(user_id=6, role="investigator")
        test_app.dependency_overrides[get_db_session] = _override_db_with_user(user)
        client = TestClient(test_app)

        token = create_access_token(subject=6)
        resp = client.get(
            "/guarded?role=admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 403

    def test_invalid_jwt_cannot_bypass_authorization(self) -> None:
        test_app = _app_with_guard(require_roles("admin"))
        test_app.dependency_overrides[get_db_session] = _override_db_with_user(
            _make_user_with_role(user_id=7, role="admin")
        )
        client = TestClient(test_app)

        resp = client.get(
            "/guarded",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )

        assert resp.status_code == 401


class TestRequireRole:
    def test_require_role_is_equivalent_to_require_roles_single(self) -> None:
        user = _make_user_with_role(user_id=8, role="admin")
        apps = [
            _app_with_guard(require_roles("admin")),
            _app_with_guard(require_role("admin")),
        ]

        for test_app in apps:
            test_app.dependency_overrides[get_db_session] = _override_db_with_user(user)
            client = TestClient(test_app)
            token = create_access_token(subject=8)
            resp = client.get("/guarded", headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code == 200


class TestDefaultRoleAuthorization:
    """Users without a role attribute receive the default investigator role."""

    def test_default_role_allows_investigator_guard(self) -> None:
        user = _make_user_with_role(user_id=3, role=None)
        client = _get_client_for_user(user)

        token = create_access_token(subject=3)
        resp = client.get("/guarded", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        assert resp.json() == {"id": 3}

    def test_default_role_denied_when_admin_required(self) -> None:
        test_app = _app_with_guard(require_role("admin"))
        user = _make_user_with_role(user_id=4, role=None)  # default → investigator
        test_app.dependency_overrides[get_db_session] = _override_db_with_user(user)
        client = TestClient(test_app)

        token = create_access_token(subject=4)
        resp = client.get("/guarded", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 403
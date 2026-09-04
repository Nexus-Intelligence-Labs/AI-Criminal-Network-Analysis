import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.auth import LoginRequest
from app.services.auth_service import authenticate_user
from app.core.security import hash_password, verify_token
from app.models.user import User

# --- UNIT TESTS FOR AUTH SERVICE (using mock DB Session) ---

def test_authenticate_user_success():
    """Correct username and password succeeds."""
    mock_session = MagicMock()
    
    mock_user = User(
        id=1,
        username="admin",
        password_hash=hash_password("correct_password")
    )
    
    # Mock the SQLAlchemy select result
    mock_session.scalars.return_value.first.return_value = mock_user
    
    request = LoginRequest(username="admin", password="correct_password")
    response = authenticate_user(mock_session, request)
    
    assert response.success is True
    assert response.user_id == 1
    assert "successful" in response.message.lower()
    assert isinstance(response.access_token, str)
    assert response.token_type == "bearer"
    
    # Verify the token is a valid JWT with the correct subject
    payload = verify_token(response.access_token)
    assert payload["sub"] == "1"
    assert "exp" in payload
    
    # Ensure sensitive fields are never in the response schema
    assert not hasattr(response, "password")
    assert not hasattr(response, "password_hash")

def test_authenticate_user_wrong_password():
    """Correct username with incorrect password fails."""
    mock_session = MagicMock()
    
    mock_user = User(
        id=1,
        username="admin",
        password_hash=hash_password("correct_password")
    )
    mock_session.scalars.return_value.first.return_value = mock_user
    
    request = LoginRequest(username="admin", password="wrong_password")
    response = authenticate_user(mock_session, request)
    
    assert response.success is False
    assert response.user_id is None
    assert response.access_token is None
    assert "invalid" in response.message.lower()

def test_authenticate_user_not_found():
    """Nonexistent username fails safely."""
    mock_session = MagicMock()
    mock_session.scalars.return_value.first.return_value = None
    
    request = LoginRequest(username="ghost", password="any_password")
    response = authenticate_user(mock_session, request)
    
    assert response.success is False
    assert response.user_id is None
    assert response.access_token is None
    assert "invalid" in response.message.lower()

def test_authenticate_user_no_password_hash():
    """User exists but password_hash is None."""
    mock_session = MagicMock()
    
    mock_user = User(
        id=1,
        username="admin",
        password_hash=None
    )
    mock_session.scalars.return_value.first.return_value = mock_user
    
    request = LoginRequest(username="admin", password="any_password")
    response = authenticate_user(mock_session, request)
    
    assert response.success is False
    assert response.user_id is None
    assert response.access_token is None
    assert "invalid" in response.message.lower()


# --- API TESTS (Requires mocked DB dependency in FastAPI) ---

def test_login_api_success():
    """Test the /api/auth/login endpoint."""
    client = TestClient(app)
    
    # We will override the dependency for DB session
    from app.db.session import get_db_session
    
    def override_get_db_session():
        mock_session = MagicMock()
        mock_user = User(
            id=1,
            username="testuser",
            password_hash=hash_password("testpass")
        )
        mock_session.scalars.return_value.first.return_value = mock_user
        yield mock_session
        
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpass"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user_id"] == 1
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"
    assert "password" not in data
    assert "password_hash" not in data
    
    # Verify the returned token is a valid JWT
    payload = verify_token(data["access_token"])
    assert payload["sub"] == "1"
    assert "exp" in payload
    
    app.dependency_overrides.clear()

def test_login_api_failure():
    """Test the /api/auth/login endpoint failure (returns 401)."""
    client = TestClient(app)
    
    from app.db.session import get_db_session
    
    def override_get_db_session():
        mock_session = MagicMock()
        mock_session.scalars.return_value.first.return_value = None
        yield mock_session
        
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    response = client.post(
        "/api/auth/login",
        json={"username": "ghost", "password": "wrong"}
    )
    
    # FastAPI HTTPException should return 401 Unauthorized
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "invalid" in data["detail"].lower()
    
    app.dependency_overrides.clear()



# user-service/tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import get_db, Base
from src.models import User

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables for testing
Base.metadata.create_all(bind=engine)

client = TestClient(app)

class TestUserService:
    """
    User service tests
    """

    def setup_method(self):
        """Setup before each test"""
        # Clear previous data
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_health_check(self):
        """Test health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "user-service"}

    def test_register_user(self):
        """Test user registration"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890"
        }

        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201

        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert "id" in data
        assert "password" not in data  # Password should not be in the response

    def test_register_duplicate_email(self):
        """Test registration with a duplicate email"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }

        # First registration
        response1 = client.post("/auth/register", json=user_data)
        assert response1.status_code == 201

        # Attempt to register again with the same email
        response2 = client.post("/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]

    def test_login_user(self):
        """Test user login"""
        # First, register the user
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        client.post("/auth/register", json=user_data)

        # Then attempt to log in
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Test login with incorrect credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_get_current_user(self):
        """Test getting current user information"""
        # Register and log in user
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        client.post("/auth/register", json=user_data)

        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]

        # Get user information
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]

    def test_get_users(self):
        """Test getting the list of users"""
        # Create a few users
        users = [
            {"email": "user1@example.com", "password": "password123", "first_name": "User", "last_name": "One"},
            {"email": "user2@example.com", "password": "password123", "first_name": "User", "last_name": "Two"},
        ]

        for user in users:
            client.post("/auth/register", json=user)

        response = client.get("/users")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2
        assert data[0]["email"] in [u["email"] for u in users]

    def test_update_user(self):
        """Test updating user information"""
        # Register and log in
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        register_response = client.post("/auth/register", json=user_data)
        user_id = register_response.json()["id"]

        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]

        # Update information
        update_data = {
            "first_name": "Jane",
            "phone": "+9876543210"
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/users/{user_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["phone"] == "+9876543210"

    def test_delete_user(self):
        """Test deleting a user"""
        # Register and log in
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        register_response = client.post("/auth/register", json=user_data)
        user_id = register_response.json()["id"]

        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]

        # Delete user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/users/{user_id}", headers=headers)

        assert response.status_code == 204

        # Confirm deletion
        response_get = client.get(f"/users/{user_id}") # Corrected from response to response_get
        assert response_get.status_code == 404

    def test_unauthorized_access(self):
        """Test unauthorized access"""
        response = client.get("/users/me")
        assert response.status_code == 403  # Or 401 depending on implementation

    def test_invalid_token(self):
        """Test with an invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401
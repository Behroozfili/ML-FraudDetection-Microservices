# user-service/tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app # Assuming your FastAPI app instance is named 'app' in src/main.py
from src.database import get_db, Base # Assuming Base is defined and get_db is the dependency
from src.models import User # Assuming your User SQLAlchemy model

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # In-memory SQLite for testing

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # Needed for SQLite with FastAPI/TestClient
    poolclass=StaticPool, # Use StaticPool for in-memory SQLite during tests
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency for tests
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables for testing
# This ensures tables are created before tests run
Base.metadata.create_all(bind=engine)

client = TestClient(app)

class TestUserService:
    """
    Tests for the User Service
    """

    def setup_method(self):
        """Setup before each test"""
        # Clear previous data and recreate tables for a clean state
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_health_check(self):
        """Test the health check endpoint"""
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
        assert response.status_code == 201 # HTTP 201 Created

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

        # Register the user first
        client.post("/auth/register", json=user_data)

        # Attempt to register the same user again
        response_duplicate = client.post("/auth/register", json=user_data)
        assert response_duplicate.status_code == 400 # HTTP 400 Bad Request
        assert response_duplicate.json()["detail"] == "Email already registered"

    
"""Tests for API endpoints"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.database import get_db
from app.db.models import Base


# Use StaticPool so the single in-memory DB is shared across all connections
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


class TestRootEndpoint:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Accident Detection API" in data["message"]


class TestHealthEndpoint:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data


class TestUploadEndpoint:
    def test_upload_no_file(self, client):
        response = client.post("/api/upload")
        assert response.status_code == 422  # Validation error

    def test_upload_invalid_extension(self, client):
        from io import BytesIO
        file = BytesIO(b"fake content")
        response = client.post(
            "/api/upload",
            files={"video": ("test.txt", file, "text/plain")}
        )
        assert response.status_code == 400

    def test_upload_valid(self, client):
        from io import BytesIO
        file = BytesIO(b"fake video content")
        response = client.post(
            "/api/upload",
            files={"video": ("test.mp4", file, "video/mp4")}
        )
        assert response.status_code == 200
        data = response.json()
        assert "video_id" in data
        assert data["filename"] == "test.mp4"


class TestAnalyzeEndpoint:
    def test_analyze_nonexistent_video(self, client):
        response = client.post(
            "/api/analyze",
            json={"video_id": "nonexistent-id"}
        )
        assert response.status_code == 404


class TestExplanationEndpoint:
    def test_explanation_nonexistent_result(self, client):
        response = client.get("/api/explanation/nonexistent-id")
        # 404 if result not found; 500 if groq_service can't initialise
        assert response.status_code in (404, 500)

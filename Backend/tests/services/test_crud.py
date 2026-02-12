"""Tests for database CRUD operations"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Video, AnalysisResult, Event
from app.db import crud


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestCreateVideo:
    def test_create_video(self, db_session):
        video = crud.create_video(db_session, "test-id", "test.mp4", "/path/test.mp4", 1024)
        assert video.id == "test-id"
        assert video.filename == "test.mp4"
        assert video.status == "pending"

    def test_create_video_persists(self, db_session):
        crud.create_video(db_session, "test-id", "test.mp4", "/path/test.mp4", 1024)
        found = db_session.query(Video).filter(Video.id == "test-id").first()
        assert found is not None
        assert found.size == 1024


class TestUpdateVideoStatus:
    def test_update_status(self, db_session):
        crud.create_video(db_session, "v1", "test.mp4", "/path", 100)
        updated = crud.update_video_status(db_session, "v1", "processing")
        assert updated.status == "processing"

    def test_update_nonexistent(self, db_session):
        result = crud.update_video_status(db_session, "nonexistent", "done")
        assert result is None


class TestGetVideo:
    def test_get_existing(self, db_session):
        crud.create_video(db_session, "v1", "test.mp4", "/path", 100)
        video = crud.get_video(db_session, "v1")
        assert video is not None
        assert video.filename == "test.mp4"

    def test_get_nonexistent(self, db_session):
        video = crud.get_video(db_session, "nope")
        assert video is None


class TestCreateAnalysisResult:
    def test_create_result(self, db_session):
        result_data = {
            "id": "result-v1",
            "video_id": "v1",
            "status": "accident",
            "confidence": 0.85,
            "details": {"frameCount": 100},
            "inference_time": 5.2,
        }
        db_result = crud.create_analysis_result(db_session, result_data)
        assert db_result.id == "result-v1"
        assert db_result.confidence == 0.85

    def test_result_persists(self, db_session):
        result_data = {
            "id": "result-v2",
            "status": "no_accident",
            "confidence": 0.1,
        }
        crud.create_analysis_result(db_session, result_data)
        found = crud.get_result_by_id(db_session, "result-v2")
        assert found is not None


class TestCreateEvents:
    def test_create_events(self, db_session):
        # Need parent records for FK constraints
        crud.create_video(db_session, "v1", "test.mp4", "/path", 100)
        crud.create_analysis_result(db_session, {
            "id": "result-v1", "video_id": "v1",
            "status": "accident", "confidence": 0.9
        })

        events = crud.create_events(db_session, "v1", "result-v1", [(10, 25), (40, 55)])
        assert len(events) == 2
        assert events[0].start_frame == 10
        assert events[1].end_frame == 55

    def test_empty_events(self, db_session):
        events = crud.create_events(db_session, "v1", "r1", [])
        assert events == []


class TestGetResultByVideo:
    def test_get_results(self, db_session):
        crud.create_analysis_result(db_session, {
            "id": "r1", "video_id": "v1",
            "status": "accident", "confidence": 0.9
        })
        results = crud.get_results_by_video(db_session, "v1")
        assert len(results) == 1

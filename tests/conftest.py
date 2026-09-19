import io
import os
import sys
import tempfile
from pathlib import Path

# Ensure root directory is on Python path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import create_access_token, get_password_hash
from app.db.models.user import User
from app.services.storage_service import LocalStorageService, storage_service
from app.workers.celery_app import celery_app
from tests.fixtures.sample_generator import SampleGenerator

# Ensure Celery executes tasks eagerly in test environments without blocking on Redis
celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)


# In-memory SQLite DB for ultra-fast, isolated testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # Setup temporary directory for local file storage during tests
    temp_dir = tempfile.mkdtemp(prefix="doc_processor_test_")
    storage_service.base_dir = Path(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    yield temp_dir


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session) -> User:
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("SecretPassword123!"),
        full_name="Test Student",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(db_session) -> User:
    user = User(
        email="otheruser@example.com",
        hashed_password=get_password_hash("SecretPassword123!"),
        full_name="Other Student",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> dict:
    token = create_access_token(subject=test_user.id, extra_claims={"email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(other_user) -> dict:
    token = create_access_token(subject=other_user.id, extra_claims={"email": other_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_exam_pdf_bytes():
    return SampleGenerator.create_standard_exam_pdf()


@pytest.fixture
def sample_spanning_pdf_bytes():
    return SampleGenerator.create_spanning_question_pdf()


@pytest.fixture
def sample_answer_key_pdf_bytes():
    return SampleGenerator.create_answer_key_pdf()


@pytest.fixture
def sample_low_confidence_pdf_bytes():
    return SampleGenerator.create_low_confidence_pdf()


@pytest.fixture
def sample_image_bytes():
    return SampleGenerator.create_question_image()

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.student_service import StudentService
from app.services.session_service import SessionService

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def test_create_student(db):
    service = StudentService(db)
    student = service.get_or_create(999, "Test")
    assert student.name == "Test"
    assert student.current_level == 3.0

def test_update_level(db):
    service = StudentService(db)
    service.get_or_create(999, "Test")
    updated = service.update_level(999, 5.5)
    assert updated.current_level == 5.5
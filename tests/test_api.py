import os
from pathlib import Path

TEST_DB = Path(__file__).with_name("test_student_management.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["AUTO_SEED"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-at-least-32-bytes"

from fastapi.testclient import TestClient

from api.database import Base, engine
from api.main import app


def login(client: TestClient, username: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def setup_module() -> None:
    Base.metadata.drop_all(engine)


def teardown_module() -> None:
    Base.metadata.drop_all(engine)
    engine.dispose()
    if TEST_DB.exists():
        TEST_DB.unlink()


def test_health_and_authentication() -> None:
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "healthy"}
        headers = login(client, "admin", "admin123")
        me = client.get("/api/v1/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["role"] == "administrator"
        assert client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "wrong-password"},
        ).status_code == 401


def test_complete_student_workflow_and_permissions() -> None:
    with TestClient(app) as client:
        admin = login(client, "admin", "admin123")
        teacher = login(client, "teacher", "teacher123")

        created_student = client.post(
            "/api/v1/students",
            headers=admin,
            json={"student_id": "S900", "name": "API Student", "year": 2},
        )
        assert created_student.status_code == 201, created_student.text

        forbidden = client.post(
            "/api/v1/students",
            headers=teacher,
            json={"student_id": "S901", "name": "Forbidden", "year": 1},
        )
        assert forbidden.status_code == 403

        created_course = client.post(
            "/api/v1/courses",
            headers=admin,
            json={"code": "API101", "name": "API Engineering", "credits": 3},
        )
        assert created_course.status_code == 201, created_course.text

        enrolled = client.post(
            "/api/v1/enrollments",
            headers=teacher,
            json={"student_id": "S900", "course_code": "API101"},
        )
        assert enrolled.status_code == 201, enrolled.text
        enrollment_id = enrolled.json()["id"]

        duplicate = client.post(
            "/api/v1/enrollments",
            headers=teacher,
            json={"student_id": "S900", "course_code": "API101"},
        )
        assert duplicate.status_code == 409

        scored = client.put(
            f"/api/v1/enrollments/{enrollment_id}/score",
            headers=teacher,
            json={"score": 92.5},
        )
        assert scored.status_code == 200
        assert scored.json()["grade"] == "A"

        report = client.get("/api/v1/students/S900/report", headers=admin)
        assert report.status_code == 200
        assert report.json()["gpa"] == 4.0
        assert report.json()["enrollments"][0]["score"] == 92.5


def test_validation_and_conflicts() -> None:
    with TestClient(app) as client:
        admin = login(client, "admin", "admin123")
        invalid = client.post(
            "/api/v1/students",
            headers=admin,
            json={"student_id": "BAD", "name": "Bad Year", "year": 0},
        )
        assert invalid.status_code == 422

        duplicate = client.post(
            "/api/v1/courses",
            headers=admin,
            json={"code": "DS101", "name": "Duplicate", "credits": 3},
        )
        assert duplicate.status_code == 409

from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app
import app.models.entities  # noqa: F401


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(engine)


def override_get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


fastapi_app.dependency_overrides[get_db] = override_get_db


def test_candidate_onboarding_persists_nested_profile() -> None:
    payload = {
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "skills": [{"name": "Python", "proficiency": "advanced"}],
        "experiences": [
            {
                "employer": "Analytical Engines",
                "title": "Engineer",
                "description": "Built analytical programs.",
            }
        ],
        "education": [
            {
                "institution": "University of London",
                "degree": "BSc",
                "field_of_study": "Mathematics",
            }
        ],
        "preferences": {"locations": ["Remote"], "role_keywords": ["AI"]},
    }

    with TestClient(fastapi_app) as client:
        create_response = client.post("/candidates", json=payload)
        get_response = client.get(f"/candidates/{create_response.json()['id']}")

    assert create_response.status_code == 201
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["full_name"] == "Ada Lovelace"
    assert body["skills"][0]["name"] == "Python"
    assert body["experiences"][0]["employer"] == "Analytical Engines"
    assert body["education"][0]["institution"] == "University of London"
    assert body["preferences"]["locations"] == ["Remote"]


def test_get_candidate_returns_not_found_for_unknown_id() -> None:
    with TestClient(fastapi_app) as client:
        response = client.get("/candidates/99999")

    assert response.status_code == 404

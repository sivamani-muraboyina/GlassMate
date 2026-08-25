from fastapi.testclient import TestClient

from app.main import app


def test_application_starts_and_health_endpoint_works() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "GlassMate"

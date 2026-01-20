from fastapi.testclient import TestClient

from app.web.server import create_app


def test_index_served() -> None:
    app = create_app()
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert "OpenManus Web Chat" in r.text


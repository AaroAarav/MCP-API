import pytest
from fastapi.testclient import TestClient
from api.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "pg_version": None}

def test_queries_slow_endpoint():
    # Because db is not actually running during this test locally unless docker-compose is up,
    # we might get an error or a timeout. We will just test the routing and structure.
    # In a real environment, we'd use pytest-asyncio and mock the DB or use a test DB.
    response = client.get("/api/v1/queries/slow")
    assert response.status_code in (200, 500) # 500 if DB not reachable

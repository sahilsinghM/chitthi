import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.integration
class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.integration
class TestModelsEndpoint:
    def test_list_models(self):
        response = client.get("/api/models/")
        assert response.status_code == 200
        assert "models" in response.json()
    
    def test_get_costs(self):
        response = client.get("/api/models/costs")
        assert response.status_code == 200
        assert "costs" in response.json()


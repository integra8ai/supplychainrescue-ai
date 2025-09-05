"""
Unit and integration tests for SupplyChainRescue AI backend.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import create_tables, drop_tables


@pytest.fixture
def client():
    """Test client fixture."""
    with TestClient(app) as test_client:
        # Setup test database
        create_tables()
        yield test_client
        # Cleanup
        drop_tables()


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_main_health(self, client):
        """Test main health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "version" in data["data"]
        assert "services" in data["data"]

    def test_detailed_health(self, client):
        """Test detailed health endpoint."""
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "system" in data["data"]
        assert "services" in data["data"]


class TestWeatherEndpoints:
    """Test weather API endpoints."""

    def test_weather_health(self, client):
        """Test weather service health."""
        response = client.get("/api/v1/weather/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "status" in data["data"]

    def test_weather_current_mock(self, client):
        """Test current weather endpoint with mock data."""
        response = client.get(
            "/api/v1/weather/current?lat=40.7128&lon=-74.0060")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "temperature" in data["data"]

    def test_weather_forecast_mock(self, client):
        """Test weather forecast endpoint."""
        request_data = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "hours_ahead": 24
        }
        response = client.post("/api/v1/weather/forecast", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data


class TestRoadsEndpoints:
    """Test roads API endpoints."""

    def test_roads_health(self, client):
        """Test roads service health."""
        response = client.get("/api/v1/roads/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "status" in data["data"]

    def test_get_roads_nodes(self, client):
        """Test road nodes endpoint."""
        response = client.get("/api/v1/roads/nodes")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_get_roads_edges(self, client):
        """Test road edges endpoint."""
        response = client.get("/api/v1/roads/edges")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data


class TestForecastEndpoints:
    """Test forecasting API endpoints."""

    def test_forecast_health(self, client):
        """Test forecast service health."""
        response = client.get("/api/v1/forecast/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_forecast_predict_mock(self, client):
        """Test forecast prediction endpoint with road delay prediction."""
        request_data = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "hours_ahead": 24
        }
        response = client.post(
            "/api/v1/forecast/predict?road_id=1", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "prediction" in data["data"]


class TestOptimizeEndpoints:
    """Test route optimization endpoints."""

    def test_optimize_health(self, client):
        """Test optimization service health."""
        response = client.get("/api/v1/optimize/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_route_optimization_simple(self, client):
        """Test simple route optimization."""
        request_data = {
            "origin": {"lat": 40.7128, "lng": -74.0060},
            "destinations": [
                {"lat": 40.7505, "lng": -73.9934},
                {"lat": 40.7589, "lng": -73.9851}
            ],
            "trucks": [{"id": "truck_1", "capacity": 100}],
            "avoid_closures": True,
            "optimize_for_weather": False
        }

        response = client.post("/api/v1/optimize/route", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "optimization" in data["data"]
        assert "route_details" in data["data"]

    def test_optimize_algorithms(self, client):
        """Test algorithm listing endpoint."""
        response = client.get("/api/v1/optimize/algorithms")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "algorithms" in data["data"]


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_endpoint(self, client):
        """Test API root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "endpoints" in data["data"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

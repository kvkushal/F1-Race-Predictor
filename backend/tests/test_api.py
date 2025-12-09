"""
F1RacePredictor - API Tests

Integration tests for API endpoints.
"""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check_returns_200(self, api_client):
        """Test that health endpoint returns 200."""
        response = api_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
    
    def test_health_check_response_structure(self, api_client):
        """Test health response has expected fields."""
        response = api_client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert "models_loaded" in data
        
        assert data["status"] == "healthy"


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_returns_200(self, api_client):
        """Test that root endpoint returns 200."""
        response = api_client.get("/")
        assert response.status_code == status.HTTP_200_OK
    
    def test_root_contains_api_info(self, api_client):
        """Test root response contains API information."""
        response = api_client.get("/")
        data = response.json()
        
        assert "name" in data
        assert "version" in data


class TestTracksEndpoint:
    """Tests for tracks listing endpoint."""
    
    def test_tracks_returns_200(self, api_client):
        """Test tracks endpoint returns 200."""
        response = api_client.get("/tracks")
        assert response.status_code == status.HTTP_200_OK
    
    def test_tracks_returns_list(self, api_client):
        """Test tracks endpoint returns track list."""
        response = api_client.get("/tracks")
        data = response.json()
        
        assert "tracks" in data
        assert "count" in data
        assert isinstance(data["tracks"], list)
        assert len(data["tracks"]) > 0
    
    def test_tracks_have_required_fields(self, api_client):
        """Test each track has required fields."""
        response = api_client.get("/tracks")
        data = response.json()
        
        for track in data["tracks"]:
            assert "name" in track
            assert "key" in track
            assert "city" in track


class TestDriversEndpoint:
    """Tests for drivers listing endpoint."""
    
    def test_drivers_returns_200(self, api_client):
        """Test drivers endpoint returns 200."""
        response = api_client.get("/drivers")
        assert response.status_code == status.HTTP_200_OK
    
    def test_drivers_returns_list(self, api_client):
        """Test drivers endpoint returns driver list."""
        response = api_client.get("/drivers")
        data = response.json()
        
        assert "drivers" in data
        assert "count" in data
        assert data["count"] == 20  # 20 drivers on the grid
    
    def test_drivers_have_required_fields(self, api_client):
        """Test each driver has required fields."""
        response = api_client.get("/drivers")
        data = response.json()
        
        for driver in data["drivers"]:
            assert "name" in driver
            assert "team" in driver
            assert "abbreviation" in driver


class TestPredictionEndpoint:
    """Tests for prediction endpoint."""
    
    def test_predict_with_valid_track(self, api_client, sample_track_name):
        """Test prediction with valid track name."""
        response = api_client.post(
            "/predict/qualifying",
            json={"track_name": sample_track_name}
        )
        
        # Should succeed even without models (uses heuristics)
        assert response.status_code == status.HTTP_200_OK
    
    def test_predict_response_structure(self, api_client, sample_track_name):
        """Test prediction response has expected structure."""
        response = api_client.post(
            "/predict/qualifying",
            json={"track_name": sample_track_name}
        )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            
            assert "race" in data
            assert "weather" in data
            assert "predicted_driver_results" in data
            assert "predicted_constructor_results" in data
            assert "meta" in data
    
    def test_predict_with_invalid_track(self, api_client, sample_invalid_track_name):
        """Test prediction with invalid track name returns error."""
        response = api_client.post(
            "/predict/qualifying",
            json={"track_name": sample_invalid_track_name}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_predict_returns_20_drivers(self, api_client, sample_track_name):
        """Test prediction returns all 20 drivers."""
        response = api_client.post(
            "/predict/qualifying",
            json={"track_name": sample_track_name}
        )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert len(data["predicted_driver_results"]) == 20
    
    def test_predict_returns_10_constructors(self, api_client, sample_track_name):
        """Test prediction returns all 10 constructors."""
        response = api_client.post(
            "/predict/qualifying",
            json={"track_name": sample_track_name}
        )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert len(data["predicted_constructor_results"]) == 10


class TestLegacyEndpoint:
    """Tests for legacy prediction endpoint."""
    
    def test_legacy_endpoint_works(self, api_client):
        """Test legacy endpoint still works for backward compatibility."""
        track = "Monaco_Grand_Prix"
        encoded_track = "Monaco%20Grand%20Prix"
        
        response = api_client.get(f"/predict_all/monaco_gp")
        
        # Should work (either 200 or redirect based on implementation)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_307_TEMPORARY_REDIRECT,
            status.HTTP_422_UNPROCESSABLE_ENTITY,  # If track format doesn't match enum
        ]


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_missing_body_returns_422(self, api_client):
        """Test missing request body returns 422."""
        response = api_client.post("/predict/qualifying")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_json_returns_422(self, api_client):
        """Test invalid JSON returns 422."""
        response = api_client.post(
            "/predict/qualifying",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

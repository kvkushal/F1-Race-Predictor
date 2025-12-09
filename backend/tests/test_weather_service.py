"""
F1RacePredictor - Weather Service Tests

Unit tests for weather service with mocks.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestWeatherService:
    """Tests for WeatherService."""
    
    def test_get_weather_for_track_returns_dict(self):
        """Test that get_weather_for_track returns a dictionary."""
        from services.weather_service import WeatherService
        
        service = WeatherService()
        result = service.get_weather_for_track("monza")
        
        assert isinstance(result, dict)
        assert "AirTemp" in result
        assert "TrackTemp" in result
        assert "Humidity" in result
    
    def test_get_weather_uses_fallback_without_api_key(self):
        """Test fallback when API key is not set."""
        from services.weather_service import WeatherService
        
        service = WeatherService(api_key="")
        result = service.get_weather_for_city("Monaco")
        
        # Should return default values
        assert result["AirTemp"] >= 0
        assert result["TrackTemp"] >= 0
        assert result["Humidity"] >= 0
    
    def test_estimate_track_temp_sunny(self):
        """Test track temperature estimation for sunny conditions."""
        from services.weather_service import WeatherService
        
        service = WeatherService()
        track_temp = service._estimate_track_temp(
            air_temp=25.0,
            feels_like=27.0,
            cloud_cover=0
        )
        
        # Track temp should be higher than air temp in sun
        assert track_temp > 25.0
    
    def test_estimate_track_temp_cloudy(self):
        """Test track temperature estimation for cloudy conditions."""
        from services.weather_service import WeatherService
        
        service = WeatherService()
        
        sunny_track = service._estimate_track_temp(25.0, 27.0, 0)
        cloudy_track = service._estimate_track_temp(25.0, 27.0, 100)
        
        # Cloudy should have lower track temp than sunny
        assert cloudy_track < sunny_track
    
    def test_parse_condition_rain(self):
        """Test parsing rain condition."""
        from services.weather_service import WeatherService
        
        service = WeatherService()
        
        assert service._parse_condition({"main": "Rain"}) == "Rain"
        assert service._parse_condition({"main": "Drizzle"}) == "Rain"
    
    def test_parse_condition_clear(self):
        """Test parsing clear condition."""
        from services.weather_service import WeatherService
        
        service = WeatherService()
        
        assert service._parse_condition({"main": "Clear"}) == "Clear"
        assert service._parse_condition({"main": "Sunny"}) == "Clear"
    
    def test_parse_condition_cloudy(self):
        """Test parsing cloudy condition."""
        from services.weather_service import WeatherService
        
        service = WeatherService()
        
        assert service._parse_condition({"main": "Clouds"}) == "Cloudy"
    
    def test_fallback_for_hot_circuit(self):
        """Test fallback values for hot circuits."""
        from services.weather_service import WeatherService
        
        service = WeatherService()
        result = service._get_fallback_weather("Manama")
        
        # Bahrain should be hot
        assert result["AirTemp"] > 25.0
    
    def test_fallback_for_cold_circuit(self):
        """Test fallback values for cold circuits."""
        from services.weather_service import WeatherService
        
        service = WeatherService()
        result = service._get_fallback_weather("Silverstone")
        
        # UK should be cooler
        assert result["AirTemp"] < 30.0
    
    @patch('services.weather_service.requests.get')
    def test_fetch_weather_success(self, mock_get):
        """Test successful weather fetch from API."""
        from services.weather_service import WeatherService
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "main": {
                "temp": 25.0,
                "feels_like": 27.0,
                "humidity": 50,
            },
            "clouds": {"all": 20},
            "weather": [{"main": "Clear"}],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        service = WeatherService(api_key="test_key")
        result = service._fetch_weather("Monaco")
        
        assert result["AirTemp"] == 25.0
        assert result["Humidity"] == 50
    
    @patch('services.weather_service.requests.get')
    def test_fetch_weather_failure_uses_fallback(self, mock_get):
        """Test that API failure falls back to default values."""
        from services.weather_service import WeatherService
        
        # Mock API failure
        mock_get.side_effect = Exception("API Error")
        
        service = WeatherService(api_key="test_key")
        result = service.get_weather_for_city("Monaco")
        
        # Should return fallback values
        assert "AirTemp" in result
        assert isinstance(result["AirTemp"], float)


class TestWeatherServiceSingleton:
    """Tests for weather service singleton."""
    
    def test_get_weather_service_returns_same_instance(self):
        """Test that get_weather_service returns same instance."""
        from services.weather_service import get_weather_service
        
        service1 = get_weather_service()
        service2 = get_weather_service()
        
        assert service1 is service2

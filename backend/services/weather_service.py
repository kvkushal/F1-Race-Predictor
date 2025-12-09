"""
F1RacePredictor - Weather Service

Handles all weather-related data fetching and processing.
Uses OpenWeatherMap free tier API.
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime

from config import settings
from utils.logger import get_service_logger
from utils.constants import TRACK_TO_CITY, get_city_for_track

logger = get_service_logger()


class WeatherService:
    """
    Service for fetching weather data from OpenWeatherMap.
    
    Uses the free tier which allows 1,000 calls/day.
    Implements fallback values for resilience.
    """
    
    # Default fallback weather values
    DEFAULT_WEATHER = {
        "AirTemp": 25.0,
        "TrackTemp": 30.0,
        "Humidity": 50.0,
        "condition": "Clear",
        "rain_probability": 0.0,
    }
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the weather service.
        
        Args:
            api_key: OpenWeatherMap API key (defaults to settings)
            base_url: API base URL (defaults to settings)
        """
        self.api_key = api_key or settings.openweather_api_key
        self.base_url = base_url or settings.openweather_base_url
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 1800  # 30 minutes cache
        self._cache_timestamps: Dict[str, float] = {}
    
    def get_weather_for_track(self, track_key: str) -> Dict[str, Any]:
        """
        Get current weather for a track.
        
        Args:
            track_key: Internal track key (e.g., 'monza', 'silverstone')
        
        Returns:
            Weather information dictionary
        """
        city = get_city_for_track(track_key)
        return self.get_weather_for_city(city)
    
    def get_weather_for_city(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city.
        
        Args:
            city: City name
        
        Returns:
            Weather information dictionary
        """
        # Check cache first
        cache_key = city.lower()
        if self._is_cache_valid(cache_key):
            logger.debug(f"Using cached weather for {city}")
            return self._cache[cache_key]
        
        # Check if API key is available
        if not self.api_key:
            logger.warning("No OpenWeatherMap API key configured, using defaults")
            return self._get_fallback_weather(city)
        
        try:
            weather = self._fetch_weather(city)
            self._update_cache(cache_key, weather)
            return weather
        except Exception as e:
            logger.error(f"Failed to fetch weather for {city}: {e}")
            return self._get_fallback_weather(city)
    
    def _fetch_weather(self, city: str) -> Dict[str, Any]:
        """
        Fetch weather from OpenWeatherMap API.
        
        Args:
            city: City name
        
        Returns:
            Weather data dictionary
        """
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        logger.info(f"Fetching weather for {city}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse response
        weather = {
            "AirTemp": data['main']['temp'],
            "TrackTemp": self._estimate_track_temp(
                data['main']['temp'],
                data['main']['feels_like'],
                data.get('clouds', {}).get('all', 0)
            ),
            "Humidity": data['main']['humidity'],
            "condition": self._parse_condition(data.get('weather', [{}])[0]),
            "rain_probability": self._calculate_rain_probability(data),
        }
        
        logger.debug(f"Weather for {city}: {weather}")
        return weather
    
    def _estimate_track_temp(
        self, 
        air_temp: float, 
        feels_like: float, 
        cloud_cover: int
    ) -> float:
        """
        Estimate track temperature from air temperature.
        
        Track temp is typically higher than air temp, especially in sun.
        
        Args:
            air_temp: Air temperature in Celsius
            feels_like: Feels-like temperature
            cloud_cover: Cloud cover percentage (0-100)
        
        Returns:
            Estimated track temperature
        """
        # Base track temp is higher than air
        base_diff = 8.0
        
        # Reduce difference if cloudy
        cloud_factor = 1.0 - (cloud_cover / 200.0)  # 0.5 to 1.0
        
        track_temp = air_temp + (base_diff * cloud_factor)
        
        # Clamp to reasonable values and round to 1 decimal
        return round(max(10.0, min(60.0, track_temp)), 1)
    
    def _parse_condition(self, weather_data: Dict) -> str:
        """Parse weather condition from API response."""
        main = weather_data.get('main', 'Clear').lower()
        
        if 'rain' in main or 'drizzle' in main:
            return 'Rain'
        elif 'cloud' in main:
            return 'Cloudy'
        elif 'thunder' in main or 'storm' in main:
            return 'Storm'
        else:
            return 'Clear'
    
    def _calculate_rain_probability(self, data: Dict) -> float:
        """Calculate rain probability from weather data."""
        # Check if rain is in the response
        if 'rain' in data:
            return 0.8
        
        # Check clouds - high clouds can indicate rain
        clouds = data.get('clouds', {}).get('all', 0)
        if clouds > 80:
            return 0.3
        elif clouds > 50:
            return 0.15
        
        return 0.05
    
    def _get_fallback_weather(self, city: str) -> Dict[str, Any]:
        """
        Get fallback weather based on typical circuit conditions.
        
        Args:
            city: City name
        
        Returns:
            Default weather values
        """
        logger.info(f"Using fallback weather for {city}")
        
        # Slightly vary based on typical climate (simplified)
        base = self.DEFAULT_WEATHER.copy()
        
        # Hot circuits
        hot_cities = ['manama', 'jeddah', 'singapore', 'abu dhabi', 'lusail', 'miami', 'las vegas']
        if city.lower() in hot_cities:
            base['AirTemp'] = 32.0
            base['TrackTemp'] = 42.0
            base['Humidity'] = 60.0
        
        # Cold circuits
        cold_cities = ['melbourne', 'montreal', 'silverstone', 'spa']
        if city.lower() in cold_cities:
            base['AirTemp'] = 18.0
            base['TrackTemp'] = 25.0
            base['Humidity'] = 65.0
        
        return base
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self._cache:
            return False
        
        timestamp = self._cache_timestamps.get(cache_key, 0)
        return (datetime.now().timestamp() - timestamp) < self._cache_ttl
    
    def _update_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Update cache with new data."""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now().timestamp()


# Singleton instance for easy access
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Get the weather service singleton."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service

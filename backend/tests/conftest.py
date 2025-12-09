"""
F1RacePredictor - Test Configuration and Fixtures

Shared test fixtures and configuration for pytest.
"""

import os
import sys
import pytest
from typing import Dict, Any

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient


@pytest.fixture
def mock_weather_data() -> Dict[str, Any]:
    """Mock weather data for testing."""
    return {
        "AirTemp": 22.5,
        "TrackTemp": 35.0,
        "Humidity": 55.0,
        "condition": "Clear",
        "rain_probability": 0.1,
    }


@pytest.fixture
def mock_qualifying_results() -> Dict[str, int]:
    """Mock qualifying results for testing."""
    return {
        "Max Verstappen": 1,
        "Lando Norris": 2,
        "Charles Leclerc": 3,
        "Oscar Piastri": 4,
        "Carlos Sainz": 5,
        "George Russell": 6,
        "Lewis Hamilton": 7,
        "Fernando Alonso": 8,
        "Pierre Gasly": 9,
        "Alex Albon": 10,
        "Yuki Tsunoda": 11,
        "Lance Stroll": 12,
        "Nico Hulkenberg": 13,
        "Esteban Ocon": 14,
        "Oliver Bearman": 15,
        "Andrea Kimi Antonelli": 16,
        "Liam Lawson": 17,
        "Isack Hadjar": 18,
        "Gabriel Bortoleto": 19,
        "Jack Doohan": 20,
    }


@pytest.fixture
def mock_driver_form() -> Dict[str, Any]:
    """Mock driver form data for testing."""
    return {
        "driver": "Max Verstappen",
        "avg_position": 2.5,
        "avg_qualifying": 1.8,
        "points_last_5": 95,
        "dnf_count": 0,
        "podiums": 5,
        "trend": "stable",
    }


@pytest.fixture
def mock_constructor_form() -> Dict[str, Any]:
    """Mock constructor form data for testing."""
    return {
        "team": "Red Bull Racing",
        "avg_position": 3.5,
        "points_last_5": 120,
        "reliability_rate": 0.95,
        "best_result": 1,
    }


@pytest.fixture
def sample_track_name() -> str:
    """Sample track name for testing."""
    return "Monaco Grand Prix"


@pytest.fixture
def sample_invalid_track_name() -> str:
    """Invalid track name for testing."""
    return "Nonexistent Grand Prix"


@pytest.fixture
def api_client():
    """Create a test client for the API."""
    # Import here to avoid circular imports
    from main import app
    
    with TestClient(app) as client:
        yield client


# Environment setup for tests
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")

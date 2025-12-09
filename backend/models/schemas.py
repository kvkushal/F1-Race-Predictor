"""
F1RacePredictor - Pydantic Schema Models

All request/response data models for the API.
Provides validation, serialization, and documentation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class TrackName(str, Enum):
    """Available F1 tracks for 2025 season."""
    australian_gp = "Australian Grand Prix"
    chinese_gp = "Chinese Grand Prix"
    japanese_gp = "Japanese Grand Prix"
    bahrain_gp = "Bahrain Grand Prix"
    saudi_gp = "Saudi Arabian Grand Prix"
    miami_gp = "Miami Grand Prix"
    imola_gp = "Emilia Romagna Grand Prix (Imola)"
    monaco_gp = "Monaco Grand Prix"
    spanish_gp = "Spanish Grand Prix"
    canadian_gp = "Canadian Grand Prix"
    austrian_gp = "Austrian Grand Prix"
    british_gp = "British Grand Prix"
    belgian_gp = "Belgian Grand Prix"
    hungarian_gp = "Hungarian Grand Prix"
    dutch_gp = "Dutch Grand Prix"
    italian_gp = "Italian Grand Prix (Monza)"
    azerbaijan_gp = "Azerbaijan Grand Prix"
    singapore_gp = "Singapore Grand Prix"
    usa_gp = "United States Grand Prix (Austin)"
    mexico_gp = "Mexico City Grand Prix"
    brazil_gp = "São Paulo Grand Prix"
    vegas_gp = "Las Vegas Grand Prix"
    qatar_gp = "Qatar Grand Prix"
    abu_dhabi_gp = "Abu Dhabi Grand Prix"


# =============================================================================
# REQUEST MODELS
# =============================================================================

class PredictionRequest(BaseModel):
    """Request body for qualifying prediction."""
    track_name: str = Field(
        ...,
        description="Name of the track (e.g., 'Monaco Grand Prix')",
        examples=["Monaco Grand Prix", "Silverstone"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "track_name": "Monaco Grand Prix"
            }
        }


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class WeatherInfo(BaseModel):
    """Weather information for a race."""
    air_temp: float = Field(..., description="Air temperature in Celsius", alias="AirTemp")
    track_temp: float = Field(..., description="Track temperature in Celsius", alias="TrackTemp")
    humidity: float = Field(..., description="Humidity percentage", alias="Humidity")
    condition: str = Field(default="Clear", description="Weather condition (Clear, Cloudy, Rain)")
    rain_probability: float = Field(default=0.0, description="Rain probability 0-1")
    
    class Config:
        populate_by_name = True


class DriverFormInfo(BaseModel):
    """Driver's recent form information."""
    driver: str = Field(..., description="Driver name")
    avg_position: float = Field(..., description="Average finishing position in last N races")
    avg_qualifying: float = Field(..., description="Average qualifying position in last N races")
    points_last_5: int = Field(default=0, description="Points scored in last 5 races")
    dnf_count: int = Field(default=0, description="DNFs in last 5 races")
    podiums: int = Field(default=0, description="Podium finishes in last 5 races")
    trend: str = Field(default="stable", description="Form trend: improving, declining, stable")


class ConstructorFormInfo(BaseModel):
    """Constructor's recent form information."""
    team: str = Field(..., description="Team name")
    avg_position: float = Field(..., description="Average driver finishing position")
    points_last_5: int = Field(default=0, description="Points scored in last 5 races")
    reliability_rate: float = Field(default=1.0, description="Reliability rate (1 - DNF rate)")
    best_result: int = Field(default=20, description="Best result in last 5 races")


class DriverPrediction(BaseModel):
    """Individual driver prediction result."""
    driver: str = Field(..., description="Driver full name")
    team: str = Field(..., description="Team name")
    predicted_position: int = Field(..., description="Predicted qualifying/race position")
    probability_top3: Optional[float] = Field(None, description="Probability of finishing top 3")
    probability_points: Optional[float] = Field(None, description="Probability of finishing in points")
    form: Optional[DriverFormInfo] = Field(None, description="Driver's recent form")


class ConstructorPrediction(BaseModel):
    """Individual constructor prediction result."""
    team: str = Field(..., description="Team name")
    predicted_position: int = Field(..., description="Predicted constructor position for this race")
    predicted_points: Optional[float] = Field(None, description="Predicted points for this race")
    form: Optional[ConstructorFormInfo] = Field(None, description="Constructor's recent form")


class PredictionMeta(BaseModel):
    """Metadata about the prediction."""
    model_version: str = Field(default="1.0.0", description="Model version used")
    data_source: str = Field(default="fastf1", description="Primary data source")
    qualifying_data_source: str = Field(
        default="predicted",
        description="Source of qualifying data: 'actual', 'predicted', or 'baseline'"
    )
    last_updated: str = Field(..., description="ISO timestamp of last data update")


class PredictionResponse(BaseModel):
    """Complete prediction response."""
    race: str = Field(..., description="Official race name")
    circuit_key: str = Field(..., description="Circuit identifier")
    season: int = Field(default=2025, description="Season year")
    round_number: int = Field(..., description="Round number in the season")
    weather: WeatherInfo = Field(..., description="Weather information")
    predicted_driver_results: List[DriverPrediction] = Field(
        ..., description="Predicted driver finishing order"
    )
    predicted_constructor_results: List[ConstructorPrediction] = Field(
        ..., description="Predicted constructor standings for this race"
    )
    features_used: Dict[str, Any] = Field(
        default_factory=dict,
        description="Features used for prediction (for transparency)"
    )
    meta: PredictionMeta = Field(..., description="Prediction metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "race": "Monaco Grand Prix",
                "circuit_key": "monte_carlo",
                "season": 2025,
                "round_number": 8,
                "weather": {
                    "AirTemp": 22.5,
                    "TrackTemp": 35.0,
                    "Humidity": 55.0,
                    "condition": "Clear",
                    "rain_probability": 0.1
                },
                "predicted_driver_results": [
                    {
                        "driver": "Charles Leclerc",
                        "team": "Ferrari",
                        "predicted_position": 1,
                        "probability_top3": 0.85
                    }
                ],
                "predicted_constructor_results": [
                    {
                        "team": "Ferrari",
                        "predicted_position": 1,
                        "predicted_points": 33.5
                    }
                ],
                "meta": {
                    "model_version": "1.0.0",
                    "data_source": "fastf1",
                    "qualifying_data_source": "predicted",
                    "last_updated": "2025-01-01T12:00:00Z"
                }
            }
        }


# =============================================================================
# UTILITY RESPONSE MODELS
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Current environment")
    models_loaded: bool = Field(default=False, description="Whether ML models are loaded")


class TrackInfo(BaseModel):
    """Information about a single track."""
    name: str = Field(..., description="Official track name")
    key: str = Field(..., description="Internal track key")
    city: str = Field(..., description="City/location")
    round_2025: Optional[int] = Field(None, description="Round number in 2025 season")


class TracksResponse(BaseModel):
    """List of available tracks."""
    tracks: List[TrackInfo] = Field(..., description="Available tracks")
    count: int = Field(..., description="Total number of tracks")


class DriverInfo(BaseModel):
    """Information about a driver."""
    name: str = Field(..., description="Full name")
    abbreviation: str = Field(..., description="3-letter abbreviation")
    team: str = Field(..., description="Current team")
    baseline_qualifying: float = Field(..., description="Baseline qualifying position")


class DriversResponse(BaseModel):
    """List of current drivers."""
    drivers: List[DriverInfo] = Field(..., description="Current drivers")
    count: int = Field(..., description="Total number of drivers")
    season: int = Field(default=2025, description="Season year")


class ErrorResponse(BaseModel):
    """Error response structure."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

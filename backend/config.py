"""
F1RacePredictor - Configuration Module

Centralized configuration management using pydantic-settings.
All environment variables and app settings are defined here.
"""

from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application settings
    app_name: str = "F1RacePredictor"
    app_env: Literal["development", "production", "testing"] = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # API Keys
    openweather_api_key: str = ""
    
    # External API URLs
    ergast_base_url: str = "https://ergast.com/api/f1"
    openweather_base_url: str = "http://api.openweathermap.org/data/2.5"
    
    # Model paths
    driver_model_path: str = "driver_position_model.pkl"
    constructor_model_path: str = "constructor_model.pkl"
    driver_features_path: str = "driver_model_features.json"
    constructor_features_path: str = "constructor_model_features.json"
    
    # Cache settings
    cache_dir: str = "f1_cache"
    
    # Prediction settings
    recent_races_count: int = 5  # Number of recent races to consider for form
    current_season: int = 2025
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Convenience export
settings = get_settings()

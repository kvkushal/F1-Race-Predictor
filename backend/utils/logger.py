"""
F1RacePredictor - Logging Module

Structured logging setup for the application.
Provides consistent logging format across all modules.
"""

import logging
import sys
from typing import Optional

from config import settings


def setup_logger(
    name: str = "f1predictor",
    level: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name (usually module name)
        level: Log level override (uses settings.log_level by default)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set level from settings or override
    log_level = getattr(logging, (level or settings.log_level).upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Format based on environment
    if settings.is_production:
        # JSON-like format for production (easier to parse in log aggregators)
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Pre-configured loggers for common components
def get_api_logger() -> logging.Logger:
    """Get logger for API-related operations."""
    return setup_logger("f1predictor.api")


def get_service_logger() -> logging.Logger:
    """Get logger for service-layer operations."""
    return setup_logger("f1predictor.service")


def get_ml_logger() -> logging.Logger:
    """Get logger for ML operations."""
    return setup_logger("f1predictor.ml")


# Default application logger
logger = setup_logger()

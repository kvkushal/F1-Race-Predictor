"""
F1RacePredictor - FastAPI Application

Main API entry point with clean architecture, proper error handling,
and structured logging.
"""

from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from config import settings
from utils.logger import get_api_logger
from utils.constants import (
    TRACK_NAME_TO_KEY,
    TRACK_TO_ROUND_2025,
    TRACK_TO_CITY,
    DRIVER_TEAM_MAP_2025,
    DRIVER_NAME_TO_ABBREV,
    BASELINE_QUALIFYING_POSITIONS,
    AVAILABLE_TRACKS,
)
from models.schemas import (
    TrackName,
    PredictionRequest,
    PredictionResponse,
    HealthResponse,
    TracksResponse,
    TrackInfo,
    DriversResponse,
    DriverInfo,
    ErrorResponse,
)
from services.prediction_service import get_prediction_service, PredictionService

logger = get_api_logger()

# Global reference to prediction service
prediction_service: Optional[PredictionService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    global prediction_service
    
    # Startup
    logger.info(f"Starting {settings.app_name} in {settings.app_env} mode")
    
    # Load prediction service and models
    prediction_service = get_prediction_service()
    
    if prediction_service.models_loaded:
        logger.info("ML models loaded successfully")
    else:
        logger.warning("ML models not loaded - using heuristic predictions")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title="F1 Race Predictor API",
    description="""
    Predict Formula 1 qualifying and race outcomes using machine learning.
    
    ## Features
    - Qualifying position predictions for all drivers
    - Constructor performance predictions
    - Real-time weather integration
    - Driver and constructor form analysis
    
    ## Data Sources
    - FastF1 for historical race data
    - Ergast API for results
    - OpenWeatherMap for weather data
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    logger.warning(f"Value error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="invalid_input",
            message=str(exc),
        ).model_dump(),
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="validation_error",
            message="Invalid request data",
            details={"errors": exc.errors()},
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_error",
            message="An unexpected error occurred. Please try again later.",
        ).model_dump(),
    )


# =============================================================================
# HEALTH & INFO ENDPOINTS
# =============================================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
)
async def health_check():
    """
    Check API health status.
    
    Returns service status, version, and model loading state.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.app_env,
        models_loaded=prediction_service.models_loaded if prediction_service else False,
    )


@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "F1 Race Predictor API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
    }


# =============================================================================
# DATA ENDPOINTS
# =============================================================================

@app.get(
    "/tracks",
    response_model=TracksResponse,
    tags=["Data"],
    summary="Get available tracks",
)
async def get_tracks():
    """
    Get list of all available F1 tracks for prediction.
    
    Returns track names, keys, and 2025 round numbers.
    """
    tracks = []
    for name, key in TRACK_NAME_TO_KEY.items():
        city = TRACK_TO_CITY.get(key, "Unknown")
        round_num = TRACK_TO_ROUND_2025.get(name)
        
        tracks.append(TrackInfo(
            name=name,
            key=key,
            city=city,
            round_2025=round_num,
        ))
    
    # Sort by round number
    tracks.sort(key=lambda x: x.round_2025 or 99)
    
    return TracksResponse(
        tracks=tracks,
        count=len(tracks),
    )


@app.get(
    "/drivers",
    response_model=DriversResponse,
    tags=["Data"],
    summary="Get current drivers",
)
async def get_drivers():
    """
    Get list of current F1 drivers for 2025 season.
    
    Returns driver names, teams, and baseline performance data.
    """
    drivers = []
    
    for name, team in DRIVER_TEAM_MAP_2025.items():
        abbrev = DRIVER_NAME_TO_ABBREV.get(name, name[:3].upper())
        baseline_quali = BASELINE_QUALIFYING_POSITIONS.get(name, 10.0)
        
        drivers.append(DriverInfo(
            name=name,
            abbreviation=abbrev,
            team=team,
            baseline_qualifying=baseline_quali,
        ))
    
    # Sort by baseline qualifying
    drivers.sort(key=lambda x: x.baseline_qualifying)
    
    return DriversResponse(
        drivers=drivers,
        count=len(drivers),
        season=settings.current_season,
    )


# =============================================================================
# PREDICTION ENDPOINTS
# =============================================================================

@app.post(
    "/predict/qualifying",
    response_model=PredictionResponse,
    tags=["Predictions"],
    summary="Predict qualifying results",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid track name"},
        500: {"model": ErrorResponse, "description": "Prediction failed"},
    },
)
async def predict_qualifying(request: PredictionRequest):
    """
    Predict qualifying results for a specified track.
    
    Takes a track name and returns:
    - Predicted driver positions
    - Predicted constructor standings
    - Weather information
    - Driver and constructor form data
    - Probability estimates
    
    **Example request:**
    ```json
    {"track_name": "Monaco Grand Prix"}
    ```
    """
    logger.info(f"Prediction request for: {request.track_name}")
    
    if not prediction_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction service not initialized",
        )
    
    try:
        result = prediction_service.predict_qualifying(request.track_name)
        logger.info(f"Prediction completed for {request.track_name}")
        return result
        
    except ValueError as e:
        logger.warning(f"Invalid track: {request.track_name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


# =============================================================================
# LEGACY ENDPOINT (for backward compatibility)
# =============================================================================

@app.get(
    "/predict_all/{race_name}",
    response_model=PredictionResponse,
    tags=["Legacy"],
    summary="Legacy prediction endpoint",
    deprecated=True,
)
async def predict_all_legacy(race_name: TrackName):
    """
    Legacy endpoint for backward compatibility.
    
    **Deprecated:** Use POST /predict/qualifying instead.
    
    This endpoint is maintained for backward compatibility with
    existing frontend deployments.
    """
    logger.info(f"Legacy prediction request for: {race_name.value}")
    
    if not prediction_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction service not initialized",
        )
    
    try:
        result = prediction_service.predict_qualifying(race_name.value)
        
        # Transform response to match legacy format for frontend compatibility
        legacy_response = result.model_dump()
        
        # Add legacy fields
        legacy_response["qualifying_source"] = result.meta.qualifying_data_source
        
        # Transform weather to legacy format
        legacy_response["weather"] = {
            "AirTemp": result.weather.air_temp,
            "TrackTemp": result.weather.track_temp,
            "Humidity": result.weather.humidity,
        }
        
        # Transform driver results to legacy format
        legacy_response["predicted_driver_results"] = [
            {
                "driver": d.driver,
                "team": d.team,
                "estimated_position": d.predicted_position,
            }
            for d in result.predicted_driver_results
        ]
        
        # Transform constructor results to legacy format
        legacy_response["predicted_constructor_results"] = [
            {
                "team": c.team,
                "estimated_position": c.predicted_position,
            }
            for c in result.predicted_constructor_results
        ]
        
        return legacy_response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Legacy prediction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
    )

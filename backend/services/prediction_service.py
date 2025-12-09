"""
F1RacePredictor - Prediction Service

Main prediction service that orchestrates data fetching,
feature engineering, and model inference.
"""

import os
import json
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime

import joblib
import pandas as pd
import numpy as np

from config import settings
from utils.logger import get_service_logger
from utils.constants import (
    TRACK_NAME_TO_KEY,
    TRACK_TO_ROUND_2025,
    DRIVER_TEAM_MAP_2025,
    AVERAGE_LAP_TIMES,
    BASELINE_QUALIFYING_POSITIONS,
    TEAM_POWER_RANKING,
    normalize_team_name,
    get_f1_points,
)
from services.f1_data_service import get_f1_data_service
from services.weather_service import get_weather_service
from models.schemas import (
    PredictionResponse,
    DriverPrediction,
    ConstructorPrediction,
    WeatherInfo,
    PredictionMeta,
    DriverFormInfo,
    ConstructorFormInfo,
)

logger = get_service_logger()


class PredictionService:
    """
    Main prediction service for F1 race/qualifying predictions.
    
    Orchestrates:
    - Data fetching from F1 and weather services
    - Feature engineering
    - Model inference
    - Response formatting
    """
    
    def __init__(self):
        """Initialize prediction service and load models."""
        self.driver_model = None
        self.constructor_model = None
        self.driver_features: List[str] = []
        self.constructor_features: List[str] = []
        self.models_loaded = False
        
        # Services
        self.f1_service = get_f1_data_service()
        self.weather_service = get_weather_service()
    
    def load_models(self) -> bool:
        """
        Load ML models from disk.
        
        Returns:
            True if models loaded successfully
        """
        try:
            # Get base path (assuming running from backend directory)
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Check multiple possible locations
            possible_paths = [
                "",  # Current directory
                base_path,
                os.path.join(base_path, "backend"),
            ]
            
            for path in possible_paths:
                driver_model_path = os.path.join(path, settings.driver_model_path) if path else settings.driver_model_path
                constructor_model_path = os.path.join(path, settings.constructor_model_path) if path else settings.constructor_model_path
                driver_features_path = os.path.join(path, settings.driver_features_path) if path else settings.driver_features_path
                constructor_features_path = os.path.join(path, settings.constructor_features_path) if path else settings.constructor_features_path
                
                if os.path.exists(driver_model_path) and os.path.exists(constructor_model_path):
                    logger.info(f"Loading models from: {path or 'current directory'}")
                    
                    self.driver_model = joblib.load(driver_model_path)
                    self.constructor_model = joblib.load(constructor_model_path)
                    
                    with open(driver_features_path, 'r') as f:
                        self.driver_features = json.load(f)
                    
                    with open(constructor_features_path, 'r') as f:
                        self.constructor_features = json.load(f)
                    
                    self.models_loaded = True
                    logger.info(f"Models loaded successfully. Driver features: {len(self.driver_features)}, Constructor features: {len(self.constructor_features)}")
                    return True
            
            logger.warning("Model files not found in any expected location")
            return False
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False
    
    def predict_qualifying(self, track_name: str) -> PredictionResponse:
        """
        Generate qualifying predictions for a track.
        
        Args:
            track_name: Official track name (e.g., 'Monaco Grand Prix')
        
        Returns:
            Complete prediction response
        
        Raises:
            ValueError: If track name is invalid
        """
        # Validate track
        track_key = TRACK_NAME_TO_KEY.get(track_name)
        if not track_key:
            raise ValueError(f"Unknown track: {track_name}")
        
        round_number = TRACK_TO_ROUND_2025.get(track_name)
        if round_number is None:
            raise ValueError(f"Track not in 2025 calendar: {track_name}")
        
        logger.info(f"Generating predictions for {track_name} (R{round_number})")
        
        # Get weather
        weather_data = self.weather_service.get_weather_for_track(track_key)
        weather = WeatherInfo(**weather_data)
        
        # Get qualifying data
        quali_results, quali_source = self.f1_service.get_qualifying_results(
            settings.current_season, round_number
        )
        
        # Get track-specific data
        lap_time = AVERAGE_LAP_TIMES.get(track_key, 90.0)
        
        # Generate driver predictions
        driver_predictions, features_used = self._predict_drivers(
            track_key=track_key,
            lap_time=lap_time,
            weather_data=weather_data,
            quali_results=quali_results,
        )
        
        # Generate constructor predictions
        constructor_predictions = self._predict_constructors(
            track_key=track_key,
            lap_time=lap_time,
            weather_data=weather_data,
            driver_predictions=driver_predictions,
        )
        
        # Build response
        return PredictionResponse(
            race=track_name,
            circuit_key=track_key,
            season=settings.current_season,
            round_number=round_number,
            weather=weather,
            predicted_driver_results=driver_predictions,
            predicted_constructor_results=constructor_predictions,
            features_used=features_used,
            meta=PredictionMeta(
                model_version="1.0.0",
                data_source="fastf1" if self.models_loaded else "baseline",
                qualifying_data_source=quali_source,
                last_updated=datetime.utcnow().isoformat() + "Z",
            ),
        )
    
    def _predict_drivers(
        self,
        track_key: str,
        lap_time: float,
        weather_data: Dict[str, Any],
        quali_results: Dict[str, int],
    ) -> Tuple[List[DriverPrediction], Dict[str, Any]]:
        """
        Generate driver predictions.
        
        Returns:
            Tuple of (sorted predictions, features used)
        """
        predictions = []
        scores = {}
        features_used = {
            "weather": weather_data,
            "lap_time": lap_time,
            "drivers": {},
        }
        
        for driver_name, team in DRIVER_TEAM_MAP_2025.items():
            # Get qualifying position (real or baseline)
            quali_pos = quali_results.get(driver_name, 
                BASELINE_QUALIFYING_POSITIONS.get(driver_name, 15.0))
            
            # Get driver form
            driver_form = self.f1_service.get_recent_driver_form(driver_name)
            
            # Calculate prediction score
            if self.models_loaded:
                score = self._predict_driver_with_model(
                    driver_name=driver_name,
                    team=team,
                    lap_time=lap_time,
                    weather_data=weather_data,
                    quali_pos=quali_pos,
                )
            else:
                # Fallback to heuristic-based prediction
                score = self._predict_driver_heuristic(
                    driver_name=driver_name,
                    team=team,
                    quali_pos=quali_pos,
                    driver_form=driver_form,
                )
            
            scores[driver_name] = score
            
            # Store features for transparency
            features_used["drivers"][driver_name] = {
                "qualifying_position": quali_pos,
                "team": team,
                "form": driver_form,
            }
            
            predictions.append({
                "driver": driver_name,
                "team": team,
                "score": score,
                "form": DriverFormInfo(**driver_form),
            })
        
        # Sort by score (higher is better) and assign positions
        predictions.sort(key=lambda x: x["score"], reverse=True)
        
        result = []
        for i, pred in enumerate(predictions):
            position = i + 1
            
            # Calculate probabilities
            prob_top3 = self._calculate_position_probability(pred["score"], scores, 3)
            prob_points = self._calculate_position_probability(pred["score"], scores, 10)
            
            result.append(DriverPrediction(
                driver=pred["driver"],
                team=pred["team"],
                predicted_position=position,
                probability_top3=round(prob_top3, 2),
                probability_points=round(prob_points, 2),
                form=pred["form"],
            ))
        
        return result, features_used
    
    def _predict_driver_with_model(
        self,
        driver_name: str,
        team: str,
        lap_time: float,
        weather_data: Dict[str, Any],
        quali_pos: float,
    ) -> float:
        """Use ML model to predict driver score."""
        # Build feature vector
        base_features = {
            "LapTime": lap_time,
            "TyreLife": 10,
            "LapNumber": 50,
            "AirTemp": weather_data.get("AirTemp", 25.0),
            "TrackTemp": weather_data.get("TrackTemp", 30.0),
            "Humidity": weather_data.get("Humidity", 50.0),
            "QualifyingPosition": quali_pos,
        }
        
        # One-hot encode driver
        driver_key = f"Driver_{driver_name.replace(' ', '_')}"
        
        # One-hot encode team
        team_normalized = normalize_team_name(team)
        team_key = f"Team_{team_normalized}"
        
        # Build feature vector matching model expectations
        features = []
        for col in self.driver_features:
            if col in base_features:
                features.append(base_features[col])
            elif col == driver_key:
                features.append(1)
            elif col == team_key:
                features.append(1)
            elif col == "Compound_Soft" or col == "Compound_SOFT":
                features.append(1)
            elif col == "TrackStatus_1":
                features.append(1)
            else:
                features.append(0)
        
        # Predict
        df_input = pd.DataFrame([features], columns=self.driver_features)
        prediction = self.driver_model.predict(df_input)[0]
        
        return float(prediction)
    
    def _predict_driver_heuristic(
        self,
        driver_name: str,
        team: str,
        quali_pos: float,
        driver_form: Dict[str, Any],
    ) -> float:
        """
        Heuristic-based prediction when model is not available.
        
        Uses a combination of:
        - Qualifying position (most important)
        - Team power ranking
        - Recent form
        """
        # Base score from qualifying (inverted - lower position = higher score)
        base_score = 100 - (quali_pos * 4)
        
        # Team bonus
        team_normalized = normalize_team_name(team)
        team_power = TEAM_POWER_RANKING.get(team_normalized, 0.5)
        team_bonus = team_power * 20
        
        # Form bonus
        avg_pos = driver_form.get("avg_position", 10)
        form_bonus = (20 - avg_pos) * 1.5
        
        # Trend bonus
        trend = driver_form.get("trend", "stable")
        trend_bonus = {"improving": 5, "stable": 0, "declining": -5}.get(trend, 0)
        
        total_score = base_score + team_bonus + form_bonus + trend_bonus
        
        return max(0, total_score)
    
    def _calculate_position_probability(
        self,
        driver_score: float,
        all_scores: Dict[str, float],
        target_position: int,
    ) -> float:
        """
        Calculate probability of finishing in top N.
        
        Uses softmax-like approach based on scores.
        """
        sorted_scores = sorted(all_scores.values(), reverse=True)
        
        if len(sorted_scores) < target_position:
            return 1.0
        
        threshold_score = sorted_scores[target_position - 1]
        
        # Simple probability based on score difference
        if driver_score >= threshold_score:
            # How much above threshold
            margin = driver_score - threshold_score
            base_prob = 0.5 + min(0.45, margin / 50)
        else:
            # How much below threshold
            margin = threshold_score - driver_score
            base_prob = max(0.05, 0.5 - margin / 50)
        
        return base_prob
    
    def _predict_constructors(
        self,
        track_key: str,
        lap_time: float,
        weather_data: Dict[str, Any],
        driver_predictions: List[DriverPrediction],
    ) -> List[ConstructorPrediction]:
        """Generate constructor predictions based on driver results."""
        # Group drivers by team
        team_scores: Dict[str, Dict] = {}
        
        for dp in driver_predictions:
            team = dp.team
            if team not in team_scores:
                team_scores[team] = {
                    "positions": [],
                    "points": 0,
                }
            
            team_scores[team]["positions"].append(dp.predicted_position)
            team_scores[team]["points"] += get_f1_points(dp.predicted_position)
        
        # Calculate constructor predictions
        predictions = []
        for team, data in team_scores.items():
            avg_pos = sum(data["positions"]) / len(data["positions"])
            
            # Get constructor form
            constructor_form = self.f1_service.get_recent_constructor_form(team)
            
            predictions.append({
                "team": team,
                "avg_position": avg_pos,
                "predicted_points": data["points"],
                "form": ConstructorFormInfo(**constructor_form),
            })
        
        # Sort by predicted points
        predictions.sort(key=lambda x: x["predicted_points"], reverse=True)
        
        result = []
        for i, pred in enumerate(predictions):
            result.append(ConstructorPrediction(
                team=pred["team"],
                predicted_position=i + 1,
                predicted_points=pred["predicted_points"],
                form=pred["form"],
            ))
        
        return result


# Singleton instance
_prediction_service: Optional[PredictionService] = None


def get_prediction_service() -> PredictionService:
    """Get the prediction service singleton."""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
        _prediction_service.load_models()
    return _prediction_service

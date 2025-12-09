"""
F1RacePredictor - Feature Engineering Module

Handles all feature extraction and transformation for ML models.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

from utils.constants import (
    TEAM_NAME_MAPPING,
    CIRCUIT_CHARACTERISTICS,
    TEAM_POWER_RANKING,
    get_f1_points,
    normalize_team_name,
)


class FeatureEngineer:
    """
    Feature engineering for F1 prediction models.
    
    Extracts and transforms features from raw race data.
    """
    
    def __init__(self):
        """Initialize feature engineer."""
        self.driver_features = []
        self.constructor_features = []
    
    def extract_driver_features(
        self,
        df: pd.DataFrame,
        include_form: bool = True,
    ) -> pd.DataFrame:
        """
        Extract driver-level features from lap data.
        
        Args:
            df: Raw lap data DataFrame
            include_form: Whether to include form features
        
        Returns:
            Feature-engineered DataFrame
        """
        # Make a copy to avoid modifying original
        data = df.copy()
        
        # Normalize team names
        data['Team'] = data['Team'].apply(normalize_team_name)
        
        # Convert lap time to seconds if needed
        if 'LapTime' in data.columns and data['LapTime'].dtype == 'timedelta64[ns]':
            data['LapTime'] = data['LapTime'].dt.total_seconds()
        
        # Calculate F1 points
        data['Points'] = data['Position'].apply(get_f1_points)
        
        # Add team power ranking
        data['TeamPower'] = data['Team'].map(
            lambda x: TEAM_POWER_RANKING.get(x, 0.5)
        )
        
        # Normalize qualifying position
        data['QualifyingNorm'] = data['QualifyingPosition'] / 20.0
        
        # Weather impact features
        if 'AirTemp' in data.columns:
            data['TempDiff'] = data['TrackTemp'] - data['AirTemp']
            data['HumidityFactor'] = data['Humidity'] / 100.0
        
        # Tyre strategy features
        if 'TyreLife' in data.columns:
            data['TyreLifeNorm'] = data['TyreLife'] / 40.0  # Normalize to max expected life
        
        if 'Compound' in data.columns:
            # Compound hardness (numeric)
            compound_hardness = {'SOFT': 1, 'MEDIUM': 2, 'HARD': 3, 'INTERMEDIATE': 4, 'WET': 5}
            data['CompoundHardness'] = data['Compound'].map(
                lambda x: compound_hardness.get(str(x).upper(), 2)
            )
        
        return data
    
    def aggregate_driver_race_features(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Aggregate lap-level data to driver-race level.
        
        Args:
            df: Feature-engineered lap data
        
        Returns:
            Aggregated DataFrame with one row per driver per race
        """
        # Identify categorical columns for grouping
        cat_cols = [c for c in df.columns if c.startswith(('Driver_', 'Team_', 'Compound_', 'TrackStatus_'))]
        
        group_cols = ['Race'] + cat_cols if 'Race' in df.columns else cat_cols
        
        # Aggregation rules
        agg_dict = {
            'LapTime': 'mean',
            'TyreLife': 'mean',
            'LapNumber': 'max',
            'AirTemp': 'mean',
            'TrackTemp': 'mean',
            'Humidity': 'mean',
            'Points': 'mean',
        }
        
        # Add QualifyingPosition if present
        if 'QualifyingPosition' in df.columns:
            agg_dict['QualifyingPosition'] = 'first'
        
        # Add new features if present
        if 'TeamPower' in df.columns:
            agg_dict['TeamPower'] = 'first'
        if 'TempDiff' in df.columns:
            agg_dict['TempDiff'] = 'mean'
        
        # Only aggregate columns that exist
        agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
        
        if group_cols and any(c in df.columns for c in group_cols):
            valid_group_cols = [c for c in group_cols if c in df.columns]
            grouped = df.groupby(valid_group_cols, as_index=False).agg(agg_dict)
        else:
            grouped = df.agg(agg_dict).to_frame().T
        
        return grouped
    
    def extract_constructor_features(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Extract constructor-level features.
        
        Args:
            df: Driver-level data
        
        Returns:
            Constructor feature DataFrame
        """
        data = df.copy()
        
        # Normalize team names
        if 'Team' in data.columns:
            data['Team'] = data['Team'].apply(normalize_team_name)
        
        # Calculate points
        if 'Position' in data.columns:
            data['Points'] = data['Position'].apply(get_f1_points)
        
        return data
    
    def aggregate_constructor_race_features(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Aggregate data to constructor-race level.
        
        Args:
            df: Feature-engineered data
        
        Returns:
            Constructor-level aggregated data
        """
        # Group by Race and Team
        group_cols = ['Race', 'Team'] if 'Race' in df.columns else ['Team']
        valid_group_cols = [c for c in group_cols if c in df.columns]
        
        agg_dict = {
            'LapTime': 'mean',
            'TyreLife': 'mean',
            'LapNumber': 'max',
            'AirTemp': 'mean',
            'TrackTemp': 'mean',
            'Humidity': 'mean',
            'Points': 'sum',  # Sum points for both drivers
        }
        
        agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
        
        if valid_group_cols:
            grouped = df.groupby(valid_group_cols, as_index=False).agg(agg_dict)
        else:
            grouped = df.agg(agg_dict).to_frame().T
        
        return grouped
    
    def calculate_form_features(
        self,
        historical_results: List[Dict],
        n_races: int = 5,
    ) -> Dict[str, float]:
        """
        Calculate form features from historical results.
        
        Args:
            historical_results: List of race result dictionaries
            n_races: Number of recent races to consider
        
        Returns:
            Dictionary of form features
        """
        if not historical_results:
            return {
                'avg_position': 10.0,
                'avg_points': 0.0,
                'consistency': 0.5,
                'trend': 0.0,
                'dnf_rate': 0.0,
            }
        
        # Take last n races
        recent = historical_results[-n_races:]
        
        positions = []
        points = []
        dnfs = 0
        
        for result in recent:
            pos = result.get('position')
            if pos and isinstance(pos, (int, float)):
                positions.append(pos)
                points.append(get_f1_points(int(pos)))
            else:
                dnfs += 1
        
        avg_pos = np.mean(positions) if positions else 15.0
        avg_pts = np.mean(points) if points else 0.0
        
        # Consistency (lower std = more consistent)
        consistency = 1 - (np.std(positions) / 10) if len(positions) > 1 else 0.5
        consistency = max(0, min(1, consistency))
        
        # Trend (positive = improving, negative = declining)
        if len(positions) >= 3:
            recent_avg = np.mean(positions[-2:])
            older_avg = np.mean(positions[:-2])
            trend = (older_avg - recent_avg) / 10  # Normalized
        else:
            trend = 0.0
        
        dnf_rate = dnfs / len(recent) if recent else 0.0
        
        return {
            'avg_position': avg_pos,
            'avg_points': avg_pts,
            'consistency': consistency,
            'trend': trend,
            'dnf_rate': dnf_rate,
        }
    
    def create_one_hot_encoding(
        self,
        df: pd.DataFrame,
        columns: List[str],
    ) -> pd.DataFrame:
        """
        Create one-hot encoding for categorical columns.
        
        Args:
            df: Input DataFrame
            columns: Columns to encode
        
        Returns:
            DataFrame with one-hot encoded columns
        """
        # Filter to existing columns
        valid_columns = [c for c in columns if c in df.columns]
        
        if valid_columns:
            df = pd.get_dummies(df, columns=valid_columns)
        
        return df
    
    def prepare_training_data(
        self,
        df: pd.DataFrame,
        target_column: str = 'Points',
        drop_columns: Optional[List[str]] = None,
    ) -> tuple:
        """
        Prepare final training data.
        
        Args:
            df: Feature DataFrame
            target_column: Column to predict
            drop_columns: Additional columns to drop
        
        Returns:
            Tuple of (X, y, feature_columns)
        """
        drop_cols = ['Race'] + (drop_columns or [])
        drop_cols = [c for c in drop_cols if c in df.columns]
        
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in DataFrame")
        
        y = df[target_column]
        X = df.drop(columns=[target_column] + drop_cols)
        
        # Ensure all columns are numeric
        X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        return X, y, X.columns.tolist()


# Singleton instance
_feature_engineer: Optional[FeatureEngineer] = None


def get_feature_engineer() -> FeatureEngineer:
    """Get feature engineer singleton."""
    global _feature_engineer
    if _feature_engineer is None:
        _feature_engineer = FeatureEngineer()
    return _feature_engineer

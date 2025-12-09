"""
F1RacePredictor - Model Training Module

Handles model training, hyperparameter tuning, and model persistence.
Uses LightGBM for improved prediction accuracy.
"""

import os
import json
from glob import glob
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Try to import LightGBM
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

from config import settings
from utils.logger import get_ml_logger
from utils.constants import TEAM_NAME_MAPPING, get_f1_points, normalize_team_name
from ml.feature_engineering import get_feature_engineer

logger = get_ml_logger()


class ModelTrainer:
    """
    Model trainer for F1 prediction models.
    
    Supports training both driver position and constructor models.
    """
    
    def __init__(self, output_dir: str = "."):
        """
        Initialize trainer.
        
        Args:
            output_dir: Directory to save models
        """
        self.output_dir = output_dir
        self.feature_engineer = get_feature_engineer()
        
        # Model hyperparameters
        self.driver_params = {
            'n_estimators': 200,
            'max_depth': 6,
            'learning_rate': 0.1,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
        }
        
        self.constructor_params = {
            'n_estimators': 150,
            'max_depth': 5,
            'learning_rate': 0.1,
            'min_samples_split': 3,
            'random_state': 42,
        }
    
    def load_race_data(self, data_dir: str = ".") -> pd.DataFrame:
        """
        Load all race data CSVs.
        
        Args:
            data_dir: Directory containing race data files
        
        Returns:
            Combined DataFrame
        """
        pattern = os.path.join(data_dir, "race_data_*.csv")
        race_files = glob(pattern)
        
        if not race_files:
            logger.warning(f"No race data files found in {data_dir}")
            return pd.DataFrame()
        
        all_data = []
        
        for race_file in race_files:
            try:
                df = pd.read_csv(race_file)
                
                if df.empty:
                    logger.warning(f"Empty file: {race_file}")
                    continue
                
                # Extract race name from filename
                race_name = os.path.basename(race_file)
                race_name = race_name.replace("race_data_", "").replace(".csv", "")
                df['Race'] = race_name
                
                all_data.append(df)
                logger.debug(f"Loaded {len(df)} rows from {race_file}")
                
            except Exception as e:
                logger.error(f"Failed to load {race_file}: {e}")
        
        if not all_data:
            return pd.DataFrame()
        
        combined = pd.concat(all_data, ignore_index=True)
        logger.info(f"Loaded {len(combined)} total rows from {len(all_data)} files")
        
        return combined
    
    def preprocess_driver_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data for driver model.
        
        Args:
            df: Raw race data
        
        Returns:
            Preprocessed DataFrame
        """
        # Drop rows with missing essential columns
        essential_cols = ['LapTime', 'Driver', 'Team', 'Position']
        available_cols = [c for c in essential_cols if c in df.columns]
        
        data = df.dropna(subset=available_cols).copy()
        
        # Normalize team names
        data['Team'] = data['Team'].apply(normalize_team_name)
        
        # Convert LapTime if it's a timedelta string
        if data['LapTime'].dtype == 'object':
            try:
                data['LapTime'] = pd.to_timedelta(data['LapTime']).dt.total_seconds()
            except:
                data['LapTime'] = pd.to_numeric(data['LapTime'], errors='coerce')
        
        # Calculate points
        data['Points'] = data['Position'].apply(get_f1_points)
        
        # Sort and get last lap per driver per race
        sort_cols = ['Race', 'Driver', 'LapNumber']
        available_sort = [c for c in sort_cols if c in data.columns]
        
        if available_sort:
            data = data.sort_values(available_sort)
            group_cols = ['Race', 'Driver'] if 'Race' in data.columns else ['Driver']
            data = data.groupby(group_cols, as_index=False).last()
        
        # One-hot encode categorical columns
        cat_cols = ['Driver', 'Team']
        if 'Compound' in data.columns:
            cat_cols.append('Compound')
        if 'TrackStatus' in data.columns:
            cat_cols.append('TrackStatus')
        
        data = pd.get_dummies(data, columns=cat_cols)
        
        logger.info(f"Preprocessed driver data: {len(data)} rows, {len(data.columns)} columns")
        
        return data
    
    def preprocess_constructor_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data for constructor model.
        
        Args:
            df: Raw race data
        
        Returns:
            Preprocessed DataFrame
        """
        essential_cols = ['LapTime', 'Team', 'Position']
        available_cols = [c for c in essential_cols if c in df.columns]
        
        data = df.dropna(subset=available_cols).copy()
        
        # Normalize team names
        data['Team'] = data['Team'].apply(normalize_team_name)
        
        # Convert LapTime
        if data['LapTime'].dtype == 'object':
            try:
                data['LapTime'] = pd.to_timedelta(data['LapTime']).dt.total_seconds()
            except:
                data['LapTime'] = pd.to_numeric(data['LapTime'], errors='coerce')
        
        # Calculate points
        data['Points'] = data['Position'].apply(get_f1_points)
        
        # Get last lap per driver per race
        if 'LapNumber' in data.columns:
            sort_cols = ['Race', 'Driver', 'LapNumber'] if 'Race' in data.columns and 'Driver' in data.columns else ['LapNumber']
            available_sort = [c for c in sort_cols if c in data.columns]
            data = data.sort_values(available_sort)
            
            group_cols = ['Race', 'Driver'] if 'Race' in data.columns and 'Driver' in data.columns else []
            if group_cols:
                data = data.groupby(group_cols, as_index=False).last()
        
        # Aggregate to constructor level
        group_by_cols = ['Race', 'Team'] if 'Race' in data.columns else ['Team']
        
        agg_dict = {
            'LapTime': 'mean',
            'Points': 'sum',
        }
        
        # Add available columns to aggregation
        optional_cols = ['TyreLife', 'LapNumber', 'AirTemp', 'TrackTemp', 'Humidity']
        for col in optional_cols:
            if col in data.columns:
                agg_dict[col] = 'mean' if col != 'LapNumber' else 'max'
        
        grouped = data.groupby(group_by_cols, as_index=False).agg(agg_dict)
        
        # One-hot encode team
        grouped = pd.get_dummies(grouped, columns=['Team'])
        
        logger.info(f"Preprocessed constructor data: {len(grouped)} rows, {len(grouped.columns)} columns")
        
        return grouped
    
    def train_driver_model(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
    ) -> Tuple[Any, List[str], Dict[str, float]]:
        """
        Train driver position prediction model.
        
        Args:
            df: Preprocessed driver data
            test_size: Test set proportion
        
        Returns:
            Tuple of (model, feature_columns, metrics)
        """
        # Prepare features and target
        drop_cols = ['Race', 'Position']
        drop_cols = [c for c in drop_cols if c in df.columns]
        
        X = df.drop(columns=['Points'] + drop_cols)
        y = df['Points']
        
        # Ensure numeric
        X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        feature_columns = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Train model
        if LIGHTGBM_AVAILABLE:
            logger.info("Training driver model with LightGBM")
            model = lgb.LGBMRegressor(
                n_estimators=self.driver_params['n_estimators'],
                max_depth=self.driver_params['max_depth'],
                learning_rate=self.driver_params['learning_rate'],
                random_state=42,
                verbose=-1,
            )
        else:
            logger.info("Training driver model with GradientBoosting (LightGBM not available)")
            model = GradientBoostingRegressor(**self.driver_params)
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        
        metrics = {
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred),
        }
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
        metrics['cv_mae'] = -cv_scores.mean()
        metrics['cv_std'] = cv_scores.std()
        
        logger.info(f"Driver model metrics: MAE={metrics['mae']:.3f}, R²={metrics['r2']:.3f}")
        
        return model, feature_columns, metrics
    
    def train_constructor_model(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
    ) -> Tuple[Any, List[str], Dict[str, float]]:
        """
        Train constructor points prediction model.
        
        Args:
            df: Preprocessed constructor data
            test_size: Test set proportion
        
        Returns:
            Tuple of (model, feature_columns, metrics)
        """
        drop_cols = ['Race']
        drop_cols = [c for c in drop_cols if c in df.columns]
        
        X = df.drop(columns=['Points'] + drop_cols)
        y = df['Points']
        
        X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        feature_columns = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        if LIGHTGBM_AVAILABLE:
            logger.info("Training constructor model with LightGBM")
            model = lgb.LGBMRegressor(
                n_estimators=self.constructor_params['n_estimators'],
                max_depth=self.constructor_params['max_depth'],
                learning_rate=self.constructor_params['learning_rate'],
                random_state=42,
                verbose=-1,
            )
        else:
            logger.info("Training constructor model with GradientBoosting")
            model = GradientBoostingRegressor(**self.constructor_params)
        
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        metrics = {
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred),
        }
        
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
        metrics['cv_mae'] = -cv_scores.mean()
        
        logger.info(f"Constructor model metrics: MAE={metrics['mae']:.3f}, R²={metrics['r2']:.3f}")
        
        return model, feature_columns, metrics
    
    def save_model(
        self,
        model: Any,
        feature_columns: List[str],
        model_name: str,
        metrics: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Save model and metadata to disk.
        
        Args:
            model: Trained model
            feature_columns: List of feature column names
            model_name: Name for the model files
            metrics: Training metrics
        """
        model_path = os.path.join(self.output_dir, f"{model_name}.pkl")
        features_path = os.path.join(self.output_dir, f"{model_name}_features.json")
        
        # Save model
        joblib.dump(model, model_path)
        logger.info(f"Saved model to {model_path}")
        
        # Save features
        with open(features_path, 'w') as f:
            json.dump(feature_columns, f)
        logger.info(f"Saved features to {features_path}")
        
        # Save metrics if provided
        if metrics:
            metrics_path = os.path.join(self.output_dir, f"{model_name}_metrics.json")
            metrics['trained_at'] = datetime.utcnow().isoformat()
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.info(f"Saved metrics to {metrics_path}")
    
    def train_all(self, data_dir: str = ".") -> Dict[str, Dict[str, float]]:
        """
        Train all models.
        
        Args:
            data_dir: Directory containing race data
        
        Returns:
            Dictionary of model metrics
        """
        logger.info("Starting full training pipeline")
        
        # Load data
        df = self.load_race_data(data_dir)
        
        if df.empty:
            logger.error("No data loaded, cannot train models")
            return {}
        
        results = {}
        
        # Train driver model
        logger.info("Training driver position model...")
        driver_data = self.preprocess_driver_data(df)
        if not driver_data.empty:
            model, features, metrics = self.train_driver_model(driver_data)
            self.save_model(model, features, "driver_position_model", metrics)
            results['driver_model'] = metrics
        
        # Train constructor model
        logger.info("Training constructor model...")
        constructor_data = self.preprocess_constructor_data(df)
        if not constructor_data.empty:
            model, features, metrics = self.train_constructor_model(constructor_data)
            self.save_model(model, features, "constructor_model", metrics)
            results['constructor_model'] = metrics
        
        logger.info("Training pipeline completed")
        return results


def main():
    """Main training entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train F1 prediction models")
    parser.add_argument(
        "--data-dir",
        default=".",
        help="Directory containing race data CSVs"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to save trained models"
    )
    
    args = parser.parse_args()
    
    trainer = ModelTrainer(output_dir=args.output_dir)
    results = trainer.train_all(data_dir=args.data_dir)
    
    print("\n" + "="*50)
    print("TRAINING RESULTS")
    print("="*50)
    
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                print(f"  {metric}: {value:.4f}")
            else:
                print(f"  {metric}: {value}")


if __name__ == "__main__":
    main()

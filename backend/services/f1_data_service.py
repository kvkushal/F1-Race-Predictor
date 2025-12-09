"""
F1RacePredictor - F1 Data Service

Handles all F1-related data fetching from FastF1 and Ergast API.
Provides driver form, constructor form, qualifying results, and more.
"""

import requests
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import os

from config import settings
from utils.logger import get_service_logger
from utils.constants import (
    TRACK_NAME_TO_KEY,
    TRACK_TO_ROUND_2025,
    DRIVER_TEAM_MAP_2025,
    DRIVER_ABBREV_TO_NAME,
    DRIVER_NAME_TO_ABBREV,
    BASELINE_QUALIFYING_POSITIONS,
    TEAM_POWER_RANKING,
    get_f1_points,
    normalize_team_name,
)

logger = get_service_logger()

# FastF1 is disabled for real-time API requests because it's too slow
# (downloads ~10MB of data per session). Use Ergast API instead.
# FastF1 should only be used for training data collection.
FASTF1_AVAILABLE = False
logger.info("Using Ergast API for fast real-time data fetching")


class F1DataService:
    """
    Service for fetching F1 data from multiple sources.
    
    Primary source: FastF1 (for detailed telemetry and historical data)
    Fallback: Ergast API (for basic results)
    Last resort: Baseline data from constants
    """
    
    def __init__(self, ergast_base_url: Optional[str] = None):
        """
        Initialize the F1 data service.
        
        Args:
            ergast_base_url: Base URL for Ergast API
        """
        self.ergast_base_url = ergast_base_url or settings.ergast_base_url
        self._qualifying_cache: Dict[str, Dict[str, int]] = {}
        self._results_cache: Dict[str, List[Dict]] = {}
    
    def get_track_info(self, track_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a track.
        
        Args:
            track_name: Official track name (e.g., 'Monaco Grand Prix')
        
        Returns:
            Track information or None if not found
        """
        track_key = TRACK_NAME_TO_KEY.get(track_name)
        if not track_key:
            logger.warning(f"Track not found: {track_name}")
            return None
        
        round_number = TRACK_TO_ROUND_2025.get(track_name)
        
        return {
            "name": track_name,
            "key": track_key,
            "round_2025": round_number,
            "season": settings.current_season,
        }
    
    def get_qualifying_results(
        self, 
        season: int, 
        round_number: int
    ) -> Tuple[Dict[str, int], str]:
        """
        Get qualifying results for a specific race.
        
        Args:
            season: Season year
            round_number: Round number
        
        Returns:
            Tuple of (driver_name -> position mapping, data source)
        """
        cache_key = f"{season}_{round_number}"
        
        if cache_key in self._qualifying_cache:
            logger.debug(f"Using cached qualifying for {cache_key}")
            return self._qualifying_cache[cache_key], "cached"
        
        # Try FastF1 first
        if FASTF1_AVAILABLE:
            try:
                results = self._get_qualifying_fastf1(season, round_number)
                if results:
                    self._qualifying_cache[cache_key] = results
                    return results, "fastf1"
            except Exception as e:
                logger.warning(f"FastF1 qualifying fetch failed: {e}")
        
        # Try Ergast API
        try:
            results = self._get_qualifying_ergast(season, round_number)
            if results:
                self._qualifying_cache[cache_key] = results
                return results, "ergast"
        except Exception as e:
            logger.warning(f"Ergast qualifying fetch failed: {e}")
        
        # Try sprint qualifying as fallback
        try:
            results = self._get_sprint_qualifying_ergast(season, round_number)
            if results:
                self._qualifying_cache[cache_key] = results
                return results, "sprint_qualifying"
        except Exception as e:
            logger.debug(f"Sprint qualifying not available: {e}")
        
        # Return baseline data
        logger.info(f"Using baseline qualifying data for {season} R{round_number}")
        return BASELINE_QUALIFYING_POSITIONS.copy(), "baseline"
    
    def _get_qualifying_fastf1(self, season: int, round_number: int) -> Dict[str, int]:
        """Fetch qualifying from FastF1."""
        if not FASTF1_AVAILABLE:
            return {}
        
        logger.info(f"Fetching qualifying from FastF1: {season} R{round_number}")
        
        session = fastf1.get_session(season, round_number, 'Q')
        session.load()
        
        results = {}
        for _, row in session.results.iterrows():
            driver_abbrev = row.get('Abbreviation', '')
            position = row.get('Position', 0)
            
            # Convert abbreviation to full name
            full_name = DRIVER_ABBREV_TO_NAME.get(driver_abbrev)
            if full_name and position:
                results[full_name] = int(position)
        
        return results
    
    def _get_qualifying_ergast(self, season: int, round_number: int) -> Dict[str, int]:
        """Fetch qualifying from Ergast API."""
        url = f"{self.ergast_base_url}/{season}/{round_number}/qualifying.json"
        
        logger.info(f"Fetching qualifying from Ergast: {url}")
        
        try:
            response = requests.get(url, timeout=3)  # Reduced timeout for faster fallback
            response.raise_for_status()
            
            data = response.json()
            races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            
            if not races:
                return {}
            
            quali_results = races[0].get('QualifyingResults', [])
            
            results = {}
            for result in quali_results:
                driver = result.get('Driver', {})
                full_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
                position = int(result.get('position', 0))
                
                if full_name.strip() and position:
                    results[full_name] = position
            
            return results
        except requests.exceptions.Timeout:
            logger.debug(f"Ergast timeout for {season} R{round_number} - using baseline")
            return {}
        except Exception as e:
            logger.debug(f"Ergast fetch failed: {e}")
            return {}
    
    def _get_sprint_qualifying_ergast(self, season: int, round_number: int) -> Dict[str, int]:
        """Fetch sprint qualifying from Ergast API."""
        url = f"{self.ergast_base_url}/{season}/{round_number}/sprint/qualifying.json"
        
        try:
            response = requests.get(url, timeout=3)  # Fast timeout
            response.raise_for_status()
            
            data = response.json()
            races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            
            if not races:
                return {}
            
            quali_results = races[0].get('SprintQualifyingResults', [])
            
            results = {}
            for result in quali_results:
                driver = result.get('Driver', {})
                full_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
                position = int(result.get('position', 0))
                
                if full_name.strip() and position:
                    results[full_name] = position
            
            return results
        except:
            return {}
    
    def get_recent_driver_form(
        self, 
        driver_name: str, 
        n_races: int = 5
    ) -> Dict[str, Any]:
        """
        Get recent form data for a driver.
        
        Args:
            driver_name: Driver's full name
            n_races: Number of recent races to consider
        
        Returns:
            Form data dictionary
        """
        # Use baseline form for fast response (Ergast is too slow from some regions)
        return self._get_baseline_driver_form(driver_name)
    
    def _get_driver_results_ergast(
        self, 
        driver_name: str, 
        limit: int = 5
    ) -> List[Dict]:
        """Fetch recent driver results from Ergast."""
        # Convert name to Ergast driver ID format
        driver_id = driver_name.lower().replace(' ', '_')
        
        # Try common ID patterns
        possible_ids = [
            driver_id,
            driver_name.split()[-1].lower(),  # Just last name
        ]
        
        for did in possible_ids:
            try:
                url = f"{self.ergast_base_url}/drivers/{did}/results.json?limit={limit}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                    if races:
                        return races
            except Exception:
                continue
        
        return []
    
    def _calculate_driver_form(
        self, 
        driver_name: str, 
        results: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate form metrics from results."""
        positions = []
        quali_positions = []
        points = 0
        dnfs = 0
        podiums = 0
        
        for race in results[-5:]:  # Last 5 races
            race_results = race.get('Results', [])
            if race_results:
                result = race_results[0]
                pos = result.get('position', '')
                
                if pos.isdigit():
                    pos_int = int(pos)
                    positions.append(pos_int)
                    points += get_f1_points(pos_int)
                    if pos_int <= 3:
                        podiums += 1
                
                # Check for DNF
                status = result.get('status', '')
                if status and status not in ['Finished', '+1 Lap', '+2 Laps']:
                    dnfs += 1
                
                # Grid position (qualifying indicator)
                grid = result.get('grid', '')
                if grid.isdigit():
                    quali_positions.append(int(grid))
        
        avg_pos = sum(positions) / len(positions) if positions else 10.0
        avg_quali = sum(quali_positions) / len(quali_positions) if quali_positions else 10.0
        
        # Determine trend
        if len(positions) >= 3:
            recent = sum(positions[-2:]) / 2
            older = sum(positions[:-2]) / max(1, len(positions) - 2)
            if recent < older - 1:
                trend = "improving"
            elif recent > older + 1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "driver": driver_name,
            "avg_position": round(avg_pos, 1),
            "avg_qualifying": round(avg_quali, 1),
            "points_last_5": points,
            "dnf_count": dnfs,
            "podiums": podiums,
            "trend": trend,
        }
    
    def _get_baseline_driver_form(self, driver_name: str) -> Dict[str, Any]:
        """Get baseline form when real data is unavailable."""
        baseline_quali = BASELINE_QUALIFYING_POSITIONS.get(driver_name, 12.0)
        
        # Estimate other metrics from baseline qualifying
        return {
            "driver": driver_name,
            "avg_position": baseline_quali + 1,  # Race position slightly worse than quali
            "avg_qualifying": baseline_quali,
            "points_last_5": max(0, (15 - int(baseline_quali)) * 4),
            "dnf_count": 0,
            "podiums": 1 if baseline_quali <= 4 else 0,
            "trend": "stable",
        }
    
    def get_recent_constructor_form(
        self, 
        team_name: str, 
        n_races: int = 5
    ) -> Dict[str, Any]:
        """
        Get recent form data for a constructor.
        
        Args:
            team_name: Team name
            n_races: Number of recent races to consider
        
        Returns:
            Form data dictionary
        """
        # Use baseline form for fast response (Ergast is too slow from some regions)
        return self._get_baseline_constructor_form(team_name)
    
    def _get_constructor_results_ergast(
        self, 
        team_name: str, 
        limit: int = 5
    ) -> List[Dict]:
        """Fetch recent constructor results from Ergast."""
        # Try common constructor ID patterns
        constructor_id = team_name.lower().replace(' ', '_').replace('-', '_')
        
        possible_ids = [
            constructor_id,
            team_name.split()[0].lower(),  # First word
            team_name.lower().replace(' ', ''),
        ]
        
        for cid in possible_ids:
            try:
                url = f"{self.ergast_base_url}/constructors/{cid}/results.json?limit={limit * 2}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                    if races:
                        return races
            except Exception:
                continue
        
        return []
    
    def _calculate_constructor_form(
        self, 
        team_name: str, 
        results: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate constructor form metrics from results."""
        positions = []
        points = 0
        dnfs = 0
        best_result = 20
        
        for race in results[-10:]:  # 10 results = ~5 races with 2 drivers
            race_results = race.get('Results', [])
            for result in race_results:
                pos = result.get('position', '')
                
                if pos.isdigit():
                    pos_int = int(pos)
                    positions.append(pos_int)
                    points += get_f1_points(pos_int)
                    best_result = min(best_result, pos_int)
                
                # Check for DNF
                status = result.get('status', '')
                if status and status not in ['Finished', '+1 Lap', '+2 Laps']:
                    dnfs += 1
        
        avg_pos = sum(positions) / len(positions) if positions else 10.0
        reliability = 1.0 - (dnfs / max(1, len(positions)))
        
        return {
            "team": team_name,
            "avg_position": round(avg_pos, 1),
            "points_last_5": points // 2,  # Approximate 5 races
            "reliability_rate": round(reliability, 2),
            "best_result": best_result,
        }
    
    def _get_baseline_constructor_form(self, team_name: str) -> Dict[str, Any]:
        """Get baseline constructor form."""
        normalized = normalize_team_name(team_name)
        power_rank = TEAM_POWER_RANKING.get(normalized, 0.5)
        
        # Estimate position from power ranking (1.0 = position 2, 0.45 = position 10)
        estimated_pos = 2 + (1 - power_rank) * 8
        
        return {
            "team": team_name,
            "avg_position": round(estimated_pos, 1),
            "points_last_5": int((1 - (estimated_pos / 20)) * 50),
            "reliability_rate": 0.85 + (power_rank * 0.1),
            "best_result": max(1, int(estimated_pos - 2)),
        }
    
    def get_current_drivers(self) -> List[Dict[str, str]]:
        """Get list of current drivers for 2025 season."""
        drivers = []
        
        for name, team in DRIVER_TEAM_MAP_2025.items():
            abbrev = DRIVER_NAME_TO_ABBREV.get(name, name[:3].upper())
            baseline_quali = BASELINE_QUALIFYING_POSITIONS.get(name, 10.0)
            
            drivers.append({
                "name": name,
                "abbreviation": abbrev,
                "team": team,
                "baseline_qualifying": baseline_quali,
            })
        
        return sorted(drivers, key=lambda x: x['baseline_qualifying'])


# Singleton instance
_f1_data_service: Optional[F1DataService] = None


def get_f1_data_service() -> F1DataService:
    """Get the F1 data service singleton."""
    global _f1_data_service
    if _f1_data_service is None:
        _f1_data_service = F1DataService()
    return _f1_data_service

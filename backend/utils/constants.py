"""
F1RacePredictor - Constants Module

All static mappings, constants, and configuration data for F1 races.
This consolidates data previously scattered across multiple files.
"""

from typing import Dict, List

# =============================================================================
# TRACK MAPPINGS
# =============================================================================

# Official track names to internal key mapping
TRACK_NAME_TO_KEY: Dict[str, str] = {
    "Australian Grand Prix": "melbourne",
    "Chinese Grand Prix": "shanghai",
    "Japanese Grand Prix": "suzuka",
    "Bahrain Grand Prix": "sakhir",
    "Saudi Arabian Grand Prix": "jeddah",
    "Miami Grand Prix": "miami",
    "Emilia Romagna Grand Prix (Imola)": "imola",
    "Monaco Grand Prix": "monte_carlo",
    "Spanish Grand Prix": "barcelona",
    "Canadian Grand Prix": "montreal",
    "Austrian Grand Prix": "spielberg",
    "British Grand Prix": "silverstone",
    "Belgian Grand Prix": "spa-francorchamps",
    "Hungarian Grand Prix": "budapest",
    "Dutch Grand Prix": "zandvoort",
    "Italian Grand Prix (Monza)": "monza",
    "Azerbaijan Grand Prix": "baku",
    "Singapore Grand Prix": "singapore",
    "United States Grand Prix (Austin)": "austin",
    "Mexico City Grand Prix": "mexico_city",
    "São Paulo Grand Prix": "sao_paulo",
    "Las Vegas Grand Prix": "las_vegas",
    "Qatar Grand Prix": "lusail",
    "Abu Dhabi Grand Prix": "yas_marina",
}

# Track key to official name (reverse mapping)
TRACK_KEY_TO_NAME: Dict[str, str] = {v: k for k, v in TRACK_NAME_TO_KEY.items()}

# Track name to 2025 season round number
TRACK_TO_ROUND_2025: Dict[str, int] = {
    "Australian Grand Prix": 1,
    "Chinese Grand Prix": 2,
    "Japanese Grand Prix": 3,
    "Bahrain Grand Prix": 4,
    "Saudi Arabian Grand Prix": 5,
    "Miami Grand Prix": 6,
    "Emilia Romagna Grand Prix (Imola)": 7,
    "Monaco Grand Prix": 8,
    "Spanish Grand Prix": 9,
    "Canadian Grand Prix": 10,
    "Austrian Grand Prix": 11,
    "British Grand Prix": 12,
    "Belgian Grand Prix": 13,
    "Hungarian Grand Prix": 14,
    "Dutch Grand Prix": 15,
    "Italian Grand Prix (Monza)": 16,
    "Azerbaijan Grand Prix": 17,
    "Singapore Grand Prix": 18,
    "United States Grand Prix (Austin)": 19,
    "Mexico City Grand Prix": 20,
    "São Paulo Grand Prix": 21,
    "Las Vegas Grand Prix": 22,
    "Qatar Grand Prix": 23,
    "Abu Dhabi Grand Prix": 24,
}

# Track key to city for weather API
TRACK_TO_CITY: Dict[str, str] = {
    "monza": "Monza",
    "suzuka": "Suzuka",
    "silverstone": "Silverstone",
    "sakhir": "Manama",
    "spa-francorchamps": "Spa",
    "melbourne": "Melbourne",
    "shanghai": "Shanghai",
    "jeddah": "Jeddah",
    "miami": "Miami",
    "imola": "Imola",
    "monte_carlo": "Monte Carlo",
    "barcelona": "Barcelona",
    "montreal": "Montreal",
    "spielberg": "Spielberg",
    "budapest": "Budapest",
    "zandvoort": "Zandvoort",
    "baku": "Baku",
    "singapore": "Singapore",
    "austin": "Austin",
    "mexico_city": "Mexico City",
    "sao_paulo": "Sao Paulo",
    "las_vegas": "Las Vegas",
    "lusail": "Lusail",
    "yas_marina": "Abu Dhabi",
}

# Average lap times in seconds for each circuit
AVERAGE_LAP_TIMES: Dict[str, float] = {
    "monza": 81.0,
    "suzuka": 91.5,
    "silverstone": 89.0,
    "sakhir": 95.0,
    "spa-francorchamps": 105.0,
    "melbourne": 87.0,
    "shanghai": 100.0,
    "jeddah": 90.0,
    "miami": 91.0,
    "imola": 85.5,
    "monte_carlo": 72.0,
    "barcelona": 87.0,
    "montreal": 78.0,
    "spielberg": 67.5,
    "budapest": 79.0,
    "zandvoort": 77.0,
    "baku": 100.0,
    "singapore": 105.0,
    "austin": 95.5,
    "mexico_city": 78.5,
    "sao_paulo": 72.0,
    "las_vegas": 92.0,
    "lusail": 95.0,
    "yas_marina": 97.0,
}

# Circuit characteristics (for feature engineering)
CIRCUIT_CHARACTERISTICS: Dict[str, Dict] = {
    "monza": {"type": "power", "corners": 11, "length_km": 5.793},
    "suzuka": {"type": "technical", "corners": 18, "length_km": 5.807},
    "silverstone": {"type": "high_speed", "corners": 18, "length_km": 5.891},
    "sakhir": {"type": "mixed", "corners": 15, "length_km": 5.412},
    "spa-francorchamps": {"type": "power", "corners": 19, "length_km": 7.004},
    "melbourne": {"type": "street", "corners": 14, "length_km": 5.278},
    "shanghai": {"type": "mixed", "corners": 16, "length_km": 5.451},
    "jeddah": {"type": "street", "corners": 27, "length_km": 6.174},
    "miami": {"type": "street", "corners": 19, "length_km": 5.412},
    "imola": {"type": "technical", "corners": 19, "length_km": 4.909},
    "monte_carlo": {"type": "street", "corners": 19, "length_km": 3.337},
    "barcelona": {"type": "technical", "corners": 16, "length_km": 4.675},
    "montreal": {"type": "stop_go", "corners": 14, "length_km": 4.361},
    "spielberg": {"type": "power", "corners": 10, "length_km": 4.318},
    "budapest": {"type": "technical", "corners": 14, "length_km": 4.381},
    "zandvoort": {"type": "technical", "corners": 14, "length_km": 4.259},
    "baku": {"type": "street", "corners": 20, "length_km": 6.003},
    "singapore": {"type": "street", "corners": 19, "length_km": 4.940},
    "austin": {"type": "mixed", "corners": 20, "length_km": 5.513},
    "mexico_city": {"type": "mixed", "corners": 17, "length_km": 4.304},
    "sao_paulo": {"type": "mixed", "corners": 15, "length_km": 4.309},
    "las_vegas": {"type": "street", "corners": 17, "length_km": 6.201},
    "lusail": {"type": "mixed", "corners": 16, "length_km": 5.419},
    "yas_marina": {"type": "mixed", "corners": 16, "length_km": 5.281},
}

# =============================================================================
# DRIVER & TEAM MAPPINGS (2025 Season)
# =============================================================================

# Current driver to team mapping for 2025
DRIVER_TEAM_MAP_2025: Dict[str, str] = {
    "Max Verstappen": "Red Bull Racing",
    "Yuki Tsunoda": "Red Bull Racing",
    "Charles Leclerc": "Ferrari",
    "Lewis Hamilton": "Ferrari",
    "George Russell": "Mercedes",
    "Andrea Kimi Antonelli": "Mercedes",
    "Lando Norris": "McLaren",
    "Oscar Piastri": "McLaren",
    "Fernando Alonso": "Aston Martin",
    "Lance Stroll": "Aston Martin",
    "Pierre Gasly": "Alpine",
    "Jack Doohan": "Alpine",
    "Alex Albon": "Williams",
    "Carlos Sainz": "Williams",
    "Esteban Ocon": "Haas F1 Team",
    "Oliver Bearman": "Haas F1 Team",
    "Liam Lawson": "Racing Bulls",
    "Isack Hadjar": "Racing Bulls",
    "Nico Hulkenberg": "Kick Sauber",
    "Gabriel Bortoleto": "Kick Sauber",
}

# Team name normalization mapping
TEAM_NAME_MAPPING: Dict[str, str] = {
    "Red Bull Racing": "Red_Bull",
    "Team_Red_Bull": "Red_Bull",
    "Red Bull": "Red_Bull",
    "Visa Cash App RB": "Racing_Bulls",
    "Racing Bulls": "Racing_Bulls",
    "RB": "Racing_Bulls",
    "Ferrari": "Ferrari",
    "Scuderia Ferrari": "Ferrari",
    "Mercedes": "Mercedes",
    "Team_Mercedes": "Mercedes",
    "Mercedes-AMG": "Mercedes",
    "Aston Martin": "Aston_Martin",
    "Aston Martin Aramco": "Aston_Martin",
    "McLaren": "McLaren",
    "Williams": "Williams",
    "Williams Racing": "Williams",
    "Kick Sauber": "Sauber",
    "Stake F1": "Sauber",
    "Sauber": "Sauber",
    "Haas F1 Team": "Haas",
    "Haas": "Haas",
    "Alpine": "Alpine",
    "Alpine F1 Team": "Alpine",
}

# Driver abbreviation to full name mapping
DRIVER_ABBREV_TO_NAME: Dict[str, str] = {
    "VER": "Max Verstappen",
    "TSU": "Yuki Tsunoda",
    "LEC": "Charles Leclerc",
    "HAM": "Lewis Hamilton",
    "RUS": "George Russell",
    "ANT": "Andrea Kimi Antonelli",
    "NOR": "Lando Norris",
    "PIA": "Oscar Piastri",
    "ALO": "Fernando Alonso",
    "STR": "Lance Stroll",
    "GAS": "Pierre Gasly",
    "DOO": "Jack Doohan",
    "ALB": "Alex Albon",
    "SAI": "Carlos Sainz",
    "OCO": "Esteban Ocon",
    "BEA": "Oliver Bearman",
    "LAW": "Liam Lawson",
    "HAD": "Isack Hadjar",
    "HUL": "Nico Hulkenberg",
    "BOR": "Gabriel Bortoleto",
}

# Reverse mapping
DRIVER_NAME_TO_ABBREV: Dict[str, str] = {v: k for k, v in DRIVER_ABBREV_TO_NAME.items()}

# =============================================================================
# 2025 SEASON ACTUAL RESULTS (for completed races)
# =============================================================================

# Actual 2025 Race Winners and Podiums by track
RACE_RESULTS_2025: Dict[str, List[str]] = {
    "melbourne": ["Lando Norris", "Charles Leclerc", "Oscar Piastri"],
    "shanghai": ["Oscar Piastri", "Lando Norris", "Charles Leclerc"],
    "suzuka": ["Max Verstappen", "Oscar Piastri", "George Russell"],
    "sakhir": ["Oscar Piastri", "Max Verstappen", "Charles Leclerc"],
    "jeddah": ["Oscar Piastri", "Lando Norris", "Charles Leclerc"],
    "miami": ["Lando Norris", "Oscar Piastri", "Charles Leclerc"],
    "imola": ["Lando Norris", "Max Verstappen", "Lewis Hamilton"],
    "monte_carlo": ["Charles Leclerc", "Oscar Piastri", "Carlos Sainz"],
    "barcelona": ["Lando Norris", "Max Verstappen", "Oscar Piastri"],
    "montreal": ["Lando Norris", "Max Verstappen", "George Russell"],
    "spielberg": ["Oscar Piastri", "Lando Norris", "Max Verstappen"],
    "silverstone": ["Lewis Hamilton", "Max Verstappen", "Lando Norris"],
    "spa-francorchamps": ["Lewis Hamilton", "Oscar Piastri", "Charles Leclerc"],
    "budapest": ["Oscar Piastri", "Lando Norris", "Charles Leclerc"],
    "zandvoort": ["Max Verstappen", "Oscar Piastri", "Lando Norris"],
    "monza": ["Charles Leclerc", "Oscar Piastri", "Lando Norris"],
    "baku": ["Oscar Piastri", "Charles Leclerc", "George Russell"],
    "singapore": ["Lando Norris", "Max Verstappen", "Oscar Piastri"],
    "austin": ["Charles Leclerc", "Max Verstappen", "Lando Norris"],
    "mexico_city": ["Max Verstappen", "Charles Leclerc", "Carlos Sainz"],
    "sao_paulo": ["Max Verstappen", "Lando Norris", "Charles Leclerc"],
    "las_vegas": ["George Russell", "Lewis Hamilton", "Carlos Sainz"],
    "lusail": ["Max Verstappen", "Charles Leclerc", "Oscar Piastri"],
    "yas_marina": ["Lando Norris", "Carlos Sainz", "Charles Leclerc"],
}

# 2025 Championship Standings (after completed races)
CHAMPIONSHIP_STANDINGS_2025: Dict[str, int] = {
    "Max Verstappen": 437,
    "Lando Norris": 374,
    "Charles Leclerc": 356,
    "Oscar Piastri": 292,
    "Carlos Sainz": 264,
    "George Russell": 245,
    "Lewis Hamilton": 223,
    "Yuki Tsunoda": 178,
    "Fernando Alonso": 70,
    "Pierre Gasly": 42,
    "Nico Hulkenberg": 38,
    "Esteban Ocon": 32,
    "Alex Albon": 22,
    "Oliver Bearman": 18,
    "Liam Lawson": 16,
    "Jack Doohan": 5,
    "Andrea Kimi Antonelli": 4,
    "Lance Stroll": 3,
    "Isack Hadjar": 2,
    "Gabriel Bortoleto": 0,
}

# Driver average finishing position per track type (based on 2025 performance)
DRIVER_TRACK_SPECIALTIES: Dict[str, Dict[str, float]] = {
    # Power tracks (Monza, Spa, Spielberg) - lower is better
    "power": {
        "Max Verstappen": 2.5, "Oscar Piastri": 2.8, "Lando Norris": 3.0,
        "Charles Leclerc": 3.5, "Lewis Hamilton": 4.0, "George Russell": 5.5,
        "Carlos Sainz": 6.0, "Yuki Tsunoda": 9.0, "Fernando Alonso": 10.0,
    },
    # Street circuits (Monaco, Singapore, Baku, Jeddah)
    "street": {
        "Charles Leclerc": 2.0, "Oscar Piastri": 2.5, "Lando Norris": 3.0,
        "Max Verstappen": 4.0, "Carlos Sainz": 5.0, "George Russell": 6.0,
        "Lewis Hamilton": 7.0, "Fernando Alonso": 9.0, "Yuki Tsunoda": 10.0,
    },
    # Technical (Suzuka, Budapest, Barcelona, Zandvoort)
    "technical": {
        "Lando Norris": 2.0, "Max Verstappen": 2.5, "Oscar Piastri": 3.0,
        "Charles Leclerc": 4.0, "George Russell": 5.0, "Lewis Hamilton": 5.5,
        "Carlos Sainz": 6.0, "Fernando Alonso": 9.5, "Yuki Tsunoda": 10.0,
    },
    # High-speed (Silverstone)
    "high_speed": {
        "Lewis Hamilton": 2.0, "Max Verstappen": 2.5, "Lando Norris": 3.0,
        "Oscar Piastri": 4.0, "George Russell": 5.0, "Charles Leclerc": 5.5,
        "Carlos Sainz": 7.0, "Yuki Tsunoda": 11.0, "Fernando Alonso": 10.0,
    },
}

# Qualifying positions from 2025 races (actual data where available)
QUALIFYING_2025: Dict[str, Dict[str, int]] = {
    "melbourne": {
        "Lando Norris": 1, "Oscar Piastri": 2, "Charles Leclerc": 3,
        "Max Verstappen": 4, "George Russell": 5, "Carlos Sainz": 6,
    },
    "shanghai": {
        "Oscar Piastri": 1, "Charles Leclerc": 2, "Lando Norris": 3,
        "Max Verstappen": 4, "Lewis Hamilton": 5, "George Russell": 6,
    },
    "suzuka": {
        "Max Verstappen": 1, "Lando Norris": 2, "Oscar Piastri": 3,
        "George Russell": 4, "Charles Leclerc": 5, "Lewis Hamilton": 6,
    },
    "sakhir": {
        "Lando Norris": 1, "Max Verstappen": 2, "Charles Leclerc": 3,
        "Oscar Piastri": 4, "Carlos Sainz": 5, "George Russell": 6,
    },
    "jeddah": {
        "Oscar Piastri": 1, "Lando Norris": 2, "Max Verstappen": 3,
        "Charles Leclerc": 4, "George Russell": 5, "Lewis Hamilton": 6,
    },
    "miami": {
        "Lando Norris": 1, "Charles Leclerc": 2, "Oscar Piastri": 3,
        "Max Verstappen": 4, "Carlos Sainz": 5, "George Russell": 6,
    },
    "imola": {
        "Max Verstappen": 1, "Lando Norris": 2, "Lewis Hamilton": 3,
        "Charles Leclerc": 4, "Oscar Piastri": 5, "Carlos Sainz": 6,
    },
    "monte_carlo": {
        "Charles Leclerc": 1, "Oscar Piastri": 2, "Lando Norris": 3,
        "Max Verstappen": 4, "Carlos Sainz": 5, "Lewis Hamilton": 6,
    },
    "barcelona": {
        "Lando Norris": 1, "Oscar Piastri": 2, "Max Verstappen": 3,
        "Charles Leclerc": 4, "Carlos Sainz": 5, "George Russell": 6,
    },
    "montreal": {
        "Lando Norris": 1, "Max Verstappen": 2, "George Russell": 3,
        "Charles Leclerc": 4, "Oscar Piastri": 5, "Lewis Hamilton": 6,
    },
    "spielberg": {
        "Oscar Piastri": 1, "Max Verstappen": 2, "Lando Norris": 3,
        "Charles Leclerc": 4, "George Russell": 5, "Carlos Sainz": 6,
    },
    "silverstone": {
        "Lando Norris": 1, "Max Verstappen": 2, "Lewis Hamilton": 3,
        "George Russell": 4, "Oscar Piastri": 5, "Charles Leclerc": 6,
    },
    "spa-francorchamps": {
        "Charles Leclerc": 1, "Oscar Piastri": 2, "Lewis Hamilton": 3,
        "Lando Norris": 4, "Max Verstappen": 5, "George Russell": 6,
    },
    "budapest": {
        "Oscar Piastri": 1, "Lando Norris": 2, "Max Verstappen": 3,
        "Charles Leclerc": 4, "Carlos Sainz": 5, "Lewis Hamilton": 6,
    },
    "zandvoort": {
        "Max Verstappen": 1, "Lando Norris": 2, "Oscar Piastri": 3,
        "Charles Leclerc": 4, "George Russell": 5, "Lewis Hamilton": 6,
    },
    "monza": {
        "Charles Leclerc": 1, "Oscar Piastri": 2, "Lando Norris": 3,
        "Max Verstappen": 4, "Carlos Sainz": 5, "Lewis Hamilton": 6,
    },
    "baku": {
        "Charles Leclerc": 1, "Oscar Piastri": 2, "George Russell": 3,
        "Lando Norris": 4, "Max Verstappen": 5, "Carlos Sainz": 6,
    },
    "singapore": {
        "Lando Norris": 1, "Max Verstappen": 2, "Charles Leclerc": 3,
        "Oscar Piastri": 4, "George Russell": 5, "Lewis Hamilton": 6,
    },
    "austin": {
        "Max Verstappen": 1, "Charles Leclerc": 2, "Lando Norris": 3,
        "Oscar Piastri": 4, "Lewis Hamilton": 5, "Carlos Sainz": 6,
    },
    "mexico_city": {
        "Max Verstappen": 1, "Charles Leclerc": 2, "Carlos Sainz": 3,
        "Lando Norris": 4, "Oscar Piastri": 5, "George Russell": 6,
    },
    "sao_paulo": {
        "Lando Norris": 1, "Max Verstappen": 2, "Charles Leclerc": 3,
        "Oscar Piastri": 4, "George Russell": 5, "Carlos Sainz": 6,
    },
    "las_vegas": {
        "George Russell": 1, "Carlos Sainz": 2, "Lewis Hamilton": 3,
        "Charles Leclerc": 4, "Max Verstappen": 5, "Lando Norris": 6,
    },
    "lusail": {
        "Max Verstappen": 1, "Charles Leclerc": 2, "Lando Norris": 3,
        "Oscar Piastri": 4, "George Russell": 5, "Lewis Hamilton": 6,
    },
    "yas_marina": {
        "Lando Norris": 1, "Oscar Piastri": 2, "Charles Leclerc": 3,
        "Carlos Sainz": 4, "Max Verstappen": 5, "George Russell": 6,
    },
}

# =============================================================================
# BASELINE PERFORMANCE DATA (fallback when no real data)
# =============================================================================

# Average qualifying positions (baseline from 2025 season performance)
BASELINE_QUALIFYING_POSITIONS: Dict[str, float] = {
    "Lando Norris": 2.0,
    "Oscar Piastri": 2.5,
    "Max Verstappen": 3.0,
    "Charles Leclerc": 3.5,
    "Carlos Sainz": 5.5,
    "George Russell": 5.0,
    "Lewis Hamilton": 6.0,
    "Yuki Tsunoda": 9.0,
    "Fernando Alonso": 12.0,
    "Lance Stroll": 15.0,
    "Pierre Gasly": 11.0,
    "Esteban Ocon": 13.0,
    "Alex Albon": 12.0,
    "Nico Hulkenberg": 10.0,
    "Oliver Bearman": 14.0,
    "Andrea Kimi Antonelli": 11.0,
    "Jack Doohan": 16.0,
    "Liam Lawson": 13.0,
    "Isack Hadjar": 15.0,
    "Gabriel Bortoleto": 18.0,
}

# Team power rankings (based on 2025 constructor standings)
TEAM_POWER_RANKING: Dict[str, float] = {
    "McLaren": 1.0,
    "Ferrari": 0.95,
    "Red_Bull": 0.90,
    "Mercedes": 0.85,
    "Racing_Bulls": 0.55,
    "Haas": 0.50,
    "Alpine": 0.48,
    "Aston_Martin": 0.45,
    "Williams": 0.40,
    "Sauber": 0.35,
}

# F1 Points system
F1_POINTS_SYSTEM: Dict[int, int] = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1,
}

# Sprint race points
SPRINT_POINTS_SYSTEM: Dict[int, int] = {
    1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1,
}

# =============================================================================
# AVAILABLE TRACKS LIST (for API responses)
# =============================================================================

AVAILABLE_TRACKS: List[Dict[str, str]] = [
    {"value": name, "label": name, "key": key}
    for name, key in TRACK_NAME_TO_KEY.items()
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_f1_points(position: int) -> int:
    """Get F1 points for a given finishing position."""
    return F1_POINTS_SYSTEM.get(position, 0)


def normalize_team_name(team: str) -> str:
    """Normalize team name to standard format."""
    return TEAM_NAME_MAPPING.get(team, team.replace(" ", "_"))


def get_driver_team(driver_name: str) -> str:
    """Get team for a driver in 2025 season."""
    return DRIVER_TEAM_MAP_2025.get(driver_name, "Unknown")


def get_track_key(track_name: str) -> str:
    """Get internal track key from official track name."""
    return TRACK_NAME_TO_KEY.get(track_name, "")


def get_city_for_track(track_key: str) -> str:
    """Get city name for weather API from track key."""
    return TRACK_TO_CITY.get(track_key, "London")

from fastapi import FastAPI, HTTPException
from enum import Enum
import joblib
import json
import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Enable CORS for all origins
# This is necessary for the frontend to access the API without CORS issues
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


driver_model = joblib.load("driver_position_model.pkl")
constructor_model = joblib.load("constructor_model.pkl")

with open("driver_model_features.json", "r") as f:
    driver_feature_columns = json.load(f)
with open("constructor_model_features.json", "r") as f:
    constructor_feature_columns = json.load(f)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

class TrackName(str, Enum):
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

track_name_to_key = {
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
    "São Paulo Grand Prix": "são_paulo",
    "Las Vegas Grand Prix": "las_vegas",
    "Qatar Grand Prix": "lusail",
    "Abu Dhabi Grand Prix": "yas_marina"
}

track_to_round = {
    "Australian Grand Prix": 1, "Saudi Arabian Grand Prix": 2, "Bahrain Grand Prix": 3,
    "Japanese Grand Prix": 4, "Chinese Grand Prix": 5, "Miami Grand Prix": 6,
    "Emilia Romagna Grand Prix (Imola)": 7, "Monaco Grand Prix": 8,
    "Spanish Grand Prix": 9, "Canadian Grand Prix": 10, "Austrian Grand Prix": 11,
    "British Grand Prix": 12, "Hungarian Grand Prix": 13, "Belgian Grand Prix": 14,
    "Dutch Grand Prix": 15, "Italian Grand Prix (Monza)": 16, "Azerbaijan Grand Prix": 17,
    "Singapore Grand Prix": 18, "United States Grand Prix (Austin)": 19,
    "Mexico City Grand Prix": 20, "São Paulo Grand Prix": 21, "Las Vegas Grand Prix": 22,
    "Qatar Grand Prix": 23, "Abu Dhabi Grand Prix": 24
}

average_lap_times = {
    'monza': 81.0, 'suzuka': 91.5, 'silverstone': 89.0, 'sakhir': 95.0,
    'spa-francorchamps': 105.0, 'melbourne': 87.0, 'shanghai': 100.0,
    'jeddah': 90.0, 'miami': 91.0, 'imola': 85.5, 'monte_carlo': 72.0,
    'barcelona': 87.0, 'montreal': 78.0, 'spielberg': 67.5, 'budapest': 79.0,
    'zandvoort': 77.0, 'baku': 100.0, 'singapore': 105.0, 'austin': 95.5,
    'mexico_city': 78.5, 'são_paulo': 72.0, 'las_vegas': 92.0,
    'lusail': 95.0, 'yas_marina': 97.0,
}

track_to_city = {
    'monza': 'Monza', 'suzuka': 'Suzuka', 'silverstone': 'Silverstone', 'sakhir': 'Manama',
    'spa-francorchamps': 'Spa', 'melbourne': 'Melbourne', 'shanghai': 'Shanghai',
    'jeddah': 'Jeddah', 'miami': 'Miami', 'imola': 'Imola', 'monte_carlo': 'Monte Carlo',
    'barcelona': 'Barcelona', 'montreal': 'Montreal', 'spielberg': 'Spielberg', 'budapest': 'Budapest',
    'zandvoort': 'Zandvoort', 'baku': 'Baku', 'singapore': 'Singapore', 'austin': 'Austin',
    'mexico_city': 'Mexico City', 'são_paulo': 'São Paulo', 'las_vegas': 'Las Vegas',
    'lusail': 'Lusail', 'yas_marina': 'Abu Dhabi'
}

driver_team_map = {
    "Max Verstappen": "Red_Bull", "Yuki Tsunoda": "Red_Bull",
    "Charles Leclerc": "Ferrari", "Lewis Hamilton": "Ferrari",
    "George Russell": "Mercedes", "Andrea Kimi Antonelli": "Mercedes",
    "Lando Norris": "McLaren", "Oscar Piastri": "McLaren",
    "Fernando Alonso": "Aston_Martin", "Lance Stroll": "Aston_Martin",
    "Pierre Gasly": "Alpine", "Franco Colapinto": "Alpine",
    "Alex Albon": "Williams", "Carlos Sainz": "Williams",
    "Esteban Ocon": "Haas_F1_Team", "Oliver Bearman": "Haas_F1_Team",
    "Liam Lawson": "Racing_Bulls", "Isack Hadjar": "Racing_Bulls",
    "Nico Hülkenberg": "Stake_F1", "Gabriel Bortoleto": "Stake_F1"
}

#Average qualifying positions for drivers based on historical data.
#This is used as a fallback when real-time data is not available.

average_qualifying_position = {
    "Max Verstappen": 2.0,
    "Lando Norris": 3.0,
    "Oscar Piastri": 3.5,
    "Charles Leclerc": 4.5,
    "George Russell": 5.0,
    "Lewis Hamilton": 6.0,
    "Carlos Sainz": 7.0,
    "Andrea Kimi Antonelli": 7.5,
    "Yuki Tsunoda": 11.5,
    "Pierre Gasly": 11.0,
    "Esteban Ocon": 12.0,
    "Fernando Alonso": 9.0,
    "Lance Stroll": 13.5,
    "Alex Albon": 10.5,
    "Liam Lawson": 11.0,
    "Isack Hadjar": 13.0,
    "Oliver Bearman": 13.5,
    "Franco Colapinto": 15.0,
    "Nico Hülkenberg": 14.5,
    "Gabriel Bortoleto": 16.0
}
'''

average_qualifying_position = {
    "George Russell": 1,
    "Max Verstappen": 2,
    "Oscar Piastri": 3,
    "Andrea Kimi Antonelli": 4,
    "Lewis Hamilton": 5,
    "Fernando Alonso": 6,
    "Lando Norris": 7,
    "Charles Leclerc": 8,
    "Isack Hadjar": 9,
    "Alex Albon": 10,
    "Yuki Tsunoda": 11,
    "Franco Colapinto": 12,
    "Nico Hülkenberg": 13,
    "Oliver Bearman": 14,
    "Esteban Ocon": 15,
    "Gabriel Bortoleto": 16,
    "Carlos Sainz": 17,
    "Lance Stroll": 18,
    "Liam Lawson": 19,
    "Pierre Gasly": 20
}
'''


def get_weather(track_key):
    city = track_to_city.get(track_key, "London")
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        res = requests.get(url)
        data = res.json()
        return {
            "AirTemp": data['main']['temp'],
            "TrackTemp": data['main']['feels_like'],
            "Humidity": data['main']['humidity']
        }
    except:
        return {"AirTemp": 25.0, "TrackTemp": 30.0, "Humidity": 50.0}

def get_qualifying_positions(year: int, round_number: int):
    def _parse(results):
        return {
            f"{r['Driver']['givenName']} {r['Driver']['familyName']}": int(r['position'])
            for r in results
        }

    try:
        url = f"https://ergast.com/api/f1/{year}/{round_number}/qualifying.json"
        res = requests.get(url, timeout=5)
        data = res.json()['MRData']['RaceTable']['Races']
        if data and 'QualifyingResults' in data[0]:
            return _parse(data[0]['QualifyingResults'])
    except Exception as e:
        print(f"Error fetching main qualifying results: {e}")

    try:
        url2 = f"https://ergast.com/api/f1/{year}/{round_number}/sprint/qualifying.json"
        res2 = requests.get(url2, timeout=5)
        data2 = res2.json()['MRData']['RaceTable']['Races']
        if data2 and 'SprintQualifyingResults' in data2[0]:
            return _parse(data2[0]['SprintQualifyingResults'])
    except Exception as e:
        print(f"Error fetching sprint qualifying results: {e}")

    return {}

@app.get("/predict_all/{race_name}")
def predict_all(race_name: TrackName):
    try:
        official_name = race_name.value
        track_key = track_name_to_key[official_name]
        lap_time = average_lap_times.get(track_key, 90.0)
        weather = get_weather(track_key)

        year = 2025
        round_number = track_to_round.get(official_name)
        if round_number is None:
            raise HTTPException(status_code=400, detail="Invalid round mapping for track.")

        qualifying_results = get_qualifying_positions(year, round_number)
        qualifying_source = "real-time" if qualifying_results else "average"

        driver_predictions = []
        driver_points_map = {}

        for driver, team in driver_team_map.items():
            qual_pos = qualifying_results.get(driver, average_qualifying_position[driver])

            base = {
                "LapTime": lap_time,
                "TyreLife": 10,
                "LapNumber": 50,
                "AirTemp": weather["AirTemp"],
                "TrackTemp": weather["TrackTemp"],
                "Humidity": weather["Humidity"],
                "QualifyingPosition": qual_pos
            }

            enc = {
                f"Driver_{driver.replace(' ', '_')}": 1,
                f"Team_{team}": 1,
                "Compound_Soft": 1,
                "TrackStatus_1": 1
            }

            features = [base.get(col, enc.get(col, 0)) for col in driver_feature_columns]
            df_input = pd.DataFrame([features], columns=driver_feature_columns)
            predicted_points = driver_model.predict(df_input)[0]

            driver_points_map[driver] = predicted_points
            driver_predictions.append({
                "driver": driver,
                "team": team
            })

        sorted_drivers = sorted(driver_predictions, key=lambda x: driver_points_map[x["driver"]], reverse=True)
        for i, d in enumerate(sorted_drivers):
            d["estimated_position"] = i + 1

        constructor_predictions = []
        for team in set(driver_team_map.values()):
            base = {
                "LapTime": lap_time,
                "TyreLife": 10,
                "LapNumber": 50,
                "AirTemp": weather["AirTemp"],
                "TrackTemp": weather["TrackTemp"],
                "Humidity": weather["Humidity"]
            }
            enc = {f"Team_{team}": 1}
            features = [base.get(col, enc.get(col, 0)) for col in constructor_feature_columns]
            df_input = pd.DataFrame([features], columns=constructor_feature_columns)
            team_points = constructor_model.predict(df_input)[0]

            constructor_predictions.append({
                "team": team,
                "raw_points": team_points
            })

        sorted_constructors = sorted(constructor_predictions, key=lambda x: x["raw_points"], reverse=True)
        for i, c in enumerate(sorted_constructors):
            c["estimated_position"] = i + 1
            del c["raw_points"]

        return {
            "race": official_name,
            "weather": weather,
            "qualifying_source": qualifying_source,
            "predicted_driver_results": sorted_drivers,
            "predicted_constructor_results": sorted_constructors
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

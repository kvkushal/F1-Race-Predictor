import fastf1
import pandas as pd
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Enable FastF1 cache
fastf1.Cache.enable_cache('f1_cache')

# Mapping circuits to cities for weather API
circuit_to_city = {
    'melbourne': 'Melbourne',
    'shanghai': 'Shanghai',
    'suzuka': 'Suzuka',
    'sakhir': 'Manama',
    'jeddah': 'Jeddah',
    'miami': 'Miami',
    'imola': 'Imola',
    'monte_carlo': 'Monte Carlo',
    'barcelona': 'Barcelona',
    'montreal': 'Montreal',
    'spielberg': 'Spielberg',
    'silverstone': 'Silverstone',
    'spa-francorchamps': 'Spa',
    'budapest': 'Budapest',
    'zandvoort': 'Zandvoort',
    'monza': 'Monza',
    'baku': 'Baku',
    'singapore': 'Singapore',
    'austin': 'Austin',
    'mexico_city': 'Mexico City',
    'são_paulo': 'São Paulo',
    'las_vegas': 'Las Vegas',
    'lusail': 'Lusail',
    'yas_marina': 'Abu Dhabi'
}

# Average Qualifying fallback
def get_average_qualifying_position(laps_df):
    try:
        return (
            laps_df.groupby("DriverNumber")["Position"]
            .mean().round().reset_index()
            .rename(columns={"Position": "QualifyingPosition"})
        )
    except:
        return pd.DataFrame()

# Try real qualifying positions
def get_qualifying_positions(year, circuit, laps_df):
    try:
        qualifying = fastf1.get_session(year, circuit, 'Q')
        qualifying.load()
        results = qualifying.results[['DriverNumber', 'Position']]
        results = results.rename(columns={'Position': 'QualifyingPosition'})
        return results
    except:
        print(f"⚠️ Qualifying not available for {circuit} {year}, using fallback average.")
        return get_average_qualifying_position(laps_df)

# Get real-time weather data
def get_realtime_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        return {
            "AirTemp": data['main']['temp'],
            "TrackTemp": data['main']['feels_like'],  # Approximate
            "Humidity": data['main']['humidity']
        }
    except Exception as e:
        print(f"⚠️ Failed to fetch weather for {city}: {e}")
        return {
            "AirTemp": 25.0,
            "TrackTemp": 30.0,
            "Humidity": 50.0
        }

# Collect race session data
def collect_race_data(year, circuit, session_type='R'):
    try:
        session = fastf1.get_session(year, circuit, session_type)
        session.load()

        laps = session.laps
        laps = laps[laps['LapTime'].notnull()]
        laps = laps[laps['IsAccurate'] == True]

        # Get weather
        city = circuit_to_city.get(circuit.lower().replace(" ", "_"), "London")
        weather_info = get_realtime_weather(city)
        for key, value in weather_info.items():
            laps[key] = value

        # Add qualifying info
        qualifying_df = get_qualifying_positions(year, circuit, laps)
        laps['DriverNumber'] = laps['DriverNumber'].astype(str)
        qualifying_df['DriverNumber'] = qualifying_df['DriverNumber'].astype(str)
        laps = laps.merge(qualifying_df, on='DriverNumber', how='left')

        # Select and export columns
        data = laps[[
            'Driver', 'DriverNumber', 'Team', 'LapNumber', 'LapTime',
            'Compound', 'TyreLife', 'TrackStatus', 'IsPersonalBest',
            'Position', 'PitInTime', 'PitOutTime', 'QualifyingPosition',
            'AirTemp', 'TrackTemp', 'Humidity'
        ]]
        data['LapTime'] = data['LapTime'].dt.total_seconds()

        race_file = f"race_data_{circuit.lower().replace(' ', '_')}_{year}.csv"
        data.to_csv(race_file, index=False)
        print(f"✅ Saved: {race_file}")
        return True

    except Exception as e:
        print(f"❌ Failed to process {circuit} {year}: {e}")
        return False

# Run the script
if __name__ == "__main__":
    races_2025 = [
        'Melbourne', 'Shanghai', 'Suzuka', 'Sakhir', 'Jeddah', 'Miami', 'Imola',
        'Monte Carlo', 'Barcelona', 'Montreal', 'Spielberg', 'Silverstone',
        'Spa-Francorchamps', 'Budapest', 'Zandvoort', 'Monza', 'Baku', 'Singapore',
        'Austin', 'Mexico City', 'São Paulo', 'Las Vegas', 'Lusail', 'Yas Marina'
    ]

    successes, failures = [], []

    for circuit in races_2025:
        if collect_race_data(2025, circuit):
            successes.append(circuit)
        else:
            failures.append(circuit)

    print("\n✅ Successful:", successes)
    print("❌ Failed:", failures)

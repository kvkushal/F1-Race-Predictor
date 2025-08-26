import os
import pandas as pd
from glob import glob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import json
import requests
from dotenv import load_dotenv

# Load OpenWeatherMap API key
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# F1 Points for positions 1–10
def get_f1_points(pos):
    f1_points = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    return f1_points.get(int(pos), 0)

# Correct team name mapping for 2025 season
team_mapping = {
    "Red Bull Racing": "Red_Bull",
    "Team_Red_Bull": "Red_Bull",
    "Visa Cash App RB": "Racing_Bulls",
    "Racing Bulls": "Racing_Bulls",
    "RB": "Racing_Bulls",
    "Ferrari": "Ferrari",
    "Mercedes": "Mercedes",
    "Team_Mercedes": "Mercedes",
    "Aston Martin": "Aston_Martin",
    "McLaren": "McLaren",
    "Williams": "Williams",
    "Kick Sauber": "Sauber",
    "Stake F1": "Sauber",
    "Sauber": "Sauber",
    "Haas F1 Team": "Haas",
    "Haas": "Haas",
    "Alpine": "Alpine"
}

# Circuit to city mapping for real-time weather
circuit_to_city = {
    'melbourne': 'Melbourne', 'shanghai': 'Shanghai', 'suzuka': 'Suzuka',
    'sakhir': 'Manama', 'jeddah': 'Jeddah', 'miami': 'Miami',
    'imola': 'Imola', 'monte_carlo': 'Monte Carlo', 'barcelona': 'Barcelona',
    'montreal': 'Montreal', 'spielberg': 'Spielberg', 'silverstone': 'Silverstone',
    'spa-francorchamps': 'Spa', 'budapest': 'Budapest', 'zandvoort': 'Zandvoort',
    'monza': 'Monza', 'baku': 'Baku', 'singapore': 'Singapore', 'austin': 'Austin',
    'mexico_city': 'Mexico City', 'são_paulo': 'São Paulo', 'las_vegas': 'Las Vegas',
    'lusail': 'Lusail', 'yas_marina': 'Abu Dhabi'
}

# Fetch weather from OpenWeatherMap
def get_weather_for_race(race_name):
    circuit_key = race_name.split("_")[0].lower()  # e.g., "melbourne"
    city = circuit_to_city.get(circuit_key, "London")
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        res = requests.get(url, timeout=5)
        data = res.json()
        return data['main']['temp'], data['main']['feels_like'], data['main']['humidity']
    except:
        print(f"⚠️ Failed to fetch weather for {city}, using fallback values.")
        return 25.0, 30.0, 50.0

# 1. Load race CSVs and merge weather dynamically
def load_and_prepare_data():
    race_files = glob("race_data_*.csv")
    all_data = []

    for race_file in race_files:
        race_name = race_file.replace("race_data_", "").replace(".csv", "")
        df = pd.read_csv(race_file)

        if df.empty:
            print(f"⚠️ Empty race data in {race_name}, skipping.")
            continue

        # Get real-time weather
        air, track, hum = get_weather_for_race(race_name)
        df['AirTemp'] = air
        df['TrackTemp'] = track
        df['Humidity'] = hum

        df['Race'] = race_name
        all_data.append(df)

    if not all_data:
        raise ValueError("❌ No valid race data to train on.")

    return pd.concat(all_data, ignore_index=True)

# 2. Preprocess data for per-race, per-constructor points
def preprocess(data):
    data = data.dropna(subset=['LapTime', 'Team', 'Driver', 'Position']).copy()

    # Normalize team names
    data['Team'] = data['Team'].replace(team_mapping)

    # Keep only last lap per driver per race
    data = data.sort_values(['Race', 'Driver', 'LapNumber']).groupby(['Race', 'Driver'], as_index=False).last()

    # Calculate points
    data['Points'] = data['Position'].apply(get_f1_points)

    print("🔍 Unique Teams After Mapping:", sorted(data['Team'].unique()))

    # Group by Race & Team (sum points)
    grouped = data.groupby(['Race', 'Team']).agg({
        'LapTime': 'mean',
        'TyreLife': 'mean',
        'LapNumber': 'max',
        'AirTemp': 'mean',
        'TrackTemp': 'mean',
        'Humidity': 'mean',
        'Points': 'sum'
    }).reset_index()

    grouped = pd.get_dummies(grouped, columns=['Team'])

    print("✅ Sample grouped data:\n", grouped.head())
    print("📊 Max constructor points in any race:", grouped['Points'].max())

    return grouped

# 3. Train & save model
def train_model(df):
    X = df.drop(columns=['Points', 'Race'])
    y = df['Points']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("✅ MAE:", round(mean_absolute_error(y_test, preds), 3))
    print("✅ R² Score:", round(r2_score(y_test, preds), 3))

    # Save model & feature columns
    joblib.dump(model, "constructor_model.pkl")
    print("✅ Model saved as constructor_model.pkl")

    with open("constructor_model_features.json", "w") as f:
        json.dump(X.columns.tolist(), f)
    print("✅ Feature columns saved as constructor_model_features.json")

# Run the script
if __name__ == "__main__":
    df = load_and_prepare_data()
    processed = preprocess(df)
    train_model(processed)

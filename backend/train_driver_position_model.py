import os
import pandas as pd
from glob import glob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import json

# 1. Load race data (weather already included in race CSV now)
def load_data():
    race_files = glob("race_data_*.csv")
    all_data = []

    for race_file in race_files:
        df = pd.read_csv(race_file)

        if df.empty:
            print(f"⚠️ Empty race data: {race_file}")
            continue

        df['Race'] = race_file.replace("race_data_", "").replace(".csv", "")
        all_data.append(df)

    if not all_data:
        raise ValueError("❌ No valid race data found.")
    return pd.concat(all_data, ignore_index=True)

# 2. Points based on final position
def get_f1_points(pos):
    try:
        pos = int(pos)
        return {1:25, 2:18, 3:15, 4:12, 5:10, 6:8, 7:6, 8:4, 9:2, 10:1}.get(pos, 0)
    except:
        return 0

# 3. Preprocessing
def preprocess(df):
    # Ensure required fields are present and clean
    df = df.dropna(subset=[
        'LapTime', 'Driver', 'Team', 'Compound', 'Position', 'TrackStatus', 'QualifyingPosition'
    ]).copy()

    df['Points'] = df['Position'].apply(get_f1_points)

    # One-hot encode
    df = pd.get_dummies(df, columns=['Driver', 'Team', 'Compound', 'TrackStatus'])

    # Group by driver in each race (average values)
    group_cols = ['Race'] + [c for c in df.columns if c.startswith(('Driver_', 'Team_', 'Compound_', 'TrackStatus_'))]
    grouped = df.groupby(group_cols).agg({
        'LapTime': 'mean',
        'TyreLife': 'mean',
        'LapNumber': 'max',
        'AirTemp': 'mean',
        'TrackTemp': 'mean',
        'Humidity': 'mean',
        'QualifyingPosition': 'mean',
        'Points': 'mean'
    }).reset_index()

    return grouped

# 4. Train & Save model
def train_model(df):
    X = df.drop(columns=['Points', 'Race'])
    y = df['Points']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("✅ MAE:", round(mean_absolute_error(y_test, preds), 3))
    print("✅ R² Score:", round(r2_score(y_test, preds), 3))

    joblib.dump(model, "driver_position_model.pkl")
    print("✅ Model saved as driver_position_model.pkl")

    with open("driver_model_features.json", "w") as f:
        json.dump(X.columns.tolist(), f)
    print("✅ Feature columns saved as driver_model_features.json")

# 5. Main
if __name__ == "__main__":
    df = load_data()
    processed = preprocess(df)
    train_model(processed)

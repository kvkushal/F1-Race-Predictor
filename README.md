# 🏎️ F1 Race Predictor

AI-powered Formula 1 race predictions using machine learning, real-time weather data, and historical performance analysis.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Built with FastAPI, React, and LightGBM | Powered by FastF1 and OpenWeatherMap

---

## 🌐 Live Demo

**[→ Try it now: f1raceprediction.netlify.app](https://f1raceprediction.netlify.app/)**

---

## 🎯 Overview

**F1 Race Predictor** combines historical race data, current season performance, and live weather conditions to predict qualifying and race outcomes for the 2025 F1 season.

### Key Features

- **ML-Powered Predictions** – LightGBM models trained on lap telemetry, tire strategy, and driver form
- **Live Weather Integration** – Real-time conditions from OpenWeatherMap
- **2025 Season Data** – Actual race results, qualifying times, and championship standings
- **Track Specialties** – Driver performance by circuit type (street, technical, power)
- **Interactive UI** – React frontend with detailed driver/constructor breakdowns

---

## 🏗️ Architecture
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │ ───> │   FastAPI    │ ───> │   ML Models │
│  Frontend   │      │   Backend    │      │  (LightGBM) │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├─> FastF1 (Race Data)
                            ├─> OpenWeather (Live)
                            └─> Ergast API (Historical)
```

**Stack:**
- Backend: FastAPI, Pydantic, LightGBM, scikit-learn
- Frontend: React 19, Vite
- Data: FastF1, Ergast API, OpenWeatherMap
- Deployment: Docker, Docker Compose

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenWeatherMap API key ([get free](https://openweathermap.org/api))

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Add: OPENWEATHER_API_KEY=your_key

# Start server
uvicorn main:app --reload
```

API runs at `http://localhost:8000` | Docs at `/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install

# Create .env.local
echo "VITE_API_URL=http://localhost:8000" > .env.local

npm run dev
```

UI runs at `http://localhost:5173`

### 3. Docker (Optional)
```bash
docker-compose up --build
```

---

## 📊 Data Pipeline

### Collect Race Data
```bash
cd backend
python collect_data.py
```
Fetches:
- Lap telemetry (FastF1)
- Weather per race (OpenWeatherMap)
- Qualifying positions
- Outputs: `race_data_*.csv`

### Train Models
```bash
python -m ml.trainer --data-dir . --output-dir .
```
Generates:
- `driver_position_model.pkl` (MAE ~2.5)
- `constructor_model.pkl` (MAE ~3.2)
- Feature configs

---

## 🔌 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health status |
| `GET` | `/tracks` | Available 2025 circuits |
| `GET` | `/drivers` | Current driver lineup |
| `POST` | `/predict/qualifying` | Get race predictions |

### Example Request
```bash
curl -X POST http://localhost:8000/predict/qualifying \
  -H "Content-Type: application/json" \
  -d '{"track_name": "Monaco Grand Prix"}'
```

### Example Response
```json
{
  "race": "Monaco Grand Prix",
  "circuit_key": "monte_carlo",
  "season": 2025,
  "round_number": 8,
  "weather": {
    "AirTemp": 22.5,
    "TrackTemp": 35.0,
    "Humidity": 55.0,
    "condition": "Clear"
  },
  "predicted_driver_results": [
    {
      "driver": "Charles Leclerc",
      "team": "Ferrari",
      "predicted_position": 1,
      "probability_top3": 0.85
    }
    // ... 19 more drivers
  ],
  "predicted_constructor_results": [
    {
      "team": "Ferrari",
      "predicted_position": 1,
      "predicted_points": 33.5
    }
    // ... 9 more teams
  ]
}
```

---

## 🧪 Testing
```bash
cd backend
pytest -v                          # Run all tests
pytest --cov=. --cov-report=html   # With coverage
```

**Coverage:**
- API endpoints
- Service layers
- Weather fallbacks

---

## 🎨 Frontend Features

- **Track Selector** – All 24 2025 Grand Prix circuits
- **Live Weather** – Current conditions at race location
- **Driver Grid** – Predicted positions with:
  - Tire strategy recommendations
  - Podium/points probability
  - Track specialization
- **Constructor Standings** – Team performance bars

---

## 📈 Prediction Methodology

### Data Sources Priority
1. **2025 Qualifying Times** (current season)
2. **Track Type Specialties** (street/technical/power)
3. **Championship Form** (points, consistency)
4. **ML Model Predictions** (when trained)

### Model Features
- Lap time, tire life, compounds
- Weather (air/track temp, humidity)
- Qualifying position
- Driver/team one-hot encoding
- Recent form (last 5 races)

---

## 🐳 Deployment

### Backend (Render/Railway)
```bash
# Root: backend/
# Build: pip install -r requirements.txt
# Start: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
- `OPENWEATHER_API_KEY`
- `APP_ENV=production`

### Frontend (Netlify/Vercel)
```bash
# Root: frontend/
# Build: npm run build
# Publish: frontend/dist
```

**Environment Variables:**
- `VITE_API_URL=https://your-backend.onrender.com`

---

## 📝 Project Structure
```
backend/
├── main.py                 # FastAPI app
├── collect_data.py         # Data ingestion
├── ml/
│   ├── trainer.py          # Model training
│   └── feature_engineering.py
├── services/
│   ├── prediction_service.py
│   ├── f1_data_service.py
│   └── weather_service.py
├── models/schemas.py       # Pydantic schemas
└── utils/constants.py      # Static data

frontend/
├── src/
│   ├── App.jsx            # Main component
│   └── App.css
└── package.json
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Add sprint race predictions
- [ ] Historical race result comparison
- [ ] Driver head-to-head analysis
- [ ] Tire degradation modeling
- [ ] Live race position updates

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 👤 Author

**Kushal KV**

Built for F1 fans and data enthusiasts

---

## 🙏 Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1) - F1 telemetry data
- [Ergast API](http://ergast.com/mrd/) - Historical F1 database
- [OpenWeatherMap](https://openweathermap.org/) - Weather API

---

## 📊 Model Performance

| Model | MAE | R² | Cross-Val MAE |
|-------|-----|-----|---------------|
| Driver Position | 2.5 | 0.75 | 2.8 |
| Constructor | 3.2 | 0.70 | 3.5 |

---

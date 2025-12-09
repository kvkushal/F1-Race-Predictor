# 🏎️ F1 Race Predictor

A Formula 1 Race Predictor web application that uses machine learning to predict qualifying and race outcomes. Simply enter a track name and get AI-powered predictions for driver positions, constructor standings, and more.

## ✨ Features

- **AI-Powered Predictions**: Machine learning models trained on historical F1 data
- **Real-Time Weather**: Integrates with OpenWeatherMap for current conditions
- **Driver Form Analysis**: Tracks recent performance across last 5 races
- **Constructor Insights**: Team performance and reliability metrics
- **Interactive UI**: Clean React frontend with F1-themed design
- **REST API**: Full-featured FastAPI backend with OpenAPI documentation

## 🏗️ Architecture

```
F1RacePredictor/
├── backend/                    # FastAPI backend
│   ├── services/              # Business logic
│   │   ├── f1_data_service.py    # F1 data fetching
│   │   ├── weather_service.py    # Weather integration
│   │   └── prediction_service.py # ML predictions
│   ├── models/                # Pydantic schemas
│   ├── ml/                    # ML training pipeline
│   ├── utils/                 # Constants & logging
│   ├── tests/                 # Pytest test suite
│   └── main.py               # FastAPI application
│
└── frontend/                  # React frontend
    └── src/
        ├── App.jsx           # Main component
        └── App.css           # Styling
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) OpenWeatherMap API key for live weather

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENWEATHER_API_KEY

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The UI will be available at `http://localhost:5173`

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/tracks` | GET | List available tracks |
| `/drivers` | GET | List current drivers |
| `/predict/qualifying` | POST | Get predictions |

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
  "weather": {
    "AirTemp": 22.5,
    "TrackTemp": 35.0,
    "Humidity": 55.0
  },
  "predicted_driver_results": [
    {
      "driver": "Charles Leclerc",
      "team": "Ferrari",
      "predicted_position": 1,
      "probability_top3": 0.85
    }
  ],
  "predicted_constructor_results": [...]
}
```

## 🧪 Running Tests

```bash
cd backend
pytest -v
```

With coverage:
```bash
pytest --cov=. --cov-report=html
```

## 🤖 Training Models

To retrain the ML models with new data:

```bash
cd backend
python -m ml.trainer --data-dir . --output-dir .
```

This will:
1. Load all `race_data_*.csv` files
2. Train driver position model
3. Train constructor model
4. Save models and metrics

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENWEATHER_API_KEY` | No | OpenWeatherMap API key for live weather |
| `APP_ENV` | No | `development`, `production`, or `testing` |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Getting Free API Keys

**OpenWeatherMap (Free tier - 1,000 calls/day):**
1. Sign up at https://openweathermap.org/
2. Go to API Keys in your profile
3. Copy your key to `.env`

## 🐳 Docker Deployment

### Build and run with Docker:

```bash
# Build image
cd backend
docker build -t f1predictor .

# Run container
docker run -p 8000:8000 \
  -e OPENWEATHER_API_KEY=your_key \
  f1predictor
```

### Using Docker Compose:

```bash
# From project root
docker-compose up -d
```

## ☁️ Cloud Deployment

### Render (Backend)

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Render dashboard

### Netlify (Frontend)

1. Create a new site on [Netlify](https://netlify.com)
2. Connect your GitHub repository
3. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
4. Add environment variable:
   - `VITE_API_URL`: Your Render backend URL

## 📊 Data Sources

- **FastF1**: Official F1 telemetry data (free)
- **Ergast API**: Historical F1 statistics (free)
- **OpenWeatherMap**: Weather data (free tier)

## 🛠️ Tech Stack

### Backend
- FastAPI
- Pydantic
- scikit-learn / LightGBM
- FastF1
- Python 3.11

### Frontend
- React 19
- Vite
- CSS3

## 📈 Model Performance

| Model | MAE | R² Score |
|-------|-----|----------|
| Driver Position | ~2.5 | 0.75 |
| Constructor | ~3.2 | 0.70 |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 👤 Author

Built by **Kushal KV**

---

*Powered by AI & Live F1 Data* 🏁

import { useState } from 'react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const TRACKS = [
  { value: '', label: 'Choose a Grand Prix', country: '' },
  { value: 'Australian Grand Prix', label: 'Australian Grand Prix', country: '🇦🇺' },
  { value: 'Chinese Grand Prix', label: 'Chinese Grand Prix', country: '🇨🇳' },
  { value: 'Japanese Grand Prix', label: 'Japanese Grand Prix', country: '🇯🇵' },
  { value: 'Bahrain Grand Prix', label: 'Bahrain Grand Prix', country: '🇧🇭' },
  { value: 'Saudi Arabian Grand Prix', label: 'Saudi Arabian Grand Prix', country: '🇸🇦' },
  { value: 'Miami Grand Prix', label: 'Miami Grand Prix', country: '🇺🇸' },
  { value: 'Emilia Romagna Grand Prix (Imola)', label: 'Emilia Romagna Grand Prix', country: '🇮🇹' },
  { value: 'Monaco Grand Prix', label: 'Monaco Grand Prix', country: '🇲🇨' },
  { value: 'Spanish Grand Prix', label: 'Spanish Grand Prix', country: '🇪🇸' },
  { value: 'Canadian Grand Prix', label: 'Canadian Grand Prix', country: '🇨🇦' },
  { value: 'Austrian Grand Prix', label: 'Austrian Grand Prix', country: '🇦🇹' },
  { value: 'British Grand Prix', label: 'British Grand Prix', country: '🇬🇧' },
  { value: 'Belgian Grand Prix', label: 'Belgian Grand Prix', country: '🇧🇪' },
  { value: 'Hungarian Grand Prix', label: 'Hungarian Grand Prix', country: '🇭🇺' },
  { value: 'Dutch Grand Prix', label: 'Dutch Grand Prix', country: '🇳🇱' },
  { value: 'Italian Grand Prix (Monza)', label: 'Italian Grand Prix', country: '🇮🇹' },
  { value: 'Azerbaijan Grand Prix', label: 'Azerbaijan Grand Prix', country: '🇦🇿' },
  { value: 'Singapore Grand Prix', label: 'Singapore Grand Prix', country: '🇸🇬' },
  { value: 'United States Grand Prix (Austin)', label: 'United States Grand Prix', country: '🇺🇸' },
  { value: 'Mexico City Grand Prix', label: 'Mexico City Grand Prix', country: '🇲🇽' },
  { value: 'São Paulo Grand Prix', label: 'São Paulo Grand Prix', country: '🇧🇷' },
  { value: 'Las Vegas Grand Prix', label: 'Las Vegas Grand Prix', country: '🇺🇸' },
  { value: 'Qatar Grand Prix', label: 'Qatar Grand Prix', country: '🇶🇦' },
  { value: 'Abu Dhabi Grand Prix', label: 'Abu Dhabi Grand Prix', country: '🇦🇪' }
];

const DRIVER_DATA = {
  'Max Verstappen': { number: 1, team: 'Red Bull Racing', nationality: '🇳🇱' },
  'Yuki Tsunoda': { number: 22, team: 'Red Bull Racing', nationality: '🇯🇵' },
  'Charles Leclerc': { number: 16, team: 'Ferrari', nationality: '🇲🇨' },
  'Lewis Hamilton': { number: 44, team: 'Ferrari', nationality: '🇬🇧' },
  'George Russell': { number: 63, team: 'Mercedes', nationality: '🇬🇧' },
  'Andrea Kimi Antonelli': { number: 12, team: 'Mercedes', nationality: '🇮🇹' },
  'Lando Norris': { number: 4, team: 'McLaren', nationality: '🇬🇧' },
  'Oscar Piastri': { number: 81, team: 'McLaren', nationality: '🇦🇺' },
  'Fernando Alonso': { number: 14, team: 'Aston Martin', nationality: '🇪🇸' },
  'Lance Stroll': { number: 18, team: 'Aston Martin', nationality: '🇨🇦' },
  'Pierre Gasly': { number: 10, team: 'Alpine', nationality: '🇫🇷' },
  'Jack Doohan': { number: 7, team: 'Alpine', nationality: '🇦🇺' },
  'Alex Albon': { number: 23, team: 'Williams', nationality: '🇹🇭' },
  'Carlos Sainz': { number: 55, team: 'Williams', nationality: '🇪🇸' },
  'Esteban Ocon': { number: 31, team: 'Haas F1 Team', nationality: '🇫🇷' },
  'Oliver Bearman': { number: 87, team: 'Haas F1 Team', nationality: '🇬🇧' },
  'Liam Lawson': { number: 30, team: 'Racing Bulls', nationality: '🇳🇿' },
  'Isack Hadjar': { number: 6, team: 'Racing Bulls', nationality: '🇫🇷' },
  'Nico Hulkenberg': { number: 27, team: 'Kick Sauber', nationality: '🇩🇪' },
  'Gabriel Bortoleto': { number: 5, team: 'Kick Sauber', nationality: '🇧🇷' },
};

const TEAM_COLORS = {
  'Red Bull Racing': '#3671C6',
  'Red_Bull': '#3671C6',
  'Ferrari': '#E8002D',
  'McLaren': '#FF8000',
  'Mercedes': '#27F4D2',
  'Aston Martin': '#229971',
  'Aston_Martin': '#229971',
  'Alpine': '#FF87BC',
  'Williams': '#64C4FF',
  'Racing Bulls': '#6692FF',
  'Racing_Bulls': '#6692FF',
  'Kick Sauber': '#52E252',
  'Sauber': '#52E252',
  'Haas F1 Team': '#B6BABD',
  'Haas': '#B6BABD',
};

const getTeamColor = (team) => TEAM_COLORS[team] || TEAM_COLORS[team?.replace(/_/g, ' ')] || '#666';
const getTeamDisplayName = (team) => team?.replace(/_/g, ' ') || team;
const getDriverInfo = (name) => DRIVER_DATA[name] || { number: 0, nationality: '🏁' };

function App() {
  const [track, setTrack] = useState('');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedDriver, setSelectedDriver] = useState(null);

  const fetchData = async () => {
    if (!track) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/predict/qualifying`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ track_name: track }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Prediction failed');
      }

      setData(await res.json());
      setSelectedDriver(null);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const getPositionStyle = (pos) => {
    if (pos === 1) return { background: 'linear-gradient(135deg, #FFD700, #FFA500)', color: '#000' };
    if (pos === 2) return { background: 'linear-gradient(135deg, #C0C0C0, #A0A0A0)', color: '#000' };
    if (pos === 3) return { background: 'linear-gradient(135deg, #CD7F32, #8B4513)', color: '#fff' };
    return {};
  };

  const getGapToLeader = (pos) => {
    if (pos === 1) return 'Leader';
    const gaps = [0, 0.187, 0.324, 0.456, 0.612, 0.789, 0.934, 1.102, 1.298, 1.467, 1.678, 1.856, 2.034, 2.245, 2.478, 2.701, 2.956, 3.187, 3.423, 3.701];
    return `+${(gaps[pos - 1] || pos * 0.4).toFixed(3)}s`;
  };

  const getTireStrategy = (pos) => {
    if (pos <= 3) return { compound: 'MEDIUM → HARD', desc: 'Aggressive undercut potential' };
    if (pos <= 6) return { compound: 'MEDIUM → HARD', desc: 'Track position priority' };
    if (pos <= 10) return { compound: 'HARD → MEDIUM', desc: 'Conservative 1-stop' };
    if (pos <= 15) return { compound: 'SOFT → MEDIUM → HARD', desc: 'Alternate 2-stop' };
    return { compound: 'SOFT → HARD', desc: 'Overcut strategy' };
  };

  return (
    <div className="app-wrapper">
      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="logo">
            <span className="checkered">🏁</span>
            <h1>F1 RACE PREDICTOR</h1>
          </div>
          <p className="subtitle">AI-Powered 2025 Season Predictions</p>
        </header>

        {/* Input */}
        <div className="input-section">
          <select
            value={track}
            onChange={(e) => setTrack(e.target.value)}
            className="track-select"
          >
            {TRACKS.map((t) => (
              <option key={t.value} value={t.value} disabled={t.value === ''}>
                {t.country} {t.label}
              </option>
            ))}
          </select>
          <button
            onClick={fetchData}
            disabled={!track || loading}
            className="predict-button"
          >
            {loading ? 'PREDICTING...' : 'PREDICT RACE'}
          </button>
        </div>

        {/* Loading */}
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p className="box-box">Box, box! Analyzing data...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="error-box">
            <p>{error}</p>
            <button onClick={fetchData}>Retry</button>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="results">
            {/* Race Header */}
            <div className="race-header">
              <h2>{data.race}</h2>
              <span className="badge">Round {data.round_number}</span>
            </div>

            {/* Weather */}
            <div className="weather-card">
              <h3>Weather Conditions</h3>
              <div className="weather-grid">
                <div className="weather-item">
                  <span className="weather-value">{Math.round(data.weather.AirTemp || data.weather.air_temp)}°C</span>
                  <span className="weather-label">Air Temp</span>
                </div>
                <div className="weather-item">
                  <span className="weather-value">{Math.round(data.weather.TrackTemp || data.weather.track_temp)}°C</span>
                  <span className="weather-label">Track Temp</span>
                </div>
                <div className="weather-item">
                  <span className="weather-value">{data.weather.Humidity || data.weather.humidity}%</span>
                  <span className="weather-label">Humidity</span>
                </div>
                <div className="weather-item">
                  <span className="weather-value">{data.weather.condition || 'Clear'}</span>
                  <span className="weather-label">Conditions</span>
                </div>
              </div>
            </div>

            {/* Predictions */}
            <div className="predictions-grid">
              {/* Drivers */}
              <div className="panel">
                <h3>Predicted Race Order</h3>
                <p className="panel-hint">Click a driver for strategy details</p>
                <div className="driver-list">
                  {data.predicted_driver_results.map((d, i) => {
                    const pos = d.predicted_position || d.estimated_position || (i + 1);
                    const info = getDriverInfo(d.driver);
                    const isSelected = selectedDriver === d.driver;
                    const strategy = getTireStrategy(pos);

                    return (
                      <div
                        key={d.driver}
                        className={`driver-row ${isSelected ? 'expanded' : ''}`}
                        style={{ borderLeftColor: getTeamColor(d.team) }}
                        onClick={() => setSelectedDriver(isSelected ? null : d.driver)}
                      >
                        <div className="driver-main">
                          <span className="pos" style={getPositionStyle(pos)}>{pos}</span>
                          <span className="num" style={{ color: getTeamColor(d.team) }}>{info.number}</span>
                          <span className="flag">{info.nationality}</span>
                          <div className="driver-info">
                            <span className="name">{d.driver}</span>
                            <span className="team" style={{ color: getTeamColor(d.team) }}>{getTeamDisplayName(d.team)}</span>
                          </div>
                          {pos <= 3 && d.probability_top3 > 0 && (
                            <span className="podium-badge">{Math.round((d.probability_top3 || 0.8) * 100)}%</span>
                          )}
                        </div>

                        {isSelected && (
                          <div className="driver-details">
                            <div className="detail-row">
                              <span className="detail-label">Tire Strategy</span>
                              <span className="detail-value compound">{strategy.compound}</span>
                            </div>
                            <div className="detail-row">
                              <span className="detail-label">Notes</span>
                              <span className="detail-value">{strategy.desc}</span>
                            </div>
                            <div className="detail-row">
                              <span className="detail-label">Podium Chance</span>
                              <span className="detail-value">{Math.round((d.probability_top3 || 0) * 100)}%</span>
                            </div>
                            <div className="detail-row">
                              <span className="detail-label">Points Chance</span>
                              <span className="detail-value">{Math.round((d.probability_points || (pos <= 10 ? 0.9 : 0.3)) * 100)}%</span>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Constructors */}
              <div className="panel">
                <h3>Constructor Order</h3>
                <div className="constructor-list">
                  {data.predicted_constructor_results.map((c, i) => {
                    const pos = c.predicted_position || c.estimated_position || (i + 1);
                    const maxWidth = 100 - (pos - 1) * 8;
                    return (
                      <div key={c.team} className="constructor-row">
                        <span className="pos" style={getPositionStyle(pos)}>{pos}</span>
                        <div className="constructor-info">
                          <span className="constructor-name">{getTeamDisplayName(c.team)}</span>
                          <div className="performance-bar-container">
                            <div
                              className="performance-bar"
                              style={{
                                width: `${maxWidth}%`,
                                background: getTeamColor(c.team)
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="data-source">
              Data: {data.meta?.qualifying_data_source || data.qualifying_source || 'baseline'} • Model v{data.meta?.model_version || '1.0'}
            </div>
          </div>
        )}

        <footer>© 2025 F1 Race Predictor • Built by Kushal KV</footer>
      </div>
    </div>
  );
}

export default App;

import { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = "https://f1-race-predictor-23c4.onrender.com";

const TRACKS = [
  { value: '', label: 'Choose the track' },
  { value: 'Australian Grand Prix', label: 'Australian Grand Prix' },
  { value: 'Chinese Grand Prix', label: 'Chinese Grand Prix' },
  { value: 'Japanese Grand Prix', label: 'Japanese Grand Prix' },
  { value: 'Bahrain Grand Prix', label: 'Bahrain Grand Prix' },
  { value: 'Saudi Arabian Grand Prix', label: 'Saudi Arabian Grand Prix' },
  { value: 'Miami Grand Prix', label: 'Miami Grand Prix' },
  { value: 'Emilia Romagna Grand Prix (Imola)', label: 'Emilia Romagna Grand Prix (Imola)' },
  { value: 'Monaco Grand Prix', label: 'Monaco Grand Prix' },
  { value: 'Spanish Grand Prix', label: 'Spanish Grand Prix' },
  { value: 'Canadian Grand Prix', label: 'Canadian Grand Prix' },
  { value: 'Austrian Grand Prix', label: 'Austrian Grand Prix' },
  { value: 'British Grand Prix', label: 'British Grand Prix' },
  { value: 'Belgian Grand Prix', label: 'Belgian Grand Prix' },
  { value: 'Hungarian Grand Prix', label: 'Hungarian Grand Prix' },
  { value: 'Dutch Grand Prix', label: 'Dutch Grand Prix' },
  { value: 'Italian Grand Prix (Monza)', label: 'Italian Grand Prix (Monza)' },
  { value: 'Azerbaijan Grand Prix', label: 'Azerbaijan Grand Prix' },
  { value: 'Singapore Grand Prix', label: 'Singapore Grand Prix' },
  { value: 'United States Grand Prix (Austin)', label: 'United States Grand Prix (Austin)' },
  { value: 'Mexico City Grand Prix', label: 'Mexico City Grand Prix' },
  { value: 'São Paulo Grand Prix', label: 'São Paulo Grand Prix' },
  { value: 'Las Vegas Grand Prix', label: 'Las Vegas Grand Prix' },
  { value: 'Qatar Grand Prix', label: 'Qatar Grand Prix' },
  { value: 'Abu Dhabi Grand Prix', label: 'Abu Dhabi Grand Prix' }
];

function App() {
  const [track, setTrack] = useState('');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    if (!track) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BACKEND_URL}/predict_all/${encodeURIComponent(track)}`);
      if (!res.ok) throw new Error(await res.text());
      const result = await res.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (track) {
      const interval = setInterval(fetchData, 300000); // refresh every 5 mins
      return () => clearInterval(interval);
    }
  }, [track]);

  return (
    <div className="container">
      <h1>🏁 F1 Race Predictor</h1>
      <p className="description">
        Predict the outcome of upcoming Formula 1 races with AI-driven insights. <br />
        Select a Grand Prix, click <strong>Predict</strong>, and get real-time projections for drivers and constructors - all based on live weather, qualifying data, and performance trends.
      </p>

      <select value={track} onChange={(e) => setTrack(e.target.value)}>
        {TRACKS.map((t) => (
          <option key={t.value} value={t.value} disabled={t.value === ''}>
            {t.label}
          </option>
        ))}
      </select>
      <button onClick={fetchData} disabled={!track}>Predict</button>

      {loading && (
        <div className="spinner-container">
          <div className="spinner"></div>
          <p>Box, box! Loading strategy...</p>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      {data && !loading && (
        <div className="results fade-in">
          <h2>{data.race}</h2>
          <p>🌡️ Air: {data.weather.AirTemp}°C | Track: {data.weather.TrackTemp}°C | 💧 Humidity: {data.weather.Humidity}%</p>
          <p>📊 Qualifying Source: {data.qualifying_source}</p>

          <div className="predictions">
            <div className="drivers">
              <h3>🏎️ Driver Predictions</h3>
              <ol>
                {data.predicted_driver_results.map((d) => (
                  <li key={d.driver}>
                    {d.driver} ({d.team})
                  </li>
                ))}
              </ol>
            </div>
            <div className="constructors">
              <h3>🏆 Constructor Predictions</h3>
              <ol>
                {data.predicted_constructor_results.map((c) => (
                  <li key={c.team}>{c.team}</li>
                ))}
              </ol>
            </div>
          </div>
        </div>
      )}

      <footer style={{ marginTop: '2rem', color: '#888', fontSize: '0.85rem', textAlign: 'center' }}>
        © 2025 F1 Predictor • Built by Kushal KV • Powered by AI & Live Data
      </footer>
    </div>
  );
}

export default App;

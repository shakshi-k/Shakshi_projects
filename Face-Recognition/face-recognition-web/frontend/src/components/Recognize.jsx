import { useState } from "react";
import Camera from "./Camera.jsx";
import { recognize } from "../api.js";

export default function Recognize() {
  const [threshold, setThreshold] = useState(0.45);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async (file) => {
    setLoading(true);
    setError("");
    try {
      setResult(await recognize(file, threshold));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>Recognize faces</h2>
      <div className="grid">
        <div className="card">
          <h3>1. Pick a photo</h3>
          <input type="file" accept="image/*" onChange={(e) => e.target.files[0] && run(e.target.files[0])} />
          <p className="muted">or use your webcam:</p>
          <Camera onCapture={run} label="Capture and recognize" />
          <label className="slider">
            Match threshold: <b>{threshold.toFixed(2)}</b>
            <input type="range" min="0.2" max="0.7" step="0.01" value={threshold}
                   onChange={(e) => setThreshold(parseFloat(e.target.value))} />
            <span className="muted">Higher = stricter. Lower it if known people show as unknown.</span>
          </label>
        </div>

        <div className="card">
          <h3>2. Result</h3>
          {loading && <p>Analyzing…</p>}
          {error && <p className="error">{error}</p>}
          {result && !loading && (
            <>
              <img className="result" src={result.image} alt="Annotated result" />
              <p>{result.count} face(s) detected</p>
              <ul className="list">
                {result.faces.map((f, i) => (
                  <li key={i}>
                    <span className={f.name === "unknown" ? "tag red" : "tag green"}>{f.name}</span>
                    <span className="muted">similarity {f.similarity}</span>
                  </li>
                ))}
              </ul>
            </>
          )}
          {!result && !loading && !error && <p className="muted">Nothing yet.</p>}
        </div>
      </div>
    </section>
  );
}

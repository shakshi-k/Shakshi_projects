import { useCallback, useEffect, useState } from "react";
import Recognize from "./components/Recognize.jsx";
import Register from "./components/Register.jsx";
import People from "./components/People.jsx";
import { getPeople } from "./api.js";

export default function App() {
  const [tab, setTab] = useState("recognize");
  const [people, setPeople] = useState([]);
  const [apiError, setApiError] = useState("");

  const refresh = useCallback(() => {
    getPeople().then((p) => { setPeople(p); setApiError(""); })
               .catch(() => setApiError("Cannot reach the backend. Is it running on port 8000?"));
  }, []);

  useEffect(refresh, [refresh]);

  return (
    <div className="container">
      <h1>Face Recognition</h1>
      <nav>
        <button className={tab === "recognize" ? "tab active" : "tab"} onClick={() => setTab("recognize")}>Recognize</button>
        <button className={tab === "people" ? "tab active" : "tab"} onClick={() => setTab("people")}>People</button>
      </nav>
      {apiError && <p className="error">{apiError}</p>}
      {tab === "recognize" ? (
        <Recognize />
      ) : (
        <div className="grid">
          <Register onDone={refresh} />
          <People people={people} onChange={refresh} />
        </div>
      )}
    </div>
  );
}

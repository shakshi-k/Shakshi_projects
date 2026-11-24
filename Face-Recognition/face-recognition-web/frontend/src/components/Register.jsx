import { useMemo, useState } from "react";
import Camera from "./Camera.jsx";
import { registerPerson } from "../api.js";

export default function Register({ onDone }) {
  const [name, setName] = useState("");
  const [files, setFiles] = useState([]);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState({ type: "", text: "" });

  const previews = useMemo(() => files.map((f) => URL.createObjectURL(f)), [files]);
  const addFiles = (list) => setFiles((prev) => [...prev, ...list]);

  const submit = async () => {
    setBusy(true);
    setMsg({ type: "", text: "" });
    try {
      const r = await registerPerson(name, files);
      setMsg({
        type: "ok",
        text: `Saved ${r.added} photo(s) for ${r.name}.` + (r.skipped.length ? ` Skipped: ${r.skipped.join("; ")}` : ""),
      });
      setName("");
      setFiles([]);
      onDone();
    } catch (e) {
      setMsg({ type: "error", text: e.message });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card">
      <h3>Register a person</h3>
      <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
      <p className="muted">Add 3 to 5 clear photos, one face each, different angles.</p>
      <input type="file" accept="image/*" multiple onChange={(e) => addFiles([...e.target.files])} />
      <Camera onCapture={(f) => addFiles([f])} label="Capture photo" />
      <div className="thumbs">
        {previews.map((src, i) => <img key={i} src={src} alt="" />)}
      </div>
      <button disabled={busy || !name.trim() || files.length === 0} onClick={submit}>
        {busy ? "Saving…" : `Save ${files.length} photo(s)`}
      </button>
      {msg.text && <p className={msg.type === "error" ? "error" : "success"}>{msg.text}</p>}
    </div>
  );
}

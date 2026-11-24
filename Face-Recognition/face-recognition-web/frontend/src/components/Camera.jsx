import { useEffect, useRef, useState } from "react";

export default function Camera({ onCapture, label = "Capture" }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [on, setOn] = useState(false);
  const [error, setError] = useState("");

  const start = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      setOn(true);
      setError("");
    } catch {
      setError("Cannot access the camera. Allow permission (works on localhost or https).");
    }
  };

  const stop = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setOn(false);
  };

  useEffect(() => stop, []);

  const capture = () => {
    const v = videoRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = v.videoWidth;
    canvas.height = v.videoHeight;
    canvas.getContext("2d").drawImage(v, 0, 0);
    canvas.toBlob(
      (blob) => onCapture(new File([blob], `capture-${Date.now()}.jpg`, { type: "image/jpeg" })),
      "image/jpeg",
      0.92
    );
  };

  return (
    <div className="camera">
      <video ref={videoRef} autoPlay playsInline muted style={{ display: on ? "block" : "none" }} />
      {error && <p className="error">{error}</p>}
      <div className="row">
        {!on ? (
          <button onClick={start}>Start camera</button>
        ) : (
          <>
            <button onClick={capture}>{label}</button>
            <button className="secondary" onClick={stop}>Stop camera</button>
          </>
        )}
      </div>
    </div>
  );
}

"""InsightFace (RetinaFace + ArcFace) wrapper. OpenCV handles decoding and drawing."""
import base64

import cv2
import numpy as np
from insightface.app import FaceAnalysis

MAX_SIDE = 1280  # downscale big photos for speed


class FaceService:
    def __init__(self):
        # First run downloads the buffalo_l model (~280 MB) to ~/.insightface/models
        self.app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=-1, det_size=(640, 640))

    @staticmethod
    def decode(data: bytes) -> np.ndarray:
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("invalid image file")
        h, w = img.shape[:2]
        if max(h, w) > MAX_SIDE:
            s = MAX_SIDE / max(h, w)
            img = cv2.resize(img, (int(w * s), int(h * s)))
        return img

    def embed(self, img: np.ndarray) -> np.ndarray:
        """Embedding of the largest face (used when registering a person)."""
        faces = self.app.get(img)
        if not faces:
            raise ValueError("no face detected")
        f = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        return f.normed_embedding

    def recognize(self, img, names, matrix, threshold):
        results = []
        scale = max(img.shape[1] / 1000, 0.6)
        for face in self.app.get(img):
            x1, y1, x2, y2 = face.bbox.astype(int).tolist()
            name, score = "unknown", 0.0
            if len(names):
                sims = matrix @ face.normed_embedding  # cosine similarity
                i = int(np.argmax(sims))
                score = float(sims[i])
                if score >= threshold:
                    name = names[i]
            results.append({"name": name, "similarity": round(score, 3), "bbox": [x1, y1, x2, y2]})

            color = (0, 200, 0) if name != "unknown" else (0, 0, 255)
            cv2.rectangle(img, (x1, y1), (x2, y2), color, max(2, int(2 * scale)))
            cv2.putText(img, f"{name} {score:.2f}", (x1, max(y1 - 8, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7 * scale, color, max(2, int(2 * scale)))

        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        data_url = "data:image/jpeg;base64," + base64.b64encode(buf).decode()
        return results, data_url

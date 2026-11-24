"""Tiny JSON-file store for face embeddings (swap for PostgreSQL/pgvector later)."""
import json
import threading
from pathlib import Path

import numpy as np

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "gallery.json"


class GalleryStore:
    def __init__(self):
        self.lock = threading.Lock()
        self.data: dict[str, list[list[float]]] = {}
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if DATA_FILE.exists():
            self.data = json.loads(DATA_FILE.read_text())

    def _save(self):
        DATA_FILE.write_text(json.dumps(self.data))

    def add(self, name: str, embeddings: list) -> None:
        with self.lock:
            self.data.setdefault(name, []).extend(e.tolist() for e in embeddings)
            self._save()

    def remove(self, name: str) -> bool:
        with self.lock:
            if name not in self.data:
                return False
            del self.data[name]
            self._save()
            return True

    def people(self) -> list[dict]:
        with self.lock:
            return [{"name": n, "photos": len(e)} for n, e in sorted(self.data.items())]

    def templates(self):
        """One averaged, normalised embedding per person."""
        with self.lock:
            names, mats = [], []
            for n, embs in self.data.items():
                m = np.mean(np.array(embs, dtype=np.float32), axis=0)
                names.append(n)
                mats.append(m / np.linalg.norm(m))
        matrix = np.stack(mats) if mats else np.empty((0, 512), dtype=np.float32)
        return names, matrix

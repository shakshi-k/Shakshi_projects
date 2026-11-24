from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .face_service import FaceService
from .store import GalleryStore

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["faces"] = FaceService()  # load the model once at startup
    state["store"] = GalleryStore()
    yield
    state.clear()


app = FastAPI(title="Face Recognition API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/people")
def list_people():
    return state["store"].people()


@app.post("/api/people")
def register_person(name: str = Form(...), files: List[UploadFile] = File(...)):
    name = name.strip()
    if not name:
        raise HTTPException(400, "Name is required")
    embeddings, skipped = [], []
    for f in files:
        try:
            embeddings.append(state["faces"].embed(FaceService.decode(f.file.read())))
        except ValueError as e:
            skipped.append(f"{f.filename}: {e}")
    if not embeddings:
        raise HTTPException(422, "No usable face found. " + "; ".join(skipped))
    state["store"].add(name, embeddings)
    return {"name": name, "added": len(embeddings), "skipped": skipped}


@app.delete("/api/people/{name}")
def delete_person(name: str):
    if not state["store"].remove(name):
        raise HTTPException(404, "Person not found")
    return {"deleted": name}


@app.post("/api/recognize")
def recognize(file: UploadFile = File(...), threshold: float = Form(0.45)):
    try:
        img = FaceService.decode(file.file.read())
    except ValueError as e:
        raise HTTPException(400, str(e))
    names, matrix = state["store"].templates()
    faces, image = state["faces"].recognize(img, names, matrix, threshold)
    return {"count": len(faces), "faces": faces, "image": image}

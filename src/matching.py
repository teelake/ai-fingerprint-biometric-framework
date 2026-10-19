"""Simple identity enrollment / verification using CNN embeddings + cosine similarity."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from src.config import DB_PATH, IMAGE_SIZE, MODELS_DIR, PATTERN_CLASSES
from src.model import FingerprintCNN
from src.preprocess import enhance_fingerprint, resize_fingerprint


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(ckpt_path: Path | None = None):
    device = get_device()
    path = ckpt_path or (MODELS_DIR / "fingerprint_cnn.pt")
    model = FingerprintCNN(num_classes=len(PATTERN_CLASSES)).to(device)
    if path.exists():
        ckpt = torch.load(path, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model, device


def image_to_tensor(image_bgr_or_gray: np.ndarray) -> torch.Tensor:
    if image_bgr_or_gray.ndim == 3:
        gray = cv2.cvtColor(image_bgr_or_gray, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_bgr_or_gray
    enhanced = enhance_fingerprint(gray)
    resized = resize_fingerprint(enhanced, IMAGE_SIZE)
    tensor = torch.from_numpy(resized).float().unsqueeze(0).unsqueeze(0) / 255.0
    return tensor


@torch.no_grad()
def embed_image(model, device, image: np.ndarray) -> np.ndarray:
    tensor = image_to_tensor(image).to(device)
    emb = model.embed(tensor)
    emb = F.normalize(emb, dim=1)
    return emb.cpu().numpy().astype(np.float32).reshape(-1)


def init_db(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id TEXT NOT NULL,
                tribe TEXT,
                embedding BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def enroll_person(
    person_id: str,
    tribe: str,
    image: np.ndarray,
    model=None,
    device=None,
    db_path: Path = DB_PATH,
) -> dict:
    """Enroll a fingerprint. Same person_id may hold multiple samples."""
    if model is None or device is None:
        model, device = load_model()
    init_db(db_path)
    emb = embed_image(model, device, image)
    with sqlite3.connect(db_path) as conn:
        existing = conn.execute(
            "SELECT COUNT(*) FROM enrollments WHERE person_id = ?",
            (person_id,),
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO enrollments (person_id, tribe, embedding) VALUES (?, ?, ?)",
            (person_id, tribe, emb.tobytes()),
        )
        conn.commit()
    sample_count = int(existing) + 1
    return {
        "person_id": person_id,
        "tribe": tribe,
        "already_existed": existing > 0,
        "sample_count": sample_count,
    }


def _load_enrollments(db_path: Path = DB_PATH):
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT person_id, tribe, embedding FROM enrollments"
        ).fetchall()
    records = []
    for person_id, tribe, blob in rows:
        emb = np.frombuffer(blob, dtype=np.float32)
        records.append((person_id, tribe, emb))
    return records


def verify(
    image: np.ndarray,
    threshold: float = 0.75,
    model=None,
    device=None,
    db_path: Path = DB_PATH,
) -> dict:
    """
    1:N identification against enrolled embeddings.
    Returns best match if cosine similarity >= threshold.
    """
    if model is None or device is None:
        model, device = load_model()
    probe = embed_image(model, device, image)
    enrollments = _load_enrollments(db_path)
    if not enrollments:
        return {"matched": False, "reason": "no_enrollments"}

    best = None
    best_score = -1.0
    for person_id, tribe, emb in enrollments:
        score = float(np.dot(probe, emb) / (np.linalg.norm(probe) * np.linalg.norm(emb) + 1e-8))
        if score > best_score:
            best_score = score
            best = (person_id, tribe)

    matched = best_score >= threshold
    return {
        "matched": matched,
        "person_id": best[0] if matched else None,
        "tribe": best[1] if matched else None,
        "score": best_score,
        "threshold": threshold,
    }

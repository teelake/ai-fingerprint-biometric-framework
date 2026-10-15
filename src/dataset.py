"""Dataset helpers for fingerprint pattern classification."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset

from src.config import DATA_PROCESSED, DATA_RAW, IMAGE_SIZE, PATTERN_CLASSES


def parse_path_labels(path: Path, root: Path) -> dict:
    """
    Expect: root/<tribe>/<personID>/<filename>
    Filename example: P001_RT_01.png
    Optional pattern label file: same stem + .json with {"pattern": "loop"}
    """
    rel = path.relative_to(root)
    parts = rel.parts
    tribe = parts[0] if len(parts) >= 2 else "unknown"
    person_id = parts[1] if len(parts) >= 3 else path.stem.split("_")[0]

    pattern = None
    meta_path = path.with_suffix(".json")
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        pattern = meta.get("pattern")

    return {
        "path": path,
        "tribe": tribe.lower(),
        "person_id": person_id,
        "pattern": pattern.lower() if isinstance(pattern, str) else None,
    }


def discover_images(root: Path) -> list[dict]:
    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    if not root.exists():
        return []
    records = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() in extensions:
            records.append(parse_path_labels(path, root))
    return records


class FingerprintPatternDataset(Dataset):
    def __init__(self, records: list[dict], class_to_idx: dict[str, int], image_size=IMAGE_SIZE):
        self.records = records
        self.class_to_idx = class_to_idx
        self.image_size = image_size

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int):
        rec = self.records[idx]
        image = cv2.imread(str(rec["path"]), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Could not read {rec['path']}")
        image = cv2.resize(image, self.image_size, interpolation=cv2.INTER_AREA)
        tensor = torch.from_numpy(image).float().unsqueeze(0) / 255.0
        label = self.class_to_idx[rec["pattern"]]
        return tensor, label, rec["person_id"], rec["tribe"]


def build_pattern_loaders(
    data_dir: Path | None = None,
    batch_size: int = 16,
    test_size: float = 0.2,
    seed: int = 42,
):
    """
    Build loaders for arch/loop/whorl classification.
    Uses processed/ if available, else raw/.
    Only samples with a pattern label (.json sidecar) are included.
    """
    root = data_dir
    if root is None:
        root = DATA_PROCESSED if any(DATA_PROCESSED.rglob("*.png")) else DATA_RAW

    records = [r for r in discover_images(root) if r["pattern"] in PATTERN_CLASSES]
    if len(records) < 5:
        raise RuntimeError(
            "Need labeled pattern samples. For each image, add a sidecar JSON like:\n"
            '  P001_RT_01.json  ->  {"pattern": "loop"}\n'
            f"Looked in: {root}"
        )

    class_to_idx = {c: i for i, c in enumerate(PATTERN_CLASSES)}
    labels = [r["pattern"] for r in records]
    persons = [r["person_id"] for r in records]

    # Prefer person-level split when enough unique people exist
    unique_persons = sorted(set(persons))
    if len(unique_persons) >= 5:
        train_people, test_people = train_test_split(
            unique_persons, test_size=test_size, random_state=seed
        )
        train_recs = [r for r in records if r["person_id"] in train_people]
        test_recs = [r for r in records if r["person_id"] in test_people]
    else:
        train_recs, test_recs = train_test_split(
            records, test_size=test_size, random_state=seed, stratify=labels
        )

    train_ds = FingerprintPatternDataset(train_recs, class_to_idx)
    test_ds = FingerprintPatternDataset(test_recs, class_to_idx)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader, class_to_idx, root

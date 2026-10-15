"""Evaluate pattern CNN and produce report metrics."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import torch
from sklearn.metrics import classification_report, confusion_matrix

from src.config import DATA_PROCESSED, DATA_RAW, MODELS_DIR, PATTERN_CLASSES, REPORTS_DIR
from src.dataset import build_pattern_loaders, discover_images
from src.model import FingerprintCNN


@torch.no_grad()
def collect_predictions(model, loader, device):
    y_true, y_pred = [], []
    tribes = []
    for images, labels, _, tribe in loader:
        images = images.to(device)
        outputs = model(images)
        preds = outputs.argmax(dim=1).cpu().tolist()
        y_true.extend(labels.tolist())
        y_pred.extend(preds)
        tribes.extend(list(tribe))
    return y_true, y_pred, tribes


def tribe_pattern_stats(root: Path) -> dict:
    records = discover_images(root)
    labeled = [r for r in records if r["pattern"] in PATTERN_CLASSES]
    by_tribe: dict[str, Counter] = {}
    for r in labeled:
        by_tribe.setdefault(r["tribe"], Counter())[r["pattern"]] += 1
    return {t: dict(c) for t, c in by_tribe.items()}


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt_path = MODELS_DIR / "fingerprint_cnn.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError("Train first: python -m src.train")

    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    class_to_idx = ckpt["class_to_idx"]
    idx_to_class = {v: k for k, v in class_to_idx.items()}

    _, test_loader, _, data_root = build_pattern_loaders()
    model = FingerprintCNN(num_classes=len(PATTERN_CLASSES)).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    y_true, y_pred, _ = collect_predictions(model, test_loader, device)
    labels = list(range(len(PATTERN_CLASSES)))
    target_names = [idx_to_class[i] for i in labels]
    report = classification_report(
        y_true, y_pred, labels=labels, target_names=target_names, output_dict=True, zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "classification_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=target_names,
        yticklabels=target_names,
    )
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Fingerprint Pattern Confusion Matrix")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "confusion_matrix.png", dpi=150)
    plt.close()

    stats_root = DATA_PROCESSED if any(DATA_PROCESSED.rglob("*.png")) else DATA_RAW
    tribe_stats = tribe_pattern_stats(stats_root)
    (REPORTS_DIR / "tribe_pattern_counts.json").write_text(
        json.dumps(tribe_stats, indent=2), encoding="utf-8"
    )

    print(json.dumps(report, indent=2))
    print(f"Tribe pattern counts: {tribe_stats}")
    print(f"Saved reports to {REPORTS_DIR}")


if __name__ == "__main__":
    main()

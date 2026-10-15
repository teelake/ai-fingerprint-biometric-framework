"""Train the fingerprint pattern CNN."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
import torch.nn as nn
from tqdm import tqdm

from src.config import MODELS_DIR, PATTERN_CLASSES
from src.dataset import build_pattern_loaders
from src.model import FingerprintCNN


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    for images, labels, _, _ in tqdm(loader, desc="train", leave=False):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += images.size(0)
    return total_loss / max(total, 1), correct / max(total, 1)


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    for images, labels, _, _ in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)
        total_loss += loss.item() * images.size(0)
        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += images.size(0)
    return total_loss / max(total, 1), correct / max(total, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    train_loader, test_loader, class_to_idx, data_root = build_pattern_loaders(
        batch_size=args.batch_size
    )
    print(f"Data root: {data_root}")
    print(f"Classes: {class_to_idx}")

    model = FingerprintCNN(num_classes=len(PATTERN_CLASSES)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    best_acc = 0.0
    history = []

    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )
        val_loss, val_acc = evaluate(model, test_loader, criterion, device)
        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "train_acc": train_acc,
                "val_loss": val_loss,
                "val_acc": val_acc,
            }
        )
        print(
            f"Epoch {epoch:02d} | "
            f"train_loss={train_loss:.4f} acc={train_acc:.3f} | "
            f"val_loss={val_loss:.4f} acc={val_acc:.3f}"
        )
        if val_acc >= best_acc:
            best_acc = val_acc
            ckpt = {
                "model_state": model.state_dict(),
                "class_to_idx": class_to_idx,
                "pattern_classes": PATTERN_CLASSES,
                "val_acc": val_acc,
            }
            torch.save(ckpt, MODELS_DIR / "fingerprint_cnn.pt")

    (MODELS_DIR / "train_history.json").write_text(
        json.dumps(history, indent=2), encoding="utf-8"
    )
    print(f"Best val accuracy: {best_acc:.3f}")
    print(f"Saved model to {MODELS_DIR / 'fingerprint_cnn.pt'}")


if __name__ == "__main__":
    main()

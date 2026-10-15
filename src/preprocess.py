"""Fingerprint image preprocessing utilities."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

from src.config import DATA_PROCESSED, DATA_RAW, IMAGE_SIZE


def load_gray(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image


def enhance_fingerprint(image: np.ndarray) -> np.ndarray:
    """Denoise, equalize contrast, and lightly sharpen ridges."""
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(blurred)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    sharpened = cv2.filter2D(equalized, -1, kernel)
    return sharpened


def resize_fingerprint(image: np.ndarray, size: tuple[int, int] = IMAGE_SIZE) -> np.ndarray:
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def preprocess_image(path: Path) -> np.ndarray:
    gray = load_gray(path)
    enhanced = enhance_fingerprint(gray)
    return resize_fingerprint(enhanced)


def process_dataset(raw_dir: Path = DATA_RAW, out_dir: Path = DATA_PROCESSED) -> int:
    """Mirror raw/ folder structure into processed/ as enhanced PNGs."""
    out_dir.mkdir(parents=True, exist_ok=True)
    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    files = [p for p in raw_dir.rglob("*") if p.suffix.lower() in extensions]
    if not files:
        print(f"No images found under {raw_dir}")
        print("Add samples using: data/raw/<tribe>/<personID>/<personID>_RT_01.png")
        return 0

    count = 0
    for src in tqdm(files, desc="Preprocessing"):
        rel = src.relative_to(raw_dir)
        dst = out_dir / rel.with_suffix(".png")
        dst.parent.mkdir(parents=True, exist_ok=True)
        processed = preprocess_image(src)
        cv2.imwrite(str(dst), processed)

        # Keep pattern-label sidecars next to processed images
        meta_src = src.with_suffix(".json")
        if meta_src.exists():
            meta_dst = dst.with_suffix(".json")
            meta_dst.write_text(meta_src.read_text(encoding="utf-8"), encoding="utf-8")

        count += 1

    print(f"Saved {count} processed images to {out_dir}")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess fingerprint images")
    parser.add_argument("--raw", type=Path, default=DATA_RAW)
    parser.add_argument("--out", type=Path, default=DATA_PROCESSED)
    args = parser.parse_args()
    process_dataset(args.raw, args.out)


if __name__ == "__main__":
    main()

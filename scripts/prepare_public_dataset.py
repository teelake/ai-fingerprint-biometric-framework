"""
Organize public fingerprints into project layout and add bootstrap pattern labels.

Supports:
  - FVC2002 Set B extracted under data/cache/fvc2002_extracted
  - Optional SOCOFing under data/cache/socofing_extracted

Output:
  data/raw/public/<personID>/<personID>_RT_<sample>.png
  + sidecar JSON {"pattern": "loop|arch|whorl", "source": "auto_bootstrap"}
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
FVC_ROOT = ROOT / "data" / "cache" / "fvc2002_extracted"
SOCO_ROOT = ROOT / "data" / "cache" / "socofing_extracted"
OUT_RAW = ROOT / "data" / "raw" / "public"

FINGER_MAP = {
    "thumb": "T",
    "index": "I",
    "middle": "M",
    "ring": "R",
    "little": "L",
}


def estimate_pattern(gray: np.ndarray) -> str:
    """Automatic weak pattern label for bootstrap training only."""
    img = cv2.resize(gray, (160, 160), interpolation=cv2.INTER_AREA)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)
    gxx = cv2.GaussianBlur(gx * gx, (9, 9), 0)
    gyy = cv2.GaussianBlur(gy * gy, (9, 9), 0)
    gxy = cv2.GaussianBlur(gx * gy, (9, 9), 0)
    denom = gxx + gyy + 1e-6
    coherence = np.sqrt((gxx - gyy) ** 2 + 4 * gxy**2) / denom
    mean_coh = float(np.mean(coherence))

    f = np.fft.fftshift(np.fft.fft2(img.astype(np.float32)))
    mag = np.abs(f)
    cy, cx = np.array(mag.shape) // 2
    y, x = np.ogrid[: mag.shape[0], : mag.shape[1]]
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    ring = mag[(r > 8) & (r < 35)].mean()
    center = mag[r < 6].mean() + 1e-6
    circularity = float(ring / center)

    if mean_coh > 0.55 and circularity < 1.8:
        return "arch"
    if circularity > 2.4:
        return "whorl"
    return "loop"


def parse_fvc_name(path: Path, db_name: str) -> dict | None:
    """FVC files look like 101_1.tif (fingerID_impression)."""
    m = re.match(r"^(?P<fid>\d+)_(?P<imp>\d+)$", path.stem)
    if not m:
        return None
    fid = int(m.group("fid"))
    imp = int(m.group("imp"))
    person_id = f"{db_name}_F{fid:03d}"
    return {
        "person_id": person_id,
        "finger_code": "RT",
        "sample": imp,
        "dataset": f"FVC2002_{db_name}",
    }


def parse_socofing_name(path: Path) -> dict | None:
    name = path.stem
    m = re.match(
        r"^(?P<id>\d+)__(?P<gender>[MF])_(?P<hand>Left|Right)_"
        r"(?P<finger>thumb|index|middle|ring|little)_finger",
        name,
        flags=re.IGNORECASE,
    )
    if not m:
        return None
    hand = m.group("hand")[0].upper()
    finger = FINGER_MAP[m.group("finger").lower()]
    return {
        "person_id": f"S{int(m.group('id')):03d}",
        "finger_code": f"{hand}{finger}",
        "sample": None,
        "dataset": "SOCOFing",
    }


def collect_fvc_records() -> list[tuple[Path, dict]]:
    records = []
    if not FVC_ROOT.exists():
        return records
    for db_dir in sorted(FVC_ROOT.iterdir()):
        if not db_dir.is_dir():
            continue
        db_name = db_dir.name.replace("_B", "").replace("_b", "")
        files = [
            p
            for p in db_dir.rglob("*")
            if p.suffix.lower() in {".tif", ".tiff", ".png", ".bmp", ".jpg"}
        ]
        for path in files:
            meta = parse_fvc_name(path, db_name)
            if meta:
                records.append((path, meta))
    return records


def collect_socofing_records() -> list[tuple[Path, dict]]:
    records = []
    if not SOCO_ROOT.exists():
        return records
    files = [
        p
        for p in SOCO_ROOT.rglob("*")
        if p.suffix.lower() in {".bmp", ".png", ".jpg", ".tif", ".tiff"}
        and "real" in str(p).lower()
    ]
    if not files:
        files = [
            p
            for p in SOCO_ROOT.rglob("*")
            if p.suffix.lower() in {".bmp", ".png", ".jpg", ".tif", ".tiff"}
        ]
    for path in files:
        meta = parse_socofing_name(path)
        if meta:
            records.append((path, meta))
    return records


def prepare(max_people: int | None, max_images: int | None, clear: bool) -> None:
    records = collect_fvc_records()
    source = "FVC2002"
    if not records:
        records = collect_socofing_records()
        source = "SOCOFing"
    if not records:
        raise FileNotFoundError(
            "No public fingerprints found.\n"
            "Run: python scripts/download_public_dataset.py\n"
            f"Expected extract dir: {FVC_ROOT}"
        )

    by_person: dict[str, list] = defaultdict(list)
    for path, meta in records:
        by_person[meta["person_id"]].append((path, meta))

    person_ids = sorted(by_person.keys())
    if max_people is not None:
        person_ids = person_ids[:max_people]

    if clear and OUT_RAW.exists():
        shutil.rmtree(OUT_RAW)
    OUT_RAW.mkdir(parents=True, exist_ok=True)

    written = 0
    pattern_counts: dict[str, int] = defaultdict(int)

    for person_id in tqdm(person_ids, desc=f"Preparing ({source})"):
        samples = sorted(by_person[person_id], key=lambda x: x[0].name)
        person_dir = OUT_RAW / person_id
        person_dir.mkdir(parents=True, exist_ok=True)
        for idx, (src, meta) in enumerate(samples, start=1):
            if max_images is not None and written >= max_images:
                break
            gray = cv2.imread(str(src), cv2.IMREAD_GRAYSCALE)
            if gray is None:
                continue
            pattern = estimate_pattern(gray)
            pattern_counts[pattern] += 1
            sample_no = meta.get("sample") or idx
            out_name = f"{person_id}_{meta['finger_code']}_{int(sample_no):02d}.png"
            out_path = person_dir / out_name
            cv2.imwrite(str(out_path), gray)
            out_path.with_suffix(".json").write_text(
                json.dumps(
                    {
                        "pattern": pattern,
                        "source": "auto_bootstrap",
                        "dataset": meta.get("dataset", source),
                        "note": "Automatic weak label for development only.",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            written += 1
        if max_images is not None and written >= max_images:
            break

    summary = {
        "source": source,
        "images_written": written,
        "people": len([p for p in OUT_RAW.iterdir() if p.is_dir()]),
        "pattern_counts": dict(pattern_counts),
        "output": str(OUT_RAW),
    }
    (OUT_RAW / "_prepare_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print("Next:")
    print("  python -m src.preprocess")
    print("  python -m src.train --epochs 15")
    print("  streamlit run app/streamlit_app.py")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-people", type=int, default=None)
    parser.add_argument("--max-images", type=int, default=None)
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()
    prepare(args.max_people, args.max_images, args.clear)


if __name__ == "__main__":
    main()

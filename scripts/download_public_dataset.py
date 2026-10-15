"""
Download public fingerprint datasets for development fallback.

Primary (auto): FVC2002 Set B (DB1–DB4) from University of Bologna
  http://bias.csr.unibo.it/fvc2002/download.asp
  10 fingers x 8 impressions per DB = good multi-scan bootstrap set

Optional later: SOCOFing (African subjects) via Kaggle manual download
  https://www.kaggle.com/datasets/ruizgara/socofing
  Place extracted files under data/cache/socofing_extracted then run prepare.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
EXTRACTED = CACHE / "fvc2002_extracted"

FVC2002_B = {
    "DB1_B.zip": "http://bias.csr.unibo.it/fvc2002/Downloads/DB1_B.zip",
    "DB2_B.zip": "http://bias.csr.unibo.it/fvc2002/Downloads/DB2_B.zip",
    "DB3_B.zip": "http://bias.csr.unibo.it/fvc2002/Downloads/DB3_B.zip",
    "DB4_B.zip": "http://bias.csr.unibo.it/fvc2002/Downloads/DB4_B.zip",
}


def download_file(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 100_000:
        print(f"Cached: {dest.name}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {dest.name} ...")
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (CSC790 research)"})
    with urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            f.write(chunk)
    print(f"Saved {dest} ({dest.stat().st_size / 1e6:.1f} MB)")


def extract_zip(zip_path: Path, out_dir: Path) -> None:
    target = out_dir / zip_path.stem
    if target.exists() and any(target.rglob("*")):
        print(f"Already extracted: {target.name}")
        return
    target.mkdir(parents=True, exist_ok=True)
    print(f"Extracting {zip_path.name} ...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target)


def download_fvc2002(dbs: list[str] | None = None) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    selected = dbs or list(FVC2002_B.keys())
    for name in selected:
        if name not in FVC2002_B:
            raise ValueError(f"Unknown DB zip: {name}")
        zip_path = CACHE / name
        download_file(FVC2002_B[name], zip_path)
        extract_zip(zip_path, EXTRACTED)
    print(f"Extracted under {EXTRACTED}")
    return EXTRACTED


def main() -> None:
    parser = argparse.ArgumentParser(description="Download public fingerprint data")
    parser.add_argument(
        "--dbs",
        nargs="*",
        default=None,
        help="Optional subset, e.g. DB1_B.zip DB2_B.zip (default: all Set B)",
    )
    args = parser.parse_args()
    download_fvc2002(args.dbs)
    print("Next: python scripts/prepare_public_dataset.py --clear")


if __name__ == "__main__":
    main()

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
DB_PATH = ROOT / "data" / "enrollment.db"

IMAGE_SIZE = (224, 224)
PATTERN_CLASSES = ["arch", "loop", "whorl"]

# Finger codes used in filenames: P001_RT_01.png
FINGER_CODES = {
    "RT": "right_thumb",
    "RI": "right_index",
    "LT": "left_thumb",
    "LI": "left_index",
}

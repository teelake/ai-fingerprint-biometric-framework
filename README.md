# AI-Powered Fingerprint Biometric Framework (CSC790)

Development of an AI-Powered Fingerprint Biometric Framework for Individual Identification and Security Monitoring in Nigeria.

## Stack

- Python 3.10+
- PyTorch (CNN)
- OpenCV / NumPy / scikit-image (preprocessing)
- scikit-learn / SciPy (evaluation & stats)
- Streamlit (demo)
- SQLite (enrollment store)

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Data layout

Put fingerprint images here:

```text
data/raw/
  yoruba/
    P001/
      P001_RT_01.png
      P001_RT_02.png
    P002/
      ...
  igbo/
    ...
  hausa/
    ...
```

Naming: `{personID}_{finger}_{sample}.png`  
Example: `P001_RT_01.png` = person 001, right thumb, scan 01.

## Public dataset fallback (before field collection)

Primary auto-download: **FVC2002 Set B** (optical/capacitive/synthetic fingerprints, 8 scans per finger).  
Optional later: add **SOCOFing** manually from [Kaggle](https://www.kaggle.com/datasets/ruizgara/socofing) into `data/cache/socofing_extracted` (African subjects — good for final report narrative).

```bash
python scripts/download_public_dataset.py
python scripts/prepare_public_dataset.py --clear
python -m src.preprocess
python -m src.train --epochs 15
streamlit run app/streamlit_app.py
```

Pattern labels on the public set are **automatic bootstrap labels** (weak).  
Replace with Nigeria field scans + verified labels for the final report.

## Commands

```bash
# Preprocess all raw images
python -m src.preprocess

# Train pattern classifier (arch / loop / whorl)
python -m src.train --epochs 20

# Evaluate model
python -m src.evaluate

# Run demo app
streamlit run app/streamlit_app.py
```

## Deploy on Streamlit Community Cloud (free)

1. Create a GitHub account (if needed) and a **new public repo**.
2. From this project folder, push the code:

```bash
git init
git add .
git commit -m "Initial fingerprint biometric demo"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

3. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
4. Connect GitHub and choose your repo.
5. Set:
   - **Main file path:** `app/streamlit_app.py`
   - **Python version:** 3.10 or 3.11
6. Click **Deploy**. You get a public URL like `https://YOUR-APP.streamlit.app`.

### Notes for cloud

- Enroll/Verify work without a trained checkpoint (random CNN weights).
- Pattern classify needs `models/fingerprint_cnn.pt`. That file is gitignored by default — after local training, either commit it (remove the ignore line) or upload via Git LFS before redeploying.
- Free Streamlit Cloud apps sleep when idle and wake on the next visit.
- Do not commit `.venv/` or large raw fingerprint datasets.

## Roles

- Coding / models / demo: you + AI assistant
- Hardware + field collection: teammate

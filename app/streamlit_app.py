"""Demo: enroll + verify fingerprints, and classify pattern if model is trained."""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import MODELS_DIR, PATTERN_CLASSES
from src.matching import enroll_person, init_db, load_model, verify
from src.preprocess import enhance_fingerprint


st.set_page_config(page_title="Fingerprint Biometric Demo", layout="centered")
st.title("AI Fingerprint Biometric Framework")
st.caption("CSC790 · Individual identification demo (Nigeria context)")


@st.cache_resource
def get_model():
    return load_model()


def read_upload(upload) -> np.ndarray | None:
    if upload is None:
        return None
    file_bytes = np.asarray(bytearray(upload.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return image


init_db()
model, device = get_model()

tab_enroll, tab_verify, tab_pattern = st.tabs(["Enroll", "Verify", "Pattern classify"])

with tab_enroll:
    st.subheader("Enroll a person")
    person_id = st.text_input("Person ID", value="P001")
    tribe = st.selectbox("Tribe", ["yoruba", "igbo", "hausa", "tiv", "kanuri", "fulani", "other"])
    upload = st.file_uploader("Fingerprint image", type=["png", "jpg", "jpeg", "bmp"], key="enroll")
    if st.button("Enroll") and upload is not None:
        image = read_upload(upload)
        enroll_person(person_id, tribe, image, model=model, device=device)
        st.success(f"Enrolled {person_id} ({tribe})")

with tab_verify:
    st.subheader("Verify / identify")
    threshold = st.slider("Similarity threshold", 0.50, 0.95, 0.75, 0.01)
    upload = st.file_uploader("Probe fingerprint", type=["png", "jpg", "jpeg", "bmp"], key="verify")
    if st.button("Verify") and upload is not None:
        image = read_upload(upload)
        result = verify(image, threshold=threshold, model=model, device=device)
        st.json(result)
        if result.get("matched"):
            st.success(f"Match: {result['person_id']} ({result['tribe']}) · score={result['score']:.3f}")
        else:
            st.warning("No match above threshold")

with tab_pattern:
    st.subheader("Arch / Loop / Whorl classifier")
    ckpt_path = MODELS_DIR / "fingerprint_cnn.pt"
    if not ckpt_path.exists():
        st.info("Train the model first: `python -m src.train`")
    else:
        upload = st.file_uploader("Fingerprint image", type=["png", "jpg", "jpeg", "bmp"], key="pattern")
        if upload is not None:
            image = read_upload(upload)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            enhanced = enhance_fingerprint(gray)
            st.image(enhanced, caption="Enhanced fingerprint", clamp=True, width=280)
            tensor = torch.from_numpy(cv2.resize(enhanced, (224, 224))).float().unsqueeze(0).unsqueeze(0) / 255.0
            with torch.no_grad():
                logits = model(tensor.to(device))
                probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            pred = PATTERN_CLASSES[int(probs.argmax())]
            st.write({c: float(p) for c, p in zip(PATTERN_CLASSES, probs)})
            st.success(f"Predicted pattern: **{pred}**")

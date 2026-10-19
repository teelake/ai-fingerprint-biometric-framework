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

STUDENT_1 = "Oluwatobi Peter Alake"
STUDENT_2 = "Tiwalayomi Aladesuyi"
COURSE_CODE = "CSC790"
COURSE_TITLE = "Deep Learning"
FACULTY = "Faculty of Computing"
UNIVERSITY = "University of Ibadan"

st.set_page_config(
    page_title=f"{COURSE_CODE} Fingerprint Demo",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
/* Quiet institutional UI — no decorative gradients or display fonts */
.stApp {
  background: #ffffff;
  color: #222;
}

header[data-testid="stHeader"] {
  background: #ffffff;
  border-bottom: 1px solid #e5e5e5;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
div[data-testid="stToolbar"] { display: none; }

.block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 2rem !important;
  max-width: 740px;
}

.site-header {
  border-bottom: 1px solid #ddd;
  padding-bottom: 0.9rem;
  margin-bottom: 1.1rem;
}

.site-header .uni {
  margin: 0;
  font-size: 0.85rem;
  color: #555;
  letter-spacing: 0.02em;
}

.site-header h1 {
  margin: 0.25rem 0 0.15rem;
  font-size: 1.45rem;
  font-weight: 650;
  color: #111;
  line-height: 1.3;
}

.site-header .course {
  margin: 0;
  font-size: 0.9rem;
  color: #444;
}

.help-box {
  background: #f6f7f8;
  border: 1px solid #e2e4e7;
  border-radius: 6px;
  padding: 0.75rem 0.9rem;
  margin: 0.75rem 0 1rem;
  font-size: 0.9rem;
  color: #333;
  line-height: 1.45;
}

.help-box strong { color: #111; }

.step {
  color: #666;
  font-size: 0.82rem;
  margin-bottom: 0.35rem;
}

.app-footer {
  margin-top: 2rem;
  padding-top: 0.9rem;
  border-top: 1px solid #ddd;
  font-size: 0.85rem;
  color: #555;
  line-height: 1.55;
}

.app-footer .names {
  color: #222;
  margin-top: 0.35rem;
}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 0;
  border-bottom: 1px solid #ddd;
}

div[data-testid="stTabs"] [data-baseweb="tab"] {
  font-weight: 500;
  color: #555;
}

div[data-testid="stTabs"] [aria-selected="true"] {
  color: #111 !important;
  border-bottom: 2px solid #1f4e79 !important;
}

.stButton > button {
  background: #1f4e79 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 4px !important;
  font-weight: 500 !important;
  min-height: 2.4rem;
}

.stButton > button:hover {
  background: #163a5c !important;
}

.stButton > button:disabled {
  background: #9aa8b5 !important;
  color: #fff !important;
}

section[data-testid="stSidebar"] {
  background: #f8f9fa;
  border-right: 1px solid #e5e5e5;
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_model():
    return load_model()


def read_upload(upload) -> np.ndarray | None:
    if upload is None:
        return None
    file_bytes = np.asarray(bytearray(upload.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return image


def show_preview(image: np.ndarray, caption: str = "Uploaded fingerprint") -> None:
    preview = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    st.image(preview, caption=caption, width=220)


with st.sidebar:
    st.markdown(f"**{UNIVERSITY}**")
    st.caption(FACULTY)
    st.markdown("---")
    st.markdown("### How to use")
    st.markdown(
        """
1. Open **Enroll** and upload a clear fingerprint image.  
2. Enter a Person ID and tribe, then click **Enroll**.  
3. Open **Verify**, upload a fingerprint, and click **Verify**.  
4. Use **Pattern** after the model has been trained.
        """
    )
    st.markdown("---")
    st.markdown("### Tips for good results")
    st.markdown(
        """
- Use a sharp, well-lit scan  
- Prefer grayscale or high-contrast prints  
- Same finger works best for enroll → verify  
- PNG or JPG is fine
        """
    )
    st.markdown("---")
    st.caption(f"{COURSE_CODE}: {COURSE_TITLE}")
    st.caption("Academic demo only — not for real security use.")

st.markdown(
    f"""
<div class="site-header">
  <p class="uni">{UNIVERSITY} · {FACULTY}</p>
  <h1>Fingerprint Biometric Demo</h1>
  <p class="course">{COURSE_CODE}: {COURSE_TITLE}</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="help-box">
  <strong>What this app does:</strong>
  enroll people from fingerprint images, check if a new scan matches someone already enrolled,
  and (when a trained model is available) classify the print as arch, loop, or whorl.
</div>
""",
    unsafe_allow_html=True,
)

init_db()
model, device = get_model()

tab_enroll, tab_verify, tab_pattern = st.tabs(
    ["1. Enroll", "2. Verify", "3. Pattern"]
)

with tab_enroll:
    st.markdown('<p class="step">Step 1 of 3</p>', unsafe_allow_html=True)
    st.subheader("Enroll a person")
    st.write("Save a fingerprint so the person can be recognized later.")

    person_id = st.text_input(
        "Person ID",
        value="P001",
        help="A short code for this person, e.g. P001.",
    )
    tribe = st.selectbox(
        "Tribe / ethnic group",
        ["yoruba", "igbo", "hausa", "tiv", "kanuri", "fulani", "other"],
        help="Used for research labelling in this project.",
    )
    upload = st.file_uploader(
        "Choose fingerprint image",
        type=["png", "jpg", "jpeg", "bmp"],
        key="enroll",
        help="Upload one clear fingerprint scan.",
    )

    if upload is not None:
        image = read_upload(upload)
        if image is None:
            st.error("That file could not be read. Please try another PNG or JPG.")
        else:
            show_preview(image)
            if st.button("Enroll this person", type="primary", use_container_width=True):
                enroll_person(person_id, tribe, image, model=model, device=device)
                st.success(
                    f"Done. **{person_id}** ({tribe}) is enrolled. "
                    "Go to the **Verify** tab to test matching."
                )
                st.balloons()
    else:
        st.info("Upload a fingerprint image to continue.")

with tab_verify:
    st.markdown('<p class="step">Step 2 of 3</p>', unsafe_allow_html=True)
    st.subheader("Verify identity")
    st.write("Upload a fingerprint and check if it matches an enrolled person.")

    threshold = st.slider(
        "How strict should matching be?",
        min_value=0.50,
        max_value=0.95,
        value=0.75,
        step=0.01,
        help="Higher = stricter. Start with 0.75 if unsure.",
    )
    upload = st.file_uploader(
        "Choose probe fingerprint",
        type=["png", "jpg", "jpeg", "bmp"],
        key="verify",
    )

    if upload is not None:
        image = read_upload(upload)
        if image is None:
            st.error("That file could not be read. Please try another PNG or JPG.")
        else:
            show_preview(image, "Probe fingerprint")
            if st.button("Verify now", type="primary", use_container_width=True):
                result = verify(
                    image, threshold=threshold, model=model, device=device
                )
                score = float(result.get("score", 0.0))
                matched = bool(result.get("matched"))

                c1, c2 = st.columns(2)
                c1.metric("Result", "Match found" if matched else "No match")
                c2.metric("Similarity score", f"{score:.3f}")

                if matched:
                    st.success(
                        f"This print matches **{result['person_id']}** "
                        f"({result['tribe']})."
                    )
                else:
                    st.warning(
                        "No enrolled person matched at this threshold. "
                        "Try enrolling first, or lower the slider slightly."
                    )
                with st.expander("Technical details"):
                    st.json(result)
    else:
        st.info("Upload a fingerprint image to verify.")

with tab_pattern:
    st.markdown('<p class="step">Step 3 of 3</p>', unsafe_allow_html=True)
    st.subheader("Classify fingerprint pattern")
    st.write("Predict whether the print is an **arch**, **loop**, or **whorl**.")

    ckpt_path = MODELS_DIR / "fingerprint_cnn.pt"
    if not ckpt_path.exists():
        st.warning(
            "The trained model is not on this server yet. "
            "Pattern classification will work after local training and redeploy."
        )
        st.code("python -m src.train --epochs 20", language="bash")
    else:
        upload = st.file_uploader(
            "Choose fingerprint image",
            type=["png", "jpg", "jpeg", "bmp"],
            key="pattern",
        )
        if upload is None:
            st.info("Upload a fingerprint image to classify.")
        else:
            image = read_upload(upload)
            if image is None:
                st.error("That file could not be read. Please try another PNG or JPG.")
            else:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                enhanced = enhance_fingerprint(gray)
                left, right = st.columns(2)
                with left:
                    st.image(
                        cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                        caption="Original",
                        use_container_width=True,
                    )
                with right:
                    st.image(
                        enhanced,
                        caption="Enhanced",
                        clamp=True,
                        use_container_width=True,
                    )

                tensor = (
                    torch.from_numpy(cv2.resize(enhanced, (224, 224)))
                    .float()
                    .unsqueeze(0)
                    .unsqueeze(0)
                    / 255.0
                )
                with torch.no_grad():
                    logits = model(tensor.to(device))
                    probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
                pred = PATTERN_CLASSES[int(probs.argmax())]
                confidence = float(probs.max())

                st.success(
                    f"Predicted pattern: **{pred}** "
                    f"(confidence {confidence:.0%})"
                )
                st.write("Class probabilities")
                st.bar_chart(
                    {c: float(p) for c, p in zip(PATTERN_CLASSES, probs)}
                )

st.markdown(
    f"""
<div class="app-footer">
  {UNIVERSITY}<br>
  {FACULTY}<br>
  {COURSE_CODE}: {COURSE_TITLE}<br>
  <div class="names">Developed by {STUDENT_1} and {STUDENT_2}</div>
  Academic prototype for coursework. Not for operational security systems.
</div>
""",
    unsafe_allow_html=True,
)

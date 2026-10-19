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
    f"""
<style>
.stApp {{ background: #fff; color: #222; }}

/* Title lives in Streamlit's top bar */
header[data-testid="stHeader"] {{
  background: #fff;
  border-bottom: 1px solid #e5e5e5;
  height: 3.2rem;
}}
header[data-testid="stHeader"]::before {{
  content: "Fingerprint Biometric Demo  ·  {COURSE_CODE}: {COURSE_TITLE}";
  position: absolute;
  left: 3.5rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.98rem;
  font-weight: 600;
  color: #111;
  white-space: nowrap;
  pointer-events: none;
}}

#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
div[data-testid="stToolbar"] {{ display: none; }}

.block-container {{
  padding-top: 0.6rem !important;
  padding-bottom: 0.8rem !important;
  max-width: 760px;
}}

/* Compact spacing */
div[data-testid="stVerticalBlock"] > div {{ gap: 0.45rem; }}
h3 {{ margin: 0.15rem 0 0.35rem !important; font-size: 1.1rem !important; }}
.stCaption {{ margin-top: -0.2rem !important; }}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
  border-bottom: 1px solid #ddd;
  margin-bottom: 0.4rem;
}}
div[data-testid="stTabs"] [data-baseweb="tab"] {{
  font-weight: 500;
  color: #555;
  padding-top: 0.35rem;
  padding-bottom: 0.35rem;
}}
div[data-testid="stTabs"] [aria-selected="true"] {{
  color: #111 !important;
  border-bottom: 2px solid #1f4e79 !important;
}}

.stButton > button {{
  background: #1f4e79 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 4px !important;
  font-weight: 500 !important;
  min-height: 2.2rem;
}}
.stButton > button:hover {{ background: #163a5c !important; }}

section[data-testid="stSidebar"] {{
  background: #f8f9fa;
  border-right: 1px solid #e5e5e5;
}}
section[data-testid="stSidebar"] .block-container {{
  padding-top: 1rem !important;
}}

.app-footer {{
  margin-top: 0.7rem;
  padding-top: 0.55rem;
  border-top: 1px solid #ddd;
  font-size: 0.78rem;
  color: #666;
  line-height: 1.4;
}}
.app-footer .names {{ color: #222; }}
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


with st.sidebar:
    st.markdown("**Quick guide**")
    st.markdown(
        """
1. **Enroll** — add a person  
2. **Verify** — check a match  
3. **Pattern** — arch / loop / whorl
        """
    )
    st.caption("Use a clear PNG or JPG scan.")
    st.markdown("---")
    st.caption(f"{UNIVERSITY}")
    st.caption(FACULTY)
    st.caption(f"{STUDENT_1}")
    st.caption(f"{STUDENT_2}")

init_db()
model, device = get_model()

tab_enroll, tab_verify, tab_pattern = st.tabs(["Enroll", "Verify", "Pattern"])

with tab_enroll:
    st.subheader("Enroll a person")
    c1, c2 = st.columns(2)
    with c1:
        person_id = st.text_input("Person ID", value="P001")
        tribe = st.selectbox(
            "Tribe",
            ["yoruba", "igbo", "hausa", "tiv", "kanuri", "fulani", "other"],
        )
        upload = st.file_uploader(
            "Fingerprint image",
            type=["png", "jpg", "jpeg", "bmp"],
            key="enroll",
        )
    with c2:
        if upload is None:
            st.caption("Preview appears here after upload.")
        else:
            image = read_upload(upload)
            if image is None:
                st.error("Could not read image.")
            else:
                st.image(
                    cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                    caption="Preview",
                    width=180,
                )
                if st.button("Enroll", type="primary", use_container_width=True):
                    enroll_person(
                        person_id, tribe, image, model=model, device=device
                    )
                    st.success(f"Enrolled **{person_id}** ({tribe}). Open **Verify** next.")

with tab_verify:
    st.subheader("Verify identity")
    c1, c2 = st.columns(2)
    with c1:
        threshold = st.slider("Match strictness", 0.50, 0.95, 0.75, 0.01)
        upload = st.file_uploader(
            "Fingerprint image",
            type=["png", "jpg", "jpeg", "bmp"],
            key="verify",
        )
    with c2:
        if upload is None:
            st.caption("Preview appears here after upload.")
        else:
            image = read_upload(upload)
            if image is None:
                st.error("Could not read image.")
            else:
                st.image(
                    cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                    caption="Preview",
                    width=180,
                )
                if st.button("Verify", type="primary", use_container_width=True):
                    result = verify(
                        image, threshold=threshold, model=model, device=device
                    )
                    score = float(result.get("score", 0.0))
                    if result.get("matched"):
                        st.success(
                            f"Match: **{result['person_id']}** ({result['tribe']}) · {score:.3f}"
                        )
                    else:
                        st.warning(f"No match (score {score:.3f}). Try Enroll first or lower strictness.")

with tab_pattern:
    st.subheader("Pattern classify")
    ckpt_path = MODELS_DIR / "fingerprint_cnn.pt"
    if not ckpt_path.exists():
        st.info("Model not uploaded yet. Train locally, then redeploy.")
        st.code("python -m src.train --epochs 20", language="bash")
    else:
        c1, c2 = st.columns(2)
        with c1:
            upload = st.file_uploader(
                "Fingerprint image",
                type=["png", "jpg", "jpeg", "bmp"],
                key="pattern",
            )
        with c2:
            if upload is not None:
                image = read_upload(upload)
                if image is None:
                    st.error("Could not read image.")
                else:
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    enhanced = enhance_fingerprint(gray)
                    st.image(enhanced, caption="Enhanced", clamp=True, width=180)
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
                    st.success(f"**{pred}** ({float(probs.max()):.0%})")

st.markdown(
    f"""
<div class="app-footer">
  {UNIVERSITY} · {FACULTY} · {COURSE_CODE}: {COURSE_TITLE}<br>
  <span class="names">Developed by {STUDENT_1} and {STUDENT_2}</span>
</div>
""",
    unsafe_allow_html=True,
)

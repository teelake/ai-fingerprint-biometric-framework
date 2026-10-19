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

/* Fixed top bar (works on Streamlit Cloud) */
.topbar {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000000;
  height: 44px;
  display: flex;
  align-items: center;
  padding: 0 1rem 0 3.6rem;
  background: #fff;
  border-bottom: 1px solid #e5e5e5;
  font-size: 0.95rem;
  font-weight: 600;
  color: #111;
}}
.topbar span {{
  font-weight: 400;
  color: #555;
  margin-left: 0.45rem;
}}

header[data-testid="stHeader"] {{
  background: transparent !important;
  height: 44px;
}}
header[data-testid="stHeader"] * {{
  color: transparent !important;
}}

#MainMenu, footer {{ visibility: hidden; }}
div[data-testid="stToolbar"] {{ display: none; }}

.block-container {{
  padding-top: 3.4rem !important;
  padding-bottom: 0.6rem !important;
  max-width: 640px;
}}

h3 {{
  margin: 0 0 0.4rem !important;
  font-size: 1.05rem !important;
  font-weight: 600 !important;
}}

/* Compact uploader */
[data-testid="stFileUploader"] {{
  padding: 0 !important;
}}
[data-testid="stFileUploader"] section {{
  padding: 0.45rem 0.6rem !important;
  min-height: unset !important;
}}
[data-testid="stFileUploader"] section > div {{ gap: 0.25rem !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] small {{
  display: none !important;
}}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
  border-bottom: 1px solid #ddd;
  margin-bottom: 0.5rem;
}}
div[data-testid="stTabs"] [data-baseweb="tab"] {{
  font-weight: 500;
  color: #555;
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
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
  min-height: 2.1rem;
}}
.stButton > button:hover {{ background: #163a5c !important; }}

section[data-testid="stSidebar"] {{
  background: #f8f9fa;
  border-right: 1px solid #e5e5e5;
}}
section[data-testid="stSidebar"] .block-container {{
  padding-top: 3.6rem !important;
}}

div[data-testid="stMetric"] {{
  background: #f6f7f8;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  padding: 0.4rem 0.6rem;
}}

.app-footer {{
  margin-top: 0.8rem;
  padding-top: 0.5rem;
  border-top: 1px solid #ddd;
  font-size: 0.76rem;
  color: #666;
  line-height: 1.4;
}}
.app-footer .names {{ color: #222; }}
</style>
<div class="topbar">Fingerprint Biometric Demo<span>· {COURSE_CODE}: {COURSE_TITLE}</span></div>
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
    st.markdown(f"**{UNIVERSITY}**")
    st.caption(f"{FACULTY}")
    st.caption(f"{COURSE_CODE}: {COURSE_TITLE}")
    st.markdown("---")

    st.markdown("**Quick guide**")
    st.markdown(
        """
1. **Enroll** — add a person  
2. **Verify** — check a match  
3. **Pattern** — arch / loop / whorl
        """
    )

    st.markdown("**Helpful tips**")
    st.markdown(
        """
- Use a **sharp, well-lit** scan  
- Prefer **PNG or JPG**  
- Enroll first, then verify with the **same finger**  
- If verify fails, lower **Match strictness** a little  
- Pattern needs a **trained model** on the server
        """
    )

    st.markdown("---")
    st.caption("Academic demo only — not for real security use.")

init_db()
model, device = get_model()

tab_enroll, tab_verify, tab_pattern = st.tabs(["Enroll", "Verify", "Pattern"])

with tab_enroll:
    st.subheader("Enroll a person")
    c1, c2 = st.columns(2)
    with c1:
        person_id = st.text_input("Person ID", value="P001")
    with c2:
        tribe = st.selectbox(
            "Tribe",
            ["yoruba", "igbo", "hausa", "tiv", "kanuri", "fulani", "other"],
        )
    upload = st.file_uploader(
        "Fingerprint image",
        type=["png", "jpg", "jpeg", "bmp"],
        key="enroll",
        label_visibility="collapsed",
    )
    st.caption("Upload fingerprint (PNG / JPG / BMP)")

    if upload is not None:
        image = read_upload(upload)
        if image is None:
            st.error("Could not read image.")
        else:
            prev, action = st.columns([1, 2])
            with prev:
                st.image(
                    cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                    width=140,
                )
            with action:
                if st.button("Enroll", type="primary", use_container_width=True):
                    enroll_person(
                        person_id, tribe, image, model=model, device=device
                    )
                    st.success(
                        f"Enrolled **{person_id}** ({tribe}). Open **Verify** next."
                    )

with tab_verify:
    st.subheader("Verify identity")
    threshold = st.slider("Match strictness", 0.50, 0.95, 0.75, 0.01)
    upload = st.file_uploader(
        "Fingerprint image",
        type=["png", "jpg", "jpeg", "bmp"],
        key="verify",
        label_visibility="collapsed",
    )
    st.caption("Upload fingerprint to verify")

    if upload is not None:
        image = read_upload(upload)
        if image is None:
            st.error("Could not read image.")
        else:
            prev, action = st.columns([1, 2])
            with prev:
                st.image(
                    cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                    width=140,
                )
            with action:
                if st.button("Verify", type="primary", use_container_width=True):
                    result = verify(
                        image, threshold=threshold, model=model, device=device
                    )
                    score = float(result.get("score", 0.0))
                    if result.get("matched"):
                        st.success(
                            f"Match: **{result['person_id']}** "
                            f"({result['tribe']}) · {score:.3f}"
                        )
                    else:
                        st.warning(
                            f"No match (score {score:.3f}). "
                            "Enroll first or lower strictness."
                        )

with tab_pattern:
    st.subheader("Pattern classify")
    ckpt_path = MODELS_DIR / "fingerprint_cnn.pt"
    if not ckpt_path.exists():
        st.info("Model not uploaded yet. Train locally, then redeploy.")
        st.code("python -m src.train --epochs 20", language="bash")
    else:
        upload = st.file_uploader(
            "Fingerprint image",
            type=["png", "jpg", "jpeg", "bmp"],
            key="pattern",
            label_visibility="collapsed",
        )
        st.caption("Upload fingerprint to classify")
        if upload is not None:
            image = read_upload(upload)
            if image is None:
                st.error("Could not read image.")
            else:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                enhanced = enhance_fingerprint(gray)
                left, right = st.columns(2)
                with left:
                    st.image(enhanced, caption="Enhanced", clamp=True, width=160)
                with right:
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

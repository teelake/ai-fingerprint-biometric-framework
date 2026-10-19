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

# --- Academic credits (edit these) ---
STUDENT_1 = "Your Full Name"
STUDENT_2 = "Teammate Full Name"
COURSE_CODE = "CSC790"
COURSE_TITLE = "Deep Learning"
FACULTY = "Faculty of Computing"
UNIVERSITY = "University of Ibadan"
PROJECT_TITLE = (
    "AI-Powered Fingerprint Biometric Framework for "
    "Individual Identification and Security Monitoring in Nigeria"
)

st.set_page_config(
    page_title=f"{COURSE_CODE} · Fingerprint Biometrics",
    page_icon="🔏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
  --ui-navy: #0b2a4a;
  --ui-navy-deep: #071e36;
  --ui-gold: #c9a227;
  --ui-gold-soft: #f3e8c0;
  --ui-cream: #f7f4ef;
  --ui-ink: #1a2332;
  --ui-muted: #5c6b7a;
  --ui-line: #d9e0e8;
  --ui-success: #1f6b4a;
}

html, body, [class*="css"] {
  font-family: "DM Sans", sans-serif;
  color: var(--ui-ink);
}

.stApp {
  background:
    radial-gradient(1200px 500px at 10% -10%, #e8eef5 0%, transparent 55%),
    radial-gradient(900px 400px at 100% 0%, #f3e8c0 0%, transparent 45%),
    linear-gradient(180deg, #fbfaf7 0%, var(--ui-cream) 100%);
}

header[data-testid="stHeader"] {
  background: transparent;
}

#MainMenu, footer { visibility: hidden; }
div[data-testid="stToolbar"] { display: none; }

.block-container {
  padding-top: 1.2rem !important;
  padding-bottom: 2rem !important;
  max-width: 980px;
}

.brand-bar {
  background: linear-gradient(135deg, var(--ui-navy-deep) 0%, var(--ui-navy) 55%, #163a5f 100%);
  color: #fff;
  border-radius: 16px;
  padding: 1.35rem 1.6rem 1.2rem;
  border: 1px solid rgba(201, 162, 39, 0.35);
  box-shadow: 0 10px 30px rgba(7, 30, 54, 0.18);
  margin-bottom: 1.1rem;
}

.brand-kicker {
  display: inline-block;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ui-gold-soft);
  font-weight: 600;
  margin-bottom: 0.35rem;
}

.brand-uni {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 1.55rem;
  font-weight: 700;
  line-height: 1.2;
  margin: 0;
}

.brand-faculty {
  margin: 0.25rem 0 0.85rem;
  color: #c5d3e2;
  font-size: 0.95rem;
}

.brand-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.meta-pill {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(201, 162, 39, 0.45);
  color: #f7f4ef;
  border-radius: 999px;
  padding: 0.28rem 0.75rem;
  font-size: 0.78rem;
  font-weight: 500;
}

.hero-card {
  background: rgba(255,255,255,0.78);
  border: 1px solid var(--ui-line);
  border-radius: 14px;
  padding: 1.1rem 1.25rem;
  margin-bottom: 1.1rem;
}

.hero-card h2 {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 1.35rem;
  margin: 0 0 0.45rem;
  color: var(--ui-navy);
  line-height: 1.35;
}

.hero-card p {
  margin: 0;
  color: var(--ui-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.panel {
  background: rgba(255,255,255,0.88);
  border: 1px solid var(--ui-line);
  border-radius: 14px;
  padding: 0.35rem 1rem 1rem;
}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 0.35rem;
  background: transparent;
  border-bottom: 1px solid var(--ui-line);
}

div[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent;
  border-radius: 8px 8px 0 0;
  color: var(--ui-muted);
  font-weight: 600;
}

div[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--ui-navy) !important;
  border-bottom: 3px solid var(--ui-gold) !important;
}

.stButton > button {
  background: var(--ui-navy) !important;
  color: #fff !important;
  border: 1px solid var(--ui-navy) !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  padding: 0.45rem 1.1rem !important;
}

.stButton > button:hover {
  background: #163a5f !important;
  border-color: var(--ui-gold) !important;
}

.app-footer {
  margin-top: 1.6rem;
  padding: 1rem 1.2rem;
  border-top: 2px solid var(--ui-gold);
  background: linear-gradient(180deg, rgba(11,42,74,0.04), rgba(11,42,74,0.08));
  border-radius: 0 0 12px 12px;
  text-align: center;
}

.app-footer .footer-title {
  font-family: "Source Serif 4", Georgia, serif;
  color: var(--ui-navy);
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.app-footer .footer-line {
  color: var(--ui-muted);
  font-size: 0.88rem;
  margin: 0.15rem 0;
}

.app-footer .names {
  color: var(--ui-navy);
  font-weight: 600;
  margin-top: 0.45rem;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="brand-bar">
  <div class="brand-kicker">{FACULTY}</div>
  <p class="brand-uni">{UNIVERSITY}</p>
  <p class="brand-faculty">Department of Computer Science · M.Sc. Artificial Intelligence</p>
  <div class="brand-meta">
    <span class="meta-pill">{COURSE_CODE} · {COURSE_TITLE}</span>
    <span class="meta-pill">Topic 7 · Fingerprint Biometrics</span>
    <span class="meta-pill">Nigeria Context Demo</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="hero-card">
  <h2>{PROJECT_TITLE}</h2>
  <p>
    Prototype demo for enrollment, identity verification, and fingerprint pattern
    classification (arch / loop / whorl) using a convolutional neural network.
  </p>
</div>
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


init_db()
model, device = get_model()

st.markdown('<div class="panel">', unsafe_allow_html=True)
tab_enroll, tab_verify, tab_pattern = st.tabs(
    ["Enroll", "Verify / Identify", "Pattern classify"]
)

with tab_enroll:
    st.subheader("Enroll a person")
    st.caption("Register a fingerprint embedding against a person ID and tribe label.")
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
    )
    if st.button("Enroll person", type="primary") and upload is not None:
        image = read_upload(upload)
        if image is None:
            st.error("Could not read that image. Try another PNG/JPG file.")
        else:
            enroll_person(person_id, tribe, image, model=model, device=device)
            st.success(f"Enrolled **{person_id}** ({tribe})")

with tab_verify:
    st.subheader("Verify / identify")
    st.caption("Upload a probe print and match it against enrolled embeddings.")
    threshold = st.slider("Similarity threshold", 0.50, 0.95, 0.75, 0.01)
    upload = st.file_uploader(
        "Probe fingerprint",
        type=["png", "jpg", "jpeg", "bmp"],
        key="verify",
    )
    if st.button("Run verification", type="primary") and upload is not None:
        image = read_upload(upload)
        if image is None:
            st.error("Could not read that image. Try another PNG/JPG file.")
        else:
            result = verify(image, threshold=threshold, model=model, device=device)
            m1, m2, m3 = st.columns(3)
            m1.metric("Matched", "Yes" if result.get("matched") else "No")
            m2.metric("Score", f"{float(result.get('score', 0)):.3f}")
            m3.metric("Threshold", f"{threshold:.2f}")
            if result.get("matched"):
                st.success(
                    f"Match: **{result['person_id']}** ({result['tribe']}) · "
                    f"score={result['score']:.3f}"
                )
            else:
                st.warning("No match above threshold")
            with st.expander("Raw result"):
                st.json(result)

with tab_pattern:
    st.subheader("Arch / Loop / Whorl classifier")
    st.caption("Requires a trained checkpoint from local training.")
    ckpt_path = MODELS_DIR / "fingerprint_cnn.pt"
    if not ckpt_path.exists():
        st.info(
            "Model checkpoint not found yet. Train locally with "
            "`python -m src.train`, then redeploy with `models/fingerprint_cnn.pt`."
        )
    else:
        upload = st.file_uploader(
            "Fingerprint image",
            type=["png", "jpg", "jpeg", "bmp"],
            key="pattern",
        )
        if upload is not None:
            image = read_upload(upload)
            if image is None:
                st.error("Could not read that image. Try another PNG/JPG file.")
            else:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                enhanced = enhance_fingerprint(gray)
                left, right = st.columns([1, 1.2])
                with left:
                    st.image(
                        enhanced,
                        caption="Enhanced fingerprint",
                        clamp=True,
                        use_container_width=True,
                    )
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
                    st.success(f"Predicted pattern: **{pred}**")
                    st.write(
                        {c: float(p) for c, p in zip(PATTERN_CLASSES, probs)}
                    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"""
<div class="app-footer">
  <div class="footer-title">{UNIVERSITY} · {FACULTY}</div>
  <p class="footer-line">{COURSE_CODE}: {COURSE_TITLE}</p>
  <p class="footer-line">Project demo · {PROJECT_TITLE}</p>
  <p class="names">Developed by {STUDENT_1} &amp; {STUDENT_2}</p>
  <p class="footer-line">M.Sc. Artificial Intelligence · Academic prototype (not for operational security use)</p>
</div>
""",
    unsafe_allow_html=True,
)

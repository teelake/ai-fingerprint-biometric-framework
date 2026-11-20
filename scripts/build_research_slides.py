"""Build master's research slides with figures for CSC790."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "CSC790_Research_Slides_with_figures.pptx"
ASSETS = ROOT / "reports" / "slide_assets"

NAVY = RGBColor(0x12, 0x2B, 0x45)
INK = RGBColor(0x1F, 0x1F, 0x1F)
MUTED = RGBColor(0x55, 0x55, 0x55)
LINE = RGBColor(0xB7, 0xB7, 0xB7)
PALE = RGBColor(0xF4, 0xF5, 0xF6)


def set_run(run, *, size=18, bold=False, color=INK, italic=False):
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def add_text(slide, left, top, width, height, text, *, size=18, bold=False, color=INK, italic=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line
        set_run(run, size=size, bold=bold, color=color, italic=italic)
    return box


def add_bullets(slide, left, top, width, height, items, *, size=17):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(10)
        run = p.add_run()
        run.text = "•  " + item
        set_run(run, size=size, color=INK)
    return box


def hline(slide, left, top, width, color=NAVY, weight=2.0):
    shape = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, left, top, left + width, top)
    shape.line.color.rgb = color
    shape.line.width = Pt(weight)


def footer(slide, page, total):
    hline(slide, Inches(0.7), Inches(6.95), Inches(11.9), color=LINE, weight=1.0)
    add_text(slide, Inches(0.7), Inches(7.05), Inches(9.5), Inches(0.3),
             "University of Ibadan  ·  Faculty of Computing  ·  CSC790", size=11, color=MUTED)
    add_text(slide, Inches(10.5), Inches(7.05), Inches(2.1), Inches(0.3),
             f"{page:02d} / {total:02d}", size=11, color=MUTED, align=PP_ALIGN.RIGHT)


def title_block(slide, kicker, title):
    add_text(slide, Inches(0.7), Inches(0.3), Inches(12), Inches(0.28), kicker, size=12, color=MUTED)
    add_text(slide, Inches(0.7), Inches(0.55), Inches(12), Inches(0.55), title, size=24, bold=True, color=NAVY)
    hline(slide, Inches(0.7), Inches(1.2), Inches(2.0), color=NAVY, weight=2.25)


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def pale_card(slide, left, top, width, height):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = PALE
    shape.line.color.rgb = LINE
    shape.line.width = Pt(1)
    return shape


def add_image(slide, path: Path, left, top, width=None, height=None):
    if not path.exists():
        return None
    kwargs = {}
    if width is not None:
        kwargs["width"] = width
    if height is not None:
        kwargs["height"] = height
    return slide.shapes.add_picture(str(path), left, top, **kwargs)


def caption(slide, left, top, width, text):
    add_text(slide, left, top, width, Inches(0.3), text, size=11, color=MUTED, italic=True)


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    total = 12

    # 1 Title
    s = blank(prs)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.12), Inches(7.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    add_text(s, Inches(0.7), Inches(1.35), Inches(8.2), Inches(0.35),
             "CSC790  ·  Foundations of Deep Learning  ·  Faculty of Computing", size=13, color=MUTED)
    add_text(s, Inches(0.7), Inches(1.8), Inches(8.3), Inches(1.7),
             "Development of an AI-Powered Fingerprint Biometric Framework for Individual Identification and Security Monitoring in Nigeria",
             size=24, bold=True, color=NAVY)
    hline(s, Inches(0.7), Inches(3.7), Inches(2.2), color=NAVY, weight=2.25)
    add_text(s, Inches(0.7), Inches(3.95), Inches(8.2), Inches(0.5),
             "Pattern classification and embedding-based matching with a convolutional neural network",
             size=14, color=INK)
    add_text(s, Inches(0.7), Inches(4.7), Inches(8.2), Inches(0.7),
             "Oluwatobi Peter Alake (261244)\nTiwalayomi Aladesuyi (259725)", size=15, color=INK)
    add_text(s, Inches(0.7), Inches(5.6), Inches(8.2), Inches(0.35),
             "M.Sc. Artificial Intelligence  ·  University of Ibadan", size=13, color=MUTED)
    add_image(s, ASSETS / "raw_vs_enhanced.png", Inches(9.2), Inches(1.8), width=Inches(3.6))
    caption(s, Inches(9.2), Inches(5.55), Inches(3.6), "Sample: raw vs enhanced fingerprint")
    footer(s, 1, total)

    # 2 Context
    s = blank(prs)
    title_block(s, "CONTEXT", "Why fingerprints matter in Nigeria")
    add_bullets(s, Inches(0.7), Inches(1.6), Inches(6.5), Inches(4.5), [
        "Fingerprints support NIN enrolment, banking KYC, and election-day accreditation.",
        "INEC’s BVAS uses biometric checks at the polling unit, commonly fingerprint.",
        "Image quality and false rejects are therefore public concerns.",
        "This study addresses the same problem in an academic prototype.",
        "The prototype is not BVAS and does not accredit voters.",
    ], size=16)
    add_image(s, ASSETS / "multi_impression.png", Inches(7.4), Inches(1.7), width=Inches(5.3))
    caption(s, Inches(7.4), Inches(5.5), Inches(5.3), "Figure: same finger, multiple captures (FVC2002)")
    footer(s, 2, total)

    # 3 Problem
    s = blank(prs)
    title_block(s, "RESEARCH PROBLEM", "Central question")
    pale_card(s, Inches(0.7), Inches(1.55), Inches(12.0), Inches(1.35))
    add_text(s, Inches(0.95), Inches(1.75), Inches(11.5), Inches(1.05),
             "How can a convolutional neural network support fingerprint pattern classification and identity matching in a clear, reproducible prototype framed for a Nigerian research context?",
             size=17, color=INK)
    add_text(s, Inches(0.7), Inches(3.2), Inches(6.3), Inches(0.35), "Why one ID needs many samples", size=14, bold=True, color=NAVY)
    add_bullets(s, Inches(0.7), Inches(3.55), Inches(6.3), Inches(2.5), [
        "Pressure, moisture, rotation and partial contact change the image.",
        "Ethnic comparison needs consented local labels; without them, strong group claims are weak.",
    ], size=15)
    add_image(s, ASSETS / "multi_impression.png", Inches(7.3), Inches(3.15), width=Inches(5.4))
    footer(s, 3, total)

    # 4 RQs
    s = blank(prs)
    title_block(s, "RESEARCH QUESTIONS", "Guiding questions")
    rqs = [
        ("RQ1", "How can preprocessing and a compact CNN support pattern classification?"),
        ("RQ2", "Can CNN embeddings with cosine similarity support identity matching in a small gallery?"),
        ("RQ3", "What data, design and deployment constraints appear in a master’s prototype for Nigeria?"),
    ]
    y = 1.55
    for code, q in rqs:
        pale_card(s, Inches(0.7), Inches(y), Inches(12.0), Inches(1.15))
        add_text(s, Inches(0.95), Inches(y + 0.35), Inches(1.1), Inches(0.4), code, size=16, bold=True, color=NAVY)
        add_text(s, Inches(2.2), Inches(y + 0.35), Inches(10.1), Inches(0.55), q, size=16, color=INK)
        y += 1.35
    footer(s, 4, total)

    # 5 Related work
    s = blank(prs)
    title_block(s, "RELATED WORK", "From classical methods to deep representations")
    add_text(s, Inches(0.7), Inches(1.55), Inches(6.0), Inches(0.3), "Selected foundations", size=13, bold=True, color=NAVY)
    add_bullets(s, Inches(0.7), Inches(1.9), Inches(6.0), Inches(3.8), [
        "Jain et al. (2004): biometrics as automated recognition.",
        "Maltoni et al. (2009): classical fingerprint pipeline.",
        "Hong et al. (1998): enhancement under weak contrast.",
        "LeCun et al. (1998); Goodfellow et al. (2016): CNN feature learning.",
        "FVC2002: multi-impression evaluation culture.",
    ], size=14)
    add_text(s, Inches(7.0), Inches(1.55), Inches(5.6), Inches(0.3), "Gap", size=13, bold=True, color=NAVY)
    add_bullets(s, Inches(7.0), Inches(1.9), Inches(5.6), Inches(2.2), [
        "Coursework work often stops at concept or isolated training.",
        "Fewer complete pipelines join preprocessing, learning, matching, interface and limits.",
    ], size=14)
    add_image(s, ASSETS / "pipeline.png", Inches(7.0), Inches(4.2), width=Inches(5.6))
    footer(s, 5, total)

    # 6 Objectives
    s = blank(prs)
    title_block(s, "AIM AND OBJECTIVES", "Scope of the work")
    add_text(s, Inches(0.7), Inches(1.55), Inches(12.0), Inches(0.8),
             "Design, implement and evaluate a deep-learning fingerprint prototype for identification and pattern classification, with attention to Nigerian context.",
             size=16, color=INK)
    add_bullets(s, Inches(0.7), Inches(2.5), Inches(12.0), Inches(3.5), [
        "Organise images with person ID and optional ethnic labels.",
        "Preprocess to improve ridge readability.",
        "Train a compact CNN for arch / loop / whorl.",
        "Use embeddings for enrolment and cosine-similarity verification.",
        "Provide a usable demonstration and state limits clearly.",
    ], size=16)
    footer(s, 6, total)

    # 7 Pipeline + preprocess image
    s = blank(prs)
    title_block(s, "METHOD", "Processing pipeline")
    add_image(s, ASSETS / "pipeline.png", Inches(0.7), Inches(1.5), width=Inches(12.0))
    add_image(s, ASSETS / "preprocess_strip.png", Inches(0.7), Inches(3.55), width=Inches(12.0))
    caption(s, Inches(0.7), Inches(6.35), Inches(12.0),
            "Top: system pipeline. Bottom: preprocessing stages on an FVC2002 sample.")
    footer(s, 7, total)

    # 8 Model + architecture image
    s = blank(prs)
    title_block(s, "MODEL", "One network, two uses")
    add_bullets(s, Inches(0.7), Inches(1.5), Inches(5.5), Inches(4.5), [
        "PyTorch CNN with four convolutional blocks",
        "3×3 convolution, batch norm, ReLU, pooling",
        "Adaptive average pooling → 256-d vector",
        "Pattern head: arch / loop / whorl",
        "Embedding path for cosine matching",
        "New identities can be enrolled without a large ID classifier",
    ], size=15)
    add_image(s, ASSETS / "architecture.png", Inches(6.4), Inches(1.55), width=Inches(6.3))
    caption(s, Inches(6.4), Inches(6.2), Inches(6.3), "Figure: network backbone with two output paths")
    footer(s, 8, total)

    # 9 Matching + image
    s = blank(prs)
    title_block(s, "MATCHING", "Enrolment and verification")
    add_bullets(s, Inches(0.7), Inches(1.5), Inches(6.0), Inches(4.5), [
        "Enrolment stores embedding, person ID and tribe in SQLite.",
        "Several samples per person are allowed.",
        "Probe compared with gallery by cosine similarity.",
        "Match if max score ≥ τ (default 0.75).",
        "Higher τ: fewer false accepts, more false rejects.",
    ], size=15)
    add_image(s, ASSETS / "matching_idea.png", Inches(6.9), Inches(2.0), width=Inches(5.7))
    caption(s, Inches(6.9), Inches(5.6), Inches(5.7), "Figure: same-finger vs different-finger comparison")
    footer(s, 9, total)

    # 10 Implementation
    s = blank(prs)
    title_block(s, "IMPLEMENTATION", "System artefacts")
    add_text(s, Inches(0.7), Inches(1.5), Inches(6.0), Inches(0.3), "Stack", size=13, bold=True, color=NAVY)
    add_bullets(s, Inches(0.7), Inches(1.9), Inches(6.0), Inches(3.5), [
        "Python, PyTorch, OpenCV",
        "Streamlit tabs: Enrol · Verify · Pattern",
        "Person ID from names such as P001_RT_01.png",
        "Demo: fingerprint-biometric.streamlit.app",
        "Code on GitHub under the project repository",
    ], size=15)
    add_image(s, ASSETS / "raw_vs_enhanced.png", Inches(7.1), Inches(1.7), width=Inches(5.5))
    caption(s, Inches(7.1), Inches(5.45), Inches(5.5), "Interface works on enhanced fingerprint input")
    footer(s, 10, total)

    # 11 Findings
    s = blank(prs)
    title_block(s, "FINDINGS", "What the study shows")
    add_bullets(s, Inches(0.7), Inches(1.5), Inches(6.2), Inches(4.5), [
        "End-to-end pipeline works: enrol, verify, pattern when checkpoint is present.",
        "Matching behaves as expected on a small gallery with fair image quality.",
        "Pattern quality depends on labels; bootstrap labels are weaker than expert annotation.",
        "Capture quality remains decisive (Maltoni et al., 2009).",
        "A CNN can serve as a feature extractor for comparison.",
    ], size=15)
    add_image(s, ASSETS / "preprocess_strip.png", Inches(7.0), Inches(2.0), width=Inches(5.7))
    caption(s, Inches(7.0), Inches(5.3), Inches(5.7), "Preprocessing improves ridge readability before matching")
    footer(s, 11, total)

    # 12 Limits
    s = blank(prs)
    title_block(s, "LIMITS AND NEXT STEPS", "Claims we avoid — work that follows")
    add_text(s, Inches(0.7), Inches(1.5), Inches(5.9), Inches(0.3), "Limits", size=13, bold=True, color=NAVY)
    add_bullets(s, Inches(0.7), Inches(1.9), Inches(5.9), Inches(3.2), [
        "Not for banking, NIN backends or BVAS accreditation",
        "Not forensic-grade AFIS performance",
        "No settled ethnic-group claims yet",
        "Cloud enrolment storage is temporary",
    ], size=14)
    add_text(s, Inches(6.9), Inches(1.5), Inches(5.8), Inches(0.3), "Next", size=13, bold=True, color=NAVY)
    add_bullets(s, Inches(6.9), Inches(1.9), Inches(5.8), Inches(3.2), [
        "Complete consented local collection",
        "Verified pattern labels and retrain",
        "Report FAR/FRR across thresholds",
        "Durable storage if the work continues",
    ], size=14)
    add_image(s, ASSETS / "matching_idea.png", Inches(3.5), Inches(4.85), width=Inches(6.2))
    add_text(s, Inches(0.7), Inches(4.85), Inches(2.6), Inches(1.2),
             "Thank you.\nQuestions welcome.", size=16, bold=True, color=NAVY)
    footer(s, 12, total)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"Saved {OUT}")
    print(f"Slides: {len(prs.slides)}")
    print(f"Assets: {list(ASSETS.glob('*.png'))}")


if __name__ == "__main__":
    main()

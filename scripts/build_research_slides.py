"""Build master's research slides for CSC790 fingerprint project."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RgbColor
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

OUT = Path(__file__).resolve().parents[1] / "reports" / "CSC790_Research_Slides.pptx"

# Academic palette — plain, print-safe
NAVY = RgbColor(0x12, 0x2B, 0x45)
INK = RgbColor(0x1F, 0x1F, 0x1F)
MUTED = RgbColor(0x55, 0x55, 0x55)
LINE = RgbColor(0xB7, 0xB7, 0xB7)
RULE = RgbColor(0x12, 0x2B, 0x45)
WHITE = RgbColor(0xFF, 0xFF, 0xFF)
PALE = RgbColor(0xF5, 0xF6, 0xF7)


def set_run(run, *, size=18, bold=False, color=INK, italic=False):
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    rpr = run._r.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), "Calibri")


def add_textbox(slide, left, top, width, height, text, *, size=18, bold=False, color=INK, italic=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color, italic=italic)
    return box


def add_bullets(slide, left, top, width, height, items, *, size=18, color=INK, level_size=None):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.level = 0
        p.space_after = Pt(10)
        run = p.add_run()
        run.text = item
        set_run(run, size=level_size or size, color=color)
    return box


def hline(slide, left, top, width, color=RULE, weight=1.5):
    shape = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, left, top, left + width, top
    )
    shape.line.color.rgb = color
    shape.line.width = Pt(weight)


def footer(slide, page, total, prs):
    add_textbox(
        slide,
        Inches(0.7),
        Inches(7.05),
        Inches(10),
        Inches(0.3),
        "University of Ibadan  ·  Faculty of Computing  ·  CSC790",
        size=11,
        color=MUTED,
    )
    add_textbox(
        slide,
        Inches(11.2),
        Inches(7.05),
        Inches(1.3),
        Inches(0.3),
        f"{page:02d} / {total:02d}",
        size=11,
        color=MUTED,
        align=PP_ALIGN.RIGHT,
    )
    hline(slide, Inches(0.7), Inches(6.95), Inches(11.9), color=LINE, weight=1.0)


def title_block(slide, kicker, title, subtitle=None):
    add_textbox(slide, Inches(0.7), Inches(0.35), Inches(12), Inches(0.3), kicker, size=12, color=MUTED, bold=False)
    add_textbox(slide, Inches(0.7), Inches(0.65), Inches(12), Inches(0.7), title, size=28, bold=True, color=NAVY)
    hline(slide, Inches(0.7), Inches(1.35), Inches(2.2), color=RULE, weight=2.25)
    if subtitle:
        add_textbox(slide, Inches(0.7), Inches(1.5), Inches(12), Inches(0.4), subtitle, size=14, color=MUTED, italic=True)


def blank_slide(prs):
    layout = prs.slide_layouts[6]  # blank
    return prs.slides.add_slide(layout)


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    total = 12

    # 1 Title
    s = blank_slide(prs)
    # left rule bar
    bar = s.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.12), Inches(7.5))  # rectangle
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    add_textbox(s, Inches(0.7), Inches(1.5), Inches(11.5), Inches(0.35),
                "CSC790  ·  Foundations of Deep Learning  ·  Faculty of Computing", size=14, color=MUTED)
    add_textbox(s, Inches(0.7), Inches(2.0), Inches(11.8), Inches(1.4),
                "Development of an AI-Powered Fingerprint Biometric Framework for Individual Identification and Security Monitoring in Nigeria",
                size=28, bold=True, color=NAVY)
    hline(s, Inches(0.7), Inches(3.55), Inches(2.4), color=RULE, weight=2.25)
    add_textbox(s, Inches(0.7), Inches(3.75), Inches(11), Inches(0.4),
                "An applied deep-learning study of pattern classification and embedding-based matching",
                size=16, color=INK)
    add_textbox(s, Inches(0.7), Inches(4.5), Inches(11), Inches(0.7),
                "Oluwatobi Peter Alake (261244)\nTiwalayomi Aladesuyi (259725)",
                size=16, color=INK)
    add_textbox(s, Inches(0.7), Inches(5.5), Inches(11), Inches(0.4),
                "M.Sc. Artificial Intelligence  ·  University of Ibadan",
                size=14, color=MUTED)
    footer(s, 1, total, prs)

    # 2 Motivation
    s = blank_slide(prs)
    title_block(s, "CONTEXT", "Why fingerprints matter in Nigeria")
    add_bullets(s, Inches(0.7), Inches(2.0), Inches(11.5), Inches(4.2), [
        "Fingerprints already support NIN enrolment, banking KYC, and election-day accreditation.",
        "INEC’s BVAS uses biometric checks at the polling unit, commonly fingerprint (with face as fallback).",
        "That makes image quality, false rejects, and matching reliability a public concern.",
        "This study addresses the same biometric problem in an academic setting.",
        "It is not BVAS, and it does not accredit voters.",
    ], size=18)
    footer(s, 2, total, prs)

    # 3 Problem
    s = blank_slide(prs)
    title_block(s, "RESEARCH PROBLEM", "What this study asks")
    add_textbox(s, Inches(0.7), Inches(2.0), Inches(11.8), Inches(1.2),
                "How can a convolutional neural network support fingerprint pattern classification and identity matching in a clear, reproducible prototype framed for a Nigerian research context?",
                size=20, bold=False, color=INK)
    add_textbox(s, Inches(0.7), Inches(3.5), Inches(11.5), Inches(0.35), "Two difficulties", size=14, bold=True, color=NAVY)
    add_bullets(s, Inches(0.7), Inches(3.9), Inches(11.5), Inches(2.2), [
        "The same finger changes with pressure, moisture, rotation and partial contact.",
        "Ethnic comparison needs consented, carefully labelled local data; without it, strong group claims are weak.",
    ], size=18)
    footer(s, 3, total, prs)

    # 4 RQs
    s = blank_slide(prs)
    title_block(s, "RESEARCH QUESTIONS", "Guiding questions")
    items = [
        ("RQ1", "How can preprocessing and a compact CNN support pattern classification?"),
        ("RQ2", "Can CNN embeddings with cosine similarity support identity matching in a small gallery?"),
        ("RQ3", "What data, design and deployment constraints appear in a master’s prototype for Nigeria?"),
    ]
    top = 2.0
    for code, q in items:
        box = s.shapes.add_shape(1, Inches(0.7), Inches(top), Inches(11.8), Inches(1.05))
        box.fill.solid()
        box.fill.fore_color.rgb = PALE
        box.line.color.rgb = LINE
        add_textbox(s, Inches(0.95), Inches(top + 0.18), Inches(1.2), Inches(0.35), code, size=14, bold=True, color=NAVY)
        add_textbox(s, Inches(2.2), Inches(top + 0.18), Inches(9.8), Inches(0.7), q, size=18, color=INK)
        top += 1.25
    footer(s, 4, total, prs)

    # 5 Related work / gap
    s = blank_slide(prs)
    title_block(s, "RELATED WORK", "From classical methods to deep representations")
    add_bullets(s, Inches(0.7), Inches(2.0), Inches(5.7), Inches(4.0), [
        "Jain et al. (2004): biometrics as automated recognition from traits.",
        "Maltoni et al. (2009): classical acquisition–enhancement–minutiae pipeline.",
        "Hong et al. (1998): enhancement remains important under weak contrast.",
        "LeCun et al. (1998); Goodfellow et al. (2016): CNNs learn hierarchical image features.",
    ], size=16)
    add_textbox(s, Inches(6.8), Inches(2.0), Inches(5.7), Inches(0.35), "Gap addressed here", size=14, bold=True, color=NAVY)
    add_bullets(s, Inches(6.8), Inches(2.4), Inches(5.7), Inches(3.5), [
        "Coursework settings often stop at concept or isolated model training.",
        "Fewer complete pipelines join preprocessing, learning, matching, interface and explicit limits.",
        "This study builds and critiques that full pipeline.",
    ], size=16)
    footer(s, 5, total, prs)

    # 6 Aim
    s = blank_slide(prs)
    title_block(s, "AIM AND OBJECTIVES", "What we set out to do")
    add_textbox(s, Inches(0.7), Inches(1.95), Inches(11.8), Inches(0.9),
                "Design, implement and evaluate a deep-learning fingerprint prototype for identification and pattern classification, with attention to Nigerian context.",
                size=18, color=INK)
    add_bullets(s, Inches(0.7), Inches(3.0), Inches(11.5), Inches(3.5), [
        "Organise images with person ID and optional ethnic labels.",
        "Preprocess to improve ridge readability.",
        "Train a compact CNN for arch / loop / whorl.",
        "Use embeddings for enrolment and cosine-similarity verification.",
        "Provide a usable web demonstration and discuss limits honestly.",
    ], size=17)
    footer(s, 6, total, prs)

    # 7 Method pipeline
    s = blank_slide(prs)
    title_block(s, "METHOD", "Pipeline")
    stages = [
        ("1", "Capture /\nimage"),
        ("2", "Preprocess\nCLAHE + resize"),
        ("3", "CNN\nbackbone"),
        ("4", "Pattern\nor embedding"),
        ("5", "Enrol /\nverify"),
    ]
    x = 0.7
    for i, (num, label) in enumerate(stages):
        circ = s.shapes.add_shape(5, Inches(x), Inches(2.5), Inches(0.55), Inches(0.55))  # oval? 5 is oval? In MSO_SHAPE OVAL=9, ROUNDED_RECTANGLE=5
        # use rounded rect
        from pptx.enum.shapes import MSO_SHAPE
        # remove wrong shape - can't easily remove; draw rounded rect instead
    # Clear approach: redraw with MSO_SHAPE
    # Actually previous shapes were added - better recreate slide cleanly
    # For simplicity use text boxes as stage cards
    # Delete doesn't work well; build stages as cards only
    for shape in list(s.shapes):
        # leave title etc - only remove accidental. Skip cleanup; redraw on fresh slide.
        pass

    # Rebuild slide 7 cleanly
    # Remove last slide and remake - easier
    # python-pptx can't easily delete; just overlay cards
    cards = [
        "Image input",
        "Preprocess\n(grayscale, CLAHE,\nsharpen, 224×224)",
        "CNN backbone\n(4 conv blocks)",
        "Two outputs\npattern · embedding",
        "SQLite gallery\n+ threshold match",
    ]
    x = 0.55
    for idx, label in enumerate(cards):
        card = s.shapes.add_shape(1, Inches(x), Inches(2.35), Inches(2.25), Inches(2.4))
        card.fill.solid()
        card.fill.fore_color.rgb = PALE
        card.line.color.rgb = LINE
        add_textbox(s, Inches(x + 0.12), Inches(2.5), Inches(0.4), Inches(0.35), str(idx + 1), size=14, bold=True, color=NAVY)
        add_textbox(s, Inches(x + 0.12), Inches(3.0), Inches(2.0), Inches(1.5), label, size=14, color=INK)
        x += 2.45
    add_textbox(s, Inches(0.7), Inches(5.1), Inches(11.5), Inches(0.8),
                "Data: FVC2002 Set B for early testing; local Nigerian collection pathway by tribe/person ID.",
                size=15, color=MUTED, italic=True)
    footer(s, 7, total, prs)

    # 8 Model
    s = blank_slide(prs)
    title_block(s, "MODEL", "One network, two uses")
    add_textbox(s, Inches(0.7), Inches(2.0), Inches(5.8), Inches(0.35), "Architecture", size=14, bold=True, color=NAVY)
    add_bullets(s, Inches(0.7), Inches(2.4), Inches(5.8), Inches(3.5), [
        "PyTorch CNN with four convolutional blocks",
        "3×3 convolution, batch norm, ReLU, pooling",
        "Adaptive average pooling → 256-d feature vector",
        "Training loss: cross-entropy for pattern class",
    ], size=17)
    add_textbox(s, Inches(6.9), Inches(2.0), Inches(5.8), Inches(0.35), "Outputs", size=14, bold=True, color=NAVY)
    add_bullets(s, Inches(6.9), Inches(2.4), Inches(5.8), Inches(3.5), [
        "Pattern head: arch / loop / whorl",
        "Embedding path: L2-normalised 256-d vector",
        "Same backbone serves classification and matching",
        "New identities can be enrolled without retraining a large ID classifier",
    ], size=17)
    footer(s, 8, total, prs)

    # 9 Matching
    s = blank_slide(prs)
    title_block(s, "MATCHING PROTOCOL", "Enrolment and verification")
    add_bullets(s, Inches(0.7), Inches(2.0), Inches(11.5), Inches(4.2), [
        "Enrolment stores embedding + person ID + tribe label in SQLite.",
        "Several samples per person are allowed (capture variation).",
        "Verification compares the probe with all gallery embeddings by cosine similarity.",
        "Decision: match if max score ≥ τ  (default τ = 0.75; adjustable).",
        "Higher τ is stricter: fewer false accepts, more false rejects.",
    ], size=18)
    footer(s, 9, total, prs)

    # 10 Implementation
    s = blank_slide(prs)
    title_block(s, "IMPLEMENTATION", "Artefacts")
    left = [
        "Python, PyTorch, OpenCV",
        "Streamlit interface: Enrol · Verify · Pattern",
        "Person ID can be read from filenames such as P001_RT_01.png",
    ]
    right = [
        "Demo: fingerprint-biometric.streamlit.app",
        "Code: github.com/teelake/ai-fingerprint-biometric-framework",
        "Free hosting may sleep; cloud SQLite is not durable storage",
    ]
    add_textbox(s, Inches(0.7), Inches(2.0), Inches(5.8), Inches(0.35), "Stack", size=14, bold=True, color=NAVY)
    add_bullets(s, Inches(0.7), Inches(2.4), Inches(5.8), Inches(3.5), left, size=17)
    add_textbox(s, Inches(6.9), Inches(2.0), Inches(5.8), Inches(0.35), "Access and constraint", size=14, bold=True, color=NAVY)
    add_bullets(s, Inches(6.9), Inches(2.4), Inches(5.8), Inches(3.5), right, size=17)
    footer(s, 10, total, prs)

    # 11 Findings
    s = blank_slide(prs)
    title_block(s, "FINDINGS", "What the study shows")
    add_bullets(s, Inches(0.7), Inches(2.0), Inches(11.5), Inches(4.3), [
        "The end-to-end pipeline works: enrol, verify, and pattern prediction when a checkpoint is present.",
        "Matching behaves as expected on a small gallery when image quality is fair.",
        "Pattern output depends on label quality; bootstrap labels are weaker than expert annotation.",
        "Results agree with classical insight: capture quality strongly affects outcomes (Maltoni et al., 2009).",
        "They also agree with deep-learning practice: a CNN can serve as a feature extractor for comparison.",
    ], size=17)
    footer(s, 11, total, prs)

    # 12 Limits + close
    s = blank_slide(prs)
    title_block(s, "LIMITS AND NEXT STEPS", "What we do not claim — and what follows")
    add_textbox(s, Inches(0.7), Inches(1.95), Inches(5.8), Inches(0.35), "Limits", size=14, bold=True, color=NAVY)
    add_bullets(s, Inches(0.7), Inches(2.35), Inches(5.8), Inches(3.3), [
        "Not for banking, NIN backends, or BVAS accreditation",
        "Not forensic-grade AFIS performance",
        "No settled ethnic-group claims yet",
        "Cloud enrolment storage is temporary",
    ], size=16)
    add_textbox(s, Inches(6.9), Inches(1.95), Inches(5.8), Inches(0.35), "Next", size=14, bold=True, color=NAVY)
    add_bullets(s, Inches(6.9), Inches(2.35), Inches(5.8), Inches(3.3), [
        "Complete consented local collection",
        "Verified pattern labels and retrain",
        "Report FAR/FRR across thresholds",
        "Durable storage if work continues",
    ], size=16)
    add_textbox(s, Inches(0.7), Inches(5.6), Inches(11.5), Inches(0.5),
                "Thank you  ·  Questions welcome",
                size=18, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    footer(s, 12, total, prs)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"Saved {OUT}")
    print(f"Slides: {len(prs.slides)}")


if __name__ == "__main__":
    main()

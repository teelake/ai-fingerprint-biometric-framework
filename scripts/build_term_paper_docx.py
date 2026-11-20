"""Build CSC790 master's term paper as a Word document."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt

OUT = Path(__file__).resolve().parents[1] / "reports" / "CSC790_Term_Paper_v2.docx"


def set_run(run, size=12, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def P(
    doc,
    text,
    *,
    size=12,
    bold=False,
    italic=False,
    align="justify",
    indent=True,
    before=0,
    after=0,
):
    p = doc.add_paragraph()
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        indent = False
    elif align == "left":
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.first_line_indent = Cm(1.27) if indent else Cm(0)
    r = p.add_run(text)
    set_run(r, size=size, bold=bold, italic=italic)
    return p


def H(doc, text, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    p.paragraph_format.space_before = Pt(18 if level == 1 else 12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run(text)
    set_run(r, size=12, bold=True)


def bullets(doc, items, numbered=False):
    for item in items:
        p = doc.add_paragraph(style="List Number" if numbered else "List Bullet")
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        p.paragraph_format.first_line_indent = Cm(0)
        if p.runs:
            p.runs[0].text = ""
        r = p.add_run(item)
        set_run(r)


def table(doc, headers, rows):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        set_run(cell.paragraphs[0].add_run(h), size=11, bold=True)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = t.rows[ri + 1].cells[ci]
            cell.text = ""
            set_run(cell.paragraphs[0].add_run(val), size=11)
    doc.add_paragraph()


def main():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1.25)
        s.right_margin = Inches(1)

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

    # Title page
    P(doc, "UNIVERSITY OF IBADAN", bold=True, align="center", indent=False, after=0)
    P(doc, "FACULTY OF COMPUTING", bold=True, align="center", indent=False, after=0)
    P(doc, "M.Sc. Artificial Intelligence", align="center", indent=False, after=18)
    P(
        doc,
        "Development of an AI-Powered Fingerprint Biometric Framework for "
        "Individual Identification and Security Monitoring in Nigeria",
        bold=True,
        align="center",
        indent=False,
        after=18,
        size=14,
    )
    P(
        doc,
        "A Term Paper submitted in partial fulfilment of the requirements for",
        align="center",
        indent=False,
    )
    P(
        doc,
        "CSC790 — Foundations of Deep Learning",
        bold=True,
        align="center",
        indent=False,
        after=18,
    )
    P(doc, "By", align="center", indent=False)
    P(doc, "Oluwatobi Peter Alake (Matric No.: 261244)", align="center", indent=False)
    P(
        doc,
        "Tiwalayomi Aladesuyi (Matric No.: 259725)",
        align="center",
        indent=False,
        after=18,
    )
    P(
        doc,
        "Note to readers: This paper is an original write-up based on the authors’ "
        "implementation and cited scholarly sources. It replaces the earlier short "
        "coursework note with a fuller master’s-level term-paper treatment.",
        italic=True,
        align="center",
        indent=False,
        after=12,
    )
    doc.add_page_break()

    # Abstract
    H(doc, "Abstract")
    P(
        doc,
        "Fingerprint biometrics remain one of the most widely used methods of "
        "automatic identity verification. In Nigeria, fingerprints already support "
        "national identification, financial-service authentication, and voter "
        "accreditation during elections through devices such as the Bimodal Voter "
        "Accreditation System (BVAS). At the same time, many academic demonstrations "
        "of biometric systems stop at conceptual discussion and do not show a "
        "complete learning pipeline. This term paper presents the design and "
        "implementation of a deep-learning fingerprint framework that performs three "
        "related tasks: image preprocessing, pattern classification into arch, loop "
        "and whorl, and identity matching through CNN embeddings.",
    )
    P(
        doc,
        "The system is built around a compact convolutional neural network "
        "implemented in PyTorch. The same backbone is used in two ways. First, a "
        "classification head predicts fingerprint pattern class. Second, an embedding "
        "vector is extracted and stored for later matching by cosine similarity. "
        "Enrolment records are kept in SQLite, and a Streamlit web application "
        "provides a practical interface for enrolment, verification and pattern "
        "classification. Public fingerprint data from FVC2002 Set B was used for "
        "early pipeline validation while local field collection was being organised.",
    )
    P(
        doc,
        "The work is positioned as a master’s-level applied study rather than a "
        "finished security product. It contributes a reproducible prototype, an "
        "explicit discussion of methodological choices, and a critical treatment of "
        "limits such as data scarcity, cloud persistence and the danger of "
        "overstating group differences without adequate local samples. The paper "
        "concludes with recommendations for stronger evaluation, ethical field "
        "collection and more durable storage if the prototype is extended beyond "
        "coursework.",
    )
    P(
        doc,
        "Keywords: fingerprint biometrics, convolutional neural network, deep "
        "learning, identity verification, pattern classification, Nigeria",
        italic=True,
        indent=False,
        before=6,
    )

    # 1
    H(doc, "1. Introduction")
    P(
        doc,
        "Automatic person recognition is no longer a laboratory curiosity. "
        "Governments and private institutions increasingly rely on biometric traits "
        "because passwords can be shared or forgotten, while physical characteristics "
        "are harder to transfer. Among biometric modalities, fingerprints occupy a "
        "special place. They are relatively stable over adult life, cheap to capture "
        "with optical or capacitive sensors, and already familiar to many users in "
        "Nigeria through national identity enrolment, banking know-your-customer "
        "procedures, and election-day voter accreditation.",
    )
    P(
        doc,
        "In recent Nigerian electoral practice, fingerprint verification has been "
        "central to efforts aimed at reducing impersonation and multiple voting. The "
        "Independent National Electoral Commission (INEC) has deployed the Bimodal "
        "Voter Accreditation System (BVAS), which uses biometric checks — commonly "
        "fingerprint, with facial capture as an alternative mode — to confirm that a "
        "voter at the polling unit matches the register. This public use of "
        "fingerprint technology strengthens the local relevance of academic work on "
        "fingerprint recognition. It also raises the standard of care expected from "
        "researchers: election biometrics operate under time pressure, variable "
        "finger conditions, and high public scrutiny. An academic prototype should "
        "therefore be honest about quality limits rather than pretending to be an "
        "electoral device.",
    )
    P(
        doc,
        "Deep learning has changed how image-based recognition systems are built. "
        "Instead of relying only on hand-crafted minutiae rules, convolutional neural "
        "networks can learn hierarchical representations directly from pixel data. "
        "For a Foundations of Deep Learning course, fingerprint recognition is "
        "therefore an attractive case study: it forces students to move from lecture "
        "concepts such as convolution, pooling, regularisation and representation "
        "learning into a concrete recognition pipeline.",
    )
    P(
        doc,
        "The present study develops a prototype framework with three practical aims. "
        "It should accept fingerprint images, enrol individuals into a searchable "
        "store, and verify later probes against that store. It should also classify "
        "basic dermatoglyphic patterns. A further requirement in the assigned topic "
        "is sensitivity to Nigeria’s multi-ethnic setting. The prototype therefore "
        "records tribe labels at enrolment so that later statistical work can be done "
        "when enough ethically collected local samples become available.",
    )
    P(
        doc,
        "This paper expands the earlier short project note into a fuller term-paper "
        "treatment. In particular, it supplies a literature review, clarifies "
        "research questions, explains design decisions, and discusses results and "
        "limits with the caution expected at master’s level.",
    )

    H(doc, "1.1 Research problem", level=2)
    P(
        doc,
        "The practical problem can be stated as follows: how can a convolutional "
        "neural network be used to support both fingerprint pattern classification "
        "and identity matching in a transparent, reproducible prototype suitable for "
        "academic demonstration in a Nigerian context?",
    )
    P(
        doc,
        "Two related difficulties make the problem non-trivial. First, fingerprint "
        "images vary with pressure, moisture, rotation and partial contact, so naive "
        "matching is unreliable. Second, claims about differences across ethnic "
        "groups require carefully labelled local data; without such data, any strong "
        "demographic conclusion would be scientifically weak and ethically careless.",
    )

    H(doc, "1.2 Research questions", level=2)
    bullets(
        doc,
        [
            "How can preprocessing and a compact CNN be combined to support pattern classification of fingerprint images?",
            "Can CNN embeddings, compared by cosine similarity, provide a workable identity-matching mechanism for a small enrolment gallery?",
            "What design, data and deployment constraints arise when such a system is implemented as a master’s coursework prototype for use in a Nigerian research setting?",
        ],
        numbered=True,
    )

    H(doc, "1.3 Contributions", level=2)
    P(doc, "Within the scope of a semester term paper, the work contributes:")
    bullets(
        doc,
        [
            "an end-to-end fingerprint pipeline covering preprocessing, CNN training, embedding-based matching and a deployable demo;",
            "a dual-use network design in which one backbone supports both pattern classification and identity representation;",
            "a critical account of dataset choice, evaluation limits and ethical caution around ethnic labelling;",
            "a documented public demonstration and source repository that make the study inspectable.",
        ],
        numbered=True,
    )

    H(doc, "1.4 Scope and organisation", level=2)
    P(
        doc,
        "The study does not claim to replace Automated Fingerprint Identification "
        "Systems used by forensic laboratories, nor does it claim certified security "
        "performance. Section 2 reviews related literature. Section 3 states "
        "objectives. Section 4 presents methodology. Section 5 describes "
        "implementation. Section 6 discusses results. Section 7 treats challenges, "
        "limitations and ethics. Section 8 concludes.",
    )

    # 2 Literature
    H(doc, "2. Literature Review")
    P(
        doc,
        "A master’s treatment of this topic must begin with what is already known. "
        "The review below is organised around biometric foundations, classical "
        "fingerprint methods, deep learning for images, deep learning for "
        "fingerprints, Nigerian identity context, and evaluation practice. The aim "
        "is synthesis, not a catalogue of abstracts.",
    )

    H(doc, "2.1 Biometrics and identity assurance", level=2)
    P(
        doc,
        "Jain, Ross and Prabhakar (2004) describe biometrics as automated recognition "
        "of individuals based on physiological or behavioural characteristics. A "
        "useful biometric trait should be universal, distinctive, permanent and "
        "collectable, while also resisting circumvention as far as practical systems "
        "allow. Fingerprints satisfy many of these criteria and have therefore become "
        "a default modality in civil and commercial identity systems.",
    )
    P(
        doc,
        "Wayman, Jain, Maltoni and Maio (2005) emphasise that biometric systems are "
        "socio-technical. Accuracy alone is not enough; usability, privacy, template "
        "protection and failure-to-enrol rates also matter. For student prototypes "
        "this warning is important. A system that works on clean laboratory images "
        "may still fail when volunteers present dry fingers or incomplete impressions.",
    )

    H(doc, "2.2 Classical fingerprint recognition", level=2)
    P(
        doc,
        "Traditional fingerprint recognition is carefully documented by Maltoni, "
        "Maio, Jain and Prabhakar (2009). Typical pipelines include image "
        "acquisition, segmentation, enhancement, feature extraction and matching. "
        "Minutiae — ridge endings and bifurcations — remain the most common features "
        "for identity matching. Pattern classes such as arch, loop and whorl are "
        "coarser labels. They are useful for indexing and for dermatoglyphic study, "
        "but they are not by themselves sufficient for unique identification.",
    )
    P(
        doc,
        "Enhancement is central because ridge contrast is often weak. Hong, Wan and "
        "Jain (1998) popularised orientation-driven enhancement strategies that "
        "remain influential. In modern deep-learning pipelines, classical "
        "enhancement is sometimes reduced, yet light denoising and contrast "
        "normalisation still help when training data are limited.",
    )
    P(
        doc,
        "Benchmark competitions such as FVC2002 (Maio, Maltoni, Cappelli, Wayman & "
        "Jain, 2002) shaped evaluation culture in the field. They showed that capture "
        "conditions vary sharply across sensors and that algorithms must cope with "
        "multiple impressions of the same finger. That lesson directly informs the "
        "present project’s decision to allow several samples under one person "
        "identifier.",
    )

    H(doc, "2.3 Deep learning and convolutional networks", level=2)
    P(
        doc,
        "LeCun, Bottou, Bengio and Haffner (1998) demonstrated that convolutional "
        "networks can learn hierarchical visual features with far less hand "
        "engineering than earlier methods. Later work, including Krizhevsky, "
        "Sutskever and Hinton (2012), showed that deeper CNNs trained on large image "
        "collections can reach strong recognition performance. Goodfellow, Bengio "
        "and Courville (2016) summarise the main building blocks used in this paper: "
        "convolution, non-linear activation, pooling, dropout and stochastic "
        "gradient training.",
    )
    P(
        doc,
        "For a Foundations of Deep Learning course, fingerprints are valuable "
        "because they make representation learning tangible. Early layers can be "
        "imagined as responding to local ridge structure; deeper layers summarise "
        "broader spatial arrangements. Whether or not one visualises filters in "
        "detail, the conceptual point remains: the network learns features from data "
        "rather than receiving only manually designed minutiae rules.",
    )

    H(doc, "2.4 Deep learning for fingerprints", level=2)
    P(
        doc,
        "Recent biometric research has explored CNNs for fingerprint enhancement, "
        "spoof detection, pattern classification and latent matching. Across deep "
        "biometric work, a recurring design choice is to learn an embedding space in "
        "which similar prints lie closer together than dissimilar ones. That idea is "
        "consistent with broader representation-learning practice in deep learning "
        "(Goodfellow et al., 2016).",
    )
    P(
        doc,
        "In applied student and research prototypes, two design patterns appear "
        "repeatedly. The first trains a classifier for a closed set of labels, for "
        "example pattern classes. The second extracts an embedding and compares "
        "probe and gallery vectors. The second pattern is attractive when the set of "
        "enrolled identities changes over time, because new people can be added "
        "without immediately retraining a giant multi-class identity head.",
    )
    P(
        doc,
        "The present study follows that dual pattern: a compact CNN provides both a "
        "three-class pattern head and a 256-dimensional embedding for matching. This "
        "is not claimed as a novel algorithm. It is claimed as a coherent master’s "
        "application of ideas taught in the course.",
    )

    H(
        doc,
        "2.5 Nigerian context: identity systems, elections and demographic caution",
        level=2,
    )
    P(
        doc,
        "Nigeria’s identity infrastructure has expanded through national "
        "identification programmes, financial-sector biometric checks, and election "
        "administration. Fingerprints are therefore not an abstract research toy in "
        "the local setting; they already participate in high-stakes public processes.",
    )
    P(
        doc,
        "A particularly visible example is voter accreditation. INEC’s BVAS was "
        "introduced to improve the integrity of accreditation by verifying voters "
        "biometrically at the polling unit. In public discussion and official "
        "communication, BVAS is associated with fingerprint capture and, where "
        "fingerprint verification is difficult, facial authentication as a "
        "complementary path. For this term paper, BVAS matters in two ways. First, "
        "it shows why fingerprint image quality, false rejects and usability are "
        "practical national concerns, not only laboratory metrics. Second, it warns "
        "against academic overclaim: a coursework CNN prototype is not BVAS, does "
        "not certify voters, and should not be presented as an electoral replacement.",
    )
    P(
        doc,
        "That institutional reality makes fingerprint research locally relevant. "
        "However, relevance is not the same as licence to over-interpret ethnicity.",
    )
    P(
        doc,
        "Dermatoglyphic studies have long examined pattern frequencies across "
        "populations, but sampling quality and definition of groups vary. For a term "
        "paper, the responsible position is modest. Tribe or ethnic labels may be "
        "stored for later analysis, yet no strong claim should be made about innate "
        "group differences until a sufficiently large, consented and carefully "
        "labelled local dataset exists. This caution is consistent with good research "
        "ethics and with the biometric literature’s insistence on population-aware "
        "evaluation (Jain et al., 2004; Wayman et al., 2005).",
    )

    H(doc, "2.6 Evaluation practice", level=2)
    P(
        doc,
        "Biometric evaluation distinguishes verification (one-to-one) from "
        "identification (one-to-many). Useful measures include true accept rate, "
        "false accept rate, false reject rate and equal error rate. Pattern "
        "classification, by contrast, is usually reported with accuracy, per-class "
        "precision/recall and confusion matrices.",
    )
    P(
        doc,
        "Public datasets enable early experimentation, but they do not automatically "
        "answer Nigerian deployment questions. Sensor mismatch, skin condition and "
        "population differences can all shift performance. Therefore, results "
        "obtained on FVC-style data should be treated as pipeline evidence, not as "
        "final operational proof.",
    )

    H(doc, "2.7 Summary of the gap", level=2)
    P(
        doc,
        "The literature shows mature classical fingerprint methods, strong evidence "
        "that CNNs work for image recognition, and growing use of deep models in "
        "biometrics. What remains scarce in many coursework settings is a complete, "
        "inspectable pipeline that joins preprocessing, learning, matching, "
        "interface and honest limitation analysis. That is the gap this term paper "
        "addresses at master’s level: not the invention of a new fingerprint "
        "theorem, but the rigorous construction and critique of an applied "
        "deep-learning biometric prototype.",
    )

    # 3
    H(doc, "3. Aim and Objectives")
    H(doc, "3.1 Aim", level=2)
    P(
        doc,
        "To design, implement and critically evaluate a deep-learning fingerprint "
        "biometric prototype for individual identification and pattern "
        "classification, with attention to Nigerian research context and "
        "master’s-level methodological standards.",
    )
    H(doc, "3.2 Specific objectives", level=2)
    bullets(
        doc,
        [
            "To organise fingerprint images in a reproducible directory and naming scheme that supports person identity and optional ethnic labels.",
            "To implement preprocessing that improves ridge readability before network input.",
            "To train a compact CNN for arch/loop/whorl pattern classification.",
            "To derive embeddings from the same network for enrolment and cosine-similarity verification.",
            "To expose the pipeline through a usable web demonstration.",
            "To discuss challenges, ethical limits and future work with academic caution.",
        ],
        numbered=True,
    )

    # 4
    H(doc, "4. Methodology")
    H(doc, "4.1 Research design", level=2)
    P(
        doc,
        "The study adopts an applied experimental design. A software prototype is "
        "built, exercised on available fingerprint images, and assessed qualitatively "
        "through demonstration behaviour and quantitatively where labelled pattern "
        "data permit. The design is appropriate for a Foundations of Deep Learning "
        "term paper because the object of study is the learning pipeline itself.",
    )

    H(doc, "4.2 Data sources", level=2)
    P(doc, "Two data streams are recognised.")
    P(
        doc,
        "Public benchmark data. FVC2002 Set B was used as a fallback for early "
        "training and preprocessing tests. It provides multiple impressions per "
        "finger and therefore illustrates intra-class variation.",
    )
    P(
        doc,
        "Local field pathway. The project structure supports Nigerian samples "
        "organised by tribe and person identity. Local collection requires informed "
        "consent, suitable scanners and careful handling of biometric data. At the "
        "time of writing, this pathway remains partially complete; the paper "
        "therefore avoids presenting unfinished local statistics as settled findings.",
    )
    P(
        doc,
        "File naming follows the pattern: data/raw/<tribe>/<personID>/"
        "<personID>_<fingerCode>_<sample>.png. Example: P001_RT_01.png denotes "
        "person P001, right thumb, sample 01.",
    )

    H(doc, "4.3 Preprocessing", level=2)
    P(
        doc,
        "Each image is converted to grayscale, lightly smoothed with a small "
        "Gaussian filter, contrast-enhanced using CLAHE, sharpened with a modest "
        "kernel, and resized to 224×224. The intention is not to replace a full "
        "classical enhancement stack. It is to give the CNN cleaner ridge structure "
        "under limited-data conditions.",
    )

    H(doc, "4.4 Model architecture", level=2)
    P(
        doc,
        "A compact CNN with four convolutional blocks was implemented in PyTorch. "
        "Each of the first blocks uses 3×3 convolution, batch normalisation, ReLU "
        "activation and max pooling. The final block ends with adaptive average "
        "pooling, producing a 256-dimensional feature vector.",
    )
    P(doc, "Two outputs are derived:")
    bullets(
        doc,
        [
            "Pattern head: fully connected layers with dropout predict three classes — arch, loop and whorl.",
            "Embedding path: the 256-dimensional feature vector is L2-normalised and stored for matching.",
        ],
        numbered=True,
    )
    P(
        doc,
        "Training uses cross-entropy loss for pattern classification, with standard "
        "minibatch gradient updates. Exact epoch count and learning-rate schedule "
        "are treated as experimental settings rather than as mystical constants; "
        "they can be adjusted as more labelled data arrive.",
    )

    H(doc, "4.5 Enrolment and verification protocol", level=2)
    P(
        doc,
        "During enrolment, an image is embedded and inserted into SQLite with person "
        "ID and tribe label. Multiple samples per person are allowed. This choice "
        "mirrors biometric practice: one noisy impression should not exhaust a "
        "person’s representation.",
    )
    P(
        doc,
        "During verification, a probe embedding is compared with all gallery "
        "embeddings by cosine similarity. If the maximum score meets or exceeds a "
        "threshold τ, the corresponding identity is returned. The demo default is "
        "τ = 0.75, adjustable by the user.",
    )

    H(doc, "4.6 Evaluation approach", level=2)
    P(
        doc,
        "For pattern classification, standard supervised metrics are appropriate "
        "once verified labels exist: accuracy, confusion matrix and classification "
        "report. For identity matching, a fuller master’s evaluation would compute "
        "false accept and false reject behaviour across thresholds. In the present "
        "prototype stage, matching is demonstrated operationally through the live "
        "application, while formal ROC-style reporting is listed as future work once "
        "the local gallery is large enough to make such curves meaningful.",
    )

    H(doc, "4.7 Implementation environment", level=2)
    table(
        doc,
        ["Component", "Choice"],
        [
            ["Language", "Python 3.10+"],
            ["Deep learning", "PyTorch"],
            ["Image processing", "OpenCV, NumPy"],
            ["Interface", "Streamlit"],
            ["Identity store", "SQLite"],
            ["Hosting for demo", "Streamlit Community Cloud"],
            ["Version control", "GitHub"],
        ],
    )

    # 5
    H(doc, "5. System Implementation")
    H(doc, "5.1 Software modules", level=2)
    P(
        doc,
        "The codebase separates concerns: preprocessing, model definition, training "
        "and evaluation, matching/enrolment logic, and the Streamlit interface. This "
        "modularity matters academically. It shows that the project is not a single "
        "opaque notebook, but a structured system that can be inspected and extended.",
    )

    H(doc, "5.2 User interface behaviour", level=2)
    P(
        doc,
        "The Streamlit application exposes three tabs: Enrol, Verify and Pattern. "
        "Usability details were added after rehearsal failures: automatic person-ID "
        "detection from structured filenames, warnings when an ID already exists, "
        "rejection of blank IDs, and clearer messages for unreadable images. These "
        "details are not cosmetic. At master’s level, a recognition system must fail "
        "intelligibly.",
    )

    H(doc, "5.3 Deployment notes", level=2)
    P(
        doc,
        "The public demo is available at https://fingerprint-biometric.streamlit.app. "
        "Free hosting introduces constraints. Applications may sleep after "
        "inactivity, and local SQLite state on the cloud instance is not a durable "
        "identity vault. Those constraints are discussed as part of the research "
        "context rather than hidden from the reader.",
    )

    # 6
    H(doc, "6. Results and Discussion")
    H(doc, "6.1 Pipeline demonstrability", level=2)
    P(
        doc,
        "The central empirical result of this term paper is that the pipeline works "
        "as an integrated prototype. A user can enrol fingerprint images, verify "
        "later probes against the gallery, and, when a trained checkpoint is "
        "present, obtain pattern predictions. This matters because many academic "
        "biometric write-ups describe architecture without showing an operable path "
        "from image to decision.",
    )

    H(doc, "6.2 Pattern classification", level=2)
    P(
        doc,
        "Pattern classification depends on labelled examples and a deployed "
        "checkpoint. With public bootstrap labels, early training can proceed, but "
        "label noise must be acknowledged. Automatic or weakly assigned pattern "
        "labels are useful for engineering progress; they are not a substitute for "
        "expert-verified dermatoglyphic annotation. Accordingly, pattern results are "
        "treated as evidence that the classification pathway exists, not as "
        "definitive anthropological findings.",
    )

    H(doc, "6.3 Identity matching behaviour", level=2)
    P(
        doc,
        "Embedding-based matching behaves as expected for a small gallery: repeated "
        "impressions of an enrolled finger tend to score higher than unrelated "
        "probes when image quality is adequate. Threshold choice remains a "
        "trade-off. A high τ reduces false accepts but increases false rejects; a "
        "low τ does the opposite. The adjustable slider in the demo makes that "
        "trade-off visible to non-specialist users and to examiners.",
    )

    H(doc, "6.4 Discussion against the literature", level=2)
    P(
        doc,
        "The results align with classical insights from Maltoni et al. (2009): "
        "capture quality dominates outcomes. They also align with deep-learning "
        "expectations from LeCun et al. (1998) and Goodfellow et al. (2016): a CNN "
        "can serve as a feature extractor for downstream comparison. The study does "
        "not overturn established biometric science. Its value lies in showing how "
        "those ideas can be combined carefully in a master’s prototype aimed at a "
        "Nigerian academic setting.",
    )

    H(doc, "6.5 What cannot yet be claimed", level=2)
    P(doc, "The paper does not claim:")
    bullets(
        doc,
        [
            "operational readiness for banking, national ID backends, or election accreditation systems such as BVAS;",
            "forensic-grade identification performance;",
            "statistically settled differences among Nigerian ethnic groups;",
            "permanence of cloud enrolment records under free hosting.",
        ],
    )
    P(doc, "Stating these non-claims is part of scholarly honesty.")

    # 7
    H(doc, "7. Challenges, Limitations and Ethical Considerations")
    H(doc, "7.1 Challenges encountered", level=2)
    P(
        doc,
        "Scope management. The assigned topic can expand into a full thesis. The "
        "team deliberately reduced scope to a working prototype with clear modules.",
    )
    P(
        doc,
        "Data collection lag. Hardware acquisition, volunteer recruitment and "
        "consent processes move more slowly than software development. Public data "
        "kept the learning pipeline alive, but local data remain essential for the "
        "Nigerian research narrative.",
    )
    P(
        doc,
        "Image quality. Dry skin, blur and partial prints still degrade matching. "
        "Preprocessing helps; it does not invent missing ridge detail.",
    )
    P(
        doc,
        "Deployment friction. Shared hosting designed for PHP sites is a poor home "
        "for PyTorch applications. Streamlit Cloud solved demonstration needs while "
        "introducing sleep and persistence limits.",
    )

    H(doc, "7.2 Technical limitations", level=2)
    P(
        doc,
        "The matcher is a thresholded embedding comparator, not a full AFIS with "
        "sophisticated latent-print logic. The pattern model is only as trustworthy "
        "as its labels. SQLite on a sleeping cloud instance is unsuitable for "
        "long-term identity storage.",
    )

    H(doc, "7.3 Ethical considerations", level=2)
    P(
        doc,
        "Biometric data are sensitive. Even a coursework prototype should minimise "
        "unnecessary retention, avoid unauthorised redistribution of volunteer "
        "prints, and obtain informed consent for local collection. Ethnic labels, if "
        "used, must serve transparent research purposes and must not be twisted into "
        "discriminatory claims. The authors therefore treat demographic fields as "
        "analytical metadata under ethical constraint, not as tools for stereotyping.",
    )

    H(doc, "7.4 Academic integrity note", level=2)
    P(
        doc,
        "This term paper is written from the authors’ own implementation experience "
        "and from engagement with published sources listed in the references. Ideas "
        "from prior scholars are acknowledged by citation. Wording is original. "
        "Where public datasets are used, they are named. Where local evidence is "
        "incomplete, the paper says so instead of fabricating certainty.",
    )

    # 8
    H(doc, "8. Conclusion and Future Work")
    P(
        doc,
        "This term paper has presented a master’s-level applied study of deep "
        "learning for fingerprint biometrics. Starting from established literature "
        "on biometrics, classical fingerprint recognition and convolutional "
        "networks, the authors designed a prototype that preprocesses fingerprint "
        "images, classifies basic patterns, and matches identities through CNN "
        "embeddings. A Streamlit interface and public repository make the work "
        "demonstrable and inspectable.",
    )
    P(
        doc,
        "The study’s main academic lesson is methodological. Deep learning becomes "
        "meaningful for biometric research only when representation learning is "
        "joined to careful data handling, explicit evaluation limits and ethical "
        "restraint. In that sense, the project serves the aims of CSC790: it turns "
        "foundational concepts into a working recognition pipeline and subjects that "
        "pipeline to critique.",
    )
    P(doc, "Future work should proceed in four directions:")
    bullets(
        doc,
        [
            "complete consented local fingerprint collection with documented scanner settings;",
            "replace weak pattern labels with verified annotations and retrain;",
            "report formal verification curves (FAR/FRR across thresholds) on a fixed test protocol;",
            "move enrolment storage to a durable service if the prototype is extended beyond coursework.",
        ],
        numbered=True,
    )

    # 9
    H(doc, "9. Division of Work")
    table(
        doc,
        ["Area", "Responsibility"],
        [
            [
                "System architecture, CNN, matching logic, Streamlit demo, repository",
                "Oluwatobi Peter Alake",
            ],
            [
                "Hardware planning, volunteer outreach, sample-collection support",
                "Tiwalayomi Aladesuyi",
            ],
            [
                "Topic framing, testing, term-paper writing and presentation",
                "Both authors",
            ],
        ],
    )

    # References
    H(doc, "References")
    refs = [
        "Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep learning. MIT Press.",
        "Independent National Electoral Commission. (n.d.). Bimodal Voter Accreditation System (BVAS) — official electoral technology used for voter accreditation in Nigeria. https://inecnigeria.org/",
        "Hong, L., Wan, Y., & Jain, A. (1998). Fingerprint image enhancement: Algorithm and performance evaluation. IEEE Transactions on Pattern Analysis and Machine Intelligence, 20(8), 777–789.",
        "Jain, A. K., Ross, A., & Prabhakar, S. (2004). An introduction to biometric recognition. IEEE Transactions on Circuits and Systems for Video Technology, 14(1), 4–20.",
        "Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012). ImageNet classification with deep convolutional neural networks. In Advances in Neural Information Processing Systems (pp. 1097–1105).",
        "LeCun, Y., Bottou, L., Bengio, Y., & Haffner, P. (1998). Gradient-based learning applied to document recognition. Proceedings of the IEEE, 86(11), 2278–2324.",
        "Maio, D., Maltoni, D., Cappelli, R., Wayman, J. L., & Jain, A. K. (2002). FVC2002: Second fingerprint verification competition. In Proceedings of the 16th International Conference on Pattern Recognition (pp. 811–814). IEEE.",
        "Maltoni, D., Maio, D., Jain, A. K., & Prabhakar, S. (2009). Handbook of fingerprint recognition (2nd ed.). Springer.",
        "Wayman, J., Jain, A., Maltoni, D., & Maio, D. (Eds.). (2005). Biometric systems: Technology, design and performance evaluation. Springer.",
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-1.27)
        set_run(p.add_run(ref))

    H(doc, "Appendix A: Artefacts")
    bullets(
        doc,
        [
            "Live demo: https://fingerprint-biometric.streamlit.app",
            "Source code: https://github.com/teelake/ai-fingerprint-biometric-framework",
            "Course: CSC790 — Foundations of Deep Learning, University of Ibadan",
        ],
    )

    H(doc, "Appendix B: Glossary")
    bullets(
        doc,
        [
            "CNN: Convolutional Neural Network; a deep model suited to images.",
            "Embedding: A list of numbers that represents a fingerprint for comparison.",
            "Cosine similarity: A score of how closely two embeddings point in the same direction.",
            "Enrolment: Saving a person’s fingerprint representation into the system.",
            "Verification / identification: Checking a new print against stored records.",
            "Arch / loop / whorl: Broad fingerprint pattern classes.",
        ],
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    words = sum(len(p.text.split()) for p in doc.paragraphs)
    print(f"Saved {OUT}")
    print(f"Paragraphs={len(doc.paragraphs)} words≈{words}")


if __name__ == "__main__":
    main()

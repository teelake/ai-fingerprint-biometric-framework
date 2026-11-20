"""Convert the CSC790 markdown report to a Word document."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "CSC790_Project_Report.docx"


def set_run_font(run, name="Times New Roman", size=12, bold=False, italic=False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def add_para(doc, text, *, size=12, bold=False, italic=False, align="left", space_after=8):
    p = doc.add_paragraph()
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading_custom(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(6)
    size = 14 if level == 1 else 12
    run = p.add_run(text)
    set_run_font(run, size=size, bold=True)
    return p


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        run = p.add_run(item)
        set_run_font(run, size=12)


def add_numbered(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        run = p.add_run(item)
        set_run_font(run, size=12)


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, size=11, bold=True)
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            cell = table.rows[r_i + 1].cells[c_i]
            cell.text = ""
            run = cell.paragraphs[0].add_run(val)
            set_run_font(run, size=11)
    doc.add_paragraph()


def main():
    doc = Document()

    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

    # Title page block
    add_para(doc, "UNIVERSITY OF IBADAN", size=14, bold=True, align="center", space_after=4)
    add_para(doc, "FACULTY OF COMPUTING", size=12, bold=True, align="center", space_after=4)
    add_para(doc, "M.Sc. Artificial Intelligence", size=12, align="center", space_after=18)

    add_para(
        doc,
        "Development of an AI-Powered Fingerprint Biometric Framework for "
        "Individual Identification and Security Monitoring in Nigeria",
        size=14,
        bold=True,
        align="center",
        space_after=18,
    )

    add_para(doc, "Course: CSC790 — Foundations of Deep Learning", align="center", space_after=4)
    add_para(doc, "Coursework Project Report", align="center", space_after=18)

    add_para(doc, "Submitted by:", align="center", space_after=4)
    add_para(doc, "Oluwatobi Peter Alake", align="center", space_after=2)
    add_para(doc, "Tiwalayomi Aladesuyi", align="center", space_after=18)

    add_para(doc, "Demo: https://fingerprint-biometric.streamlit.app", align="center", space_after=2)
    add_para(
        doc,
        "Repository: https://github.com/teelake/ai-fingerprint-biometric-framework",
        align="center",
        space_after=24,
    )

    doc.add_page_break()

    # 1
    add_heading_custom(doc, "1. Introduction")
    add_para(
        doc,
        "This report presents the coursework project we carried out for CSC790 "
        "(Foundations of Deep Learning). The assigned topic was to develop an "
        "AI-powered fingerprint biometric framework that can support individual "
        "identification, with attention to a Nigerian context.",
        align="justify",
    )
    add_para(doc, "In simple terms, we set out to build a working prototype that can:", align="justify")
    add_numbered(
        doc,
        [
            "accept fingerprint images,",
            "enrol a person into a small identity store,",
            "verify whether a new scan matches someone already enrolled, and",
            "classify fingerprint patterns into arch, loop, or whorl.",
        ],
    )
    add_para(
        doc,
        "We are not claiming to have built a production security system. What we have "
        "is a coursework prototype that shows how deep learning ideas taught in class "
        "can be applied to a biometric problem.",
        align="justify",
    )
    add_para(
        doc,
        "Work was shared between us. Oluwatobi focused on the software side: "
        "preprocessing, model design, matching logic, and the web demo. Tiwalayomi "
        "focused on hardware considerations and the practical side of collecting "
        "fingerprint samples across different groups. Both of us worked together on "
        "the project framing, testing, and this report.",
        align="justify",
    )

    # 2
    add_heading_custom(doc, "2. Problem Statement")
    add_para(
        doc,
        "Fingerprint biometrics are already used in many identity systems in Nigeria, "
        "including national identification and banking-related verification. At the "
        "same time, student and research prototypes often stop at theory. For this "
        "course, we wanted something we could actually run and demonstrate.",
        align="justify",
    )
    add_para(doc, "The main problem we addressed was:", align="justify")
    add_para(
        doc,
        "How can a convolutional neural network be used to support fingerprint-based "
        "identification and pattern classification in a small, workable prototype?",
        italic=True,
        align="justify",
    )
    add_para(
        doc,
        "A second concern in the project brief was the study of dermatoglyphic "
        "features across selected Nigerian ethnic groups. In this coursework version, "
        "we prepared the system to store tribe labels during enrolment. Full "
        "statistical comparison across groups depends on enough field samples, which "
        "remains an ongoing part of the work.",
        align="justify",
    )

    # 3
    add_heading_custom(doc, "3. Objectives")
    add_para(doc, "Our objectives for the semester project were:", align="justify")
    add_numbered(
        doc,
        [
            "Collect or organise fingerprint images in a clear folder structure.",
            "Preprocess the images to make ridge detail easier for a model to use.",
            "Train a CNN for pattern classification (arch, loop, whorl).",
            "Use CNN embeddings for simple identity matching (enrol and verify).",
            "Build a simple web demo that non-technical users can try.",
            "Document what worked, what did not, and what still needs improvement.",
        ],
    )

    # 4
    add_heading_custom(doc, "4. Related Background (Brief)")
    add_para(
        doc,
        "Fingerprint recognition generally involves image capture, enhancement, "
        "feature extraction, and matching. Traditional systems rely heavily on "
        "minutiae. In this project we took a deep learning route: a CNN learns useful "
        "representations directly from the fingerprint image.",
        align="justify",
    )
    add_para(doc, "We used the CNN in two ways:", align="justify")
    add_bullets(
        doc,
        [
            "as a pattern classifier for arch / loop / whorl, and",
            "as an embedding extractor for identity matching, using cosine similarity "
            "between enrolled and probe embeddings.",
        ],
    )
    add_para(
        doc,
        "This fitted the course focus. Instead of only writing about neural networks, "
        "we had to train one, wire it into a small application, and explain the pipeline.",
        align="justify",
    )

    # 5
    add_heading_custom(doc, "5. Methodology")
    add_heading_custom(doc, "5.1 Overall pipeline", level=2)
    add_para(
        doc,
        "The system follows this flow: Raw fingerprint image → preprocessing → CNN → "
        "either pattern prediction or embedding → enrol / verify decision.",
        align="justify",
    )

    add_heading_custom(doc, "5.2 Data organisation", level=2)
    add_para(
        doc,
        "We adopted a simple naming and folder convention:",
        align="justify",
    )
    add_para(
        doc,
        "data/raw/<tribe>/<personID>/<personID>_<finger>_<sample>.png",
        italic=True,
    )
    add_para(
        doc,
        "Example: P001_RT_01.png means person P001, right thumb, first sample. Tribe "
        "labels such as Yoruba, Igbo, Hausa, Tiv, Kanuri, Fulani, or Other can be "
        "attached during enrolment. This keeps the door open for later group-level "
        "analysis when more local samples are available.",
        align="justify",
    )
    add_para(
        doc,
        "While field collection was being arranged, we also prepared a path to use "
        "public fingerprint sets (for example FVC2002 Set B) so training and pipeline "
        "testing would not stall.",
        align="justify",
    )

    add_heading_custom(doc, "5.3 Preprocessing", level=2)
    add_para(
        doc,
        "Each image is converted to grayscale, lightly denoised, contrast-enhanced "
        "with CLAHE, and sharpened so ridges stand out better. Images are then resized "
        "to 224×224 for the network. This step mattered a lot. Without enhancement, "
        "weak scans were harder for both humans and the model to interpret.",
        align="justify",
    )

    add_heading_custom(doc, "5.4 Model", level=2)
    add_para(
        doc,
        "We implemented a compact CNN in PyTorch with four convolutional blocks, batch "
        "normalisation, ReLU activations, max pooling, and dropout in the classifier "
        "head. The network has two uses:",
        align="justify",
    )
    add_bullets(
        doc,
        [
            "Classification head: outputs probabilities for arch, loop, and whorl.",
            "Embedding path: takes the feature vector before the final classification "
            "layers and uses it as an identity descriptor.",
        ],
    )

    add_heading_custom(doc, "5.5 Enrolment and verification", level=2)
    add_para(
        doc,
        "During enrolment, the system computes an embedding and stores it in a SQLite "
        "database together with the person ID and tribe label. The same person ID may "
        "hold more than one sample. That is intentional; extra samples can make "
        "matching more stable.",
        align="justify",
    )
    add_para(
        doc,
        "During verification, a probe image is converted to an embedding and compared "
        "with all stored embeddings using cosine similarity. If the best score is "
        "above a chosen threshold, the system reports a match.",
        align="justify",
    )

    add_heading_custom(doc, "5.6 Demo application", level=2)
    add_para(
        doc,
        "We built a Streamlit web application with three main actions: Enroll, Verify, "
        "and Pattern classify. The interface includes University of Ibadan and Faculty "
        "of Computing details, course information, and both student names. Person ID "
        "can be filled automatically from filenames such as P001_RT_01.png, which made "
        "testing faster during the demo. The live demo is hosted on Streamlit "
        "Community Cloud.",
        align="justify",
    )

    # 6
    add_heading_custom(doc, "6. Implementation Summary")
    add_table(
        doc,
        ["Component", "Tool / approach"],
        [
            ["Language", "Python"],
            ["Deep learning", "PyTorch"],
            ["Image processing", "OpenCV, NumPy"],
            ["Identity store", "SQLite"],
            ["Demo UI", "Streamlit"],
            ["Deployment", "Streamlit Community Cloud"],
            ["Evaluation helpers", "scikit-learn / SciPy"],
        ],
    )
    add_para(
        doc,
        "Local commands used during development included preprocessing, training, "
        "evaluation, and launching the demo: python -m src.preprocess; "
        "python -m src.train --epochs 20; python -m src.evaluate; "
        "streamlit run app/streamlit_app.py.",
        align="justify",
    )

    # 7
    add_heading_custom(doc, "7. Results and Demonstration")
    add_para(doc, "By the time of presentation, we had a working end-to-end demo:", align="justify")
    add_numbered(
        doc,
        [
            "A user uploads a fingerprint image.",
            "The person can be enrolled with an ID and tribe label.",
            "A later upload can be checked against enrolled records.",
            "If a trained checkpoint is available, pattern classification can also be shown.",
        ],
    )
    add_para(
        doc,
        "In practice, enrolment and verification were the most reliable parts of the "
        "live demo. Pattern classification depends on having a trained model file "
        "deployed with the app. Where that checkpoint was not yet on the cloud host, "
        "the Pattern tab correctly informed the user that training was still required.",
        align="justify",
    )
    add_para(
        doc,
        "We also added small usability details after testing: clearer messages when an "
        "ID already exists, warnings when tribe labels change for the same ID, and "
        "clearer errors for blank IDs or unreadable images. These sound minor, but they "
        "mattered during rehearsal because they stopped the demo from failing silently.",
        align="justify",
    )

    # 8
    add_heading_custom(doc, "8. Challenges Faced")
    add_para(doc, "A few challenges stood out.", align="justify")

    add_para(doc, "1. Time versus scope", bold=True, space_after=2)
    add_para(
        doc,
        "The topic can easily grow into a full research thesis. For a semester course "
        "project we had to cut scope. We focused on a working prototype rather than a "
        "complete national-scale biometric system.",
        align="justify",
    )

    add_para(doc, "2. Data collection", bold=True, space_after=2)
    add_para(
        doc,
        "Collecting clean fingerprint images from volunteers across different groups "
        "takes time, consent, and suitable hardware. That part moved more slowly than "
        "the coding. To keep progress going, we structured the project so public "
        "datasets could support early training while field samples were being organised.",
        align="justify",
    )

    add_para(doc, "3. Image quality", bold=True, space_after=2)
    add_para(
        doc,
        "Not every scan is usable. Blurry, dry, or poorly lit prints reduce matching "
        "quality. Preprocessing helped, but it cannot fully repair a bad capture.",
        align="justify",
    )

    add_para(doc, "4. Hosting choices", bold=True, space_after=2)
    add_para(
        doc,
        "We considered ordinary cPanel hosting first, but Streamlit and PyTorch are not "
        "a natural fit there. Streamlit Community Cloud worked better for a Python "
        "demo. The trade-off is that free apps sleep after inactivity, so the demo "
        "sometimes needs to be woken before presentation.",
        align="justify",
    )

    add_para(doc, "5. Cloud storage behaviour", bold=True, space_after=2)
    add_para(
        doc,
        "Enrolment records live in SQLite on the cloud instance. When the app sleeps "
        "or restarts, those temporary records may not persist. That is acceptable for "
        "a coursework demo, but it would not be acceptable for a real identity system.",
        align="justify",
    )

    add_para(doc, "6. Model readiness on the live app", bold=True, space_after=2)
    add_para(
        doc,
        "Training can be done locally without much drama. Getting the trained weights "
        "onto the hosted demo is an extra step. Until that is done, pattern "
        "classification on the public URL stays limited.",
        align="justify",
    )

    # 9
    add_heading_custom(doc, "9. Limitations")
    add_para(doc, "We are deliberate about what this project is not.", align="justify")
    add_bullets(
        doc,
        [
            "It is an academic prototype, not a certified security product.",
            "The identity matcher is embedding-based and threshold-driven; it is not a full forensic AFIS.",
            "Statistical comparison across Nigerian ethnic groups needs a larger, carefully labelled local dataset before strong claims can be made.",
            "Free cloud hosting is convenient for demonstration, not for permanent enrolment storage.",
            "Performance depends heavily on scan quality and on whether a properly trained checkpoint is available.",
        ],
    )

    # 10
    add_heading_custom(doc, "10. Conclusion")
    add_para(
        doc,
        "This CSC790 project gave us a practical way to apply foundations of deep "
        "learning to a biometric problem. We designed a pipeline from image "
        "preprocessing through CNN modelling to a usable web demo for enrolment, "
        "verification, and pattern classification.",
        align="justify",
    )
    add_para(
        doc,
        "The main achievement is not that the system is finished for real-world "
        "deployment. It is that we now have a concrete prototype we can run, explain, "
        "and improve. The work also made the usual course concepts — convolution, "
        "representation learning, training, evaluation, and overfitting risks — feel "
        "less abstract because they were tied to an actual task.",
        align="justify",
    )
    add_para(doc, "Going forward, the natural next steps are:", align="justify")
    add_numbered(
        doc,
        [
            "complete local fingerprint collection with proper consent,",
            "train and deploy a stronger pattern model on the verified labels,",
            "evaluate matching performance more formally (accuracy, false accept/reject rates), and",
            "replace temporary SQLite storage if the prototype is ever extended beyond coursework use.",
        ],
    )

    # 11
    add_heading_custom(doc, "11. Division of Work")
    add_table(
        doc,
        ["Area", "Lead"],
        [
            ["Software architecture, CNN, matching, Streamlit demo", "Oluwatobi Peter Alake"],
            ["Hardware planning, volunteer outreach, sample collection support", "Tiwalayomi Aladesuyi"],
            ["Project framing, testing, report and presentation", "Both"],
        ],
    )

    # 12
    add_heading_custom(doc, "12. References")
    add_numbered(
        doc,
        [
            "Course materials, CSC790 — Foundations of Deep Learning, University of Ibadan.",
            "Maltoni, D., Maio, D., Jain, A. K., & Prabhakar, S. Handbook of Fingerprint Recognition. Springer.",
            "PyTorch documentation. https://pytorch.org/docs/",
            "Streamlit documentation. https://docs.streamlit.io/",
            "FVC2002 Fingerprint Verification Competition datasets (used as a public fallback for early pipeline testing).",
        ],
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()

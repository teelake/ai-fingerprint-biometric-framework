"""Convert CSC790_Term_Paper.md to a clean Word report."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "reports" / "CSC790_Term_Paper.md"
OUT = ROOT / "reports" / "CSC790_Project_Report_Term_Paper.docx"


def font(run, size=12, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def plain(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return text


def add_p(doc, text, *, size=12, bold=False, italic=False, align="justify", indent=True, before=0, after=0):
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
    r = p.add_run(plain(text))
    font(r, size=size, bold=bold, italic=italic)


def add_h(doc, text, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    p.paragraph_format.space_before = Pt(16 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run(plain(text))
    font(r, size=12, bold=True)


def main():
    lines = MD.read_text(encoding="utf-8").splitlines()
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

    i = 0
    header_mode = True
    while i < len(lines):
        raw = lines[i].strip()
        if not raw or raw == "---":
            if raw == "---":
                header_mode = False
            i += 1
            continue

        if raw.startswith("# "):
            add_p(doc, raw[2:], size=14, bold=True, align="center", indent=False, after=8)
            i += 1
            continue
        if raw.startswith("## "):
            header_mode = False
            add_h(doc, raw[3:], 1)
            i += 1
            continue
        if raw.startswith("### "):
            add_h(doc, raw[4:], 2)
            i += 1
            continue

        if raw.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in row):
                    rows.append(row)
                i += 1
            if rows:
                table = doc.add_table(rows=len(rows), cols=len(rows[0]))
                table.style = "Table Grid"
                for ri, row in enumerate(rows):
                    for ci, val in enumerate(row):
                        cell = table.rows[ri].cells[ci]
                        cell.text = ""
                        rr = cell.paragraphs[0].add_run(plain(val))
                        font(rr, size=11, bold=(ri == 0))
                doc.add_paragraph()
            continue

        if re.match(r"^\d+\.\s", raw) or raw.startswith("- "):
            style_name = "List Number" if re.match(r"^\d+\.\s", raw) else "List Bullet"
            p = doc.add_paragraph(style=style_name)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            p.paragraph_format.first_line_indent = Cm(0)
            clean = re.sub(r"^\d+\.\s*", "", raw)
            if clean.startswith("- "):
                clean = clean[2:]
            if p.runs:
                p.runs[0].text = ""
            r = p.add_run(plain(clean))
            font(r)
            i += 1
            continue

        if header_mode:
            add_p(doc, raw, bold=("Authors" in raw or raw.startswith("**")), align="center", indent=False)
            i += 1
            continue

        add_p(doc, raw)
        i += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    words = sum(len(p.text.split()) for p in doc.paragraphs if p.text.strip())
    joined = "\n".join(p.text for p in doc.paragraphs)
    print(f"Saved {OUT}")
    print(f"words≈{words}")
    for key in ["Literature Review", "BVAS", "Conclusion", "References"]:
        print(key, key in joined)


if __name__ == "__main__":
    main()

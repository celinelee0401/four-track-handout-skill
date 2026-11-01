#!/usr/bin/env python3
"""Render a four-track handout Markdown source into Word files.

One source file per track produces two documents:
  <name>.docx           student version: every [[answer]] becomes a blank
  教用/<name>_教用.docx  teacher version: answers in bold red on the blanks,
                      followed by the Teacher Guide section

The script only does layout. All wording comes from the source file.
See references/source-format.md for the syntax.

Usage:
  python3 render_handout.py SOURCE.md [--out-dir DIR] [--pdf]
"""
import argparse
import copy
import re
import subprocess
import sys
from pathlib import Path

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Inches

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "assets" / "golden_template.docx"
QR_IMAGE = SKILL_DIR / "assets" / "class_qr.png"  # your class QR, used for every Task 4/5 (optional)

EMOJI_FONT = "Segoe UI Emoji" if sys.platform == "win32" else "Apple Color Emoji"

BLACK = RGBColor(0, 0, 0)
RED = RGBColor(0xFF, 0, 0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TASK_FILL = "D9D9D9"
LABEL_FILL = "737373"
HEAD_FILL = "F2F2F2"
BLUE_FILL = "D9EAF7"
BODY_PT = 12
SMALL_PT = 10.5
CONTENT_WIDTH_IN = 7.08  # A4 minus 0.59" margins

EMOJI_RE = re.compile(
    "([\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2B55\u23F0-\u23FF\u2190-\u21FF\uFE0F\u200D]+)"
)
ANSWER_RE = re.compile(r"\[\[(.+?)\]\]")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


# ---------------------------------------------------------------- parsing

def parse_source(text):
    meta, body = {}, text
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        for line in fm.strip().splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
    parts = re.split(r"^===\s*TEACHER GUIDE\s*===\s*$", body, flags=re.M)
    student = parts[0]
    teacher = parts[1] if len(parts) > 1 else ""
    return meta, student, teacher


# ---------------------------------------------------------------- xml helpers

def shade_run(run, fill):
    rpr = run._r.get_or_add_rPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    rpr.append(shd)


def shade_cell(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def cell_margins(cell):
    tcpr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for side, val in (("top", 90), ("left", 110), ("bottom", 90), ("right", 110)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tcpr.append(mar)


def table_borders(table, color="000000", size=4):
    tblpr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tblpr.append(borders)


def repeat_header(row):
    trpr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    trpr.append(el)


def keep_with_next(paragraph):
    paragraph.paragraph_format.keep_with_next = True


def set_cjk_font(run):
    rpr = run._r.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    fonts.set(qn("w:hint"), "eastAsia")


# ---------------------------------------------------------------- inline text

class Renderer:
    def __init__(self, doc, mode):
        self.doc = doc
        self.mode = mode  # "student" or "teacher"
        self.blank_cap = 78  # max underscores per blank; lowered inside table cells
        self.step_no = 0  # numbered steps restart at each Task bar
        self.step_label = "Step {n}"

    def add_runs(self, paragraph, text, size=BODY_PT, bold=False, color=BLACK):
        """Write text with **bold**, [[answer]] and emoji handling."""
        pos = 0
        tokens = []
        pattern = re.compile(r"\[\[(.+?)\]\]|\{\{(.+?)\}\}|\*\*(.+?)\*\*")
        for m in pattern.finditer(text):
            if m.start() > pos:
                tokens.append(("text", text[pos:m.start()]))
            if m.group(1) is not None:
                tokens.append(("answer", m.group(1)))
            elif m.group(2) is not None:
                tokens.append(("choice", m.group(2)))
            else:
                tokens.append(("bold", m.group(3)))
            pos = m.end()
        if pos < len(text):
            tokens.append(("text", text[pos:]))

        for kind, value in tokens:
            if kind == "answer":
                self._answer(paragraph, value, size)
            elif kind == "choice":
                self._choice(paragraph, value, size)
            else:
                self._plain(paragraph, value, size, bold or kind == "bold", color)

    def _choice(self, paragraph, value, size):
        """{{was* / were}}: students circle; teachers see the starred option in red."""
        options = [o.strip() for o in value.split("/")]
        self._plain(paragraph, "( ", size, False, BLACK)
        for i, opt in enumerate(options):
            if i:
                self._plain(paragraph, " / ", size, False, BLACK)
            correct = opt.endswith("*")
            opt = opt.rstrip("*").strip()
            if correct and self.mode == "teacher":
                self._plain(paragraph, opt, size, True, RED)
            else:
                self._plain(paragraph, opt, size, False, BLACK)
        self._plain(paragraph, " )", size, False, BLACK)

    def _plain(self, paragraph, text, size, bold, color):
        for piece in EMOJI_RE.split(text):
            if not piece:
                continue
            run = paragraph.add_run(piece)
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color
            if EMOJI_RE.fullmatch(piece):
                run.font.name = EMOJI_FONT
            else:
                set_cjk_font(run)

    def _answer(self, paragraph, value, size):
        # [[answer]] or [[answer|blank length]]
        answer, _, width = value.partition("|")
        answer = answer.strip()
        if answer in ("x", "☑"):
            # checkbox: empty box for students, red ticked box for teachers
            run = paragraph.add_run("☑" if self.mode == "teacher" else "□")
            run.font.size = Pt(size)
            run.font.bold = self.mode == "teacher"
            run.font.color.rgb = RED if self.mode == "teacher" else BLACK
            return
        if self.mode == "teacher":
            run = paragraph.add_run(f" {answer} ")
            run.font.size = Pt(size)
            run.font.bold = True
            run.font.underline = True
            run.font.color.rgb = RED
            set_cjk_font(run)
        else:
            n = int(width) if width.strip().isdigit() else max(8, int(len(answer) * 1.4))
            n = min(n, self.blank_cap)
            run = paragraph.add_run("_" * n)
            run.font.size = Pt(size)
            run.font.color.rgb = BLACK

    # ------------------------------------------------------------ blocks

    def para(self, text="", size=BODY_PT, bold=False, align=None, after=4, before=0, color=BLACK):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.line_spacing = 1.0
        if align == "center":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if text:
            self.add_runs(p, text, size=size, bold=bold, color=color)
        return p

    def title(self, text):
        self.para(text, size=20, bold=True, align="center", after=6)

    def identity(self):
        self.para("Class: ________  Number: ________  Name: __________  Group: _________",
                  align="center", after=8)

    def part(self, text):
        p = self.para(text, size=14, bold=True, after=4)
        keep_with_next(p)

    def goal(self, text):
        p = self.para(after=7)
        self.add_runs(p, "Goal: ", bold=True)
        self.add_runs(p, text)

    def task_bar(self, text, small=False):
        self.step_no = 0
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        keep_with_next(p)
        for piece in EMOJI_RE.split(text):
            if not piece:
                continue
            run = p.add_run(piece)
            run.font.size = Pt(12 if small else 14)
            run.font.bold = True
            run.font.color.rgb = BLACK
            if EMOJI_RE.fullmatch(piece):
                run.font.name = EMOJI_FONT
            else:
                set_cjk_font(run)
            shade_run(run, TASK_FILL)

    def flow(self, text):
        p = self.para(text, after=4)
        keep_with_next(p)

    def instruction(self, text, label="Instruction:", steps=None):
        """Dark-grey label; optional five-ring steps, one per line."""
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2 if steps else 6)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(label)
        run.font.size = Pt(BODY_PT)
        run.font.bold = True
        run.font.color.rgb = WHITE
        set_cjk_font(run)
        shade_run(run, LABEL_FILL)
        if text:
            self.add_runs(p, " " + text)
        for n, step in enumerate(steps or []):
            sp = self.doc.add_paragraph()
            sp.paragraph_format.left_indent = Inches(0.25)
            sp.paragraph_format.space_after = Pt(6 if n == len(steps) - 1 else 1)
            sp.paragraph_format.line_spacing = 1.0
            self.add_runs(sp, step)

    def step(self, text, keep=True):
        """One five-ring step placed right above the item it refers to:
        icon + dark-grey "Step N" chip + A1 sentence."""
        self.step_no += 1
        m = EMOJI_RE.match(text)
        icon, rest = (m.group(0), text[m.end():].strip()) if m else ("", text)
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.0
        if keep:
            keep_with_next(p)
        if icon:
            self._plain(p, icon + " ", BODY_PT, False, BLACK)
        run = p.add_run(" " + self.step_label.format(n=self.step_no) + " ")
        run.font.size = Pt(BODY_PT)
        run.font.bold = True
        run.font.color.rgb = WHITE
        set_cjk_font(run)
        shade_run(run, LABEL_FILL)
        self.add_runs(p, " " + rest)

    def subheading(self, text):
        p = self.para(text, bold=True, after=3, before=4)
        keep_with_next(p)

    def lines(self, n, sample=None, criteria=None):
        if self.mode == "teacher" and sample:
            self.para("參考答案：" + sample, color=RED, bold=True, after=2)
            if criteria:
                self.para("可接受條件：" + criteria, color=RED, after=6)
            return
        for _ in range(n):
            self.para("_" * 80, size=SMALL_PT, after=6)

    def teacher_note(self, text):
        if self.mode == "teacher":
            self.para(text, color=RED, after=4)

    def box(self, text_lines):
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table_borders(table)
        cell = table.rows[0].cells[0]
        cell_margins(cell)
        cell.width = Inches(CONTENT_WIDTH_IN)
        first = True
        for line in text_lines:
            p = cell.paragraphs[0] if first else cell.add_paragraph()
            first = False
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.0
            self.add_runs(p, line)
        self.para(after=2)

    def table(self, rows, widths=None, blue_heading=None, small=False):
        ncols = max(len(r) for r in rows)
        rows = [r + [""] * (ncols - len(r)) for r in rows]
        extra = 1 if blue_heading else 0
        table = self.doc.add_table(rows=len(rows) + extra, cols=ncols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        table_borders(table)
        size = SMALL_PT if small else BODY_PT

        if widths and len(widths) != ncols:
            print(f"warning: widths {widths} do not match {ncols} columns; using equal widths",
                  file=sys.stderr)
            widths = None
        if widths:
            total = sum(widths)
            col_in = [CONTENT_WIDTH_IN * w / total for w in widths]
        else:
            col_in = [CONTENT_WIDTH_IN / ncols] * ncols

        # fixed layout + explicit grid so Word and LibreOffice both honour the widths
        tblpr = table._tbl.tblPr
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        tblpr.append(layout)
        for gc, w in zip(table._tbl.tblGrid.findall(qn("w:gridCol")), col_in):
            gc.set(qn("w:w"), str(int(w * 1440)))

        if blue_heading:
            merged = table.rows[0].cells[0].merge(table.rows[0].cells[-1])
            shade_cell(merged, BLUE_FILL)
            cell_margins(merged)
            p = merged.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            self.add_runs(p, blue_heading, size=size, bold=True)
            repeat_header(table.rows[0])

        for r, row in enumerate(rows):
            trow = table.rows[r + extra]
            is_head = r == 0
            if is_head:
                repeat_header(trow)
            for c, value in enumerate(row):
                cell = trow.cells[c]
                cell.width = Inches(col_in[c])
                self.blank_cap = max(6, int(col_in[c] * 10) - 3)
                cell_margins(cell)
                if is_head:
                    shade_cell(cell, HEAD_FILL)
                for i, chunk in enumerate(value.split("<br>")):
                    p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.0
                    if is_head:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    self.add_runs(p, chunk.strip(), size=size, bold=is_head)
            no_split = OxmlElement("w:cantSplit")
            trow._tr.get_or_add_trPr().append(no_split)
        # short tables stay on one page: every row keeps with the next one
        if len(table.rows) <= 10:
            for trow in table.rows[:-1]:
                for cell in trow.cells:
                    for p in cell.paragraphs:
                        keep_with_next(p)
        self.blank_cap = 78
        self.para(after=2)

    def qr(self, task_text):
        table = self.doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table_borders(table)
        left, right = table.rows[0].cells
        left.width, right.width = Inches(1.6), Inches(CONTENT_WIDTH_IN - 1.6)
        for cell in (left, right):
            cell_margins(cell)
        lp = left.paragraphs[0]
        lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if QR_IMAGE.exists():
            lp.add_run().add_picture(str(QR_IMAGE), width=Inches(1.2))
        else:
            shade_cell(left, HEAD_FILL)
            self.add_runs(lp, "QR code\n(請貼上)", size=SMALL_PT)
            for _ in range(3):
                left.add_paragraph()
        rp = right.paragraphs[0]
        self.add_runs(rp, task_text)
        right.vertical_alignment = 1  # center
        self.para(after=2)

    def page_break(self):
        p = self.doc.add_paragraph()
        p.add_run().add_break(WD_BREAK.PAGE)


# ---------------------------------------------------------------- body walker

def parse_table(lines, i):
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        line = lines[i].strip()
        if not re.fullmatch(r"\|[\s:\-|]+\|", line):
            # split on | but not inside [[answer|width]]
            protected = re.sub(r"\[\[(.+?)\]\]", lambda m: m.group(0).replace("|", "\x00"), line)
            cells = [c.strip().replace("\x00", "|") for c in protected.strip().strip("|").split("|")]
            rows.append(cells)
        i += 1
    return rows, i


def render_body(r, text):
    lines = text.splitlines()
    i = 0
    pending = {}
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if not line or line.startswith("<!--"):
            i += 1
            continue
        if line.startswith("## "):
            r.task_bar(line[3:].strip())
        elif line.startswith("### "):
            r.subheading(line[4:].strip())
        elif line.startswith("# "):
            r.part(line[2:].strip())
        elif line.lower().startswith("flow:"):
            r.flow(line.split(":", 1)[1].strip())
        elif line.lower().startswith("instruction:") or line.startswith(("任務說明：", "操作指令：")):
            if line.lower().startswith("instruction:"):
                label, rest = "Instruction:", line.split(":", 1)[1].strip()
            else:
                head, rest = line.split("：", 1)
                label, rest = head + "：", rest.strip()
            steps = []
            while i + 1 < len(lines) and lines[i + 1].strip().startswith("- "):
                i += 1
                steps.append(lines[i].strip()[2:].strip())
            r.instruction(rest, label=label, steps=steps)
        elif line.lower().startswith("step:"):
            # a step glues to the item below it, except the last step before the next
            # Task / Part heading: otherwise the whole wrap-up block is dragged onto the next page
            # A "### " sub-heading (■ A. …) is the step's own item, so the step keeps with it.
            # Consecutive steps must not glue to each other either: a run of 4 steps + a table
            # moves as one block and leaves half a page empty (2026-10-31). Only the step right
            # above its item keeps with next.
            nxt = next((l.strip() for l in lines[i + 1:] if l.strip()), "")
            # "### Part C" opens a new section, so a wrap-up step above it stays behind (2026-11-01)
            r.step(line.split(":", 1)[1].strip(),
                   keep=not (re.match(r"#{1,2} |### Part ", nxt) or nxt.lower().startswith("step:")))
        elif line.lower().startswith("widths:"):
            pending["widths"] = [float(x) for x in line.split(":", 1)[1].replace(",", " ").split()]
        elif line.lower().startswith("blue:"):
            pending["blue"] = line.split(":", 1)[1].strip()
        elif line.lower() == "small-table":
            pending["small"] = True
        elif line.startswith("|"):
            rows, i = parse_table(lines, i)
            r.table(rows, widths=pending.get("widths"), blue_heading=pending.get("blue"),
                    small=pending.get("small", False))
            pending = {}
            continue
        elif line.lower().startswith("lines:"):
            # lines: 3  |  lines: 3 | sample answer | criteria
            parts = [p.strip() for p in line.split(":", 1)[1].split("|")]
            n = int(parts[0])
            r.lines(n, parts[1] if len(parts) > 1 else None, parts[2] if len(parts) > 2 else None)
        elif line.lower().startswith("key:"):
            r.teacher_note(line.split(":", 1)[1].strip())
        elif line.lower().startswith("qr:"):
            r.qr(line.split(":", 1)[1].strip())
        elif line == "[box]":
            box_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != "[/box]":
                if lines[i].strip():
                    box_lines.append(lines[i].strip())
                i += 1
            r.box(box_lines)
        elif line == "[teacher]":
            # teacher-only block: rendered in place in 教用版, skipped in the student file
            block = []
            i += 1
            while i < len(lines) and lines[i].strip() != "[/teacher]":
                block.append(lines[i])
                i += 1
            if r.mode == "teacher":
                keep_with_next(r.para("🍎 教用版補充（學生版不顯示）", color=RED, bold=True, after=2))
                render_body(r, "\n".join(block))
        elif line == "---pagebreak---":
            r.page_break()
        else:
            p = r.para(line)
            # keep a question stem and its (A)/(B)/(C) option lines on one page
            nxt = next((l.strip() for l in lines[i + 1:] if l.strip()), "")
            if re.match(r"^\(?[A-D]\)", nxt) or re.match(r"^[a-d]\. ", nxt):
                keep_with_next(p)
        i += 1


# ---------------------------------------------------------------- document

def fresh_document(meta):
    doc = docx.Document(str(TEMPLATE))
    # the template's default East Asian language is en-US, so Word skips the Chinese
    # line-break rules and can start a line with "，" — mark it zh-TW (2026-10-31)
    defaults = doc.styles.element.find(qn("w:docDefaults"))
    lang = defaults.find(".//" + qn("w:lang")) if defaults is not None else None
    if lang is not None:
        lang.set(qn("w:eastAsia"), "zh-TW")
    body = doc.element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)
    locator = meta.get("locator", "")
    header_text = f"{meta.get('course', '115-1 G8')} {locator}".strip()
    for section in doc.sections:
        for p in section.header.paragraphs:
            if p.text.strip():
                for run in p.runs[1:]:
                    run.text = ""
                p.runs[0].text = header_text
        for t in section.footer.tables:
            cells = t.rows[0].cells
            for cell, text in ((cells[0], meta.get("teacher", "")), (cells[-1], locator)):
                p = cell.paragraphs[0]
                for run in p.runs[1:]:
                    run.text = ""
                if p.runs:
                    p.runs[0].text = text
                else:
                    p.add_run(text)
    return doc


def build(meta, student, teacher, mode):
    doc = fresh_document(meta)
    r = Renderer(doc, mode)
    r.step_label = meta.get("step_label", "Step {n}")
    r.title(meta["title"])
    r.identity()
    render_body(r, student)
    if mode == "teacher" and teacher.strip():
        r.page_break()
        r.title(meta["title"])
        r.para("■ 教師教用版 (Teacher's Guide)", size=14, bold=True, after=6)
        render_body(r, teacher)
    shrink_trailing_paragraph(doc)
    return doc


def shrink_trailing_paragraph(doc):
    # Word needs a paragraph after a final table; when the last page is full,
    # that empty paragraph spills onto a blank page. Make it 1 pt tall.
    body = doc.element.body
    kids = [c for c in body if c.tag != qn("w:sectPr")]
    if not kids or kids[-1].tag != qn("w:p") or "".join(kids[-1].itertext()).strip():
        return
    p = docx.text.paragraph.Paragraph(kids[-1], doc)
    fmt = p.paragraph_format
    fmt.space_before = fmt.space_after = docx.shared.Pt(0)
    fmt.line_spacing = docx.shared.Pt(1)
    ppr = p._p.get_or_add_pPr()
    rpr = ppr.find(qn("w:rPr"))
    if rpr is None:
        rpr = docx.oxml.OxmlElement("w:rPr")
        ppr.append(rpr)
    for tag in ("w:sz", "w:szCs"):
        el = docx.oxml.OxmlElement(tag)
        el.set(qn("w:val"), "2")
        rpr.append(el)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out-dir")
    ap.add_argument("--pdf", action="store_true", help="also export PDFs with LibreOffice for QA")
    args = ap.parse_args()

    src = Path(args.source)
    meta, student, teacher = parse_source(src.read_text(encoding="utf8"))
    for key in ("title", "locator", "filename"):
        if key not in meta:
            sys.exit(f"front matter is missing '{key}'")
    out_dir = Path(args.out_dir) if args.out_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    for mode, suffix in (("student", ""), ("teacher", "_教用")):
        target = out_dir if mode == "student" else out_dir / "教用"
        target.mkdir(exist_ok=True)
        path = target / f"{meta['filename']}{suffix}.docx"
        build(meta, student, teacher, mode).save(path)
        outputs.append(path)
        print(f"wrote {path}")

    if args.pdf:
        soffice = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        pdf_dir = out_dir / "qa-pdf"
        pdf_dir.mkdir(exist_ok=True)
        for path in outputs:
            subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir",
                            str(pdf_dir), str(path)], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"PDF previews in {pdf_dir}")


if __name__ == "__main__":
    main()

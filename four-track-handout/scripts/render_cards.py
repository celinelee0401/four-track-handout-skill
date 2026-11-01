#!/usr/bin/env python3
"""LoiLoNote summary cards: cards source (.md) -> 16:9 PDFs via headless Chrome.

Outputs (in --out-dir):
  <name>_成對版.pdf  each card twice: blank page, then answer page (cards with no blanks once)
  <name>_挖空版.pdf  blank pages only (can be sent to students)
  <name>_答案版.pdf  answer pages only
  <name>_漸進版.pdf  progressive reveal: blank page, then one more row revealed per page
                     (newest row highlighted yellow); cards with no blanks once

Source syntax (see references/loilo-cards.md):
  ---  front matter: title, locator, filename  ---
  === card                 start a card
  tag: T1 Strategy Lab     chip at top left
  title: ...               big card title
  cover: true              cover card (no blank/answer badge, never doubled)
  reveal: all              reveal every answer in one step (default: one row/bullet/line per step)
  compact: true            smaller type for a long card (e.g. an 8-row table) so it stays on one page
  - item                   bullet
  | a | b |                table (first row = header)
  [box] ... [/box]         highlighted box
  plain line               paragraph
Inline: **bold**, [[answer]] / [[answer|12]] blank, {{a* / b}} circle, [[x]] tick box.
Reveal order (progressive版): each table row / bullet / line with a blank is one step, top to bottom.
  [[ans@2]]    put this row in step 2 (rows sharing a step appear together)
  [[ans@last]] reveal in a final extra step (e.g. a conclusion box)
  More than 6 steps are merged automatically.
"""
import argparse
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

def find_chrome():
    # Chrome on macOS; Chrome or Edge on Windows (both print to PDF headless).
    if sys.platform == "win32":
        import os
        for base in (os.environ.get("PROGRAMFILES", ""), os.environ.get("PROGRAMFILES(X86)", ""), os.environ.get("LOCALAPPDATA", "")):
            for rel in (r"Google\Chrome\Application\chrome.exe", r"Microsoft\Edge\Application\msedge.exe"):
                path = Path(base) / rel
                if base and path.exists():
                    return str(path)
        sys.exit("Chrome or Edge not found")
    return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


CHROME = find_chrome()

CSS = """
@page { size: 13.333in 7.5in; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans TC", "PingFang TC", "Heiti TC", sans-serif; color: #1f2937; }
.card { width: 13.333in; height: 7.5in; padding: 0.42in 0.6in 0.35in; position: relative;
        page-break-after: always; overflow: hidden; background: #fffdf7;
        display: flex; flex-direction: column; }
.card:last-child { page-break-after: auto; }
.top { display: flex; align-items: center; gap: 14px; margin-bottom: 10px; }
.tag { background: #1f3a5f; color: #fff; font-weight: 700; font-size: 24px; padding: 6px 16px; border-radius: 999px; }
.badge { margin-left: auto; font-weight: 700; font-size: 24px; padding: 6px 16px; border-radius: 999px; }
.badge.blank { background: #fde68a; color: #7c4a03; }
.badge.ans { background: #fee2e2; color: #b91c1c; }
h1 { font-size: 50px; margin: 0 0 14px; line-height: 1.2; }
.body { font-size: 34px; line-height: 1.45; flex: 1; }
.body p { margin: 0 0 10px; }
.body ul { margin: 0 0 10px; padding-left: 1.1em; }
.body li { margin-bottom: 6px; }
table { border-collapse: collapse; width: 100%; margin: 4px 0 12px; font-size: 31px; }
th, td { border: 2px solid #cbd5e1; padding: 8px 14px; text-align: left; vertical-align: top; }
th { background: #e8eef6; }
.box { background: #eef6ff; border-left: 8px solid #1f3a5f; padding: 12px 20px; margin: 6px 0 12px; border-radius: 6px; }
.blank { border-bottom: 3px solid #475569; color: transparent; padding: 0 .35em; }
.ans { color: #dc2626; font-weight: 700; border-bottom: 3px solid #dc2626; padding: 0 .35em; }
.circ { border: 3px solid #dc2626; border-radius: 999px; padding: 0 8px; color: #dc2626; font-weight: 700; }
.ans.new { background: #fde047; border-radius: 6px; }
.circ.new { background: #fde047; }
.tick { font-weight: 700; }
.tick.on { color: #dc2626; }
.foot { position: absolute; bottom: 0.18in; right: 0.6in; font-size: 16px; color: #94a3b8; }
.compact h1 { font-size: 40px; margin-bottom: 8px; }
.compact .body { font-size: 27px; line-height: 1.3; }
.compact table { font-size: 25px; margin-bottom: 6px; }
.compact th, .compact td { padding: 4px 12px; }
.cover { justify-content: center; align-items: center; text-align: center; background: #1f3a5f; color: #fff; }
.cover h1 { font-size: 60px; }
.cover .body { flex: 0; font-size: 30px; }
"""


def parse(text):
    meta, body = {}, text
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        for line in fm.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
    cards = []
    for chunk in re.split(r"^===\s*card\s*$", body, flags=re.M)[1:]:
        card = {"lines": []}
        for line in chunk.strip("\n").splitlines():
            m = re.match(r"^(tag|title|cover|reveal|compact):\s*(.*)$", line.strip())
            if m and not card["lines"]:
                card[m.group(1)] = m.group(2).strip()
            else:
                card["lines"].append(line.rstrip())
        cards.append(card)
    return meta, cards


def has_blank(card):
    return any(re.search(r"\[\[|\{\{", l) for l in card["lines"])


def split_step(content):
    content, _, step = content.rpartition("§")
    return (content, int(step)) if _ else (step, 0)


def inline(text, level):
    """level: None = every answer shown (no highlight); n = steps <= n shown, step n highlighted."""
    out = html.escape(text)

    def state(step):
        if level is None:
            return "ans"
        return "ans new" if step == level else ("ans" if step < level else None)

    def blank(m):
        content, step = split_step(m.group(1))
        val = content.partition("|")[0]
        st = state(step)
        if val.strip() == "x":
            return f'<span class="tick on">☑</span>' if st else '<span class="tick">□</span>'
        if st:
            return f'<span class="{st}">{val}</span>'
        # same text, made invisible, so blank and answer pages share one layout
        return f'<span class="blank" style="font-weight:700">{val}</span>'

    def circle(m):
        content, step = split_step(m.group(1))
        st = state(step)
        parts = []
        for o in [o.strip() for o in content.split("/")]:
            star = o.endswith("*")
            o = o.rstrip("*").strip()
            parts.append(f'<span class="circ{" new" if st == "ans new" else ""}">{o}</span>' if (star and st) else o)
        return "( " + " / ".join(parts) + " )"

    out = re.sub(r"\[\[(.+?)\]\]", blank, out)
    out = re.sub(r"\{\{(.+?)\}\}", circle, out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    return out


BLANK_RE = re.compile(r"\[\[(.+?)\]\]|\{\{(.+?)\}\}")
MARK_RE = re.compile(r"@(\d+|last)(?=\]\]|\}\})")
MAX_STEPS = 6


def annotate(card):
    """Tag every blank with its reveal step (suffix §n). Returns (title, lines, n_steps)."""
    rows = [card.get("title", "")] + card["lines"]
    info = []  # per row: None (no blank) or explicit step or "auto"
    for r in rows:
        if not BLANK_RE.search(r):
            info.append(None)
            continue
        m = MARK_RE.search(r)
        info.append(m.group(1) if m else "auto")
    one = card.get("reveal") == "all"
    auto_rows = [i for i, v in enumerate(info) if v == "auto"]
    k = max([len(auto_rows)] + [int(v) for v in info if v and v not in ("auto", "last")])
    g = -(-k // MAX_STEPS) if k > MAX_STEPS else 1
    groups = -(-k // g) if k else 0
    has_last = "last" in info
    n_steps = 1 if one else groups + (1 if has_last else 0)
    nth = 0
    out = []
    for r, v in zip(rows, info):
        if v is None:
            out.append(r)
            continue
        if v == "auto":
            nth += 1
            step = nth
        elif v == "last":
            step = k + 1
        else:
            step = int(v)
        step = 1 if one else (groups + 1 if v == "last" else (step - 1) // g + 1)
        r = MARK_RE.sub("", r)
        out.append(BLANK_RE.sub(lambda m: m.group(0)[:-2] + f"§{step}" + m.group(0)[-2:], r))
    return out[0], out[1:], n_steps


def body_html(lines, level):
    parts, i = [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == "[box]":
            inner = []
            i += 1
            while i < len(lines) and lines[i].strip() != "[/box]":
                inner.append(lines[i])
                i += 1
            parts.append(f'<div class="box">{body_html(inner, level)}</div>')
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            t = ["<table>"]
            for r, cells in enumerate(rows):
                tag = "th" if r == 0 else "td"
                t.append("<tr>" + "".join(
                    f"<{tag}>{inline(c, level).replace('&lt;br&gt;', '<br>')}</{tag}>" for c in cells) + "</tr>")
            t.append("</table>")
            parts.append("".join(t))
            continue
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(f"<li>{inline(lines[i].strip()[2:], level)}</li>")
                i += 1
            parts.append("<ul>" + "".join(items) + "</ul>")
            continue
        else:
            parts.append(f"<p>{inline(line, level)}</p>")
        i += 1
    return "".join(parts)


def card_html(card, meta, level, n, total):
    """level: 0 = blank page, 1..N = progressive, None = full answer page."""
    if card.get("cover"):
        return (f'<section class="card cover"><h1>{html.escape(card.get("title", ""))}</h1>'
                f'<div class="body">{body_html(card["lines"], None)}</div></section>')
    title, lines, steps = annotate(card)
    badge = ""
    if steps:
        if level is None:
            badge = '<span class="badge ans">✓ 答案</span>'
        elif level == 0:
            badge = '<span class="badge blank">? 想一想</span>'
        else:
            badge = f'<span class="badge ans">✓ 揭曉 {level}/{steps}</span>'
    cls = "card compact" if card.get("compact") else "card"
    return (f'<section class="{cls}"><div class="top"><span class="tag">{html.escape(card.get("tag", ""))}</span>{badge}</div>'
            f'<h1>{inline(title, level)}</h1>'
            f'<div class="body">{body_html(lines, level)}</div>'
            f'<div class="foot">{html.escape(meta.get("locator", ""))} · {n}/{total}</div></section>')


def to_pdf(sections, out_pdf):
    doc = f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(sections)}</body></html>'
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf8") as f:
        f.write(doc)
        tmp = f.name
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", Path(tmp).as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    Path(tmp).unlink(missing_ok=True)
    print("wrote", out_pdf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out-dir", default=".")
    a = ap.parse_args()
    meta, cards = parse(Path(a.src).read_text(encoding="utf8"))
    name = meta.get("filename", Path(a.src).stem)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    total = sum(1 for c in cards if not c.get("cover"))
    paired, blank, answer, prog, n = [], [], [], [], 0
    for c in cards:
        if not c.get("cover"):
            n += 1
        r = card_html(c, meta, None, n, total)
        if c.get("cover") or not has_blank(c):
            for lst in (paired, blank, answer, prog):
                lst.append(r)
            continue
        b = card_html(c, meta, 0, n, total)
        paired += [b, r]; blank.append(b); answer.append(r)
        steps = annotate(c)[2]
        prog.append(b)
        prog += [card_html(c, meta, lv, n, total) for lv in range(1, steps + 1)]
    to_pdf(paired, str(out / f"{name}_成對版.pdf"))
    to_pdf(blank, str(out / f"{name}_挖空版.pdf"))
    to_pdf(answer, str(out / f"{name}_答案版.pdf"))
    to_pdf(prog, str(out / f"{name}_漸進版.pdf"))


if __name__ == "__main__":
    sys.exit(main())

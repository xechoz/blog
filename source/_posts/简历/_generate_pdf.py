#!/usr/bin/env python3
"""Convert _my_work.md to a styled PDF via chromium headless printing.

Usage:
    python _generate_pdf.py [basename] [output.pdf]
Defaults: basename '_my_work', output 'Android_开发_郑建辉.pdf'.
"""

import html
import os
import subprocess
import sys
import tempfile

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = sys.argv[1] if len(sys.argv) > 1 else "_my_work"
PDF_NAME = sys.argv[2] if len(sys.argv) > 2 else "Android_开发_郑建辉.pdf"
MD_PATH = os.path.join(SRC_DIR, f"{BASE}.md")
PDF_PATH = os.path.join(SRC_DIR, PDF_NAME)

CSS = """
@page { size: A4; margin: 10mm 12mm 12mm 12mm; }
body { font-family: "Noto Sans CJK SC", sans-serif; font-size: 11pt;
       color: #1f2328; line-height: 1.5; margin: 0; }
h1 { font-size: 15pt; color: #007ACC; border-bottom: 1.8px solid #007ACC;
     padding-bottom: 4px; margin: 10px 0 6px; }
h2 { font-size: 12.5pt; color: #0e639c; margin: 8px 0 5px; }
blockquote { margin: 3px 0 8px; padding: 4px 10px; border-left: 3px solid #007ACC;
             background: #f0f7fc; color: #3d4a55; }
table { border-collapse: collapse; width: 100%; margin: 6px 0; }
th, td { border: 1px solid #c9d4dc; padding: 5px 8px; font-weight: normal; text-align: left; }
table.info { table-layout: auto; }
table.info td:nth-child(1), table.info td:nth-child(3), table.info td:nth-child(4) { white-space: nowrap; width: 1%; }
table.info td:nth-child(2) { width: auto; }
ul { margin: 3px 0 8px; padding-left: 20px; }
li { margin: 2px 0; }
p { margin: 3px 0; }
b { font-weight: 700; }
"""


def inline(text):
    parts = text.split("**")
    out = []
    for i, part in enumerate(parts):
        if not part:
            continue
        esc = html.escape(part)
        out.append(f"<b>{esc}</b>" if i % 2 == 1 else esc)
    return "".join(out)


def convert(md_text):
    lines = md_text.split("\n")
    body = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(c in ("---", ":--", "--:") for c in cells):
                    rows.append(cells)
                i += 1
            cls = ' class="info"' if (rows and rows[0][0] == "姓名") else ""
            body.append(f"<table{cls}>")
            for r, row in enumerate(rows):
                tag = "th" if r == 0 and len(rows) > 1 else "td"
                body.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in row) + "</tr>")
            body.append("</table>")
            continue
        if stripped.startswith("# "):
            body.append(f"<h1>{inline(stripped[2:])}</h1>")
            i += 1
            continue
        if stripped.startswith("## "):
            body.append(f"<h2>{inline(stripped[3:])}</h2>")
            i += 1
            continue
        if stripped.startswith(">"):
            body.append(f"<blockquote>{inline(stripped.lstrip('> '))}</blockquote>")
            i += 1
            continue
        if stripped.startswith("- "):
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append(f"<li>{inline(lines[i].strip()[2:])}</li>")
                i += 1
            body.append("<ul>" + "".join(items) + "</ul>")
            continue
        body.append(f"<p>{inline(stripped)}</p>")
        i += 1
    return "\n".join(body)


def main():
    with open(MD_PATH, encoding="utf-8") as f:
        md_text = f.read()
    content = convert(md_text)
    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>郑建辉 简历</title>
<style>{CSS}</style>
</head>
<body>
{content}
</body>
</html>"""
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
        f.write(doc)
        html_path = f.name

    result = subprocess.run(
        [
            "chromium", "--headless", "--disable-gpu", "--no-sandbox",
            f"--print-to-pdf={PDF_PATH}", "--no-pdf-header-footer",
            f"file://{html_path}",
        ],
        capture_output=True, text=True,
    )
    os.unlink(html_path)
    if result.returncode != 0:
        print(f"Error: chromium failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"Output: {PDF_PATH}")


if __name__ == "__main__":
    main()

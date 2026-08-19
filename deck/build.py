"""Build the VERB deck.

    python deck/build.py

Reads deck/slides/*.md in filename order, renders them into a single
self-contained deck/index.html, and generates the QR codes into deck/assets/.

Design constraints, all of them deliberate:

* **No npm install to view.** The output is one HTML file that opens from disk.
  There is no bundler, no package manager and no node_modules.
* **No network requests at runtime.** No CDN, no webfont, no analytics. A deck
  that needs the conference wifi is a deck that fails at the conference.
* **Markup compatible with reveal.js.** Slides are `<section>` elements with
  `<aside class="notes">` for speaker notes, so dropping a reveal.js dist into
  deck/vendor and switching one line gives you the full reveal feature set. The
  built-in engine covers what a talk actually needs: next, previous, overview,
  speaker notes, jump to slide, and a print view.
* **QR codes generated here.** tools/qr.py, pure python. Not fetched from a QR
  service, because that would put the URL on somebody else's server and make the
  build depend on their uptime.

Visual direction is documented in deck/README.md.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SLIDES = HERE / "slides"
ASSETS = HERE / "assets"
OUTPUT = HERE / "index.html"

sys.path.insert(0, str(ROOT))
from tools.qr import encode, to_png, to_svg  # noqa: E402

# ---------------------------------------------------------------------------
# The one place any of these change.
# ---------------------------------------------------------------------------

REPO_URL = "https://github.com/hotragn/verb"
PAGES_URL = "https://hotragn.github.io/verb"
LINKEDIN_URL = "https://www.linkedin.com/in/hotragn-pettugani/"

# The QR payload is the same destination without the www or the trailing slash.
# tools/qr.py stops at version 3, which is 42 bytes, and the canonical URL is 46.
# LinkedIn resolves the short form to the same page, so nothing is lost and the
# alternative would be implementing multi-block interleaving for four characters.
LINKEDIN_QR = "https://linkedin.com/in/hotragn-pettugani"
X_URL = "https://x.com/hotragn"

AUTHOR = "Hotragn Pettugani"
TITLE = "The Verification Budget"

QR_CODES = {
    "qr-repo": (REPO_URL, "Repository: github.com/hotragn/verb"),
    "qr-calculator": (PAGES_URL, "Calculator: hotragn.github.io/verb"),
    "qr-linkedin": (LINKEDIN_QR, "LinkedIn: Hotragn Pettugani"),
    "qr-x": (X_URL, "X: x.com/hotragn"),
}

TOKENS = {
    "REPO_URL": REPO_URL,
    "PAGES_URL": PAGES_URL,
    "LINKEDIN_URL": LINKEDIN_URL,
    "X_URL": X_URL,
    "REPO_SHORT": REPO_URL.replace("https://", ""),
    "PAGES_SHORT": PAGES_URL.replace("https://", ""),
    "LINKEDIN_SHORT": "linkedin.com/in/hotragn-pettugani",
    "X_SHORT": "x.com/hotragn",
    "AUTHOR": AUTHOR,
}


# ---------------------------------------------------------------------------
# A small markdown subset. Enough for slides, and nothing more.
# ---------------------------------------------------------------------------

INLINE = [
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)"), r"<em>\1</em>"),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), r'<a href="\2">\1</a>'),
]


#: Inline tags authors may use inside a paragraph, a list item or a table cell.
#: Everything else is escaped. The class chips in the decision-class table are
#: the reason this exists.
ALLOWED_INLINE_TAGS = ("span", "br", "b", "i", "sup", "sub", "abbr")
_ESCAPED_TAG = re.compile(
    r"&lt;(/?(?:" + "|".join(ALLOWED_INLINE_TAGS) + r")(?:\s[^&]*?)?/?)&gt;"
)


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = _ESCAPED_TAG.sub(lambda m: "<" + m.group(1).replace("&quot;", '"') + ">", out)
    for pattern, replacement in INLINE:
        out = pattern.sub(replacement, out)
    return out


def render_markdown(source: str) -> str:
    """Headings, paragraphs, lists, tables, quotes, code fences, raw HTML."""
    lines = source.split("\n")
    out: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Raw HTML passes straight through. A block runs until the next blank
        # line, so a multi-line <p>...</p> stays one element rather than having
        # its closing tag rendered as text.
        if stripped.startswith("<") and not stripped.startswith("<!--"):
            while i < len(lines) and lines[i].strip():
                out.append(lines[i])
                i += 1
            continue

        if stripped.startswith("<!--"):
            i += 1
            continue

        # Fenced code, kept verbatim. Used for the formula and the diagrams.
        if stripped.startswith("```"):
            language = stripped[3:].strip()
            i += 1
            block: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            css = f' class="lang-{language}"' if language else ""
            out.append(f"<pre{css}><code>{html.escape(chr(10).join(block))}</code></pre>")
            continue

        # Headings.
        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
            continue

        # Horizontal rule.
        if re.fullmatch(r"-{3,}", stripped):
            out.append("<hr>")
            i += 1
            continue

        # Table. A header row, a separator row, then body rows.
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]
        ):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            body: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table>")
            out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr></thead>")
            out.append("<tbody>")
            for row in body:
                cells = "".join(
                    f'<td class="num">{inline(c)}</td>' if _is_numeric(c) else f"<td>{inline(c)}</td>"
                    for c in row
                )
                out.append(f"<tr>{cells}</tr>")
            out.append("</tbody></table>")
            continue

        # Blockquote.
        if stripped.startswith(">"):
            quoted: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quoted.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(quoted))}</blockquote>")
            continue

        # Unordered list.
        if re.match(r"^[-*]\s+", stripped):
            items: list[str] = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>")
            continue

        # Ordered list.
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ol>")
            continue

        # Paragraph, gathered until a blank line.
        para: list[str] = []
        while i < len(lines) and lines[i].strip() and not _starts_block(lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")

    return "\n".join(out)


def _is_numeric(cell: str) -> bool:
    return bool(re.fullmatch(r"[\d.,%x+\-<>=\s/]*\d[\d.,%x+\-<>=\s/]*", cell.replace("**", "")))


def _starts_block(stripped: str) -> bool:
    return (
        stripped.startswith(("#", ">", "|", "```", "<"))
        or re.match(r"^[-*]\s+", stripped) is not None
        or re.match(r"^\d+\.\s+", stripped) is not None
        or re.fullmatch(r"-{3,}", stripped) is not None
    )


# ---------------------------------------------------------------------------
# Slide files
# ---------------------------------------------------------------------------


def parse_slide(path: Path) -> dict[str, str]:
    """Split leading `key: value` front matter from the body."""
    text = path.read_text(encoding="utf-8")
    for key, value in TOKENS.items():
        text = text.replace("{{" + key + "}}", value)

    meta: dict[str, str] = {"layout": "default", "notes": "", "section": ""}
    body = text

    if "\n---\n" in text[:900]:
        head, body = text.split("\n---\n", 1)
        for line in head.split("\n"):
            if ":" in line and not line.startswith(" "):
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()

    notes = ""
    if "\n@notes\n" in body:
        body, notes = body.split("\n@notes\n", 1)

    meta["body"] = body.strip()
    meta["notes"] = notes.strip()
    meta["file"] = path.name
    return meta


def render_slide(meta: dict[str, str], index: int, total: int) -> str:
    classes = ["slide", f"layout-{meta['layout']}"]
    if str(meta.get("dense", "")).lower() in ("true", "yes", "1"):
        classes.append("dense")
    attrs = f' data-index="{index}"'
    if meta.get("section"):
        attrs += f' data-section="{html.escape(meta["section"], quote=True)}"'

    parts = [f'<section class="{" ".join(classes)}"{attrs}>']
    if meta.get("section") and meta["layout"] not in ("title", "closing", "part"):
        parts.append(f'<div class="eyebrow">{inline(meta["section"])}</div>')
    parts.append('<div class="content">')
    parts.append(render_markdown(meta["body"]))
    parts.append("</div>")

    if meta["layout"] not in ("title", "closing", "part"):
        parts.append(
            '<footer class="slide-foot">'
            f'<span class="foot-links"><a href="{REPO_URL}">{TOKENS["REPO_SHORT"]}</a>'
            f'<a href="{X_URL}">{TOKENS["X_SHORT"]}</a>'
            f'<a href="{LINKEDIN_URL}">{TOKENS["LINKEDIN_SHORT"]}</a></span>'
            f'<span class="pageno">{index}<span class="of"> / {total}</span></span>'
            "</footer>"
        )

    if meta["notes"]:
        parts.append(f'<aside class="notes">{render_markdown(meta["notes"])}</aside>')
    parts.append("</section>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# QR codes
# ---------------------------------------------------------------------------


def build_qr_codes() -> dict[str, str]:
    """Write each QR to deck/assets and return the SVG source for inlining.

    Both, deliberately. The files exist so they can be dropped into a slide in
    any other tool, and the inline copy exists so index.html is genuinely one
    portable file: emailed, put on a memory stick or opened from a download
    folder, it still shows the codes.
    """
    ASSETS.mkdir(parents=True, exist_ok=True)
    sources: dict[str, str] = {}
    for name, (url, title) in QR_CODES.items():
        matrix = encode(url)
        svg = to_svg(matrix, module=8, quiet_zone=4, title=title)
        (ASSETS / f"{name}.svg").write_text(svg, encoding="utf-8")
        # A PNG as well, because PowerPoint and most document tools will not
        # place an SVG.
        (ASSETS / f"{name}.png").write_bytes(to_png(matrix, module=10, quiet_zone=4))
        sources[name] = svg
        print(f"  {name}.svg + .png  {url}")
    return sources


def inline_qr_codes(page: str, sources: dict[str, str]) -> str:
    """Replace assets/<name>.svg references with a data URI of the same SVG."""
    for name, svg in sources.items():
        uri = "data:image/svg+xml;charset=utf-8," + quote(svg, safe="")
        page = page.replace(f'src="assets/{name}.svg"', f'src="{uri}"')
    return page


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------

CSS = """
/* Meter, set for a projector.

   The visual direction is derived from Edward Tufte's information design
   principles rather than from a slide template: show the content, keep the
   ink-to-content ratio high, erase anything that is not carrying meaning,
   use the margin for the second voice. Serif for prose, mono for every number,
   hairlines instead of boxes, one accent colour at a time.

   Not a copy of anything. No webfont is loaded, so this renders identically
   with the conference wifi switched off. */

:root{
  --ink:#101418; --slate:#2A333B; --steel:#4A555F; --mist:#6B7780;
  --line:#D8D4CB; --shell:#EDEBE5; --paper:#F7F6F3;
  --brand:#1F3A34; --bright:#2E7D6B;
  --a:#2E7D6B; --b:#3C6E9F; --c:#B8843A; --d:#A34432;
  --ok:#1F7A5C; --limit:#B8843A; --over:#A34432;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
}

*{box-sizing:border-box; margin:0; padding:0}
html,body{height:100%}
body{
  background:var(--shell); color:var(--ink);
  font-family:var(--serif); font-size:16px; line-height:1.5;
  overflow:hidden;
}

/* The stage keeps a fixed 16:9 canvas and scales it, so type size is
   predictable on any projector. */
/* The canvas is centred by translating from the midpoint rather than by grid
   alignment. A scaled element keeps its unscaled layout box, so on a viewport
   narrower than 1280 a centred grid item overflows to one side and the scale
   lands off screen. */
#stage{position:fixed; inset:0; overflow:hidden}
#canvas{
  width:1280px; height:720px; position:absolute; left:50%; top:50%;
  background:var(--paper); box-shadow:0 2px 40px rgba(16,20,24,.13);
  transform-origin:center center;
}

.slide{
  position:absolute; inset:0; padding:46px 80px 40px;
  display:none; flex-direction:column;
}
.slide.active{display:flex}
.slide .content{flex:1; min-height:0; display:flex; flex-direction:column;
  justify-content:center; gap:16px}

/* Type ------------------------------------------------------------------- */
h1{font-size:62px; line-height:1.04; letter-spacing:-.018em; font-weight:600}
h2{font-size:36px; line-height:1.10; letter-spacing:-.012em; font-weight:600;
   max-width:24ch}
h3{font-size:21px; line-height:1.2; font-weight:600; color:var(--slate)}
h4{font-family:var(--mono); font-size:13px; font-weight:600; letter-spacing:.09em;
   text-transform:uppercase; color:var(--mist)}
p{font-size:20px; line-height:1.42; max-width:48ch; color:var(--slate)}
p.lead{font-size:25px; line-height:1.32; color:var(--ink); max-width:38ch}
p.small{font-size:16px; max-width:66ch; line-height:1.44}
strong{font-weight:650; color:var(--ink)}
em{font-style:italic}
code{font-family:var(--mono); font-size:.88em; background:var(--shell);
  padding:1px 5px; border-radius:3px}
a{color:var(--brand); text-decoration:none; border-bottom:1px solid var(--line)}

ul,ol{margin-left:0; list-style:none; max-width:46ch}
ul li,ol li{font-size:19px; line-height:1.38; color:var(--slate);
  padding:7px 0 7px 24px; position:relative; border-bottom:1px solid var(--line)}
ul li:last-child,ol li:last-child{border-bottom:none}
ul li:before{content:""; position:absolute; left:0; top:16px;
  width:9px; height:1px; background:var(--mist)}
ol{counter-reset:n}
ol li{counter-increment:n}
ol li:before{content:counter(n); position:absolute; left:0; top:7px;
  font-family:var(--mono); font-size:14px; color:var(--mist)}

blockquote{font-size:26px; line-height:1.30; color:var(--ink); max-width:34ch;
  border-left:3px solid var(--bright); padding-left:24px; font-style:italic}

pre{font-family:var(--mono); font-size:17px; line-height:1.5; color:var(--ink);
  background:transparent; white-space:pre; overflow:visible}
pre.lang-formula{font-size:27px; line-height:1.45}
pre.lang-small{font-size:13.5px; line-height:1.48}

hr{border:none; border-top:1px solid var(--line); margin:6px 0}

/* Tables: hairlines only, numbers in mono and right-aligned. Tufte's rule. */
table{border-collapse:collapse; font-family:var(--sans); font-size:15.5px; width:100%}
th{font-family:var(--mono); font-size:11px; letter-spacing:.08em; text-transform:uppercase;
  color:var(--mist); font-weight:600; text-align:left; padding:6px 16px 6px 0;
  border-bottom:1px solid var(--ink)}
td{padding:6px 14px 6px 0; border-bottom:1px solid var(--line); color:var(--slate);
  vertical-align:top}
td.num{font-family:var(--mono); text-align:right; padding-right:24px; white-space:nowrap;
  color:var(--ink)}
th:last-child,td:last-child{padding-right:0}
tr:last-child td{border-bottom:none}

/* Margin note, the second voice. */
.margin{position:absolute; right:80px; top:104px; width:200px;
  font-family:var(--sans); font-size:14px; line-height:1.45; color:var(--mist);
  border-top:1px solid var(--line); padding-top:10px}
.margin b{color:var(--slate); font-weight:600}

/* Class chips and figures ------------------------------------------------- */
.chip{display:inline-grid; place-items:center; width:26px; height:26px; border-radius:5px;
  font-family:var(--mono); font-weight:700; font-size:14px; color:#F7F6F3;
  vertical-align:-5px; margin-right:8px}
.chip.A{background:var(--a)} .chip.B{background:var(--b)}
.chip.C{background:var(--c)} .chip.D{background:var(--d)}

.figure{font-family:var(--mono); font-size:74px; line-height:1; letter-spacing:-.02em}
.figure.over{color:var(--over)}
.figure.ok{color:var(--ok)}
.figure-note{font-family:var(--sans); font-size:16px; color:var(--mist); margin-top:8px}

.cols{display:grid; grid-template-columns:1fr 1fr; gap:48px; align-items:start}
.cols-3{display:grid; grid-template-columns:repeat(3,1fr); gap:36px; align-items:start}
.stat{border-top:1px solid var(--ink); padding-top:12px}
.stat .k{font-family:var(--mono); font-size:11px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--mist)}
.stat .v{font-family:var(--mono); font-size:32px; line-height:1.1; margin-top:4px}
.stat .n{font-family:var(--sans); font-size:15px; color:var(--mist); margin-top:6px;
  line-height:1.4}

/* Eyebrow and footer ------------------------------------------------------ */
.eyebrow{font-family:var(--mono); font-size:12px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--mist); padding-bottom:10px;
  border-bottom:1px solid var(--line); margin-bottom:16px}
.slide-foot{display:flex; justify-content:space-between; align-items:center;
  font-family:var(--mono); font-size:11px; color:var(--mist);
  border-top:1px solid var(--line); padding-top:9px; margin-top:14px}
.foot-links a{color:var(--mist); border:none; margin-right:22px}
.foot-links a:hover{color:var(--brand)}
.pageno .of{opacity:.55}

/* Title and closing ------------------------------------------------------- */
.layout-title{background:var(--paper)}
.layout-title .content{justify-content:center; gap:26px}
.layout-title h1{font-size:80px; max-width:16ch}
.layout-title .byline{font-family:var(--sans); font-size:19px; color:var(--mist);
  display:flex; gap:26px; flex-wrap:wrap; align-items:center}
.layout-title .byline a{color:var(--mist); border:none}
.layout-title .rule{width:96px; height:3px; background:var(--ink)}

.layout-closing{background:var(--ink); color:var(--paper)}
.layout-closing h1,.layout-closing h2{color:var(--paper)}
.layout-closing p{color:#C9C6BF}
.layout-closing a{color:#7FD8C2; border-bottom-color:#2E4A44}
.layout-closing td,.layout-closing th{border-color:#2B3238; color:#C9C6BF}
.qr-row{display:flex; gap:40px; flex-wrap:wrap; margin-top:8px}
.qr{width:150px}
.qr img{width:150px; height:150px; display:block; background:#F7F6F3;
  border-radius:6px}
.qr .cap{font-family:var(--mono); font-size:12px; color:#C9C6BF; margin-top:10px;
  line-height:1.45}
.qr .cap b{color:var(--paper); display:block; font-size:13px}

/* Density step, for slides that carry more than the default scale allows.
   Set `dense: true` in a slide's front matter. */
.slide.dense p{font-size:18px}
.slide.dense p.lead{font-size:22px}
.slide.dense p.small{font-size:15px}
.slide.dense ul li,.slide.dense ol li{font-size:17px; padding:5px 0 5px 22px}
.slide.dense ul li:before{top:14px}
.slide.dense ol li:before{top:5px}
.slide.dense h2{font-size:32px}
.slide.dense h4{font-size:12px}
.slide.dense pre.lang-formula{font-size:24px}
.slide.dense .quad{min-height:200px}
.slide.dense .quad .qd{font-size:14px}
.slide.dense .content{gap:12px}

/* Part dividers ----------------------------------------------------------- */
.layout-part{background:var(--ink); color:var(--paper)}
.layout-part .content{justify-content:center; gap:22px}
.layout-part h1{color:var(--paper); font-size:60px; max-width:18ch}
.layout-part p.lead{color:#C9C6BF; max-width:38ch}
.part-num{font-family:var(--mono); font-size:13px; letter-spacing:.16em;
  text-transform:uppercase; color:#7FD8C2; padding-bottom:18px;
  border-bottom:1px solid #2B3238; width:190px; margin-bottom:8px}

/* Four across, for the dashboard contrast --------------------------------- */
.cols-4{display:grid; grid-template-columns:repeat(4,1fr); gap:30px; align-items:start}
.cols-4 .stat .v{font-size:42px}

/* Quadrant figure --------------------------------------------------------- */
.quad{display:grid; grid-template-columns:repeat(2,1fr); grid-template-rows:auto auto;
  border:1px solid var(--ink); width:600px; min-height:240px; font-family:var(--sans)}
.quad div{padding:16px 18px; border-right:1px solid var(--line);
  border-bottom:1px solid var(--line)}
.quad div:nth-child(2n){border-right:none}
.quad div:nth-child(n+3){border-bottom:none}
.quad .qt{font-family:var(--mono); font-size:12px; letter-spacing:.08em;
  text-transform:uppercase; font-weight:700; margin-bottom:8px}
.quad .qd{font-size:15px; line-height:1.4; color:var(--mist)}
.quad .hot .qt{color:var(--over)}
.quad .go .qt{color:var(--ok)}

/* Stage furniture --------------------------------------------------------- */
#progress{position:fixed; left:0; bottom:0; height:2px; background:var(--brand);
  transition:width .18s ease; z-index:20}
#help{position:fixed; right:14px; bottom:12px; font-family:var(--mono); font-size:11px;
  color:var(--mist); z-index:20; opacity:.6}
#overview{position:fixed; inset:0; background:var(--shell); z-index:30; display:none;
  overflow:auto; padding:32px}
#overview.on{display:block}
#overview .grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(210px,1fr));
  gap:16px; max-width:1400px; margin:0 auto}
#overview .card{background:var(--paper); border:1px solid var(--line); border-radius:6px;
  padding:14px 16px; cursor:pointer; min-height:118px}
#overview .card:hover{border-color:var(--ink)}
#overview .card .n{font-family:var(--mono); font-size:11px; color:var(--mist)}
#overview .card .t{font-family:var(--serif); font-size:17px; line-height:1.25;
  margin-top:6px; color:var(--ink)}
#overview .card .s{font-family:var(--mono); font-size:10px; letter-spacing:.07em;
  text-transform:uppercase; color:var(--mist); margin-top:8px}
#overview h2{font-family:var(--mono); font-size:13px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--mist); text-align:center; margin-bottom:24px}

#notespane{position:fixed; left:0; right:0; bottom:0; max-height:42vh; overflow:auto;
  background:var(--ink); color:var(--paper); padding:22px 30px; z-index:25; display:none;
  font-family:var(--sans); font-size:16px; line-height:1.55}
#notespane.on{display:block}
#notespane p{color:#C9C6BF; font-size:16px; max-width:none; font-family:var(--sans)}
#notespane strong{color:var(--paper)}
#notespane h4{color:#7FD8C2; margin-bottom:8px}
.notes{display:none}

/* Print, one slide per page. Open with ?print and use the browser's PDF export. */
@media print{
  @page{size:1280px 720px; margin:0}
  body{background:#fff; overflow:visible}
  #stage{position:static; overflow:visible}
  #canvas{width:1280px; height:auto; position:static; box-shadow:none;
    transform:none!important}
  .slide{position:relative; display:flex!important; height:720px;
    page-break-after:always; break-after:page}
  #progress,#help,#overview,#notespane{display:none!important}
}
"""

JS = r"""
(function(){
  "use strict";
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var canvas = document.getElementById("canvas");
  var progress = document.getElementById("progress");
  var overview = document.getElementById("overview");
  var notespane = document.getElementById("notespane");
  var current = 0;

  function scale(){
    var pad = 34;
    var k = Math.min((window.innerWidth - pad) / 1280, (window.innerHeight - pad) / 720);
    canvas.style.transform = "translate(-50%, -50%) scale(" + k + ")";
  }

  function show(index){
    current = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach(function(s, i){ s.classList.toggle("active", i === current); });
    progress.style.width = ((current + 1) / slides.length * 100) + "%";
    if (location.hash !== "#" + (current + 1)) {
      history.replaceState(null, "", "#" + (current + 1));
    }
    renderNotes();
  }

  function renderNotes(){
    var note = slides[current].querySelector(".notes");
    notespane.innerHTML = note
      ? '<h4>Slide ' + (current + 1) + ' notes</h4>' + note.innerHTML
      : '<h4>Slide ' + (current + 1) + '</h4><p>No note on this one.</p>';
  }

  function buildOverview(){
    var grid = overview.querySelector(".grid");
    slides.forEach(function(s, i){
      var head = s.querySelector("h1, h2, h3");
      var card = document.createElement("div");
      card.className = "card";
      card.innerHTML =
        '<div class="n">' + (i + 1) + '</div>' +
        '<div class="t">' + (head ? head.textContent : "") + '</div>' +
        '<div class="s">' + (s.getAttribute("data-section") || "") + '</div>';
      card.addEventListener("click", function(){
        overview.classList.remove("on"); show(i);
      });
      grid.appendChild(card);
    });
  }

  document.addEventListener("keydown", function(e){
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var k = e.key;
    if (k === "ArrowRight" || k === "ArrowDown" || k === " " || k === "PageDown"){
      e.preventDefault(); show(current + 1);
    } else if (k === "ArrowLeft" || k === "ArrowUp" || k === "PageUp"){
      e.preventDefault(); show(current - 1);
    } else if (k === "Home"){ show(0); }
    else if (k === "End"){ show(slides.length - 1); }
    else if (k === "Escape" || k === "o" || k === "O"){
      overview.classList.toggle("on");
    } else if (k === "s" || k === "S"){
      notespane.classList.toggle("on");
    } else if (k === "f" || k === "F"){
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen();
    } else if (/^[0-9]$/.test(k)){
      var buffer = (window.__jump || "") + k;
      window.__jump = buffer;
      clearTimeout(window.__jumpTimer);
      window.__jumpTimer = setTimeout(function(){
        show(parseInt(window.__jump, 10) - 1); window.__jump = "";
      }, 550);
    }
  });

  canvas.addEventListener("click", function(e){
    if (e.target.closest("a")) return;
    show(current + (e.clientX < window.innerWidth / 2 ? -1 : 1));
  });

  var touchX = null;
  canvas.addEventListener("touchstart", function(e){ touchX = e.touches[0].clientX; },
                          {passive:true});
  canvas.addEventListener("touchend", function(e){
    if (touchX === null) return;
    var dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 45) show(current + (dx < 0 ? 1 : -1));
    touchX = null;
  }, {passive:true});

  window.addEventListener("resize", scale);
  window.addEventListener("hashchange", function(){
    var n = parseInt(location.hash.slice(1), 10);
    if (!isNaN(n) && n - 1 !== current) show(n - 1);
  });

  buildOverview();
  scale();
  var start = parseInt(location.hash.slice(1), 10);
  show(isNaN(start) ? 0 : start - 1);

  if (location.search.indexOf("print") !== -1){
    slides.forEach(function(s){ s.classList.add("active"); });
    document.body.classList.add("printing");
  }
})();
"""

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | {author}</title>
<meta name="description" content="An operating model for autonomous AI in project delivery and end to end PMO.">
<meta name="author" content="{author}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23101418'/%3E%3Crect x='14' y='17' width='12' height='6' rx='3' fill='%232E7D6B'/%3E%3Crect x='14' y='27' width='20' height='6' rx='3' fill='%233C6E9F'/%3E%3Crect x='14' y='37' width='27' height='6' rx='3' fill='%23B8843A'/%3E%3Crect x='14' y='47' width='46' height='6' rx='3' fill='%23A34432'/%3E%3C/svg%3E">
<style>{css}</style>
</head>
<body>
<div id="stage"><div id="canvas">
{slides}
</div></div>
<div id="progress"></div>
<div id="help">arrows move &middot; o overview &middot; s notes &middot; f fullscreen</div>
<div id="overview"><h2>All slides</h2><div class="grid"></div></div>
<div id="notespane"></div>
<script>{js}</script>
</body>
</html>
"""


def main() -> int:
    if not SLIDES.exists():
        print(f"no slides directory at {SLIDES}", file=sys.stderr)
        return 1

    print("QR codes")
    qr_sources = build_qr_codes()

    files = sorted(p for p in SLIDES.glob("*.md") if not p.name.startswith("_"))
    if not files:
        print(f"no slide files in {SLIDES}", file=sys.stderr)
        return 1

    metas = [parse_slide(path) for path in files]
    total = len(metas)
    rendered = [render_slide(meta, i + 1, total) for i, meta in enumerate(metas)]

    page = SHELL.format(
        title=TITLE,
        author=AUTHOR,
        css=CSS,
        js=JS,
        slides="\n\n".join(rendered),
    )
    page = inline_qr_codes(page, qr_sources)
    OUTPUT.write_text(page, encoding="utf-8")

    print()
    print(f"slides   {total}")
    with_notes = sum(1 for m in metas if m["notes"])
    print(f"notes    {with_notes} of {total}")
    print(f"output   {OUTPUT.relative_to(ROOT)}  ({len(page) / 1024:.0f} kB, self-contained)")
    print()
    print("Open it directly from disk. No server, no install, no network.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the DataBP demo site's generated parts from their sources.

Sources: tools/brand.css, tools/header.html, tools/footer.html (the brand),
and pilot/*.md, each a copy of one Pilot item, its first line naming the
item and version. Pilot is the source; the copy here is what the page was
built from. Run from the repository root:

    python3 tools/build.py          rebuild the pages
    python3 tools/build.py --check  exit 1 if any page differs from a rebuild
"""
import html, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "business.html", "openflow.html", "ask.html"]
GENERATED = ["tutorial.html", "build-log.html", "documents.html"]  # and one page per DOCS item

# Private details masked when the tutorial is built for the public site;
# Pilot keeps the item whole (Ray, 2026-11-19, answer 1a). Order matters.
MASKS = [
    (r"op://[^`\s)]+", "[vault item]"),
    (r"[A-Za-z0-9-]+\.[a-z0-9]+\.[a-z0-9-]+\.rds\.amazonaws\.com", "[RDS endpoint]"),
    (r"(?i)\bfiamfdn-igb87170\b", "[Snowflake account]"),
    (r"\beg472\.(semantic-layer\.)?us1\.dbt\.com", "[dbt host]"),
    (r"[A-Za-z0-9._%+-]+@integrationals\.com", "[email address]"),
    (r"C:\\Users\\[^`\s,;)]+", "[local path]"),
    (r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b", "[IP address]"),
    (r"\bsgr-[0-9a-f]+\b", "[security group entry]"),
    (r"\brds!db-[0-9a-f-]+…?", "[secret name]"),
    (r"\bm-[0-9a-f]{32}\b", "[id]"),
    (r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "[id]"),
    (r"\b[0-9a-z]{26}\b", "[id]"),
    (r"\b\d{11,}\b", "[id]"),
    (r"app\.hex\.tech/[^\s`\"]+", "app.hex.tech/[app address]"),
]


def mask(text):
    for pattern, repl in MASKS:
        text = re.sub(pattern, repl, text)
    return text


DOCS = [   # the branch documents published on the site, by effort, in delivery order (Ray, 2026-11-20 12:05 ET)
    ("DIG-655", "The reconciliation", 813, "Source profile", "What the sources hold, column by column, and the data the app needs"),
    ("DIG-655", "The reconciliation", 806, "Design document", "The decisions, D-1 to D-24, each with its reason and evidence"),
    ("DIG-655", "The reconciliation", 814, "Test plan", "Every logic path and the test that proves it, written before the code"),
    ("DIG-655", "The reconciliation", 815, "Implementation guide, 1 of 4", "Staging and silver, step by step"),
    ("DIG-655", "The reconciliation", 816, "Implementation guide, 2 of 4", "Gold and the five checks, step by step"),
    ("DIG-656", "Morgan, the agent", 817, "Design document", "A pluggable agent service: core, persona and route"),
    ("DIG-656", "Morgan, the agent", 819, "Test plan", "The route's tests and the live probes"),
    ("DIG-656", "Morgan, the agent", 818, "Implementation guide", "Building and deploying the service"),
]

PAGE_CSS = """body{margin:0}
.doc{max-width:960px;margin:0 auto;padding:32px 24px 56px;line-height:1.7;font-size:16px;overflow-wrap:anywhere}
.doc h2{margin-top:36px} .doc h3{margin-top:26px}
.doc table{border-collapse:collapse;width:100%;font-size:14px;margin:12px 0 20px;display:block;overflow-x:auto}
.doc th,.doc td{border-bottom:1px solid var(--brand-line);padding:6px 8px;text-align:left;vertical-align:top}
.doc code{font-size:13px;background:#f3f6fa;padding:1px 4px;border-radius:4px;overflow-wrap:anywhere}
.doc pre{background:#f3f6fa;border:1px solid var(--brand-line);border-radius:8px;padding:12px;overflow-x:auto} .doc pre code{background:none;padding:0}
.note{background:var(--brand-sky);border-radius:12px;padding:12px 16px;font-size:14px;margin:0 0 24px}"""


def page(title, crumb, lead, content, note=""):
    note_html = f'<p class="note">{html.escape(note)}</p>' if note else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · DataBP POC</title>
<style>
{PAGE_CSS}
</style>
</head>
<body>
{band(crumb, title, lead)}
<main class="doc">
{note_html}
{content}
</main>
</body>
</html>
"""


def morgan_face(cls, size=84, uid="mg"):
    """Morgan's portrait (tools/morgan_face.svg), with its own class, size and gradient ids."""
    svg = (ROOT / "tools/morgan_face.svg").read_text().strip()
    svg = svg.replace('class="morgan"', f'class="morgan {cls}"').replace('width="84" height="84"', f'width="{size}" height="{size}"')
    return svg.replace('id="mg-', f'id="{uid}-').replace('url(#mg-', f'url(#{uid}-')


def band(crumb, title, lead):
    """The navy title band every page but the home page opens with."""
    crumbs = ""
    if crumb:
        trail = "".join(f' / <a href="{h}">{html.escape(t)}</a>' for t, h in crumb[:-1]) + f" / {html.escape(crumb[-1][0])}"
        crumbs = f'<div class="crumbs"><a href="./">DataBP POC</a>{trail}</div>'
    face = morgan_face("band-face") if title == "Ask Morgan" else ""
    head = f'<h1>{html.escape(title)}</h1>'
    if face:   # Morgan's portrait beside her name: the human side of the agent (Ray, 2026-11-20 13:02 ET)
        head = f'<div class="band-title">{face}{head}</div>'
    return (f'<section class="page-band"><div class="in">{crumbs}'
            f'{head}<p class="lead">{html.escape(lead)}</p></div></section>')


def render(item, strip_header=False):
    """A Pilot item's copy as HTML, masked, its own first heading left to the band."""
    import markdown
    src = (ROOT / f"pilot/k111ki{item}.md").read_text()
    origin = src.splitlines()[0]
    body = src.split("\n", 1)[1]
    body = re.sub(r"^\s*# .*\n", "", body, count=1)
    if strip_header:
        parts = body.split("\n\n")
        while parts and (not parts[0].strip() or parts[0].lstrip().startswith("|")):
            parts.pop(0)
        body = "\n\n".join(parts)
    body = re.sub(r"(?m)^ {3}(?! )", "    ", mask(body))   # list continuations: four spaces, as Markdown needs
    m = re.match(r"<!-- Pilot knowledge (\d+) item (\d+), version (\d+): (.*) -->", origin)
    return origin, m, markdown.markdown(body, extensions=["tables", "pymdownx.superfences"])


def tutorial():
    origin, m, content = render(463)
    note = (f"Built from Pilot knowledge {m.group(1)} item {m.group(2)}, version {m.group(3)}, as it stands: the working "
            "log kept while building, every step with its values and decisions. Private details such as addresses, "
            "identifiers and paths are masked here; Pilot holds the whole.")
    return page("The build tutorial", [("Build log", "build-log.html"), ("The build tutorial", "")],
                "Every step as it happened, with its values: the source the build log is drawn from.", origin + content, note)


def build_log():
    origin, m, content = render(820, strip_header=True)
    return page("The build log", [("The build log", "")],
                "How the reconciliation POC was built, step by step with its commands, and how it is proven.",
                origin + content + '<p class="note">Every step with its values is in <a href="tutorial.html">the build tutorial</a>; '
                'the branch documents behind each decision are in <a href="documents.html">Documents</a>.</p>')


def doc_slug(item):
    return f"doc-{item}.html"


def documents():
    groups = {}
    for issue, effort, item, kind, gist in DOCS:
        groups.setdefault((issue, effort), []).append((item, kind, gist))
    out = ['<p class="note">These are the working files exactly as kept in Pilot, our knowledge base, which a client\'s team '
           'receives with the work. Every code is an address in it: a standard, a decision, a profile result, and who '
           'decided and when.</p>',
           '<p class="lead-in">Every piece of work here ran the same way: an issue and a branch; a source profile where data '
           'is read; a design whose numbered decisions each carry their reason and evidence; a test plan written before the '
           'code; implementation guides for the steps; then a pull request whose tests are explained one by one, a review, '
           'and a live read after the merge. Claude, an AI agent, wrote these documents and did the engineering; Ray Serrano '
           'made every decision, each one quoted with its time in the documents themselves.</p>']
    for (issue, effort), docs in groups.items():
        out.append(f'<h2>{html.escape(effort)} <span class="pill">{issue}</span></h2><div class="docgrid">')
        for item, kind, gist in docs:
            out.append(f'<a class="brand-card doccard" href="{doc_slug(item)}"><span class="kind">{html.escape(kind)}</span>'
                       f'<p>{html.escape(gist)}</p></a>')
        out.append("</div>")
    css = ('<style>.lead-in{max-width:68ch}.pill{display:inline-block;font-size:13px;background:var(--brand-sky);color:var(--brand-teal);'
           'border-radius:999px;padding:3px 12px;vertical-align:middle;margin-left:8px;font-weight:600}'
           '.docgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin:16px 0 8px}'
           '.doccard{display:block;padding:18px 20px;text-decoration:none;color:var(--brand-text)}'
           '.doccard:hover{box-shadow:0 10px 30px rgba(15,57,82,.14)}.doccard .kind{font-weight:600;color:var(--brand-ink)}'
           '.doccard p{margin:6px 0 0;font-size:14px;line-height:1.55}</style>')
    return page("Documents", [("Documents", "")],
                "The branch documents behind the POC, as kept in Pilot: the agentic development process, shown by its own work.",
                css + "\n".join(out))


def doc(item):
    issue, effort, _i, kind, gist = next(d for d in DOCS if d[2] == item)
    origin, m, content = render(item)
    note = (f"{effort} ({issue}). Built from Pilot knowledge {m.group(1)} item {m.group(2)}, version {m.group(3)}, as kept "
            "while building; private details such as addresses, identifiers and paths are masked here.")
    return page(m.group(4), [("Documents", "documents.html"), (kind, "")], gist + ".", origin + content, note)


PAGE_BANDS = {   # the title band each hand-written page opens with
    "business.html": ([], "The business",
                      "Market data licensing from the exchange to the subscriber, and where reconciliation fits."),
    "openflow.html": ([], "The platform",
                      "Openflow in our own AWS network, level by level, from the VPC to the connector."),
    "ask.html": ([("Ask Morgan", "")], "Ask Morgan",
                 "Morgan answers questions about the reconciliation in your own words. Every number comes from a query she "
                 "runs against the dbt Semantic Layer, the same metrics the app reads, and the query is shown under the answer."),
}

FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap">'


def between(text, name, content, anchor_before=None, anchor_after=None):
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    block = f"{start}\n{content}\n{end}"
    if start in text:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: block, text, count=1, flags=re.S)
    if anchor_before:
        assert text.count(anchor_before) == 1, (name, anchor_before)
        return text.replace(anchor_before, block + "\n" + anchor_before, 1)
    assert text.count(anchor_after) == 1, (name, anchor_after)
    return text.replace(anchor_after, anchor_after + "\n" + block, 1)


def brand(text):
    css = (ROOT / "tools/brand.css").read_text().strip()
    text = between(text, "brand-style", FONT + "\n<style>\n" + css + "\n</style>", anchor_before="</head>")
    text = between(text, "brand-header", (ROOT / "tools/header.html").read_text().strip(), anchor_after=re.search(r"<body[^>]*>", text).group(0))
    text = between(text, "brand-footer", (ROOT / "tools/footer.html").read_text().strip(), anchor_before="</body>")
    return text


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)


def a_to_z():
    src = (ROOT / "pilot/k111ki809.md").read_text()
    origin = src.splitlines()[0]
    body = src.split("\n", 1)[1]
    parts = [p.strip() for p in body.split("\n\n") if p.strip()]
    summary = next(p for p in parts if not p.startswith(("#", "|")))
    table = next(p for i, p in enumerate(parts) if p.startswith("| #"))
    rows = [r for r in table.splitlines()[2:]]
    items = [re.sub(r"^\d+\. ", "", l) for l in body.splitlines() if re.match(r"^\d+\. ", l)]
    sources, paras = [], []
    for it in items:
        text, _, src_ = it.partition(" Sources: ")
        paras.append(text)
        sources += [s.strip().rstrip(".") for s in src_.split(";") if s.strip()]
    seen = []
    for s in sources:
        if s not in seen:
            seen.append(s)
    out = ['<section id="az" class="az">', origin, f'<p class="az-sum">{inline(summary)}</p>',
           '<table class="az-t"><thead><tr><th>#</th><th>Who or what</th><th>In short</th></tr></thead><tbody>']
    for r in rows:
        c = [x.strip() for x in r.strip("|").split("|")]
        out.append(f'<tr class="az-r"><td>{c[0]}</td><td>{inline(c[1])}</td><td>{inline(c[2])}</td></tr>')
    out.append("</tbody></table>")
    out.append('<ol class="az-n">' + "".join(f"<li>{inline(p)}</li>" for p in paras) + "</ol>")
    out.append(f'<p class="note">Sources: {inline("; ".join(seen))}.</p>')
    out.append("</section>")
    return "\n".join(out)


def build():
    result = {"tutorial.html": brand(tutorial()), "build-log.html": brand(build_log()),
              "documents.html": brand(documents())}
    for d in DOCS:
        result[doc_slug(d[2])] = brand(doc(d[2]))
    for name in PAGES:
        text = (ROOT / name).read_text()
        text = brand(text)
        if name == "index.html":   # Morgan's face where the home page sends people to her (Ray, 2026-11-20 13:06 ET, 2y)
            text = between(text, "morgan-card", morgan_face("card-face", 56, "mgc"), anchor_after='<a class="brand-card" href="ask.html">')
            text = between(text, "morgan-close", morgan_face("close-face", 96, "mgx"), anchor_after='<section class="band navy close">\n    <div class="in">')
        if name in PAGE_BANDS:
            crumb, title, lead = PAGE_BANDS[name]
            text = between(text, "page-band", band(crumb, title, lead), anchor_after="<!-- brand-header:end -->")
        if name == "business.html":
            text = re.sub(r'<section id="az" class="az">.*?</section>\n', "", text, count=1, flags=re.S) if "<!-- az:start -->" not in text else text
            text = between(text, "az", a_to_z(), anchor_before='<div class="bar">')
        result[name] = text
    return result

if __name__ == "__main__":
    built = build()
    if "--check" in sys.argv:
        stale = [n for n, t in built.items() if (ROOT / n).read_text() != t]
        print("stale: " + ", ".join(stale) if stale else "all pages match their sources")
        sys.exit(1 if stale else 0)
    for n, t in built.items():
        (ROOT / n).write_text(t)
    print("built: " + ", ".join(built))

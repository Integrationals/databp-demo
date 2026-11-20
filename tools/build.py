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
GENERATED = ["tutorial.html", "build-log.html"]

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


def tutorial():
    import markdown
    src = (ROOT / "pilot/k111ki463.md").read_text()
    origin = src.splitlines()[0]
    body = mask(src.split("\n", 1)[1])
    content = markdown.markdown(body, extensions=["tables", "fenced_code"])
    m = re.match(r"<!-- Pilot knowledge (\d+) item (\d+), version (\d+): (.*) -->", origin)
    note = (f"Built from Pilot knowledge {m.group(1)} item {m.group(2)}, version {m.group(3)}, "
            "as it stands: a working draft, published to be reviewed and improved, Pilot first. "
            "Private details such as addresses, identifiers and paths are masked here; Pilot holds the whole.")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The build tutorial · DataBP POC</title>
<style>
body{{margin:0}}
main{{max-width:960px;margin:0 auto;padding:20px 24px 40px;line-height:1.65;font-size:16px}}
.crumbs{{font-size:13px;color:var(--brand-muted)}} .crumbs a{{color:var(--brand-muted)}}
.draft{{background:var(--brand-sky);border:1px solid var(--brand-line);border-radius:12px;padding:12px 16px;font-size:14px;margin:12px 0 20px}}
table{{border-collapse:collapse;width:100%;font-size:14px;margin:12px 0}} th,td{{border-bottom:1px solid var(--brand-line);padding:6px 8px;text-align:left;vertical-align:top}}
code{{font-size:13px;background:#f3f6fa;padding:1px 4px;border-radius:4px;overflow-wrap:anywhere}}
pre{{background:#f3f6fa;border:1px solid var(--brand-line);border-radius:8px;padding:12px;overflow-x:auto}} pre code{{background:none;padding:0}}
</style>
</head>
<body>
<main>
<div class="crumbs"><a href="./">DataBP POC</a> / The build tutorial</div>
{origin}
<p class="draft">{html.escape(note)}</p>
{content}
</main>
</body>
</html>
"""

def build_log():
    """The build log page, from Pilot knowledge 111 item 820: the title, then the body after the item's
    own header table (its publication notes are for Pilot, not the page)."""
    import markdown
    src = (ROOT / "pilot/k111ki820.md").read_text()
    origin = src.splitlines()[0]
    body = src.split("\n", 1)[1]
    title, rest = body.split("\n", 1)
    parts = rest.split("\n\n")
    while parts and (not parts[0].strip() or parts[0].lstrip().startswith("|")):
        parts.pop(0)
    text = re.sub(r"(?m)^ {3}(?! )", "    ", "\n\n".join(parts))   # list continuations: four spaces, as Markdown needs
    content = markdown.markdown(title + "\n\n" + text, extensions=["tables", "pymdownx.superfences"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The build log · DataBP POC</title>
<style>
body{{margin:0}}
main{{max-width:960px;margin:0 auto;padding:20px 24px 40px;line-height:1.65;font-size:16px}}
.crumbs{{font-size:13px;color:var(--brand-muted)}} .crumbs a{{color:var(--brand-muted)}}
code{{font-size:13px;background:#f3f6fa;padding:1px 4px;border-radius:4px;overflow-wrap:anywhere}}
pre{{background:#f3f6fa;border:1px solid var(--brand-line);border-radius:8px;padding:12px;overflow-x:auto}} pre code{{background:none;padding:0}}
table{{border-collapse:collapse;width:100%;font-size:14px;margin:12px 0 20px}} th,td{{border-bottom:1px solid var(--brand-line);padding:6px 8px;text-align:left;vertical-align:top}}
</style>
</head>
<body>
<main>
<div class="crumbs"><a href="./">DataBP POC</a> / The build log</div>
{origin}
{content}
</main>
</body>
</html>
"""

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
    result = {"tutorial.html": brand(tutorial()), "build-log.html": brand(build_log())}
    for name in PAGES:
        text = (ROOT / name).read_text()
        text = brand(text)
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

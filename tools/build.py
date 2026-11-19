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
PAGES = ["index.html", "business.html", "openflow.html"]
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
    result = {}
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

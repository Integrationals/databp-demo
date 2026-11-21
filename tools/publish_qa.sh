#!/bin/sh
# Publish the QA site: build for qa and replace the pages of Integrationals/databp-demo-qa, keeping its CNAME and
# .nojekyll, then commit and push (DIG-657 design D-2; guide step 5, after DIG-598's folder copy).
# Run after Ray merges into qa, from a clean checkout of qa's tip, with GH_TOKEN holding the machine user's token.
set -eu
R=$(cd "$(dirname "$0")/.." && pwd); O=$(mktemp -d); W=$(mktemp -d)
python3 "$R/tools/build.py" --env qa --out "$O"
git clone -q "https://x-access-token:${GH_TOKEN:?the machine user's token}@github.com/Integrationals/databp-demo-qa.git" "$W"
git -C "$W" remote set-url origin https://github.com/Integrationals/databp-demo-qa.git
find "$W" -mindepth 1 -maxdepth 1 ! -name .git ! -name CNAME ! -name .nojekyll -exec rm -rf {} +
cp "$O"/*.html "$W"/
cd "$W" && git add -A
git commit -q -m "QA: databp-demo qa at $(git -C "$R" rev-parse --short HEAD)" && \
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$GH_TOKEN" | base64 -w0)" push -q origin main
echo "published: $(ls "$O"/*.html | wc -l) pages from $(git -C "$R" rev-parse --short HEAD) to databp-demo-qa"

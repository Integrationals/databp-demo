#!/bin/sh
# Publish a site environment: build for dev or qa and replace the pages of its hosting repository,
# Integrationals/databp-demo-dev or databp-demo-qa, keeping its CNAME and .nojekyll, then commit and push
# (DIG-657 design D-2, D-9; guide step 5, after DIG-598's folder copy). Production is published by Pages from main.
# usage: publish.sh --env dev|qa [--dry-run]; GH_TOKEN holds the machine user's token unless --dry-run.
# dev runs before every pull request into qa; qa runs after Ray merges into qa, from a clean checkout of qa's tip.
set -eu
case "${1:-} ${2:-}" in
  "--env dev") E=dev; REPO=databp-demo-dev ;;
  "--env qa") E=qa; REPO=databp-demo-qa ;;
  "--env prod") echo "publish.sh: production is published by Pages from main" >&2; exit 2 ;;
  *) echo "publish.sh: name the environment: --env dev or qa" >&2; exit 2 ;;
esac
R=$(cd "$(dirname "$0")/.." && pwd); O=$(mktemp -d); W=$(mktemp -d)
python3 "$R/tools/build.py" --env "$E" --out "$O" >/dev/null
if [ "${3:-}" = "--dry-run" ]; then echo "dry run: $E build in $O for Integrationals/$REPO"; exit 0; fi
git clone -q "https://x-access-token:${GH_TOKEN:?the machine user's token}@github.com/Integrationals/$REPO.git" "$W"
git -C "$W" remote set-url origin "https://github.com/Integrationals/$REPO.git"
find "$W" -mindepth 1 -maxdepth 1 ! -name .git ! -name CNAME ! -name .nojekyll -exec rm -rf {} +
cp "$O"/*.html "$W"/
cd "$W" && git add -A
git commit -q -m "$E: databp-demo at $(git -C "$R" rev-parse --short HEAD)" || echo "no change to publish"
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$GH_TOKEN" | base64 -w0)" push -q origin main
echo "published: $(ls "$O"/*.html | wc -l) pages from $(git -C "$R" rev-parse --short HEAD) to Integrationals/$REPO"

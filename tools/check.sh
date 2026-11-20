#!/bin/sh
# usage: check.sh <site dir>; prints one line per check, PASS or FAIL
D=$1; r(){ google-chrome --headless=new --no-sandbox --disable-gpu --virtual-time-budget=3000 --dump-dom "file://$D/$1" 2>/dev/null; }
t(){ if eval "$2"; then echo "PASS $1"; else echo "FAIL $1"; fi; }
rows(){ r "$1" | grep -o '<tr><td>' | wc -l; }
t "1 home page lists business.html and openflow.html" "r index.html | grep -q 'href=\"business.html\"' && r index.html | grep -q 'href=\"openflow.html\"'"
t "2 business page level 0 renders its diagram and five rows" "[ -f $D/business.html ] && [ \$(rows business.html) -eq 5 ] && r business.html | grep -q 'data-go=\"reconciliation\" tabindex'"
t "3 openflow screens view names DATABP_RUNTIME" "[ -f $D/openflow.html ] && r 'openflow.html#screens' | grep -q '>DATABP_RUNTIME<'"
t "4 openflow page no longer says None yet" "[ -f $D/openflow.html ] && ! grep -q 'None yet' $D/openflow.html"
t "5 business page: four views below level 0 each open at their address, with their path and five rows" "[ -f $D/business.html ] && ( for v in parties:'Level 1: The parties' documents:'Level 1: The four documents' counting:'Level 2: Counting the use' reconciliation:'Level 1: Entitlement and billing reconciliation'; do a=\${v%%:*}; p=\${v#*:}; [ \$(rows business.html#\$a) -eq 5 ] && r business.html#\$a | grep -q \"\$p\" || exit 1; done )"
t "6 business page: DataBP at level 0 opens its own view, with its path and five rows" "[ -f $D/business.html ] && r business.html | grep -q 'data-go=\"databp\"' && [ \$(rows business.html#databp) -eq 5 ] && r business.html#databp | grep -q 'Level 1: DataBP'"
t "7 business page names the app in the DataBP view and as the reconciliation view's heading" "[ -f $D/business.html ] && r business.html#databp | grep -q 'Entitlement and billing reconciliation for one data provider' && r business.html#reconciliation | grep -q '<h1 id=\"title\">Entitlement and billing reconciliation'"
t "8 no page mentions the north star" "! grep -qiE 'north[- ]?star' $D/index.html $D/business.html $D/openflow.html"
t "9 business page level 0 draws the loop with a line legend" "[ -f $D/business.html ] && r business.html | grep -q 'A step of the loop' && r business.html | grep -q '>submitted by the vendor to the exchange<'"
t "10 openflow page leads back to the home page" "r openflow.html | grep -q '<a class=\"brand-home\" href=\"./\">DataBP'"
t "11 documents view: each of the four documents opens its sample" "python3 - \"$D\" <<'PY'
import asyncio,sys
from playwright.async_api import async_playwright
async def m(d):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await b.new_page(); await pg.goto('file://'+d+'/business.html#documents')
        for k,t in [('license','Market data license agreement'),('entitlement','Subscriber entitlement'),('usage','Monthly usage report'),('invoice','Invoice')]:
            await pg.click('[data-doc=\"'+k+'\"]', timeout=3000)
            assert await pg.evaluate('document.getElementById(\"doc\").open')
            assert (await pg.inner_text('#doc-title'))==t
            assert 'Sample, invented' in await pg.inner_text('#doc')
            await pg.click('#doc-close')
        await b.close()
asyncio.run(m(sys.argv[1]))
PY"
t "12 business page: the A to Z summary shows on level 0 only, with five rows" "[ -f $D/business.html ] && [ \$(r business.html | grep -o '<tr class=\"az-r\">' | wc -l) -eq 5 ] && r business.html | grep -q '<section id=\"az\" class=\"az\">' && r business.html#databp | grep -q '<section id=\"az\" class=\"az\" hidden=\"\">'"
t "13 every page wears the brand: DataBP's type, the POC bar, the not-a-DataBP-site footer, no DataBP logo" "( for f in index.html business.html openflow.html; do grep -q 'family=Poppins' $D/\$f && grep -q 'class=\"brand-bar\"' $D/\$f && grep -q 'Integrationals, as a POC for DataBP' $D/\$f && grep -q 'This is not a DataBP site' $D/\$f && ! grep -qi "databp.com/wp-content" $D/\$f || exit 1; done )"
t "14 every generated part matches its source: the brand files and the Pilot item k111ki809" "[ -f $D/tools/build.py ] && (cd $D && python3 tools/build.py --check >/dev/null)"
t "15 no Pilot copy and no tutorial page in the site: Pilot is read through the connector at build time" "[ ! -e $D/pilot ] && [ ! -e $D/tutorial.html ] && ! grep -lq 'tutorial.html' $D/*.html"
t "16 reconciliation view: five checks, under-reporting among them, no box text overflowing" "r business.html#reconciliation | grep -q 'Entitled beyond reported' && [ \$(r business.html#reconciliation | grep -o '<g class=\"q\">' | wc -l) -eq 6 ] && python3 $(dirname "$0")/shot.py $D/business.html | grep -q 'overflow: \[\]'"
t "17 next steps: the multi-tenant Digest Diagram opens its views, each with five facts, and Up one returns to level 0" "python3 - \"$D\" <<'PY'
import asyncio,sys
from playwright.async_api import async_playwright
async def m(d):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await b.new_page(); await pg.goto('file://'+d+'/next-steps.html')
        assert (await pg.inner_text('.dd-title')).startswith('Multi-tenant')
        for v in ['mt-stamp','mt-maps','mt-closed','mt-readers']:
            await pg.click('[data-go=\"'+v+'\"] >> nth=0', timeout=3000)
            assert len(await pg.query_selector_all('.dd-facts tbody tr'))==5
            assert 'Level 1' in await pg.inner_text('.dd-crumbs')
            await pg.click('.dd-up')
            assert (await pg.inner_text('.dd-title')).startswith('Multi-tenant')
        await b.close()
asyncio.run(m(sys.argv[1]))
PY"

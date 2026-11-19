import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=b.new_page(viewport={'width':1100,'height':900})
    pg.goto('file://'+sys.argv[1]+'#reconciliation'); pg.wait_for_timeout(800)
    over=pg.evaluate("""()=>[...document.querySelectorAll('svg g.q')].map(g=>{const r=g.querySelector('rect').getBBox();return [...g.querySelectorAll('text')].map(t=>t.getBBox().width>r.width-8?t.textContent:null).filter(Boolean)}).flat()""")
    print('overflow:',over); pg.screenshot(path='/tmp/rec.png',full_page=True); b.close()

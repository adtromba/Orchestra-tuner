import os
HERE=os.path.dirname(os.path.abspath(__file__))
INDEX=os.path.join(os.path.dirname(HERE),'index.html')
TEST=os.path.join(HERE,'_test.html')   # temp copy with test hooks, git-ignored
import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    errs=[]
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    for (w,h,tag) in ((1180,820,'land'),(820,1180,'port'),(390,844,'phone')):
        pg=b.new_page(viewport={'width':w,'height':h}); pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+INDEX+'')
        print(tag,'goals:',pg.eval_on_selector_all('.goal','els=>els.filter(e=>e.offsetParent).map(e=>e.querySelector(".gt").firstChild.textContent)'))
        pg.click('.goal[data-g=practice]'); pg.click('#modePick button[data-v=scale]')
        pg.evaluate("window.scrollTo(0,0)")
        # give the report something to show
        pg.screenshot(path=f'/tmp/x_{tag}.png')
        L=pg.evaluate("(()=>{const a=document.querySelector('#meter').getBoundingClientRect(), r=document.querySelector('#scaleCard').getBoundingClientRect(); return [Math.round(a.left),Math.round(a.right),Math.round(r.left),Math.round(r.right)]})()")
        print('   meter x-range', L[:2], '| scale report x-range', L[2:], '| side by side:', L[1] <= L[2])
        pg.click('#backBtn'); pg.click('.goal[data-g=check]'); pg.click('#modePick button[data-v=notes]')
        print('   notes mode: meter width', pg.evaluate("Math.round(document.querySelector('#meter').getBoundingClientRect().width)"), '| overflow', pg.evaluate('document.documentElement.scrollWidth>window.innerWidth'))
        pg.close()
    print('ERRORS',errs); b.close()

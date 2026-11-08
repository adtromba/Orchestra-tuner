import os
HERE=os.path.dirname(os.path.abspath(__file__))
INDEX=os.path.join(os.path.dirname(HERE),'index.html')
TEST=os.path.join(HERE,'_test.html')   # temp copy with test hooks, git-ignored
from playwright.sync_api import sync_playwright
src=open(INDEX,encoding='utf-8').read()
i=src.rindex('})();')
src=src[:i]+"window.__t={feed:function(f,ts){climbFeed(f,ts)},step:function(){return guide.i},hold:function(){return climb.hold},base:baseFreq};\n"+src[i:]
open(TEST,'w',encoding='utf-8').write(src)
init="navigator.mediaDevices.getUserMedia=()=>{const c=new AudioContext();return Promise.resolve(c.createMediaStreamDestination().stream)};window.__o=0;const oc=AudioContext.prototype.createOscillator;AudioContext.prototype.createOscillator=function(){const o=oc.call(this);const st=o.start.bind(o);o.start=function(t){if(o.type==='sine')window.__o++;return st(t)};return o};"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.add_init_script(init)
    pg.goto('file://'+TEST+'')
    pg.click('#tabSeg button[data-v=tuner]'); pg.click('#modeSeg button[data-v=climb]'); pg.click('#go'); pg.wait_for_timeout(4600)
    f=pg.evaluate('__t.base()'); base=pg.evaluate('__o')
    run="([f,c,n,t0])=>{let t=t0;for(let k=0;k<n;k++){__t.feed(f*Math.pow(2,c/1200),t);t+=33}}"
    pg.evaluate(run,[f,8,60,1000]);print('8c off 2s: hold',pg.evaluate('__t.hold()'),'pings',pg.evaluate('__o')-base)
    pg.evaluate(run,[f,3,90,5000]);print('3c 3s: hold',pg.evaluate('__t.hold()'),'step',pg.evaluate('__t.step()'),'pings',pg.evaluate('__o')-base)
    pg.evaluate(run,[f,3,30,9000]);pg.wait_for_timeout(300);print('after 4s: step',pg.evaluate('__t.step()'),'pings',pg.evaluate('__o')-base)
    print(errs); b.close()

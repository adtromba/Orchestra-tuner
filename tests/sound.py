# Synthetic-tone checks for sound.html (Centered / Aim higher / Aim lower) and layout at 390 and 320 px.
import os, json
HERE=os.path.dirname(os.path.abspath(__file__))
PAGE='file://'+os.path.join(os.path.dirname(HERE),'sound.html')
JS = """
(args)=>{
  const sr=48000,N=window.__sound.WINDOW,f=window.__sound.TARGET_HZ*(args.cents?Math.pow(2,args.cents/1200):1);
  let seed=12345; const rnd=()=>{seed=(seed*1664525+1013904223)>>>0; return seed/4294967296;};
  const gauss=()=>Math.sqrt(-2*Math.log(rnd()+1e-12))*Math.cos(2*Math.PI*rnd());
  const x=new Float32Array(N);
  for(let k=1;k<=args.amps.length;k++){const a=args.amps[k-1]; for(let i=0;i<N;i++) x[i]+=a*Math.sin(2*Math.PI*k*f*i/sr);}
  if(args.noise) for(let i=0;i<N;i++) x[i]+=args.noise*gauss();
  const r=window.__sound.analyze(x,sr,440);
  return {r, v: (r&&!r.quiet)?window.__sound.verdictOf(r):null};
}
"""
cases=[
 ('strong fundamental, little noise','Centered',dict(amps=[0.3,0.04,0.05,0.03,0.02,0.015,0.01],noise=0.0005)),
 ('boosted 2nd harmonic','Aim higher',dict(amps=[0.15,0.3,0.1,0.05,0.03,0.02,0.01],noise=0.0005)),
 ('weak fundamental + broadband noise','Aim lower',dict(amps=[0.03,0.002,0.06,0.05,0.04,0.03],noise=0.02)),
]
from playwright.sync_api import sync_playwright
bad=0
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    errs=[]
    pg=b.new_page(viewport={'width':390,'height':844}); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(PAGE)
    for name,want,a in cases:
        o=pg.evaluate(JS,a); r=o['r']
        ok=o['v']==want; bad+=not ok
        print('PASS' if ok else 'FAIL',name,'->',o['v'],'(want',want+')', {k:round(v,1) for k,v in r.items() if isinstance(v,(int,float))} if r else r)
    for w in (390,320):
        pg2=b.new_page(viewport={'width':w,'height':844}); pg2.goto(PAGE)
        pg2.evaluate("document.querySelector('details').open=true")
        over=pg2.evaluate("document.documentElement.scrollWidth>window.innerWidth")
        print('layout',w,'overflow:',over); bad+=over
        pg2.screenshot(path=f'/tmp/sound_{w}.png',full_page=True); pg2.close()
    print('ERRORS',errs); bad+=len(errs); b.close()
raise SystemExit(1 if bad else 0)

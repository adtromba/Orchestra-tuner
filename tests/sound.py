# Checks for sound.html v2: pitch peak/FUND_SHARE ordering, calibration judging, word hysteresis, full calibration flow, layout.
import os
HERE=os.path.dirname(os.path.abspath(__file__))
PAGE='file://'+os.path.join(os.path.dirname(HERE),'sound.html')
SETUP = """
window.T = (()=>{
  const sr=48000,N=window.__sound.WINDOW,f0=window.__sound.TARGET_HZ;
  let seed=777; const rnd=()=>{seed=(seed*1664525+1013904223)>>>0; return seed/4294967296;};
  const gauss=()=>Math.sqrt(-2*Math.log(rnd()+1e-12))*Math.cos(2*Math.PI*rnd());
  const tone=(amps,noise=0.0005)=>{const x=new Float32Array(N); for(let k=1;k<=amps.length;k++){const a=amps[k-1]; for(let i=0;i<N;i++) x[i]+=a*Math.sin(2*Math.PI*k*f0*i/sr);} for(let i=0;i<N;i++) x[i]+=noise*gauss(); return x;};
  return {sr,tone,
    silence: tone([],0.0005),
    pinched: tone([0.3,0.05,0.03,0.02]),
    flat:    tone([0.03,0.05,0.25,0.2,0.1,0.05]),
    mid:     tone([0.07,0.1,0.15,0.1,0.05]),
    veryPinched: tone([0.2,0.05,0.05,0.03,0.02]),
    near:    tone([0.12,0.1,0.15,0.1,0.05]),
    lowOctaveStrong: tone([0.03,0.05,0.25,0.2,0.1,0.05])};
})();
"""
FLOW = """
(args)=>{
  const S=window.__sound,T=window.T; let now=1000; S.testStart(now);
  const pick={silent:T.silence,pinched:T.pinched,flat:T[args.flat||'flat'],centered:T[args.mid]};
  for(let i=0;i<args.maxTicks;i++){
    const st=S.state(); if(st.phase!=='cal') break;
    S.process(pick[st.step]||T.silence,T.sr,now); now+=100;
  }
  return {st:S.state(), now};
}
"""
from playwright.sync_api import sync_playwright
bad=0
def check(name,ok,info=''):
    global bad; bad+=(not ok); print('PASS' if ok else 'FAIL',name,info)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    errs=[]
    pg=b.new_page(viewport={'width':390,'height':844}); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(PAGE); pg.evaluate(SETUP)
    # 1. tones: fundamental share and f0 (never 698)
    R=pg.evaluate("()=>{const S=window.__sound,T=window.T,o={}; for(const k of ['pinched','mid','flat']) o[k]=S.analyze(T[k],T.sr,440); return o;}")
    for k in ('pinched','mid','flat'):
        r=R[k]; check(f'{k}: f0 near 349',r['ok'] and abs(r['f0']-349.23)<1.5,{x:round(v,1) for x,v in r.items() if isinstance(v,(int,float))})
    check('fund-heavy > mid > weak-fundamental',R['pinched']['fund']>R['mid']['fund']>R['flat']['fund'],[round(R[k]['fund'],1) for k in ('pinched','mid','flat')])
    P,F=R['pinched']['fund'],R['flat']['fund']
    check('fund-heavy lands right of centre',(R['pinched']['fund']-F)/(P-F)>0.83); check('weak-fundamental lands left',(R['flat']['fund']-F)/(P-F)<0.17)
    # 2. calibration judging
    J=pg.evaluate("()=>{const S=window.__sound; return {mid:S.centerCheck(-2,-19,-10), hi:S.centerCheck(-2,-19,-4.5), lo:S.centerCheck(-2,-19,-17), span:S.spanTooSmall(-2,-9), spanOk:S.spanTooSmall(-2,-19)}}")
    check('mid C accepted',J['mid']['status']=='ok',J['mid']); check('C at pos 0.85 flagged pinched',J['hi']['status']=='pinched',J['hi']); check('C low flagged flat',J['lo']['status']=='flat')
    check('span under 8 dB rejected',J['span'] is True and J['spanOk'] is False)
    # 3. word hysteresis
    H=pg.evaluate("""()=>{const S=window.__sound,w=S.newWord(); let t=0,log=[];
      for(;t<=2000;t+=100) S.wordStep(w,'centered',t); log.push(w.shown);          // settles on centered
      for(;t<=2500;t+=100) S.wordStep(w,'flat',t); log.push(w.shown);              // 0.5 s blip: no change
      for(;t<=3500;t+=100) S.wordStep(w,'centered',t); log.push(w.shown);
      for(;t<=5000;t+=100) S.wordStep(w,'pinched',t); log.push(w.shown);           // 1.5 s: changes
      return log;}""")
    check('word hysteresis',H==['centered','centered','centered','pinched'],H)
    # 4. full flow with synthetic audio
    o=pg.evaluate(FLOW,{'mid':'mid','maxTicks':600}); st=o['st']
    check('calibration accepts a mid C',st['phase']=='practice' and 0.3<=st['center']<=0.7,st)
    o2=pg.evaluate("""(now)=>{const S=window.__sound,T=window.T,w=[]; let t=now+500;
      for(let i=0;i<30;i++){S.process(T.mid,T.sr,t); t+=100;} w.push(S.state().word);
      for(let i=0;i<5;i++){S.process(T.pinched,T.sr,t); t+=100;} w.push(S.state().word);   // 0.5 s blip
      for(let i=0;i<5;i++){S.process(T.mid,T.sr,t); t+=100;}
      for(let i=0;i<16;i++){S.process(T.pinched,T.sr,t); t+=100;} w.push(S.state().word);
      for(let i=0;i<16;i++){S.process(T.flat,T.sr,t); t+=100;} w.push(S.state().word);
      return w;}""",o['now'])
    check('practice: Centered, blip ignored, then pinched, then flat',o2==['centered','centered','pinched','flat'],o2)
    pg.evaluate("document.getElementById('tbl')"); pg.screenshot(path='/tmp/sound_practice.png')
    o=pg.evaluate(FLOW,{'mid':'veryPinched','maxTicks':600}); st=o['st']
    check('centered at pos >0.7 is flagged',st['step']=='leansPinched',st)
    o=pg.evaluate(FLOW,{'mid':'mid','flat':'near','maxTicks':600}); st=o['st']
    check('pinched/flat span too small rejected',st['step']=='span',st)
    # 5. layout
    for w in (390,320):
        for view in ('cal','practice'):
            pg2=b.new_page(viewport={'width':w,'height':844}); pg2.goto(PAGE)
            if view=='practice': pg2.evaluate("window.__sound.demo(0.9)")
            pg2.evaluate("document.querySelector('details').open=true")
            over=pg2.evaluate("document.documentElement.scrollWidth>window.innerWidth"); check(f'layout {w} {view} no overflow',not over)
            pg2.screenshot(path=f'/tmp/sound_{w}_{view}.png',full_page=True); pg2.close()
    check('no page errors',not errs,errs); b.close()
raise SystemExit(1 if bad else 0)

#!/usr/bin/env python3
"""HE part 1 test suite (headless Chromium via playwright).
Usage: python3 he_p1_test.py <baseline aria_v31.html> <aria_v32_p1.html>
Layers run: L3 in-page harness (rAF stubbed, Math.random seeded + counted, update()/draw0() driven by hand).
The dummy enemies are registered ONLY from this script at run time; nothing of them lives in the game file."""
import sys, os, json
from playwright.sync_api import sync_playwright

BASE, NEW = [os.path.abspath(p) for p in sys.argv[1:3]]
FAIL = []; PASS = [0]

def check(name, cond, detail=''):
    if cond: PASS[0] += 1; print('  ok  ', name)
    else: FAIL.append(name); print('  FAIL', name, detail)

INIT = r"""
(()=>{
  let s=(%SEED%)>>>0,n=0;
  Math.random=()=>{s=(s+0x6D2B79F5)|0;let t=Math.imul(s^(s>>>15),1|s);t=(t+Math.imul(t^(t>>>7),61|t))^t;n++;return((t^(t>>>14))>>>0)/4294967296};
  Object.defineProperty(window,'__rc',{get:()=>n});
  window.requestAnimationFrame=()=>0;
  window.__errs=[];window.__warns=[];
  window.addEventListener('error',e=>window.__errs.push(String(e.message)));
  const cw=console.warn;console.warn=(...a)=>{window.__warns.push(a.map(String).join(' '))};
})();
"""
DRIVER = r"""
window.__c={init:0,ai:0,draw:0,dmg:0,contact:0,kill:0,reset:0,step:0,dB:0,dF:0,dP:0,pj:0,bl:0,minD:1e9,spawns:[],ddraw:0};
window.__reg=(t,o)=>{HEX[t]=Object.assign({name:'Dummy'+t,w:30,h:30,unlock:1,max:1,weight:1,place:'air',hp:()=>3,
  init(e){__c.init++;const d=Math.hypot(e.x+e.w/2-(pl.x+16),e.y+e.h/2-(pl.y+21));__c.minD=Math.min(__c.minD,d);__c.spawns.push([tick,e.t,Math.round(e.x),Math.round(e.y)])},
  ai(e){__c.ai++},
  draw(e){__c.draw++;if(e.dd)__c.ddraw++;c.fillStyle=e.fl>0?'#fff':'#0f0';c.fillRect(e.x,e.y,e.w,e.h)},
  dmg(e,d){__c.dmg++;return d>=2?d:0},
  contact(e,px,py,bot){__c.contact++;return false},
  onKill(e){__c.kill++}},o||{})};
window.__start=(d,n)=>{mute=1;beginAt(d,n);maxhp=hp=99999;pl.inv=0};
window.DRAWN=300;   /* draw0 costs ~0.7 s per frame in this software-rendered sandbox, so frames are drawn sparsely */
window.__drive=(ticks,draw)=>{
  const out={log:[],mx:0,mxT:{}};const seen=new Set();
  for(let i=0;i<ticks;i++){
    const ph=i%240;K['@r']=ph<70;K['@l']=ph>=120&&ph<190;K['@j']=(i%97)<6;K['@f']=(i%31)<4;
    update();
    if(draw&&i%DRAWN==0){RA=.5;ipOn();draw0()}
    let h=0;const ht={};
    for(const e of E){if(!seen.has(e)){seen.add(e);out.log.push([tick,e.t,Math.round(e.x*100),Math.round(e.y*100)])}
      if(e.a&&e.t>=6){h++;ht[e.t]=(ht[e.t]||0)+1}}
    out.mx=Math.max(out.mx,h);for(const k in ht)out.mxT[k]=Math.max(out.mxT[k]||0,ht[k]);
  }
  K['@r']=K['@l']=K['@j']=K['@f']=0;
  out.state={tick,st,score,hp,px:+pl.x.toFixed(3),py:+pl.y.toFixed(3),stage,rc:__rc,nE:E.length,pj:pj.length,bl:bl.length,S:S.length,
    E:E.map(e=>[e.t,+e.x.toFixed(2),+e.y.toFixed(2),e.hp,e.a])};
  return out;
};
"""

def new_page(br, path, seed=1, query=''):
    ctx = br.new_context(viewport={'width': 1000, 'height': 600})
    pg = ctx.new_page()
    pg.add_init_script(INIT.replace('%SEED%', str(seed)))
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'WebGL' not in m.text and 'GPU' not in m.text else None)
    pg.goto('file://' + path + query)
    pg.wait_for_timeout(150)
    pg.evaluate(DRIVER)
    pg._errs = errs
    return pg

def run(br, path, d, n, ticks, seed, pre=None, draw=False):
    pg = new_page(br, path, seed)
    pg.evaluate('([d,n])=>__start(d,n)', [d, n])
    if pre: pg.evaluate(pre)
    out = pg.evaluate('([t,dr])=>__drive(t,dr)', [ticks, draw])
    out['errs'] = pg._errs + pg.evaluate('__errs'); pg.context.close()
    return out

with sync_playwright() as p:
    br = p.chromium.launch()

    # ------------------------------------------------------------------ (a) parity vs v31
    print('\n[a] parity v31 vs p1 (seeded Math.random, 3000 ticks, scripted input, update() only)')
    for d in (() if os.environ.get('SKIPA') else (0, 1, 2)):
        for n in (1, 3, 6, 8, 12):
            seed = 101 + d * 17 + n
            a = run(br, BASE, d, n, 3000, seed); b = run(br, NEW, d, n, 3000, seed)
            nm = 'dif%d stage%d' % (d, n)
            check(nm + ': spawn sequence (tick,type,x,y) identical (%d spawns)' % len(a['log']), a['log'] == b['log'] and len(a['log']) > 0)
            check(nm + ': final state + Math.random count identical', a['state'] == b['state'], '%s vs %s' % (a['state']['rc'], b['state']['rc']))
            check(nm + ': no page errors', not a['errs'] and not b['errs'], (a['errs'][:1], b['errs'][:1]))
    print('\n[a2] Easy/Normal with dummies REGISTERED (HE must stay completely inert)')
    for d in (() if os.environ.get('SKIPA') else (0, 1)):
        seed = 777 + d
        pre = "__reg(6,{unlock:1,max:3});__reg(7,{unlock:1,place:'ceiling'});HE.share=1"
        a = run(br, BASE, d, 6, 3000, seed); b = run(br, NEW, d, 6, 3000, seed, pre)
        check('dif%d: identical to v31 with dummies registered' % d, a['log'] == b['log'] and a['state'] == b['state'])
    a = run(br, BASE, 2, 2, 3000, 4242)
    b = run(br, NEW, 2, 2, 3000, 4242, "__reg(6,{unlock:3});HE.share=1")
    check('Hard stage2 (below every unlock): identical to v31 (no randomness consumed)', a['log'] == b['log'] and a['state'] == b['state'])

    # ------------------------------------------------------------------ (b) dummy registry behaviour on Hard
    print('\n[b] dummies on Hard')
    # b1/b2 unlock + max + total cap + minDist for every placement kind
    pre = """HE.share=1;
      __reg(6,{unlock:3,max:2,place:'air'});__reg(7,{unlock:9,max:2,place:'ceiling'});
      __reg(8,{unlock:1,max:2,place:'platform'});
      let k=0;__reg(9,{unlock:1,max:1,place:e=>{if(++k<4)return false;e.x=pl.x+400;e.y=100;return true}});"""
    o = run(br, NEW, 2, 3, 3000, 55, pre, True)
    types = sorted(set(x[1] for x in o['log'] if x[1] >= 6))
    check('stage3: only unlocked types appear (6,8,9; never 7)', 7 not in types and set(types) <= {6, 8, 9} and len(types) > 0, types)
    check('stage3: total alive HE <= HE.maxNew (2)', o['mx'] <= 2 and o['mx'] == 2, o['mx'])
    check('stage3: per-type max respected (t6,t8 <=2, t9 <=1)', o['mxT'].get('6', 0) <= 2 and o['mxT'].get('8', 0) <= 2 and o['mxT'].get('9', 0) <= 1, o['mxT'])
    check('stage3: no page errors', not o['errs'], o['errs'][:2])
    pg = new_page(br, NEW, 56); pg.evaluate('__start(2,12)')
    pg.evaluate("HE.share=1;__reg(6,{max:3});__reg(7,{max:3,place:'ceiling'});__reg(8,{max:3,place:'platform'});__reg(9,{max:3})")
    o = pg.evaluate('__drive(3000,true)')
    check('stage12 (>= lateStage): total alive HE cap is maxNewLate (3)', o['mx'] == 3, o['mx'])
    check('stage12: no page errors', not (pg._errs + pg.evaluate('__errs')))
    pg.context.close()
    pg = new_page(br, NEW, 57); pg.evaluate('__start(2,8)')
    pg.evaluate("HE.share=1;HE.maxNew=9;__reg(6,{max:9,place:'air'});__reg(7,{max:9,place:'ceiling'});__reg(8,{max:9,place:'platform'});__reg(9,{max:9,place:e=>{e.x=pl.x+20;e.y=pl.y;return true}})")
    o = pg.evaluate('__drive(3500,true)')
    c_ = pg.evaluate('__c')
    check('minDist: every created HE enemy (air/ceiling/platform) starts >= 220px from the player (min %.1f)' % c_['minD'], c_['minD'] >= 220 and c_['init'] > 3, c_['minD'])
    check('place function violating minDist: gives up silently (t9 never created), no errors', 9 not in set(x[1] for x in o['log']) and not pg._errs and not pg.evaluate('__errs'))
    check('platform walkers carry e.p and stand on it', pg.evaluate("E.filter(e=>e.t==8&&e.a).every(e=>e.p&&Math.abs(e.y-(e.p.y-e.h))<1e-6)"))
    pg.context.close()

    # b4 hooks: ai/draw/dmg/contact/onKill/step/draw hooks/pjHit/blHit/reset/quiet/score
    pg = new_page(br, NEW, 60); pg.evaluate('__start(2,6)')
    pg.evaluate("HE.share=1;__reg(6,{max:2});__reg(8,{max:1,place:'platform',quiet:true});__reg(7,{unlock:99})")
    pg.evaluate("HEH.step.push(()=>__c.step++);HEH.drawBack.push(()=>__c.dB++);HEH.drawFront.push(()=>__c.dF++);HEH.drawPlayer.push((x,y)=>{__c.dP++;__c.ppBad=(__c.ppBad||0)+((x==pl.x+16&&y==pl.y+21)?0:1)});HEH.reset.push(()=>__c.reset++)")
    t0 = pg.evaluate('tick'); o = pg.evaluate('__drive(1500,true)'); c_ = pg.evaluate('__c'); dt = pg.evaluate('tick') - t0
    check('ai/contact run every tick for live HE enemies', c_['ai'] > 100 and c_['contact'] > 100, (c_['ai'], c_['contact']))
    check('painter runs (dE2 dispatch)', c_['draw'] >= 5, c_['draw'])
    check('HEH.step: exactly once per play tick (%d ticks)' % dt, c_['step'] == dt and dt > 1400, (c_['step'], dt))
    check('drawBack/drawFront/drawPlayer called once per drawn frame (5)', c_['dB'] == 5 and c_['dF'] == 5 and c_['dP'] == 5, (c_['dB'], c_['dF'], c_['dP']))
    check('drawPlayer receives the player centre (x+16,y+21) every frame', pg.evaluate('__c.dP>0&&!__c.ppBad'))
    check('quiet type: no hint pop-up registered; loud type: hint registered once', pg.evaluate('heSeen.has(6)&&!heSeen.has(8)'))
    e = pg.evaluate("(()=>{const e=E.find(q=>q.a&&q.t==6);return e?[e.hp,e.id]:null})()")
    check('an alive t6 exists for the damage test', e is not None)
    r = pg.evaluate("""(()=>{const e=E.find(q=>q.a&&q.t==6);e.fl=0;const d0=__c.dmg;hitE(e,1);const h1=e.hp,alive1=e.a;hitE(e,2);const h2=e.hp;
      const k0=__c.kill;cb=0;const n0=pt.length;hitE(e,5);const pp=pt.slice(n0).filter(p=>p.s&&p.s[0]=='+').map(p=>p.s);
      return {dm:__c.dmg-d0,h1,alive1,h2,dead:!e.a,kill:__c.kill-k0,pop:pp,sc:Math.round(420*D.sc)}})()""")
    check('dmg hook: returning 0 = immune (hp unchanged), >0 applied', r['dm'] == 3 and r['h1'] == 3 and r['alive1'] == 1 and r['h2'] == 1, r)
    check('kill(): onKill called once, t6 score = 420 (pop "+%d")' % r['sc'], r['dead'] and r['kill'] == 1 and ('+%d' % r['sc']) in r['pop'], r)
    sc = pg.evaluate("""(()=>{const o={};for(const t of [6,7,8,9,10]){HEX[t]=HEX[t]||{name:'x',w:20,h:20,hp:()=>1,draw(){}};cb=0;const n0=pt.length;
      kill({t,x:100,y:100,w:20,h:20,a:1,hp:0,dz:0});o[t]=pt.slice(n0).filter(p=>p.s&&p.s[0]=='+').map(p=>p.s)[0]}return o})()""")
    exp = {t: '+%d' % round(v * 1.6) for t, v in zip([6, 7, 8, 9, 10], [420, 520, 380, 600, 450])}
    check('kill() score table for t6..t10 = 420/520/380/600/450 (Hard sc 1.6)', {int(k): v for k, v in sc.items()} == exp, sc)
    # pjHit / blHit
    r = pg.evaluate("""(()=>{pl.inv=0;iv=0;au=0;const o={};
      HEH.pjHit.web=(q,i,px,py)=>{__c.pj++;pj.splice(i,1);return true};
      HEH.pjHit.keep=(q,i)=>{__c.pj+=10;return true};
      HEH.pjHit.pass=(q,i)=>false;
      const mk=k=>({x:pl.x+16,y:pl.y+21,vx:0,vy:0,r:9,c:'#fff',k});
      let h0=hp;hs=0;pj=[mk('web')];update();o.web=[hp==h0,pj.length,__c.pj];
      h0=hp;hs=0;pj=[mk('keep')];pl.inv=0;update();o.keep=[hp==h0,pj.length,__c.pj];
      h0=hp;hs=0;pj=[mk('pass')];pl.inv=0;update();o.pass=[hp<h0];
      pj=[];
      HEH.blHit.push((b,i)=>{__c.bl++;return b.k=='eat'});
      bl=[{x:60,y:60,vx:0,vy:0,l:80,h:[],hm:false,k:'eat'},{x:62,y:61,vx:0,vy:0,l:80,h:[],hm:false,k:'keep'}];hs=0;update();o.bl=[bl.length,bl[0]&&bl[0].k,__c.bl];
      return o})()""")
    check('pjHit true: generic hurt skipped, handler removes its projectile', r['web'] == [True, 0, 1], r['web'])
    check('pjHit true without removal: projectile survives, no hurt', r['keep'][0] and r['keep'][1] == 1, r['keep'])
    check('pjHit false: falls through to the generic hit test (hurt)', r['pass'] == [True], r['pass'])
    check('blHit true consumes the star, false keeps it', r['bl'][0] == 1 and r['bl'][1] == 'keep', r['bl'])
    # reset hooks
    r0 = pg.evaluate('__c.reset')
    pg.evaluate('retry()'); r1 = pg.evaluate('__c.reset')
    pg.evaluate('restartStage()'); r2 = pg.evaluate('__c.reset')
    pg.evaluate('st="play";need=0;clearStage()'); r3 = pg.evaluate('__c.reset')
    pg.evaluate('load(6)'); r4 = pg.evaluate('__c.reset')
    check('HEH.reset: retry, restartStage, clearStage, load(n) each call it once', (r1 - r0, r2 - r1, r3 - r2, r4 - r3) == (1, 1, 1, 1), (r0, r1, r2, r3, r4))
    # drawing hooks are state-safe
    r = pg.evaluate("""(()=>{HEH.drawBack.push(()=>{c.globalAlpha=.1;c.translate(50,50);c.shadowBlur=30});const a0=c.getTransform().e;heDrawH(HEH.drawBack);return [c.globalAlpha,c.getTransform().e-a0,c.shadowBlur]})()""")
    check('draw hooks are wrapped in save/restore (alpha, transform, shadow restored)', r == [1, 0, 0], r)
    check('no page errors (hooks section)', not (pg._errs + pg.evaluate('__errs')), (pg._errs + pg.evaluate('__errs'))[:2])
    pg.context.close()

    # step hook is Hard-only
    pg = new_page(br, NEW, 61); pg.evaluate('__start(1,3)'); pg.evaluate("HEH.step.push(()=>__c.step++);HEH.reset.push(()=>__c.reset++)")
    pg.evaluate('__drive(300,false)')
    check('Normal: HEH.step is never called', pg.evaluate('__c.step') == 0)
    pg.context.close()

    # quiet = no pop-in scale / aura / hint ; loud = pop-in scale starts at 0
    pg = new_page(br, NEW, 62); pg.evaluate('__start(2,6)')
    pg.evaluate("__reg(6,{place:'air'});__reg(8,{quiet:true,place:'air'});window.__sc=[];const o=c.scale.bind(c);c.scale=(a,b)=>{__sc.push(a);o(a,b)};0")
    pg.evaluate("""window.__mk=(t)=>{const r=HEX[t];const e={t,w:r.w,h:r.h,hp:3,a:1,fl:0,d:1,cd:80,id:1,born:tick,mn:100,tp:0,sp:1,st:0,tm:0,x:700,y:200};E.push(e);return e};0""")
    pg.evaluate("__sc.length=0;__mk(6);RA=0;ipOn();draw0()"); loud = pg.evaluate('__sc.some(v=>Math.abs(v)<1e-9)')
    pg.evaluate("E=[];__sc.length=0;__mk(8);RA=0;ipOn();draw0()"); quiet = pg.evaluate('__sc.some(v=>Math.abs(v)<1e-9)')
    check('non-quiet HE enemy gets the pop-in scale (starts at 0), quiet one does not', loud and not quiet, (loud, quiet))
    check('no page errors (quiet section)', not (pg._errs + pg.evaluate('__errs')))
    pg.context.close()

    # death dissolve uses a full snapshot of the entity
    pg = new_page(br, NEW, 63); pg.evaluate('__start(2,6)')
    pg.evaluate("__reg(6,{place:'air'});HE.share=1")
    pg.evaluate("__drive(400,true)")
    r = pg.evaluate("""(()=>{const e=E.find(q=>q.a&&q.t==6);if(!e)return null;e.st='custom';e.tm=77;e.zz=5;K['@r']=0;const d0=__c.ddraw;hitE(e,9);
      for(let i=0;i<7;i++){update();update();update();RA=.5;ipOn();draw0()}return {dd:__c.ddraw-d0,g:enG.length}})()""")
    check('death dissolve: painter called with the dd flag (snapshot path) and no errors', r is not None and r['dd'] > 0 and not (pg._errs + pg.evaluate('__errs')), r)
    r = pg.evaluate("""(()=>{enG.length=0;enM.clear();HEX[6].draw=function(e){__c.snap=[e.st,e.tm,e.zz,e.dd]};const e={t:6,x:300,y:300,w:30,h:30,hp:3,a:1,fl:0,d:1,cd:0,id:1,born:-99,st:'custom',tm:77,zz:5};E=[e];st='play';enP=1;enS=stage;RA=0;ipOn();draw0();e.a=0;enM;draw0();return __c.snap})()""")
    check('snapshot carries custom fields (st,tm,zz) + dd=1', r == ['custom', 77, 5, 1], r)
    pg.context.close()

    # ------------------------------------------------------------------ (c) heFail paths
    print('\n[c] exceptions inside HE code -> heFail (HE_ON=0, HE enemies removed, game goes on)')
    TH = "(()=>{throw new Error('boom')})()"
    cases = {
        'ai': ("__reg(6,{ai(e){if(__c.ai++>5)throw new Error('boom')}})", None),
        'draw': ("__reg(6,{draw(e){throw new Error('boom')}})", None),
        'contact': ("__reg(6,{contact(){throw new Error('boom')}})", None),
        'dmg': ("__reg(6,{dmg(){throw new Error('boom')}})", "(()=>{const e=E.find(q=>q.a&&q.t==6);hitE(e,3)})()"),
        'onKill': ("__reg(6,{onKill(){throw new Error('boom')}})", "(()=>{const e=E.find(q=>q.a&&q.t==6);hitE(e,9)})()"),
        'dazed': ("__reg(6,{dazed(){throw new Error('boom')}})", "(()=>{const e=E.find(q=>q.a&&q.t==6);e.z=50})()"),
        'init': ("__reg(6,{init(){throw new Error('boom')}})", None),
        'hp': ("__reg(6,{hp(){throw new Error('boom')}})", None),
        'place': ("__reg(6,{place(){throw new Error('boom')}})", None),
        'step hook': ("__reg(6,{});HEH.step.push(()=>{throw new Error('boom')})", None),
        'drawBack hook': ("__reg(6,{});HEH.drawBack.push(()=>{throw new Error('boom')})", None),
        'drawPlayer hook': ("__reg(6,{});HEH.drawPlayer.push(()=>{throw new Error('boom')})", None),
        'reset hook': ("__reg(6,{});HEH.reset.push(()=>{throw new Error('boom')})", "load(6)"),
        'pjHit': ("__reg(6,{});HEH.pjHit.web=()=>{throw new Error('boom')}", "(()=>{pl.inv=0;pj.push({x:pl.x+16,y:pl.y+21,vx:0,vy:0,r:9,c:'#fff',k:'web'})})()"),
        'blHit': ("__reg(6,{});HEH.blHit.push(()=>{throw new Error('boom')})", "bl.push({x:60,y:60,vx:0,vy:0,l:80,h:[],hm:false})"),
    }
    for nm, (reg, trig) in cases.items():
        pg = new_page(br, NEW, 70); pg.evaluate('__start(2,6)'); pg.evaluate('HE.share=1;' + reg + ';0')
        if trig and nm in ('dmg', 'onKill', 'dazed'):
            pg.evaluate('__drive(400,false)')
            pg.evaluate(trig)
        elif trig:
            pg.evaluate('__drive(5,false)'); pg.evaluate(trig)
        o = pg.evaluate('__drive(900,true)')
        er = pg._errs + pg.evaluate('__errs')
        ok = pg.evaluate("HE_ON===0&&!E.some(e=>e.a&&HEX[e.t])&&!pj.some(q=>q.k=='web')")
        w = pg.evaluate('__warns.filter(x=>x.includes("HE")).length')
        legacy = o['state']['tick'] > 0
        check('%-15s -> HE_ON=0, HE enemies/projectiles gone, 1 warning, game keeps running, no page errors' % nm, ok and w == 1 and legacy and not er, (ok, w, er[:2]))
        pg.context.close()
    pg = new_page(br, NEW, 71); pg.evaluate('__start(2,6)'); pg.evaluate("HE.share=1;__reg(6,{ai(e){if(__c.ai++>5)throw new Error('boom')}})")
    pg.evaluate('__drive(1200,false)')
    check('after heFail the legacy spawner keeps spawning (E gets legacy types)', pg.evaluate('E.some(e=>e.t<6)') and not pg.evaluate('heOn()') and pg.evaluate('HE_ON')==0)
    pg.context.close()

    # ------------------------------------------------------------------ (d) boss / final stages
    print('\n[d] boss stages spawn no HE enemies; normal late stages do')
    for n in (5, 10, 14):
        pg = new_page(br, NEW, 80 + n); pg.evaluate('__start(2,%d)' % n)
        pg.evaluate("HE.share=1;__reg(6,{max:3});__reg(7,{max:3,place:'ceiling'})")
        o = pg.evaluate('__drive(1800,true)')
        check('stage %d (boss): no HE enemy ever created' % n, not [x for x in o['log'] if x[1] >= 6] and not (pg._errs + pg.evaluate('__errs')), (pg._errs + pg.evaluate('__errs'))[:2])
        pg.context.close()
    for n in (11, 13):
        pg = new_page(br, NEW, 90 + n); pg.evaluate('__start(2,%d)' % n)
        pg.evaluate("HE.share=1;__reg(6,{max:3});__reg(7,{max:3,place:'ceiling'})")
        o = pg.evaluate('__drive(1800,true)')
        check('stage %d: HE enemies do appear' % n, any(x[1] >= 6 for x in o['log']) and not (pg._errs + pg.evaluate('__errs')))
        pg.context.close()

    # ------------------------------------------------------------------ (e) debug hooks
    print('\n[e] debug')
    pg = new_page(br, NEW, 95, '?hedebug'); pg.evaluate('__reg(6,{unlock:99})')
    check('?hedebug exposes __heSpawn/__heHard', pg.evaluate("typeof __heSpawn=='function'&&typeof __heHard=='function'"))
    pg.evaluate('__heHard()'); pg.evaluate('beginAt(0,3)')
    r = pg.evaluate("(()=>{const e=__heSpawn(6,500,300);return [!!e,E.includes(e),dif]})()")
    check('__heSpawn ignores gates (unlock 99, Easy) and pushes into E', r[0] and r[1] and r[2] == 0, r)
    pg.evaluate('__drive(300,true)')
    check('debug-spawned enemy runs without errors', not (pg._errs + pg.evaluate('__errs')))
    pg.context.close()
    pg = new_page(br, NEW, 96)
    check('without ?hedebug no debug globals', pg.evaluate("typeof __heSpawn=='undefined'&&typeof __heHard=='undefined'"))
    check('fresh load: HE_ON=1, HEX empty, HEH shape, tunables', pg.evaluate("HE_ON===1&&Object.keys(HEX).length==0&&['step','reset','drawBack','drawFront','drawPlayer','blHit'].every(k=>Array.isArray(HEH[k]))&&typeof HEH.pjHit=='object'&&HE.maxNew==2&&HE.maxNewLate==3&&HE.lateStage==10&&HE.minDist==220&&HE.share==.3"))
    check('no page errors at load', not (pg._errs + pg.evaluate('__errs')))
    pg.context.close()
    br.close()

print('\n%d checks passed, %d failed' % (PASS[0], len(FAIL)))
for f in FAIL: print('  FAILED:', f)
sys.exit(1 if FAIL else 0)

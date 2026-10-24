#!/usr/bin/env python3
"""HE part 3 test suite (headless Chromium via playwright): Night-Fang (t8).
Usage: python3 he_p3_test.py <aria_v32_p2.html> <aria_v32_p3.html> [shots_dir]
In-page harness (L3): requestAnimationFrame stubbed, Math.random seeded + counted, update()/draw0() driven by hand, ?hedebug for __heSpawn.
draw0() costs ~0.7 s per frame in this software-rendered sandbox, so frames are drawn sparsely."""
import sys, os
from playwright.sync_api import sync_playwright

P2, P3 = [os.path.abspath(p) for p in sys.argv[1:3]]
SHOTS = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else None
FAIL = []; PASS = [0]

def check(name, cond, detail=''):
    if cond: PASS[0] += 1; print('  ok  ', name)
    else: FAIL.append(name); print('  FAIL', name, detail)

INIT = r"""
(()=>{
  let s=(%SEED%)>>>0,n=0;
  const rr=()=>{s=(s+0x6D2B79F5)|0;let t=Math.imul(s^(s>>>15),1|s);t=(t+Math.imul(t^(t>>>7),61|t))^t;n++;return((t^(t>>>14))>>>0)/4294967296};
  window.__rnd0=rr;Math.random=rr;
  Object.defineProperty(window,'__rc',{get:()=>n});
  window.requestAnimationFrame=()=>0;
  window.__errs=[];window.__warns=[];
  window.addEventListener('error',e=>window.__errs.push(String(e.message)));
  console.warn=(...a)=>{window.__warns.push(a.map(String).join(' '))};
})();
"""
DRIVER = r"""
window.__start=(d,n)=>{mute=1;beginAt(d,n);maxhp=hp=99999;pl.inv=0};
window.__setup=(stage,px)=>{mute=1;beginAt(2,stage);X.length=0;maxhp=hp=99999;pl.inv=0;hs=0;E.length=0;pj.length=0;bl.length=0;S=[];sp=1e9;wzT=1e9;K={};
  pl.x=px===undefined?100:px;pl.y=GY-42;pl.vx=pl.vy=0;pl.g=null;pl.rt=0;pl.rtI=0;jb=0;dnq=0;ups.dash=1;ups.dj=0;sh=0;au=0;iv=0;tm.i=0;tm.p=0;need=999;wb.length=0;wdDead.length=0};
window.__layout=(k,px)=>{lava=0;X.length=0;E.length=0;pj.length=0;bl.length=0;
  P=k=='flat'?[mk(0,GY,W)]:k=='small'?[mk(0,GY,W),mk(300,420,200)]:k=='pit'?[mk(0,GY,430),mk(540,GY,460)]:k=='step'?[mk(0,GY,W),mk(380,520,160)]:k=='step2'?[mk(0,GY,W),mk(300,520,220)]:k=='mov'?[mk(0,GY,W),mk(300,520,220,'h',60,1.1)]:k=='two'?[mk(0,GY,W),mk(300,420,150),mk(700,420,150)]:P;
  movP();movP();pl.x=px===undefined?700:px;pl.y=GY-42;pl.vx=pl.vy=0;pl.g=null;pl.inv=99999;hs=0};
window.__tk=(n,f)=>{for(let i=0;i<n;i++){hs=0;if(f&&f(i)===false)return i;update()}return n};
window.__withRand=(v,fn)=>{const o=Math.random;Math.random=()=>v;try{return fn()}finally{Math.random=o}};
window.__sig=()=>({tick,st,score,hp,px:+pl.x.toFixed(3),py:+pl.y.toFixed(3),stage,rc:__rc,nE:E.length,pj:pj.length,bl:bl.length,E:E.map(e=>[e.t,+e.x.toFixed(2),+e.y.toFixed(2),e.hp,e.a])});
window.__drive=(ticks)=>{
  const out={log:[]};const seen=new Set();
  for(let i=0;i<ticks;i++){
    const ph=i%240;K['@r']=ph<70;K['@l']=ph>=120&&ph<190;K['@j']=(i%97)<6;K['@f']=(i%31)<4;
    update();
    for(const e of E){if(!seen.has(e)){seen.add(e);out.log.push([tick,e.t,Math.round(e.x*100),Math.round(e.y*100)])}}
  }
  K['@r']=K['@l']=K['@j']=K['@f']=0;out.state=__sig();return out;
};
"""

def new_page(br, path, seed=1, query='?hedebug'):
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

def ev(pg, js, arg=None):
    return pg.evaluate(js, arg) if arg is not None else pg.evaluate(js)

def clean(pg):
    return not pg._errs and not ev(pg, '__errs') and not ev(pg, '__warns')

with sync_playwright() as p:
    br = p.chromium.launch()
    LOG = lambda pg: (pg._errs[:1], ev(pg, '__warns')[:1])

    # ------------------------------------------------------------------ [a] parity p2 vs p3
    print('\n[a] parity p2 vs p3: Easy/Normal (all stages) and Hard stages 1-3 (Night-Fang unlocks at 4) -> identical, incl. Math.random count')
    def run(path, d, n, seed, ticks=3000):
        pg = new_page(br, path, seed, '')
        ev(pg, '([d,n])=>__start(d,n)', [d, n])
        out = ev(pg, 't=>__drive(t)', ticks)
        out['errs'] = pg._errs + ev(pg, '__errs'); pg.context.close(); return out
    for d, n in [(0, 1), (0, 4), (0, 8), (0, 12), (1, 1), (1, 4), (1, 8), (1, 12), (2, 1), (2, 2), (2, 3)]:
        seed = 401 + d * 17 + n
        a = run(P2, d, n, seed); b = run(P3, d, n, seed)
        nm = 'dif%d stage%d' % (d, n)
        check(nm + ': spawn sequence identical (%d spawns)' % len(a['log']), a['log'] == b['log'] and len(a['log']) > 0)
        check(nm + ': final state + Math.random count identical', a['state'] == b['state'], '%s vs %s' % (a['state']['rc'], b['state']['rc']))
        check(nm + ': no page errors', not a['errs'] and not b['errs'], (a['errs'][:1], b['errs'][:1]))

    # ------------------------------------------------------------------ [b] registry + natural spawns
    print('\n[b] registry + natural spawn gating')
    pg = new_page(br, P3)
    r = ev(pg, '''()=>{const r=HEX[8];return {name:r.name,w:r.w,h:r.h,unlock:r.unlock,max:r.max,weight:r.weight,place:r.place,moving:r.moving,quiet:r.quiet,
      hp3:r.hp(3),hp7:r.hp(7),hp8:r.hp(8),hp14:r.hp(14),keys:Object.keys(HEX).join(','),cw:typeof HEH.pjHit.cw,fr:HEH.drawFront.length,
      dmg:typeof r.dmg,contact:typeof r.contact,dazed:typeof r.dazed,g:HE.fang.g,pg:(typeof pl!='undefined')}}''')
    check('HEX[8] registered: Night-Fang 44x28, unlock 4, max 2, weight 1, place platform (+moving platforms)', r['name'] == 'Night-Fang' and r['w'] == 44 and r['h'] == 28 and r['unlock'] == 4 and r['max'] == 2 and r['weight'] == 1 and r['place'] == 'platform' and r['moving'] and not r['quiet'], r)
    check('hp = 3 + (stage>>3): 3 at stage 4/7, 4 at 8/14', (r['hp3'], r['hp7'], r['hp8'], r['hp14']) == (3, 3, 4, 4), r)
    check('registry keys 6,8 only; pjHit.cw + drawFront hooks; dmg/contact/dazed overrides; g == player gravity .62', r['keys'] == '6,8' and r['cw'] == 'function' and r['fr'] == 2 and r['dmg'] == 'function' and r['contact'] == 'function' and r['dazed'] == 'function' and r['g'] == .62, r)
    check('player gravity in update() really is .62 (grep)', open(P3, encoding='utf-8').read().count('pl.vy=Math.min(14,pl.vy+.62)') >= 1)
    pg.context.close()
    def spawn_run(d, n, ticks=4000, share=1):
        pg = new_page(br, P3, 177 + n + d, '')
        ev(pg, '([d,n,s])=>{HE.share=s;__start(d,n)}', [d, n, share])
        res = ev(pg, '''t=>{let mx=0,tot=0,seen=new Set(),bad=[];for(let i=0;i<t;i++){const ph=i%240;K['@r']=ph<70;K['@l']=ph>=120&&ph<190;K['@j']=(i%97)<6;K['@f']=(i%31)<4;update();
          let k=0;for(const e of E)if(e.a&&e.t==8){k++;if(!seen.has(e)){seen.add(e);tot++;if(!e.p||e.hp!=HEX[8].hp(stage))bad.push(['spawn',e.hp,!!e.p])}}mx=Math.max(mx,k)}return {mx,tot,bad}}''', ticks)
        e = pg._errs + ev(pg, '__errs'); w = ev(pg, '__warns'); pg.context.close(); return res, e, w
    res, e, w = spawn_run(2, 4)
    check('Hard stage 4 (share=1): hounds spawn (%d), never more than 2 alive (%d), placed on a platform with the right hp' % (res['tot'], res['mx']), res['tot'] >= 1 and res['mx'] <= 2 and not res['bad'], res)
    check('  ... no errors / no HE warnings', not e and not w, (e[:1], w[:1]))
    for d, n, nm in [(2, 3, 'Hard stage 3 (locked)'), (0, 4, 'Easy stage 4'), (1, 4, 'Normal stage 4'), (2, 5, 'Hard boss stage 5'), (2, 10, 'Hard boss stage 10')]:
        res, e, w = spawn_run(d, n, 2500)
        check(nm + ': no Night-Fang', res['tot'] == 0, res)

    # ------------------------------------------------------------------ [c] patrol + hunt
    print('\n[c] patrol (fast, turns at platform ends), hunt trigger (380 px horizontally, |dy| < 200)')
    pg = new_page(br, P3)
    ev(pg, '__setup(4,900)'); ev(pg, '()=>{bn=0;__tk(2);__layout("small",900)}')
    r = ev(pg, '''()=>{const e=__heSpawn(8,320,420-28);e.cd=1e9;const o={sp:e.sp,steps:[],turns:0,minx:1e9,maxx:-1e9,onp:!!e.p&&e.p.y==420,hu:[]};let d0=e.d,px0=e.x;
      for(let n=0;n<160;n++){const x0=e.x;hs=0;update();if(e.d!=d0){o.turns++;d0=e.d}else o.steps.push(+(e.x-x0).toFixed(9)*e.d);o.minx=Math.min(o.minx,e.x);o.maxx=Math.max(o.maxx,e.x);o.hu.push(e.hu)}
      o.fast=o.steps.every(s=>Math.abs(s-e.sp*1.5)<1e-6);return o}''')
    check('fang is placed on the 420 platform and patrols at e.sp*1.5 px/tick', r['onp'] and r['fast'], (r['sp'], r['steps'][:3]))
    check('turns at both platform ends (%d turns) and never leaves [300, 456]' % r['turns'], r['turns'] >= 2 and r['minx'] >= 300 - 1e-9 and r['maxx'] <= 456 + 1e-9, r)
    check('player 570 px away: not hunting (hu 0)', not any(r['hu']), r['hu'][:5])
    def hunt(px, py, spawnx=320):
        return ev(pg, '''([px,py,sx])=>{__layout("small",900);const e=__heSpawn(8,sx,420-28);e.cd=1e9;pl.x=px;pl.y=py;pl.vy=0;pl.g=null;hs=0;update();return {hu:e.hu,d:e.d}}''', [px, py, spawnx])
    r = hunt(560, 518)
    check('player 176 px away, 133 px below (|dy|<200): hunting, faces the player', r['hu'] == 1 and r['d'] == 1, r)
    r = hunt(760, 518)
    check('player 432 px away: not hunting; 332 px away: hunting (limit 380)', r['hu'] == 0 and hunt(670, 518)['hu'] == 1, r)
    r = hunt(560, 150)
    check('player 235 px above (|dy| >= 200): not hunting', r['hu'] == 0, r)
    r = hunt(40, 518)
    check('player on the left: hunting turns the fang left (d == -1)', r['hu'] == 1 and r['d'] == -1, r)
    check('[c] no errors / no HE warnings', clean(pg), LOG(pg)); pg.context.close()

    # ------------------------------------------------------------------ [d] crouch / leap / lock
    print('\n[d] CROUCH 28f, ballistic leap (speed <= 11, player gravity), target locked when the crouch ends, e.p cleared while airborne')
    pg = new_page(br, P3)
    ev(pg, '__setup(4,700)'); ev(pg, '()=>{bn=0;__tk(2);__layout("flat",700)}')
    r = ev(pg, '''()=>{const e=__heSpawn(8,470,GY-28);e.cd=0;e.born=-99;const o={seq:[],pAir:[]};let last=-1,n1=-1,n4=-1,v0=null,x1=null;
      for(let n=0;n<200;n++){
        hs=0;update();
        if(e.st!=last){o.seq.push([n,e.st]);last=e.st;if(e.st==1)n1=n;if(e.st==4){n4=n;v0=Math.hypot(e.vx,e.vy)}}
        if(e.st==4)o.pAir.push(e.p===null||e.p===undefined);
        if(e.st==6)break}
      o.crouch=n4-n1;o.v0=v0;o.landed=e.st==6;o.onFloor=e.p===P[0];o.y=e.y;o.fyOK=Math.abs(e.y+e.h-GY)<1e-9;o.airNoP=o.pAir.length>0&&o.pAir.every(Boolean);
      o.tm=e.tm;return o}''')
    check('sequence PATROL -> CROUCH -> LEAP -> DAZED; crouch lasts exactly 28 ticks', [s for _, s in r['seq']][:4] == [0, 1, 4, 6] and r['crouch'] == 28, r['seq'])
    check('launch speed %.2f <= 11 (maxV); fang lands on the floor (e.p = platform, feet on the surface); e.p is null while airborne' % r['v0'], r['v0'] <= 11 + 1e-9 and r['landed'] and r['onFloor'] and r['fyOK'] and r['airNoP'], r)
    r = ev(pg, '''()=>{__layout("flat",700);pl.x=720;const e=__heSpawn(8,470,GY-28);e.cd=0;e.born=-99;const o={};let n1=-1,pLock=null,pStart=null,landed=-1;
      for(let n=0;n<260;n++){
        const dur=e.st==1;
        K['@l']=dur&&(n-n1<10);K['@r']=(e.st==4||e.st==6);
        hs=0;update();
        if(e.st==1&&n1<0){n1=n;pStart=pl.x+16}
        if(e.st==4&&pLock===null)pLock=pl.x+16;     /* AI ran after the player moved in the same tick: this is the locked target */
        if(e.st==6){landed=e.x+e.w/2;break}}
      K['@l']=K['@r']=0;o.pStart=pStart;o.pLock=pLock;o.landed=landed;o.pFinal=pl.x+16;o.moved=Math.abs(pLock-pStart);return o}''')
    check('lock: fang lands where the player WAS at the end of the crouch (%.1f vs %.1f), not where he was at its start (moved %.0f px) or ended up (%.0f)' % (r['landed'], r['pLock'], r['moved'], r['pFinal']),
          abs(r['landed'] - r['pLock']) < .6 and r['moved'] > 25 and abs(r['landed'] - r['pFinal']) > 40, r)
    # unreachable target
    ev(pg, '__layout("two",700)')
    r = ev(pg, '''()=>{__layout("two",700);pl.x=700;pl.y=420-42;const e=__heSpawn(8,380,420-28);e.cd=0;e.born=-99;let crouch=0,hu=0;
      for(let n=0;n<200;n++){hs=0;update();if(e.st==1||e.st==4)crouch=1;hu=Math.max(hu,e.hu)}return {crouch,hu,st:e.st}}''')
    check('target beyond the launch-speed range (hunting but 11 px/tick is not enough): never crouches / leaps', r['hu'] == 1 and r['crouch'] == 0, r)
    # boundary of the launch speed over many solutions (flat distances 60..300)
    r = ev(pg, '''()=>{__layout("flat",700);const e=__heSpawn(8,100,GY-28);let ok=0,no=0,mx=0;for(let d=40;d<=330;d+=10){const s=fgSolve(e,e.x+22+d,GY+1);if(s){ok++;mx=Math.max(mx,s.s)}else no++}return {ok,no,mx}}''')
    check('fgSolve: every accepted solution has speed <= 11 (max %.3f); reachable distances up to ~200 px on flat ground (%d ok / %d out of range)' % (r['mx'], r['ok'], r['no']), r['mx'] <= 11 + 1e-9 and 14 <= r['ok'] <= 22 and r['no'] >= 8, r)
    # high target: the arc is ballistic with g = .62 (apex consistent with vy0)
    r = ev(pg, '''()=>{__layout("step",700);const e=__heSpawn(8,330,GY-28);const s=fgSolve(e,420,520+1);if(!s)return {s:null};let y=e.y,v=s.vy,apex=y;for(let i=0;i<s.T;i++){v+=.62;y+=v;apex=Math.min(apex,y)}return {s:1,T:s.T,vy:s.vy,sp:s.s,landY:y+e.h,plat:s.p.y,apexUp:e.y-apex}}''')
    check('ballistic exactness: after T steps (g = .62) the feet are exactly on the target (521) and the landing platform is the step (y 520)', r['s'] == 1 and abs(r['landY'] - 521) < 1e-6 and r['plat'] == 520, r)
    check('[d] no errors / no HE warnings', clean(pg), LOG(pg)); pg.context.close()

    # ------------------------------------------------------------------ [e] never leaps into pits / spikes / lava / moving platforms
    print('\n[e] landing safety: pits, spike strips, lava, moving platforms, edges')
    pg = new_page(br, P3)
    ev(pg, '__setup(4,700)'); ev(pg, '()=>{bn=0;__tk(2)}')
    def leaps(js):
        return ev(pg, js)
    base = '''()=>{%s;const e=__heSpawn(8,%d,%s);e.cd=0;e.born=-99;let c=0,l=0;for(let n=0;n<%d;n++){%s;hs=0;update();if(e.st==1)c=1;if(e.st==4)l=1}return {crouch:c,leap:l,st:e.st,hp:e.hp}}'''
    # pit: fang on the left floor piece, player floating over the gap
    r = leaps(base % ('__layout("pit",480)', 395, 'GY-28', 160, 'pl.x=480;pl.y=400;pl.vy=0;pl.g=null'))
    check('player over a pit (target above the gap): the hound never crouches or leaps', r['crouch'] == 0 and r['leap'] == 0, r)
    r = leaps(base % ('__layout("pit",545)', 395, 'GY-28', 160, 'pl.x=545;pl.y=GY-42;pl.vy=0'))
    check('control: player standing on the far floor piece (inside the safe margin): the hound leaps ACROSS the pit', r['crouch'] == 1 and r['leap'] == 1, r)
    r = leaps(base % ('__layout("flat",700);X.push([690,60])', 470, 'GY-28', 160, 'pl.x=700;pl.y=GY-42;pl.vy=0'))
    check('player standing in a spike strip X[]: no leap (landing point would be in the strip)', r['crouch'] == 0 and r['leap'] == 0, r)
    r = leaps(base % ('__layout("flat",700)', 470, 'GY-28', 160, 'pl.x=700;pl.y=GY-42;pl.vy=0'))
    check('control: same spot without the spikes: leaps', r['crouch'] == 1 and r['leap'] == 1, r)
    r = leaps(base % ('__layout("small",650);lava=1', 320, '420-28', 160, 'pl.x=650;pl.y=GY-42;pl.vy=0'))
    check('lava stage, target on the lava-level floor: no leap', r['crouch'] == 0 and r['leap'] == 0, r)
    r = leaps(base % ('__layout("small",650);lava=0', 320, '420-28', 160, 'pl.x=650;pl.y=GY-42;pl.vy=0'))
    check('control: same without lava: leaps down to the floor', r['crouch'] == 1 and r['leap'] == 1, r)
    r = leaps(base % ('__layout("mov",360)', 290, 'GY-28', 120, 'pl.x=360;pl.y=P[1].y-42;pl.vy=0;pl.g=null'))
    check('player standing on a MOVING platform: no leap (landing is unpredictable)', r['crouch'] == 0 and r['leap'] == 0, r)
    r = leaps(base % ('__layout("step2",360)', 290, 'GY-28', 120, 'pl.x=360;pl.y=520-42;pl.vy=0;pl.g=null'))
    check('control: same on a static platform: leaps', r['crouch'] == 1 and r['leap'] == 1, r)
    r = ev(pg, '''()=>{__layout("step2",360);const e=__heSpawn(8,290,GY-28);e.cd=0;e.born=-99;let landedOn=null;for(let n=0;n<200;n++){pl.x=360;pl.y=520-42;pl.vy=0;pl.g=null;hs=0;update();if(e.st==6){landedOn=e.p===P[1];break}}return {landedOn,y:e.y+e.h}}''')
    check('control: the hound lands ON the static platform (e.p = the step, feet at y 520)', r['landedOn'] is True and abs(r['y'] - 520) < 1e-9, r)
    r = ev(pg, '''()=>{__layout("step2",305);const e=__heSpawn(8,260,GY-28);const s=fgSolve(e,305,520+1);const s2=fgSolve(e,360,520+1);return {edge:!!s,mid:!!s2}}''')
    check('landing within 10 px of a platform edge is refused (edge margin), the middle is accepted', (not r['edge']) and r['mid'], r)
    # failsafe
    r = ev(pg, '''()=>{__layout("flat",700);const e=__heSpawn(8,300,GY-28);e.cd=1e9;e.st=4;e.p=null;e.tr=[];e.vx=0;e.vy=0;P=[];hs=0;let n=0;for(;n<80&&e.a;n++){update();}
      return {alive:e.a,st:e.st,n}}''')
    check('failsafe: a hound falling past every platform is removed (no stuck / endless fall)', r['alive'] == 0, r)
    r = ev(pg, '''()=>{__layout("flat",700);const e=__heSpawn(8,300,GY-28);e.cd=1e9;e.st=4;e.p=null;e.tr=[];e.vx=0;e.vy=0;e.y=300;P=[mk(0,GY,W),mk(100,500,300)];P[1].y=500;
      /* rescue branch when platforms exist but none is crossed: x outside every platform, fall below H */
      P=[mk(0,GY,200)];e.x=600;hs=0;for(let n=0;n<120&&e.st==4;n++)update();return {st:e.st,hasP:!!e.p,x:e.x,y:e.y,alive:e.a}}''')
    check('failsafe: rescue puts a hound that fell off the world back on the nearest static platform (patrol again)', r['alive'] == 1 and r['hasP'] and r['st'] == 0 and r['x'] <= 200 - 44 + 1, r)
    check('[e] no errors / no HE warnings', clean(pg), LOG(pg)); pg.context.close()

    # ------------------------------------------------------------------ [f] feint
    print('\n[f] feint (30%): crouch 28 -> hop back 12 -> second crouch 18 with WHITE eyes -> leap; target locked at the very end')
    pg = new_page(br, P3)
    ev(pg, '__setup(4,700)'); ev(pg, '()=>{bn=0;__tk(2)}')
    seqjs = '''(rv)=>{__layout("flat",720);const e=__heSpawn(8,470,GY-28);e.cd=0;e.born=-99;const seq=[];let last=-1,t0=0,xs=[],px=[];
      const o=Math.random;Math.random=()=>rv;
      for(let n=0;n<260;n++){hs=0;update();if(e.st!=last){seq.push([n,e.st]);last=e.st;if(e.st==1)Math.random=o}if(e.st==2)xs.push(e.x);if(e.st==6)break}
      Math.random=o;return {seq,xs,landed:e.x+22,hp:e.hp,pxEnd:pl.x+16}}'''
    r = ev(pg, seqjs, .29)
    st = [s for _, s in r['seq']]
    check('random < .3 (feint): PATROL, CROUCH, HOP, CROUCH2, LEAP, DAZED', st[:6] == [0, 1, 2, 3, 4, 6], r['seq'])
    lens = [r['seq'][i + 1][0] - r['seq'][i][0] for i in range(1, 4)]
    check('lengths: crouch 28, hop 12, second crouch 18', lens == [28, 12, 18], lens)
    check('the hop goes BACK (away from the player, x decreases) and stays on the platform', r['xs'] and r['xs'][-1] < r['xs'][0] - 20, r['xs'][:3])
    r = ev(pg, seqjs, .31)
    st = [s for _, s in r['seq']]
    lens = [r['seq'][i + 1][0] - r['seq'][i][0] for i in range(1, 2)]
    check('random >= .3: no feint: PATROL, CROUCH(28), LEAP, DAZED', st[:4] == [0, 1, 4, 6] and lens == [28], r['seq'])
    r = ev(pg, '''()=>{__layout("flat",720);const e=__heSpawn(8,470,GY-28);e.cd=0;e.born=-99;let last=-1,n3=-1,pLock=null;const o=Math.random;
      for(let n=0;n<260;n++){const sty=e.st;K['@l']=(sty==3&&n-n3<8);K['@r']=(e.st==4||e.st==6);if(e.st==1&&last!=1)Math.random=()=>.1;hs=0;update();if(e.st!=last){if(e.st==3)n3=n;if(e.st==4)pLock=pl.x+16;last=e.st}if(e.st==6)break;}
      K['@l']=K['@r']=0;Math.random=o;return {landed:e.x+22,pLock,pEnd:pl.x+16,n3}}''')
    check('feint: the landing spot is locked at the END of the second crouch (%.1f vs %.1f; final player x %.0f)' % (r['landed'], r['pLock'] or -1, r['pEnd']), r['pLock'] is not None and abs(r['landed'] - r['pLock']) < .6 and abs(r['landed'] - r['pEnd']) > 40, r)
    check('[f] no errors / no HE warnings', clean(pg), LOG(pg)); pg.context.close()

    # ------------------------------------------------------------------ [g] claw waves
    print('\n[g] claw waves: two per landing, 4.2 px/tick, 160 px reach, removed at platform edges, height aware (must be jumped)')
    pg = new_page(br, P3)
    ev(pg, '__setup(4,700)'); ev(pg, '()=>{bn=0;__tk(2)}')
    r = ev(pg, '''()=>{__layout("flat",600);const e=__heSpawn(8,300,GY-28);e.cd=1e9;e.born=-99;pl.x=900;
      const o={};fgLandOn(e,P[0]);const w=pj.filter(q=>q.k=='cw');o.n=w.length;o.vx=w.map(q=>q.vx).sort((a,b)=>a-b);o.y=w.map(q=>q.y);o.sy=w.map(q=>q.sy);o.he=w.every(q=>q.he==1);o.st=e.st;o.tm=e.tm;
      const x0=e.x+22;let n=0,rm=[];const seen=new Map();w.forEach(q=>seen.set(q,0));
      for(;n<120&&pj.some(q=>q.k=='cw');n++){hs=0;update();for(const q of w)if(!pj.includes(q)&&seen.get(q)==0){seen.set(q,1);rm.push([n,Math.abs(q.x-x0)])}}
      o.rm=rm;return o}''')
    check('landing spawns exactly 2 waves (k cw, he:1), speeds -4.2 / +4.2, 7 px above the surface, then DAZED for 45 ticks', r['n'] == 2 and r['vx'] == [-4.2, 4.2] and r['he'] and all(abs(y - (560 - 7)) < 1e-9 for y in r['y']) and r['st'] == 6 and r['tm'] == 45, r)
    check('on a wide floor each wave is removed after travelling 160 px (%s)' % [round(d) for _, d in r['rm']], len(r['rm']) == 2 and all(160 <= d <= 160 + 4.2 + 1e-6 for _, d in r['rm']), r['rm'])
    r = ev(pg, '''()=>{__layout("step",440);const e=__heSpawn(8,300,GY-28);e.cd=1e9;e.born=-99;pl.x=900;pl.y=GY-42;
      const pf=P[1];e.x=pf.x+78;e.y=pf.y-e.h;e.p=pf;fgLandOn(e,pf);const w=pj.filter(q=>q.k=='cw');const x0=e.x+22;const rm=[];
      for(let n=0;n<80&&pj.some(q=>q.k=='cw');n++){hs=0;update();for(const q of w)if(!pj.includes(q)&&!q._r){q._r=1;rm.push([q.x,Math.abs(q.x-x0)])}}
      return {rm,plat:[pf.x,pf.x+pf.w]}}''')
    check('on a short platform both waves are removed at the platform edges (before 160 px)', len(r['rm']) == 2 and all(d < 160 for _, d in r['rm']) and any(abs(x - r['plat'][0]) < 6 for x, _ in r['rm']) and any(abs(x - r['plat'][1]) < 6 for x, _ in r['rm']), r)
    wave = '''([px,feet,inv,vy])=>{__layout("flat",px);pl.inv=inv;pl.x=px;const q={x:640,y:GY-7,vx:-4.2,vy:0,r:8,c:'#ff5a3c',k:'cw',he:1,x0:640,pf:P[0],sy:GY,hw:9,dir:-1};pj.push(q);const h0=hp;let n=0;
      for(;n<26&&pj.includes(q);n++){pl.y=GY-pl.h-feet;pl.vy=0;pl.g=null;hs=0;update()}return {dh:h0-hp,gone:!pj.includes(q),n}}'''
    r = ev(pg, wave, [560, 0, 0, 0])
    check('player standing on the floor in the wave path: hurt exactly once (-1 hp), wave removed', r['dh'] == 1 and r['gone'], r)
    r = ev(pg, wave, [560, 20, 0, 0])
    check('player in the air (feet 20 px up, clear of the 14 px wave): not hit', r['dh'] == 0, r)
    r = ev(pg, wave, [560, 15, 0, 0])
    check('feet 15 px up (just above the 14 px wave) is a clean jump', r['dh'] == 0, r)
    r = ev(pg, wave, [560, 10, 0, 0])
    check('feet 10 px up (hop too low) is still hit', r['dh'] == 1, r)
    r = ev(pg, wave, [560, 0, 30, 0])
    check('player with i-frames (dash / pl.inv): the wave passes through, no damage', r['dh'] == 0, r)
    r = ev(pg, '''()=>{__layout("mov",900);const e=__heSpawn(8,150,GY-28);e.cd=1e9;e.born=-99;const pf=P[1];e.x=pf.x+80;e.y=pf.y-e.h;e.p=pf;fgLandOn(e,pf);const w=pj.filter(q=>q.k=='cw');let maxd=0,n=0;
      for(;n<40&&pj.some(q=>q.k=='cw');n++){hs=0;update();for(const q of pj)if(q.k=='cw')maxd=Math.max(maxd,Math.abs(q.sy-pf.y))}return {maxd,n}}''')
    check('waves on a moving platform stay glued to its surface (max |sy - platform y| = %.2e)' % r['maxd'], r['maxd'] < 1e-9, r)
    check('[g] no errors / no HE warnings', clean(pg), LOG(pg)); pg.context.close()

    # ------------------------------------------------------------------ [h] stomp / damage / daze
    print('\n[h] stomp rules and damage: no stomp while airborne, stomp OK patrolling/dazed, double damage while dazed, always shoot-able')
    pg = new_page(br, P3)
    ev(pg, '__setup(4,700)'); ev(pg, '()=>{bn=0;__tk(2)}')
    stomp = '''([st])=>{__layout("flat",700);pl.inv=0;maxhp=hp=99999;const e=__heSpawn(8,600,GY-28);e.cd=1e9;e.born=-99;
      if(st==4){e.st=4;e.p=null;e.y=GY-110;e.vx=0;e.vy=0;e.tr=[]}else if(st==6){e.st=6;e.tm=45}
      pl.x=e.x+6;pl.y=e.y-38;pl.vy=6;pl.vx=0;pl.g=null;const h0=hp,e0=e.hp;hs=0;update();return {dh:h0-hp,de:e0-e.hp,a:e.a,vy:pl.vy}}'''
    r = ev(pg, stomp, [0])
    check('patrolling hound: stomp works (hp 3 -> 1), player bounces, no damage', r['de'] == 2 and r['dh'] == 0 and r['vy'] < 0, r)
    r = ev(pg, stomp, [4])
    check('airborne hound: NOT stompable: the player is hurt (-1), the hound is untouched', r['dh'] == 1 and r['de'] == 0, r)
    r = ev(pg, stomp, [6])
    check('dazed hound: stomp (2) is doubled -> dead', r['a'] == 0 and r['dh'] == 0, r)
    hit = '''([st,d])=>{__layout("flat",900);const e=__heSpawn(8,300,GY-28);e.cd=1e9;e.born=-99;if(st==4){e.st=4;e.p=null;e.y=GY-120;e.tr=[]}else if(st==6){e.st=6;e.tm=45}
      const h0=e.hp;hitE(e,d);return {de:h0-e.hp,a:e.a}}'''
    check('damage: patrolling 1 -> 1, dazed 1 -> 2 (double), airborne 1 -> 1 (always shoot-able)', [ev(pg, hit, [0, 1])['de'], ev(pg, hit, [6, 1])['de'], ev(pg, hit, [4, 1])['de']] == [1, 2, 1])
    r = ev(pg, '''()=>{__layout("flat",900);const e=__heSpawn(8,300,GY-28);e.cd=1e9;e.born=-99;e.st=4;e.p=null;e.y=GY-150;e.tr=[];e.vx=0;e.vy=0;bl.length=0;const h0=e.hp;
      bl.push({x:e.x+22,y:e.y+14,vx:0,vy:0,l:30,h:[],hm:false});hs=0;update();return {de:h0-e.hp,bl:bl.length}}''')
    check('a real player star hits a hound in mid-leap (hp -1, star consumed)', r['de'] == 1 and r['bl'] == 0, r)
    r = ev(pg, '''()=>{__layout("flat",900);const e=__heSpawn(8,300,GY-28);e.cd=1e9;e.born=-99;e.st=6;e.tm=45;bl.length=0;const h0=e.hp;
      bl.push({x:e.x+22,y:e.y+14,vx:0,vy:0,l:30,h:[],hm:false});hs=0;update();return {de:h0-e.hp}}''')
    check('a real star on a dazed hound deals double damage (hp 3 -> 1)', r['de'] == 2, r)
    r = ev(pg, '''()=>{__layout("flat",700);pl.inv=0;tm.i=300;const e=__heSpawn(8,600,GY-28);e.cd=1e9;e.born=-99;e.st=4;e.p=null;e.y=GY-80;e.vx=0;e.vy=0;e.tr=[];pl.x=e.x+6;pl.y=e.y-10;pl.vy=0;hs=0;update();tm.i=0;return {a:e.a}}''')
    check('invincibility power-up kills an airborne hound on contact (as the legacy test does)', r['a'] == 0, r)
    r = ev(pg, '''()=>{__layout("flat",900);const e=__heSpawn(8,300,GY-28);e.cd=1e9;e.born=-99;e.st=4;e.p=null;e.y=GY-200;e.vx=2;e.vy=0;e.tr=[];e.z=60;let n=0;for(;n<80&&e.st==4;n++){hs=0;update()}return {st:e.st,z:e.z,n,onFloor:e.p===P[0]}}''')
    check('Neon-Star daze mid-leap: the hound still completes its fall and lands (never frozen in the air)', r['st'] == 6 and r['onFloor'], r)
    r = ev(pg, '''()=>{__layout("flat",900);const e=__heSpawn(8,300,GY-28);e.cd=0;e.born=-99;e.z=40;pl.x=420;let st=e.st,x0=e.x;for(let n=0;n<30;n++){hs=0;update()}return {st:e.st,moved:Math.abs(e.x-x0),cd:e.cd}}''')
    check('Neon-Star daze on the ground: AI frozen (no patrol, cooldown untouched)', r['st'] == 0 and r['moved'] < 1e-9, r)
    r = ev(pg, '''()=>{__layout("flat",900);const e=__heSpawn(8,300,GY-28);e.cd=1e9;e.born=-99;e.st=6;e.tm=45;let n=0,st=[];for(;n<60;n++){hs=0;update();if(!st.length||st[st.length-1]!=e.st)st.push(e.st)}return {st,cd:e.cd}}''')
    check('DAZED lasts 45 ticks, then PATROL again with the after-cooldown (90, counting down: %d left)' % r['cd'], r['st'] == [6, 0] and 70 <= r['cd'] <= 90, r)
    r = ev(pg, '''()=>{__layout("flat",900);const e=__heSpawn(8,300,GY-28);e.cd=0;e.born=-99;e.st=6;e.tm=1;e.cd=0;pl.x=900;hs=0;update();return {st:e.st,cd:e.cd,s0:HE.fang.after}}''')
    check('(cooldown value after DAZED = HE.fang.after = 90)', r['st'] == 0 and r['cd'] == 90, r)
    r = ev(pg, '''()=>{__layout("flat",900);const e=__heSpawn(8,300,GY-28);e.cd=1e9;e.born=-99;const s0=score;hitE(e,99);return {a:e.a,sc:score-s0}}''')
    check('kill score 380 (t8 entry of the score table)', r['a'] == 0 and r['sc'] >= 380, r)
    check('[h] no errors / no HE warnings', clean(pg), LOG(pg)); pg.context.close()

    # ------------------------------------------------------------------ [i] moving platforms
    print('\n[i] moving platforms: carried while patrolling, can leap from one, never lands on one by design')
    pg = new_page(br, P3)
    ev(pg, '__setup(4,700)'); ev(pg, '()=>{bn=0;__tk(2)}')
    r = ev(pg, '''()=>{__layout("mov",900);const pf=P[1];const e=__heSpawn(8,pf.x+50,pf.y-28);e.cd=1e9;e.born=-99;const o={onP:e.p===pf,bad:0,dx:0,minx:1e9,maxx:-1e9};
      const x0=pf.x;for(let n=0;n<260;n++){hs=0;update();if(Math.abs(e.y-(pf.y-e.h))>1e-9)o.bad++;if(e.x<pf.x-1e-6||e.x>pf.x+pf.w-e.w+1e-6)o.bad++;o.minx=Math.min(o.minx,pf.x);o.maxx=Math.max(o.maxx,pf.x)}
      o.span=o.maxx-o.minx;return o}''')
    check('hound patrols a moving platform: carried (always on its surface and inside its span), platform moved %.0f px' % r['span'], r['onP'] and r['bad'] == 0 and r['span'] > 40, r)
    r = ev(pg, '''()=>{__layout("mov",620);const pf=P[1];pl.x=620;pl.y=GY-42;const e=__heSpawn(8,pf.x+60,pf.y-28);e.cd=0;e.born=-99;let l=0,landed=-1;for(let n=0;n<200;n++){hs=0;update();if(e.st==4)l=1;if(e.st==6){landed=1;break}}return {l,landed,onFloor:e.p===P[0],a:e.a}}''')
    check('a hound on a moving platform leaps at the player on the floor and lands on the floor', r['l'] == 1 and r['landed'] == 1 and r['onFloor'], r)
    check('[i] no errors / no HE warnings', clean(pg), LOG(pg)); pg.context.close()

    # ------------------------------------------------------------------ [j] heFail paths
    print('\n[j] failure paths -> heFail, game continues like v31')
    def fail_case(nm, js):
        pg = new_page(br, P3)
        ev(pg, '__setup(4,700)'); ev(pg, '()=>{bn=0;__tk(2);__layout("flat",700);pl.inv=0}')
        r = ev(pg, js)
        e = ev(pg, '''()=>{__tk(5);return {on:HE_ON,fangs:E.filter(q=>q.a&&q.t==8).length,cw:pj.filter(q=>q.k=='cw').length}}''')
        check(nm + ': HE_ON=0, no hounds, no claw waves left', e['on'] == 0 and e['fangs'] == 0 and e['cw'] == 0, (r, e))
        r2 = ev(pg, '''()=>{const x0=pl.x;K['@r']=1;__tk(20);K['@r']=0;return pl.x-x0}''')
        check(nm + ': player moves normally afterwards', r2 > 10, r2)
        pg.context.close()
    fail_case('throw in ai', '''()=>{const e=__heSpawn(8,470,GY-28);fgLandOn(e,P[0]);HEX[8].ai=()=>{throw new Error('x')};hs=0;update();return 1}''')
    fail_case('throw in draw', '''()=>{const e=__heSpawn(8,470,GY-28);fgLandOn(e,P[0]);HEX[8].draw=()=>{throw new Error('x')};RA=.5;ipOn();draw0();return 1}''')
    fail_case('throw in contact', '''()=>{const e=__heSpawn(8,470,GY-28);fgLandOn(e,P[0]);HEX[8].contact=()=>{throw new Error('x')};hs=0;update();return 1}''')
    fail_case('throw in dmg', '''()=>{const e=__heSpawn(8,470,GY-28);fgLandOn(e,P[0]);HEX[8].dmg=()=>{throw new Error('x')};hitE(e,1);hs=0;update();return 1}''')
    fail_case('throw in dazed', '''()=>{const e=__heSpawn(8,470,GY-28);fgLandOn(e,P[0]);HEX[8].dazed=()=>{throw new Error('x')};e.z=30;hs=0;update();return 1}''')
    fail_case('throw in pjHit.cw', '''()=>{const e=__heSpawn(8,470,GY-28);fgLandOn(e,P[0]);HEH.pjHit.cw=()=>{throw new Error('x')};hs=0;update();return 1}''')
    fail_case('throw in onKill', '''()=>{const e=__heSpawn(8,470,GY-28);fgLandOn(e,P[0]);HEX[8].onKill=()=>{throw new Error('x')};hitE(e,99);hs=0;update();return 1}''')

    # ------------------------------------------------------------------ [k] drawing + determinism + screenshots
    print('\n[k] drawing: every state, preview arc + landing mark, after-images, waves, dazed stars; deterministic; no Math.random in painters')
    pg = new_page(br, P3)
    ev(pg, '__setup(4,700)'); ev(pg, '()=>{bn=0;__tk(2);__layout("flat",700)}')
    states = ev(pg, '''()=>{const e=__heSpawn(8,470,GY-28);e.cd=1e9;e.born=-99;const res=[];pl.x=604;pl.y=GY-42;
      const cfgs=[['patrol',e=>{e.st=0}],['crouch',e=>{e.st=1;e.tm=10;e.sol=fgSolve(e,620,GY+1);e.arc=e.sol&&e.sol.pts}],['hop',e=>{e.st=2;e.tm=6;e.hd=-1}],['crouch2',e=>{e.st=3;e.tm=6;e.sol=fgSolve(e,620,GY+1);e.arc=e.sol&&e.sol.pts}],
        ['air',e=>{e.st=4;e.p=null;e.vx=6;e.vy=-4;e.y=300;e.tr=[e.x-8,e.y+6,e.x-16,e.y+10,e.x-24,e.y+13];e.mx=640;e.my=GY}],['dazed',e=>{e.st=6;e.p=P[0];e.y=GY-28;e.sq=6}]];
      for(const [nm,f] of cfgs){f(e);RA=.5;ipOn();draw0();res.push([nm,HE_ON])}
      fgWaves(Object.assign({},e,{x:300,w:44}),P[0]);RA=.5;ipOn();draw0();res.push(['waves',HE_ON]);return res}''')
    check('draw0 in every hound state (patrol, crouch+arc, hop, crouch2 white eyes, airborne after-images, dazed) + claw waves: HE stays on', all(x[1] == 1 for x in states) and clean(pg), (states, LOG(pg)))
    r = ev(pg, '''()=>{const e=E.find(q=>q.t==8);e.st=1;e.tm=10;e.sol=fgSolve(e,620,GY+1);e.arc=e.sol.pts;const r0=__rc;RA=.5;ipOn();draw0();const rc=__rc-r0;
      const hash=()=>{c.setTransform(1,0,0,1,0,0);c.globalAlpha=1;c.globalCompositeOperation='source-over';c.shadowBlur=0;c.clearRect(0,0,W,H);heDraw(e);heDrawH(HEH.drawFront);return c.canvas.toDataURL()};
      const h1=hash(),h2=hash();e.st=4;e.p=null;e.vx=6;e.vy=-4;e.y=300;e.tr=[e.x-8,e.y+6,e.x-16,e.y+10];e.mx=640;e.my=GY;const h3=hash(),h4=hash();
      return {rc,s1:h1===h2,s2:h3===h4,ne:h1.length>3000,diff:h1!==h3}}''')
    check('no Math.random calls inside draw0 with the hound in view', r['rc'] == 0, r)
    check('hound / waves painters deterministic in crouch and airborne states (identical pixels on re-render, non-empty, states differ)', r['s1'] and r['s2'] and r['ne'] and r['diff'], r)
    r = ev(pg, '''()=>{const e=E.find(q=>q.t==8);e.st=6;e.p=P[0];e.y=GY-28;hitE(e,99);const o=[];for(let i=0;i<4;i++){hs=0;update();RA=.5;draw0();o.push(HE_ON)}return o}''')
    check('death dissolve snapshot (dd: no eyes, no arc, no after-images) draws without errors', all(x == 1 for x in r) and clean(pg), (r, LOG(pg)))
    if SHOTS:
        os.makedirs(SHOTS, exist_ok=True)
        pg2 = new_page(br, P3)
        ev(pg2, '__setup(4,700)'); ev(pg2, '()=>{bn=0;__tk(2);__layout("flat",700)}')
        def shot(nm, js):
            ev(pg2, js); ev(pg2, '()=>{RA=.5;ipOn();draw0()}')
            pg2.locator('canvas').first.screenshot(path=os.path.join(SHOTS, nm + '.png'))
        shot('fang_patrol', '''()=>{E.length=0;pj.length=0;pl.x=880;pl.y=GY-42;const e=__heSpawn(8,330,GY-28);e.cd=1e9;e.born=-99;e.st=0;e.d=1}''')
        shot('fang_crouch', '''()=>{const e=E.find(q=>q.t==8);pl.x=470;pl.y=GY-42;e.st=1;e.tm=8;e.d=1;e.sol=fgSolve(e,486,GY+1);e.arc=e.sol.pts}''')
        shot('fang_feint_eyes', '''()=>{const e=E.find(q=>q.t==8);e.st=3;e.tm=6;e.sol=fgSolve(e,486,GY+1);e.arc=e.sol.pts}''')
        shot('fang_air', '''()=>{const e=E.find(q=>q.t==8);e.st=4;e.p=null;e.vx=7;e.vy=-3;e.x=420;e.y=360;e.tr=[e.x-9,e.y+7,e.x-19,e.y+11,e.x-29,e.y+14,e.x-39,e.y+16];e.mx=520;e.my=GY;e.arc=null}''')
        shot('fang_land_dazed', '''()=>{const e=E.find(q=>q.t==8);pj.length=0;e.st=0;e.p=P[0];e.x=500;e.y=GY-28;fgLandOn(e,P[0]);e.sq=0;pl.x=900}''')
        pg2.context.close()
    check('[k] no errors / no HE warnings', clean(pg), LOG(pg)); pg.context.close()

    # ------------------------------------------------------------------ [l] fuzz
    print('\n[l] fuzz: Hard stages 4,6,8,9,12 x 6000 ticks, hounds + widows forced (share=1), scripted random input; invariants every tick')
    totleaps = 0
    for n in (4, 6, 8, 9, 12):
        pg = new_page(br, P3, 1900 + n, '?hedebug')
        r = ev(pg, '''n=>{HE.share=1;__start(2,n);let bad=[],leaps=0,landings=0,mxF=0,mxW=0,prevSt=new Map(),seed=n*7919;const rd=()=>{seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff};
        for(let i=0;i<6000;i++){
          if(i%40==0){K['@l']=rd()<.4;K['@r']=rd()<.4;K['@j']=rd()<.3;K['@f']=rd()<.6;K['@u']=rd()<.15;K['@d']=rd()<.1}
          if(i%900==450)maxhp=hp=99999;
          update();
          if(st!='play'){if(st=='over'){maxhp=hp=99999;st='play'}}
          let f=0;
          for(const e of E){if(!e.a||e.t!=8)continue;f++;
            const ps=prevSt.get(e);prevSt.set(e,e.st);
            if(ps!==undefined&&ps!=4&&e.st==4)leaps++;
            if(ps==4&&e.st==6){landings++;const cx=e.x+22;if(e.p.y>=GY-1&&X.some(q=>cx>q[0]-14&&cx<q[0]+q[1]+14)&&!e.p.t)bad.push(['spike-landing',i,cx]);if(lava&&e.p.y>=GY-20)bad.push(['lava-landing',i])}
            if(e.st!=4){if(!e.p)bad.push(['nop',i,e.st]);else{const dyy=Math.abs(e.y-(e.p.y-e.h));if(dyy>HE.fang.hopH+1e-6&&e.st!=2)bad.push(['offsurface',i,e.st,dyy]);if(e.p.t=='f')bad.push(['fading',i])}}
            else{if(e.p)bad.push(['airp',i]);if(!(e.y<H+31))bad.push(['fell',i,e.y])}
            if(!(e.x>=-1e-6&&e.x<=W-e.w+1e-6))bad.push(['xrange',i,e.x]);
          }
          mxF=Math.max(mxF,f);let w=0;for(const e of E)if(e.a&&e.t==6)w++;mxW=Math.max(mxW,w);
          if(pj.filter(q=>q.k=='cw').length>12)bad.push(['waves',i]);
          if(HE_ON==0){bad.push(['HE_OFF',i]);break}
        }
        return {bad:bad.slice(0,6),leaps,landings,mxF,mxW,tick,stage}}''', n)
        totleaps += r['leaps']
        check('stage %d: invariants hold (on a platform when grounded / e.p null + above the pit line when airborne, no spike/lava landings, inside the screen, <= 2 hounds, <= 2 widows, HE stays on); leaps=%d landings=%d maxHounds=%d' % (n, r['leaps'], r['landings'], r['mxF']),
              not r['bad'] and r['mxF'] <= 2 and r['mxW'] <= 2, r)
        check('stage %d: no page errors / warnings' % n, clean(pg), LOG(pg))
        pg.context.close()
    check('fuzz exercised the leap path (total leaps %d)' % totleaps, totleaps >= 3, totleaps)
    br.close()

print('\nRESULT: %d passed, %d failed' % (PASS[0], len(FAIL)))
for f in FAIL: print('  FAILED:', f)
sys.exit(1 if FAIL else 0)

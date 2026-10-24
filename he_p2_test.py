#!/usr/bin/env python3
"""HE part 2 test suite (headless Chromium via playwright): root system + Silk Widow (t6) + web patches.
Usage: python3 he_p2_test.py <aria_v32_p1.html> <aria_v32_p2.html> [shots_dir]
In-page harness (L3): requestAnimationFrame stubbed, Math.random seeded + counted, update()/draw0() driven by hand, ?hedebug for __heSpawn.
draw0() costs ~0.7 s per frame in this software-rendered sandbox, so frames are drawn sparsely."""
import sys, os
from playwright.sync_api import sync_playwright

P1, P2 = [os.path.abspath(p) for p in sys.argv[1:3]]
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

    # ------------------------------------------------------------------ [a] parity p1 vs p2
    print('\n[a] parity p1 vs p2: Easy/Normal (all stages) and Hard stages 1-2 (widow unlocks at 3) -> identical, incl. Math.random count')
    def run(path, d, n, seed, ticks=3000):
        pg = new_page(br, path, seed, '')
        ev(pg, '([d,n])=>__start(d,n)', [d, n])
        out = ev(pg, 't=>__drive(t)', ticks)
        out['errs'] = pg._errs + ev(pg, '__errs'); pg.context.close(); return out
    for d, n in [(0, 1), (0, 3), (0, 6), (0, 8), (0, 12), (1, 1), (1, 3), (1, 6), (1, 8), (1, 12), (2, 1), (2, 2)]:
        seed = 301 + d * 17 + n
        a = run(P1, d, n, seed); b = run(P2, d, n, seed)
        nm = 'dif%d stage%d' % (d, n)
        check(nm + ': spawn sequence identical (%d spawns)' % len(a['log']), a['log'] == b['log'] and len(a['log']) > 0)
        check(nm + ': final state + Math.random count identical', a['state'] == b['state'], '%s vs %s' % (a['state']['rc'], b['state']['rc']))
        check(nm + ': no page errors', not a['errs'] and not b['errs'], (a['errs'][:1], b['errs'][:1]))

    # ------------------------------------------------------------------ [b] registry + natural spawns
    print('\n[b] registry + natural spawn gating')
    pg = new_page(br, P2)
    r = ev(pg, '''()=>{const r=HEX[6];return {name:r.name,w:r.w,h:r.h,unlock:r.unlock,max:r.max,weight:r.weight,place:r.place,quiet:r.quiet,
      hp3:r.hp(3),hp7:r.hp(7),hp8:r.hp(8),hp14:r.hp(14),keys:Object.keys(HEX).join(','),pjhit:typeof HEH.pjHit.web,bl:HEH.blHit.length,
      root:HE.root,hasRoot:typeof heRoot,ps:DF[2].ps,bc:DF[2].bc}}''')
    check('HEX[6] registered: Silk Widow 40x34, unlock 3, max 2, weight 1, place ceiling', r['name'] == 'Silk Widow' and r['w'] == 40 and r['h'] == 34 and r['unlock'] == 3 and r['max'] == 2 and r['weight'] == 1 and r['place'] == 'ceiling' and not r['quiet'], r)
    check('hp = 4 + (stage>>3): 4 at stage 3/7, 5 at 8/14', (r['hp3'], r['hp7'], r['hp8'], r['hp14']) == (4, 4, 5, 5), r)
    check('t6 registered (later parts may add more), web pjHit + blHit hooks present, HE.root tunables', '6' in r['keys'].split(',') and r['pjhit'] == 'function' and r['bl'] == 1 and r['root'] == {'ticks': 130, 'mash': 8, 'imm': 150, 'shieldInv': 70}, r)
    def spawn_run(d, n, ticks=4000, share=1):
        pg = new_page(br, P2, 77 + n + d, '')
        ev(pg, '([d,n,s])=>{HE.share=s;__start(d,n)}', [d, n, share])
        mx = ev(pg, '''t=>{let mx=0,tot=0,seen=new Set();for(let i=0;i<t;i++){const ph=i%240;K['@r']=ph<70;K['@l']=ph>=120&&ph<190;K['@j']=(i%97)<6;K['@f']=(i%31)<4;update();
          let k=0;for(const e of E)if(e.a&&e.t==6){k++;if(!seen.has(e)){seen.add(e);tot++}}mx=Math.max(mx,k)}return [mx,tot]}''', ticks)
        e = pg._errs + ev(pg, '__errs'); w = ev(pg, '__warns'); pg.context.close(); return mx, e, w
    mx, e, w = spawn_run(2, 3)
    check('Hard stage 3 (share=1; the widow is the only eligible type there): widows spawn (%d), never more than max 2 alive (%d)' % (mx[1], mx[0]), mx[1] >= 1 and mx[0] <= 2, mx)
    check('  ... no errors / no HE warnings', not e and not w, (e[:1], w[:1]))
    for d, n, nm in [(2, 2, 'Hard stage 2 (locked)'), (0, 4, 'Easy stage 4'), (1, 4, 'Normal stage 4'), (2, 5, 'Hard boss stage 5'), (2, 10, 'Hard boss stage 10')]:
        mx, e, w = spawn_run(d, n, 2500)
        check(nm + ': no widow', mx[1] == 0, mx)

    # ------------------------------------------------------------------ [c] root core
    print('\n[c] root core (heRoot, movement lock, shoot/aim stay on, timer, mash, immunity, invulnerable states, shield)')
    pg = new_page(br, P2)
    def web_hit():
        return ev(pg, '''()=>{pj.push({x:pl.x+16,y:pl.y+21,vx:0,vy:0,r:9,c:'#8ffbff',k:'web',he:1});const h0=hp;hs=0;update();return {rt:pl.rt,rtI:pl.rtI,pj:pj.filter(q=>q.k=='web').length,dh:h0-hp,vx:pl.vx}}''')
    ev(pg, '__setup(3)'); ev(pg, '__tk(5)')
    r = web_hit()
    check('web ball on player: pl.rt == 130, ball removed, no damage', r['rt'] == 130 and r['pj'] == 0 and r['dh'] == 0, r)
    r = ev(pg, '''()=>{const x0=pl.x;K['@r']=1;__tk(30);const a=pl.x-x0;K['@r']=0;K['@l']=1;__tk(30);const b=pl.x-x0;K['@l']=0;return {a,b,vx:pl.vx,rt:pl.rt,g:!!pl.g}}''')
    check('rooted: holding right/left does not move the player (pl.vx = 0)', abs(r['a']) < 1e-9 and abs(r['b']) < 1e-9 and r['vx'] == 0, r)
    r = ev(pg, '''()=>{jb=8;K['@j']=1;const y0=pl.y;__tk(10);const d=pl.y-y0;K['@j']=0;return {d,g:!!pl.g,jb}}''')
    check('rooted: jump key ignored (still grounded, jump buffer flushed)', abs(r['d']) < 1e-9 and r['g'] and r['jb'] == 0, r)
    r = ev(pg, '''()=>{pl.dc=0;pl.dt=0;K['@d']=1;let m=0;__tk(10,()=>{m=Math.max(m,pl.dt)});K['@d']=0;return {m,dc:pl.dc}}''')
    check('rooted: dash ignored (pl.dt stays 0, cooldown not consumed)', r['m'] == 0 and r['dc'] <= 0, r)
    r = ev(pg, '''()=>{bl.length=0;pl.cool=0;K['@f']=1;K['@u']=1;let n=0,vy=0;__tk(20,()=>{});for(const b of bl){vy=Math.min(vy,b.vy)}n=bl.length;K['@u']=0;K['@f']=0;return {n,vy,rt:pl.rt}}''')
    check('rooted: shooting + aiming stay active (up-shots fired: %d, vy %.1f)' % (r['n'], r['vy']), r['n'] >= 1 and r['vy'] < -10 and r['rt'] > 0, r)
    r = ev(pg, '''()=>{bl.length=0;pl.cool=0;K['@f']=1;K['@l']=1;__tk(20);let vx=0;for(const b of bl)vx=Math.min(vx,b.vx);const d=pl.d;K['@f']=0;K['@l']=0;return {n:bl.length,vx,d,rt:pl.rt}}''')
    check('rooted: shooting left works (star vx<0, facing left)', r['n'] >= 1 and r['vx'] < -10 and r['d'] == -1, r)
    r = ev(pg, '''()=>{__setup(3);__tk(3);pl.y=60;pl.g=null;pl.vy=0;heRoot(130);const y0=pl.y,x0=pl.x;__tk(8);return {dy:pl.y-y0,dx:pl.x-x0,vy:pl.vy}}''')
    check('rooted in mid-air: gravity still applies, no horizontal drift', r['dy'] > 5 and abs(r['dx']) < 1e-9 and r['vy'] > 0, r)
    # timer
    r = ev(pg, '''()=>{__setup(3);__tk(3);pl.cool=1e9;heRoot(130);let n=0;while(pl.rt>0&&n<400){hs=0;update();n++}return {n,rt:pl.rt,rtI:pl.rtI}}''')
    check('unmashed root lasts exactly 130 ticks, then pl.rtI == 150', r['n'] == 130 and r['rtI'] == 150, r)
    r = ev(pg, '''()=>{web_=null;const out={};pj.push({x:pl.x+16,y:pl.y+21,vx:0,vy:0,r:9,c:'#8ffbff',k:'web',he:1});hs=0;update();out.rt=pl.rt;out.pj=pj.filter(q=>q.k=='web').length;out.dh=0;
      out.imm1=pl.rtI;__tk(149);out.imm2=pl.rtI;__tk(2);out.imm3=pl.rtI;return out}''')
    check('immunity: web ball during rtI does not root (and is removed); rtI counts down 150 -> 0', r['rt'] == 0 and r['pj'] == 0 and r['imm1'] in (149, 150) and r['imm2'] <= 1 and r['imm3'] == 0, r)
    r = web_hit()
    check('after immunity ends the player can be rooted again', r['rt'] == 130, r)
    # mash
    def mash(js):
        return ev(pg, js)
    r = mash('''()=>{__setup(3);__tk(3);heRoot(130);let n=0;while(pl.rt>0&&n<400){K['@l']=(n%2==0);K['@r']=(n%2==1);hs=0;update();n++}K['@l']=K['@r']=0;return {n,rtI:pl.rtI}}''')
    check('mash (alternating every tick): root breaks in %d ticks (<<130), immunity granted' % r['n'], r['n'] < 25 and r['rtI'] == 150, r)
    r = mash('''()=>{__setup(3);__tk(3);heRoot(130);let n=0;while(pl.rt>0&&n<400){const ph=n%6;K['@l']=ph<3;K['@r']=0;hs=0;update();n++}K['@l']=0;return {n}}''')
    check('same-direction repeats do not count (only the first edge): root lasts %d ticks' % r['n'], 115 <= r['n'] <= 124, r)
    r = mash('''()=>{__setup(3);__tk(3);heRoot(130);let n=0;while(pl.rt>0&&n<400){const ph=n%12;K['ArrowLeft']=ph<3;K['ArrowRight']=ph>=6&&ph<9;hs=0;update();n++}K={};return {n}}''')
    check('mash with real keys (ArrowLeft/ArrowRight): ~every 6 ticks alternating -> breaks in %d ticks' % r['n'], r['n'] < 90, r)
    r = mash('''()=>{__setup(3);__tk(3);heRoot(130);__tk(10);const a=pl.rt;hurt(1);const b=pl.rt;__tk(1);return {a,b,c:pl.rt}}''')
    check('taking damage never extends the root', r['b'] == r['a'] and r['c'] == r['a'] - 1, r)
    # who can be rooted
    r = ev(pg, '''()=>{const res={};
      const t=(nm,set,un)=>{__setup(3);__tk(2);set();res[nm]=heRoot(130);res[nm+'_rt']=pl.rt;un()};
      t('inv',()=>{pl.inv=50},()=>{});t('tmi',()=>{tm.i=50},()=>{});t('iv',()=>{iv=50},()=>{});t('au',()=>{au=50},()=>{});t('dt',()=>{pl.dt=5},()=>{});t('rtI',()=>{pl.rtI=50},()=>{});
      __setup(3);__tk(2);heRoot(130);res.again=heRoot(130);res.again_rt=pl.rt;
      __setup(3);__tk(2);sh=2;res.sh=heRoot(130);res.sh_rt=pl.rt;res.sh_left=sh;res.sh_inv=pl.inv;res.sh_hp=hp;
      return res}''')
    check('invulnerable states never root (pl.inv, tm.i, iv, au, pl.dt, rtI)', not any(r[k] for k in ('inv', 'tmi', 'iv', 'au', 'dt', 'rtI')) and not any(r[k + '_rt'] for k in ('inv', 'tmi', 'iv', 'au', 'dt', 'rtI')), r)
    check('already rooted -> second heRoot returns false and does not refresh', r['again'] is False and r['again_rt'] == 130, r)
    check('shield absorbs the web (sh-- , inv 70, no root, no damage)', r['sh'] is True and r['sh_rt'] == 0 and r['sh_left'] == 1 and r['sh_inv'] == 70 and r['sh_hp'] == 99999, r)
    r = ev(pg, '''()=>{__setup(3);__tk(3);heRoot(130);__tk(5);au=270;__tk(1);return {rt:pl.rt,rtI:pl.rtI}}''')
    check('Aurora (au>0) burns the silk away: root released, immunity set', r['rt'] == 0 and r['rtI'] >= 149, r)
    check('[c] no errors / no HE warnings', clean(pg), (pg._errs[:1], ev(pg, '__warns')[:1]))
    pg.context.close()

    # ------------------------------------------------------------------ [d] widow: drop/hang/shoot
    print('\n[d] widow behaviour: DROP 50f, HANG 60-90f, SHOOT tell 40f, aim lock (no lead), cooldown, no shot at rooted/immune player')
    pg = new_page(br, P2)
    ev(pg, '__setup(3)'); ev(pg, '__tk(3)')
    r = ev(pg, '''()=>{const e=__heSpawn(6,520,-40);const o={st0:e.st,tl:e.tl,hy:e.hy,hx:e.hx,y0:e.y};let n=0;while(e.st==0&&n<200){hs=0;update();n++}o.drop=n;o.hang=e.tm;o.hy2=e.y;o.hyOK=e.hy>=120&&e.hy<=320;o.dist=Math.hypot(e.hx+20-(pl.x+16),e.hy+17-(pl.y+21));return o}''')
    check('DROP lasts 50 ticks and ends at the hang point y in [120,320]', r['st0'] == 0 and r['drop'] == 50 and r['hyOK'], r)
    check('hang point keeps >= 220 px from the player', r['dist'] >= 220 - 1e-6, r)
    check('HANG length 60-90 ticks', 60 <= r['hang'] <= 90, r)
    r = ev(pg, '''()=>{const e=E.find(q=>q.t==6);const hang=e.tl;let n=0;while(e.st==1&&n<200){hs=0;update();n++}return {hang,n,st:e.st}}''')
    check('HANG ticks elapse exactly (tl == ticks until decision)', r['n'] == r['hang'] - 0 or r['n'] == r['hang'], r)
    # forced shoot
    r = ev(pg, '''()=>{__setup(3);__tk(3);K['@r']=1;const e=__heSpawn(6,560,150);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=1;e.cd=0;e.x0=e.x;e.y0=e.y;
      __withRand(.1,()=>{hs=0;update()});const o={st:e.st,tm:e.tm};
      let n=0,hist=[];while(!pj.some(q=>q.k=='web')&&n<100){hs=0;update();n++;hist.push([e.tx,pl.x+16])}
      const b=pj.find(q=>q.k=='web');o.n=n;o.estAfter=e.st;o.cd=e.cd;o.D=[DF[2].ps,DF[2].bc];
      o.ball=b?{r:b.r,k:b.k,he:b.he,sp:Math.hypot(b.vx,b.vy),c:b.c}:null;
      // aim: constant over the last lock ticks while the player keeps walking right
      o.tx=e.tx;o.ty=e.ty;o.locked=hist.slice(-18).every(h=>h[0]==hist[hist.length-18][0]);o.moved=hist[hist.length-1][1]-hist[hist.length-18][1];
      const mx=e.x+e.w/2,my=e.y+e.h/2+16;
      o.dirOK=b&&Math.abs(Math.atan2(b.vy,b.vx)-Math.atan2(e.ty-my,e.tx-mx))<1e-6;
      // no lead: direction towards the player's CURRENT position differs from the shot direction
      o.noLead=b&&Math.abs(Math.atan2(b.vy,b.vx)-Math.atan2(pl.y+21-my,pl.x+16-mx))>.02;
      K['@r']=0;return o}''')
    check('roll < .65 and ready -> TELL (st 2) with tm 40', r['st'] == 2 and r['tm'] == 40, r)
    check('web ball appears after exactly 40 more ticks (tell 40f)', r['n'] == 40 - 1 + 1 or r['n'] == 40, r)
    check('web ball: k web, r 9, speed 5*ps (=6), he:1; widow goes to REC (st 3), cooldown 150*bc (=120)', r['ball'] and r['ball']['k'] == 'web' and r['ball']['r'] == 9 and abs(r['ball']['sp'] - 5 * r['D'][0]) < 1e-9 and r['ball']['he'] == 1 and r['estAfter'] == 3 and r['cd'] == round(150 * r['D'][1]), r)
    check('aim is locked for the last 18 ticks while the player keeps moving (moved %.0f px)' % r['moved'], r['locked'] and r['moved'] > 30, r)
    check('shot direction == locked aim point; NOT a lead shot', r['dirOK'] and r['noLead'], r)
    # no shot at rooted / immune
    r = ev(pg, '''()=>{__setup(3);__tk(3);const e=__heSpawn(6,560,150);e.hx=e.x;e.hy=e.y;e.st=2;e.tl=e.tm=40;e.tx=pl.x;e.ty=pl.y;e.cd=0;
      __tk(10);pl.rtI=200;let n=0;__tk(60);return {st:e.st,balls:pj.filter(q=>q.k=='web').length}}''')
    check('immune player: the tell is cancelled, no web ball', r['balls'] == 0 and r['st'] in (1, 2, 4, 5), r)
    r = ev(pg, '''()=>{__setup(3);__tk(3);const e=__heSpawn(6,560,150);e.hx=e.x;e.hy=e.y;e.st=2;e.tl=e.tm=40;e.tx=pl.x;e.ty=pl.y;e.cd=0;
      __tk(10);heRoot(130);__tk(2);return {st:e.st,balls:pj.filter(q=>q.k=='web').length}}''')
    check('rooted player: tell cancelled -> punish (st 6), no web ball', r['balls'] == 0 and r['st'] == 6, r)
    r = ev(pg, '''()=>{__setup(3);__tk(3);const e=__heSpawn(6,560,150);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=1;e.cd=0;pl.rtI=100;
      __withRand(.1,()=>{hs=0;update()});return {st:e.st}}''')
    check('decision with rtI>0 never starts a shot (goes to the trap instead: CLIMB st 4)', r['st'] == 4, r)
    r = ev(pg, '''()=>{__setup(3);__tk(3);const e=__heSpawn(6,560,150);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=1;e.cd=50;
      __withRand(.1,()=>{hs=0;update()});return {st:e.st,tm:e.tm}}''')
    check('decision while on cooldown: keeps hanging (no shot before cd expires)', r['st'] == 1 and 10 <= r['tm'] <= 40, r)
    # web ball vs floor / generic hit never hurts
    r = ev(pg, '''()=>{__setup(3,100);__tk(3);pj.push({x:600,y:GY-20,vx:0,vy:8,r:9,c:'#8ffbff',k:'web',he:1});__tk(5);return {n:pj.filter(q=>q.k=='web').length}}''')
    check('web ball vanishes on the floor', r['n'] == 0, r)
    check('[d] no errors / no HE warnings', clean(pg), (pg._errs[:1], ev(pg, '__warns')[:1]))
    pg.context.close()

    # ------------------------------------------------------------------ [e] web patches
    print('\n[e] web patches: planting rules, ghost->solid, root on touch, stars, cap 5, expiry, clear on reset')
    pg = new_page(br, P2)
    r = ev(pg, '''()=>{__setup(6,60);__tk(3);const res={plants:[],bad:[],dist:[]};
      const e=__heSpawn(6,700,150);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=1;e.cd=1e9;
      __withRand(.9,()=>{hs=0;update()});res.st=e.st;
      let seen=0,n=0;
      const chk=()=>{for(const q of wb){if(q._s)continue;q._s=1;res.plants.push([wdT,Math.round(q.x),Math.round(q.y),q.w,q.h,q.life]);
        const pf=P.find(p=>!p.t&&!p.fx&&q.y==p.y-30&&q.x>=p.x&&q.x+46<=p.x+p.w);if(!pf)res.bad.push(['platform',q.x,q.y]);
        else if(pf.y>=GY-1&&X.some(x=>q.x+46>x[0]-8&&q.x<x[0]+x[1]+8))res.bad.push(['pit',q.x]);
        res.dist.push(Math.hypot(q.x+23-(pl.x+16),q.y+15-(pl.y+21)))}};
      while(n<400&&(e.st!=1||n<5)){hs=0;update();chk();n++}
      res.n=n;res.count=wb.length;res.lastSt=e.st;res.sc=e.sc;res.plan=e.plan.length;return res}''')
    check('TRAP: roll >= .65 -> CLIMB (st 4)', r['st'] == 4, r)
    check('patches planted (%d): 1-2 per trap, geometry 46x30, life 1500' % r['count'], 1 <= r['count'] <= 2 and all(q[3] == 46 and q[4] == 30 and q[5] == 1500 for q in r['plants']), r)
    check('every patch on top of a STATIC platform (no p.t, no p.fx), never over a pit', not r['bad'], r['bad'])
    check('every patch >= 120 px from the player', all(d >= 120 for d in r['dist']), r['dist'])
    r = ev(pg, '''()=>{__setup(3,60);__tk(2);const res={};wb.length=0;wdPlant({x:700,y:GY-30});const q=wb[0];res.born=q.born;
      // ghost: harmless to the player, not hit by stars
      pl.x=q.x+5;pl.y=q.y+5;pl.vy=0;__tk(1);res.rtGhost=pl.rt;res.wbGhost=wb.length;
      pl.x=100;pl.y=GY-42;bl.push({x:q.x+10,y:q.y+10,vx:0,vy:0,l:30,h:[],hm:false});__tk(1);res.starGhost=bl.length;res.wbGhost2=wb.length;bl.length=0;
      __tk(40-3);res.age=wdT-q.born;return res}''')
    check('ghost phase: stepping into it does not root, patch stays; stars pass through', r['rtGhost'] == 0 and r['wbGhost'] == 1 and r['wbGhost2'] == 1 and r['starGhost'] == 1, r)
    r = ev(pg, '''()=>{__setup(3,60);__tk(2);wb.length=0;wdPlant({x:700,y:GY-30});const q=wb[0];wdT+=38;const res={};
      pl.x=q.x+5;pl.y=GY-42;pl.vy=0;__tk(1);res.rt39=pl.rt;res.wb39=wb.length;
      pl.x=q.x+5;pl.y=GY-42;pl.vy=0;__tk(1);res.rt=pl.rt;res.wb=wb.length;res.hp=hp;return res}''')
    check('ghost -> solid after 40 ticks; touching a solid patch roots (pl.rt ~130) and consumes it, no damage', r['rt39'] == 0 and r['wb39'] == 1 and r['rt'] == 130 and r['wb'] == 0 and r['hp'] == 99999, r)
    r = ev(pg, '''()=>{__setup(3,60);__tk(2);wb.length=0;wdPlant({x:700,y:GY-30});wb[0].born-=100;pl.x=wb[0].x+5;pl.y=GY-42;pl.rtI=100;__tk(2);const r1={wb:wb.length,rt:pl.rt};return r1}''')
    check('immune player walking through a solid patch: not rooted, patch NOT consumed', r['rt'] == 0 and r['wb'] == 1, r)
    r = ev(pg, '''()=>{__setup(3,60);__tk(2);wb.length=0;wdPlant({x:700,y:GY-30});wb[0].born-=100;const q=wb[0];const res={};
      tm.p=0;bl.push({x:q.x+10,y:q.y+10,vx:0,vy:0,l:30,h:[],hm:false});__tk(1);res.normal_wb=wb.length;res.normal_bl=bl.filter(b=>b.l>0).length;bl.length=0;
      wdPlant({x:700,y:GY-30});wb[0].born-=100;const q2=wb[0];tm.p=300;bl.push({x:q2.x+10,y:q2.y+10,vx:0,vy:0,l:30,h:[],hm:false});__tk(1);res.pierce_wb=wb.length;res.pierce_bl=bl.length;tm.p=0;return res}''')
    check('normal star destroys a solid patch and is consumed', r['normal_wb'] == 0 and r['normal_bl'] == 0, r)
    check('pierce star (tm.p>0) destroys the patch and keeps flying', r['pierce_wb'] == 0 and r['pierce_bl'] == 1, r)
    r = ev(pg, '''()=>{__setup(3,60);__tk(2);wb.length=0;const res={};for(let i=0;i<7;i++){wdPlant({x:20+i*60,y:GY-30});wdT+=2}
      res.total=wb.length;res.alive=wb.filter(q=>!q.dy).length;res.dying=wb.filter(q=>q.dy).length;res.dyOldest=wb[0].dy>0&&wb[1].dy>0;
      __tk(40);res.after=wb.length;res.alive2=wb.filter(q=>!q.dy).length;return res}''')
    check('cap: never more than 5 alive; the oldest ones fade (dy) and are removed afterwards', r['alive'] == 5 and r['dying'] == 2 and r['dyOldest'] and r['after'] == 5 and r['alive2'] == 5, r)
    r = ev(pg, '''()=>{__setup(3,60);__tk(2);wb.length=0;wdPlant({x:700,y:GY-30});const q=wb[0];q.born=wdT-(40+1500-2);__tk(1);const a=wb.length;__tk(3);return {a,b:wb.length}}''')
    check('patch expires after ghost 40 + life 1500 ticks', r['a'] == 1 and r['b'] == 0, r)
    r = ev(pg, '''()=>{__setup(3,60);__tk(2);wdPlant({x:700,y:GY-30});heRoot(130);pj.push({x:10,y:10,vx:0,vy:1,r:9,c:'#fff',k:'web',he:1});clearStage();return {wb:wb.length,rt:pl.rt,rtI:pl.rtI}}''')
    check('clearStage() / reset hook: patches cleared, root + immunity reset', r['wb'] == 0 and r['rt'] == 0 and r['rtI'] == 0, r)
    r = ev(pg, '''()=>{__setup(3,60);__tk(2);wdPlant({x:700,y:GY-30});heRoot(130);load(4);return {wb:wb.length,rt:pl.rt}}''')
    check('load(n) (retry/respawn): patches + root cleared', r['wb'] == 0 and r['rt'] == 0, r)
    check('[e] no errors / no HE warnings', clean(pg), (pg._errs[:1], ev(pg, '__warns')[:1]))
    pg.context.close()

    # ------------------------------------------------------------------ [f] punish / bite
    print('\n[f] punish: lowers toward a rooted player, bites after >=90f with a 20f tell, mash/kill wins the race')
    pg = new_page(br, P2)
    r = ev(pg, '''()=>{__setup(3,300);__tk(3);const e=__heSpawn(6,480,120);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=999;e.cd=1e9;pl.cool=1e9;
      if(!heRoot(130))throw new Error('root not applied');const h0=hp;let n=0,t6=-1,t7=-1,t8=-1,rtEnd=-1;
      while(n<200&&t8<0){hs=0;update();n++;if(e.st==6&&t6<0)t6=n;if(e.st==7&&t7<0)t7=n;if(e.st==8&&t8<0)t8=n;if(pl.rt<=0&&rtEnd<0)rtEnd=n}
      return {t6,t7,t8,rtEnd,dh:h0-hp,st:e.st,ex:e.x,exp:pl.x}}''')
    check('rooted player: widow switches HANG -> LOWER (st 6) at once', r['t6'] == 1, r)
    check('bite tell starts no earlier than 90 ticks after the punish began', r['t7'] >= 1 + 90 - 1, r)
    check('bite tell lasts exactly 20 ticks, then the bite hurts the rooted player (1 hp)', r['t8'] - r['t7'] == 20 and r['dh'] == 1, r)
    r = ev(pg, '''()=>{__setup(3,300);__tk(3);const e=__heSpawn(6,480,120);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=999;e.cd=1e9;pl.cool=1e9;
      heRoot(130);const h0=hp;let n=0,st7=-1,cancel=-1;
      while(n<300){K['@l']=(n%6<3);K['@r']=(n%6>=3);hs=0;update();n++;if(e.st==7&&st7<0)st7=n;if(pl.rt<=0)break}
      K['@l']=K['@r']=0;const afterFree=e.st;__tk(3);return {n,st7,st:afterFree,st2:e.st,dh:h0-hp}}''')
    check('mashing free (~10 presses/s) before the bite: no damage, widow retreats (CLIMB st 4)', r['dh'] == 0 and r['st2'] in (4, 0) and (r['st7'] < 0 or r['st7'] > r['n']), r)
    r = ev(pg, '''()=>{__setup(3,300);__tk(3);const e=__heSpawn(6,480,120);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=999;e.cd=1e9;pl.cool=1e9;
      heRoot(130);const h0=hp;let n=0,seen7=0,cancelled=0;
      while(n<250){if(e.st==7&&!seen7){seen7=n;K['@l']=1}if(seen7&&n>seen7){K['@l']=(n%2==0);K['@r']=(n%2==1)}hs=0;update();n++;if(seen7&&pl.rt<=0)break}
      K['@l']=K['@r']=0;const st=e.st;__tk(2);return {n,seen7,st,st2:e.st,dh:h0-hp}}''')
    check('breaking free DURING the bite tell cancels the bite (no damage)', r['seen7'] > 0 and r['dh'] == 0 and r['st2'] in (4, 0), r)
    r = ev(pg, '''()=>{__setup(3,300);__tk(3);const e=__heSpawn(6,300-20+16,pl.y-34-6-80);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=999;e.cd=1e9;
      heRoot(130);const h0=hp;let n=0,killed=-1;K['@f']=1;K['@u']=1;pl.cool=0;
      while(n<200){hs=0;update();n++;if(!e.a&&killed<0){killed=n;break}}
      K['@f']=K['@u']=0;return {n,killed,dh:h0-hp,dead:wdDead.length,hp:e.hp}}''')
    check('rooted player who shoots the widow (4 hp) up wins the race: killed at tick %d (< 110), no bite damage' % r['killed'], 0 < r['killed'] < 110 and r['dh'] == 0, r)
    r = ev(pg, '''()=>{__setup(3,300);__tk(3);const e=__heSpawn(6,300,150);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=999;e.cd=1e9;
      __tk(3);const a=e.st;heRoot(130);const h0=hp;let n=0;while(n<400&&!(e.st==8)){hs=0;update();n++}
      // everything still alive after the strike: widow retreats to the ceiling and drops again
      let seen4=0;__tk(60,()=>{if(e.st==4)seen4=1});return {a,n,seen4,st:e.st}}''')
    check('after the bite the widow retreats (CLIMB) and re-hangs', r['seen4'] == 1, r)
    # stomp / death / dazed
    r = ev(pg, '''()=>{__setup(3,300);__tk(3);const e=__heSpawn(6,284,300);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=999;e.cd=1e9;e.born=-99;
      pl.x=e.x+4;pl.y=e.y-60;pl.vy=6;pl.g=null;const h0=e.hp;let k=0;__tk(12,()=>{});return {h0,h1:e.hp,vy:pl.vy,dh:99999-hp}}''')
    check('widow is stomp-able from above (default contact): hp 4 -> 2, player bounces, no damage', r['h0'] == 4 and r['h1'] == 2 and r['dh'] == 0, r)
    r = ev(pg, '''()=>{__setup(3,100);__tk(3);const e=__heSpawn(6,560,150);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=999;e.cd=1e9;const y0=e.y;e.z=60;__tk(20);return {st:e.st,tm:e.tm,dz:e.dz}}''')
    check('Neon-Star daze: AI frozen (state/timer untouched)', r['st'] == 1 and r['tm'] == 999 and r['dz'], r)
    r = ev(pg, '''()=>{__setup(3,100);__tk(3);const e=__heSpawn(6,560,150);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=999;e.cd=1e9;const s0=score;hitE(e,99);__tk(2);return {a:e.a,dead:wdDead.length,score:score-s0,th:wdDead[0]&&wdDead[0].th}}''')
    check('death: score 420 (t6 entry), husk spawned, thread-snap flag set', r['a'] == 0 and r['dead'] == 1 and r['th'] == 1 and r['score'] >= 420, r)
    check('[f] no errors / no HE warnings', clean(pg), (pg._errs[:1], ev(pg, '__warns')[:1]))
    pg.context.close()

    # ------------------------------------------------------------------ [g] heFail paths
    print('\n[g] failure paths -> heFail, game continues like v31 (no root left over)')
    def fail_case(nm, js):
        pg = new_page(br, P2)
        ev(pg, '__setup(3,300)'); ev(pg, '__tk(3)')
        r = ev(pg, js)
        e = ev(pg, '''()=>{__tk(5);return {on:HE_ON,rt:pl.rt,rtI:pl.rtI,wb:wb.length,webs:pj.filter(q=>q.k=='web').length,hw:E.filter(q=>q.a&&q.t==6).length,x:pl.x}}''')
        check(nm + ': HE_ON=0, widows gone, patches/webs gone, no root left', e['on'] == 0 and e['rt'] == 0 and e['wb'] == 0 and e['webs'] == 0 and e['hw'] == 0, (r, e))
        r2 = ev(pg, '''()=>{const x0=pl.x;K['@r']=1;__tk(20);K['@r']=0;return pl.x-x0}''')
        check(nm + ': player moves normally afterwards', r2 > 10, r2)
        pg.context.close()
    fail_case('throw in ai', '''()=>{const e=__heSpawn(6,560,150);heRoot(130);wdPlant({x:700,y:GY-30});const o=HEX[6].ai;HEX[6].ai=()=>{throw new Error('x')};hs=0;update();return 1}''')
    fail_case('throw in draw', '''()=>{const e=__heSpawn(6,560,150);heRoot(130);wdPlant({x:700,y:GY-30});HEX[6].draw=()=>{throw new Error('x')};RA=.5;ipOn();draw0();return 1}''')
    fail_case('throw in pjHit.web', '''()=>{__heSpawn(6,560,150);heRoot(130);wdPlant({x:700,y:GY-30});pj.push({x:600,y:300,vx:0,vy:0,r:9,c:'#fff',k:'web',he:1});HEH.pjHit.web=()=>{throw new Error('x')};hs=0;update();return 1}''')
    fail_case('throw in blHit', '''()=>{__heSpawn(6,560,150);heRoot(130);wdPlant({x:700,y:GY-30});HEH.blHit[0]=()=>{throw new Error('x')};bl.push({x:400,y:300,vx:0,vy:0,l:30,h:[],hm:false});hs=0;update();return 1}''')
    fail_case('throw in step hook', '''()=>{__heSpawn(6,560,150);heRoot(130);wdPlant({x:700,y:GY-30});HEH.step.push(()=>{throw new Error('x')});hs=0;update();return 1}''')
    fail_case('throw in heRtTick (root tick)', '''()=>{__heSpawn(6,560,150);heRoot(130);wdPlant({x:700,y:GY-30});window.act=null;const o=heRtTick;heRtTick=function(){throw new Error('x')};hs=0;update();return 1}''')

    # ------------------------------------------------------------------ [h] drawing + determinism + screenshots
    print('\n[h] drawing: every state, patches, web ball, cocoon, husk, dissolve snapshot; deterministic (no Math.random in draw)')
    pg = new_page(br, P2)
    ev(pg, '__setup(6,300)'); ev(pg, '__tk(3)')
    r = ev(pg, '''()=>{const e=__heSpawn(6,520,170);e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=9999;e.cd=1e9;
      wdPlant({x:640,y:GY-30});wdPlant({x:760,y:GY-30});wb[0].born-=100;
      pj.push({x:430,y:330,vx:6,vy:0,r:9,c:'#8ffbff',k:'web',he:1});
      wdDead.push({x:200,y:200,vx:0,vy:0,rot:.4,vr:0,age:5,id:1.3,tx:220,thY:210,th:1});
      const o={};RA=.5;ipOn();draw0();const r0=__rc;const a=document.querySelector('canvas').toDataURL();draw0();const b=document.querySelector('canvas').toDataURL();
      o.rcDraw=__rc-r0;o.len=a.length;
      const hash=()=>{c.setTransform(1,0,0,1,0,0);c.globalAlpha=1;c.globalCompositeOperation='source-over';c.shadowBlur=0;c.clearRect(0,0,W,H);
        const ee=E.find(q=>q.t==6);heDrawH(HEH.drawBack);heDraw(ee);heDrawH(HEH.drawFront);pl.rt=60;heRt.max=130;heDrawH(HEH.drawPlayer,pl.x+16,pl.y+21);pl.rt=0;return c.canvas.toDataURL()};
      const h1=hash(),h2=hash();o.same=h1===h2;o.nonEmpty=h1.length>3000;return o}''')
    check('draw0 with widow(HANG), ghost+solid patches, web ball, husk: no Math.random calls inside draw', r['rcDraw'] == 0, r)
    check('widow/patch/web-ball/husk/cocoon painters deterministic (two renders of the same state give identical pixels, non-empty)', r['same'] and r['nonEmpty'], r)
    states = ev(pg, '''()=>{const e=E.find(q=>q.t==6);const res=[];const w2=[];
      const cfgs=[[0,e=>{e.st=0;e.tl=50;e.tm=25;e.x0=e.x;e.y0=-40}],[2,e=>{e.st=2;e.tl=40;e.tm=14;e.tx=pl.x+16;e.ty=pl.y+21}],[2,e=>{e.st=2;e.tl=40;e.tm=30;e.tx=pl.x+16;e.ty=pl.y+21}],[5,e=>{e.st=5;e.y=4;e.plan=[];e.pi=0;e.sc=0}],[6,e=>{e.st=6}],[7,e=>{e.st=7;e.tl=20;e.tm=8}],[8,e=>{e.st=8;e.tl=8;e.tm=4}]];
      for(const [s,f] of cfgs){f(e);if(s==5||s==6||s==7)heRoot(130);RA=.5;draw0();res.push([s,HE_ON])}
      return res}''')
    check('draw0 in every widow state (DROP, TELL early/locked, SCUT, LOWER, BITE tell, STRIKE) + cocoon: HE stays on', all(x[1] == 1 for x in states) and clean(pg), (states, pg._errs[:1], ev(pg, '__warns')[:1]))
    r = ev(pg, '''()=>{const e=E.find(q=>q.t==6);hitE(e,99);const o=[];for(let i=0;i<4;i++){hs=0;update();RA=.5;draw0();o.push(HE_ON)}return {o,dead:wdDead.length,enG:typeof enG!='undefined'?enG.length:-1}}''')
    check('death dissolve snapshot (dd) + falling husk draw without errors', all(x == 1 for x in r['o']) and clean(pg), (r, pg._errs[:1], ev(pg, '__warns')[:1]))
    if SHOTS:
        os.makedirs(SHOTS, exist_ok=True)
        pg2 = new_page(br, P2)
        ev(pg2, '__setup(3,300)'); ev(pg2, '()=>{bn=0;__tk(3)}')   # bn=0: no stage-intro iris in the screenshots
        def shot(nm, js):
            ev(pg2, js); ev(pg2, '()=>{RA=.5;ipOn();draw0()}')
            pg2.locator('canvas').first.screenshot(path=os.path.join(SHOTS, nm + '.png'))
        shot('widow_hang', '''()=>{E.length=0;pj.length=0;wb.length=0;const e=__heSpawn(6,430,150);e.born=-99;e.hx=e.x;e.hy=e.y;e.st=1;e.tl=e.tm=9999;e.cd=1e9;wdPlant({x:640,y:GY-30});wdPlant({x:760,y:GY-30});wb[0].born-=100;pj.push({x:520,y:330,vx:6,vy:0,r:9,c:'#8ffbff',k:'web',he:1})}''')
        shot('widow_tell', '''()=>{const e=E.find(q=>q.t==6);e.st=2;e.tl=40;e.tm=12;e.tx=pl.x+16;e.ty=pl.y+21}''')
        shot('rooted_cocoon', '''()=>{E.length=0;pj.length=0;heRoot(130);pl.rt=70}''')
        pg2.context.close()
    pg.context.close()

    # ------------------------------------------------------------------ [i] fuzz
    print('\n[i] fuzz: Hard stages 3,4,6,8,9,12 x 6000 ticks, widows forced (share=1), scripted random input; invariants every tick')
    for n in (3, 4, 6, 8, 9, 12):
        pg = new_page(br, P2, 900 + n, '?hedebug')
        r = ev(pg, '''n=>{HE.share=1;__start(2,n);let bad=[],mxRt=0,mxI=0,mxWb=0,mxW=0,roots=0,prev=0,bites=0,seed=n*7919;const rd=()=>{seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff};
        for(let i=0;i<6000;i++){
          if(i%40==0){K['@l']=rd()<.4;K['@r']=rd()<.4;K['@j']=rd()<.3;K['@f']=rd()<.6;K['@u']=rd()<.15;K['@d']=rd()<.1}
          if(i%900==450)maxhp=hp=99999;
          const hb=hp,tb=tick;update();
          if(st!='play'){if(st=='over'){maxhp=hp=99999;st='play'}}
          mxRt=Math.max(mxRt,pl.rt||0);mxI=Math.max(mxI,pl.rtI||0);mxWb=Math.max(mxWb,wb.length);
          if((pl.rt>0)&&!prev)roots++;prev=pl.rt>0?1:0;
          let w=0;for(const e of E)if(e.a&&e.t==6){w++;if(!(e.x>-200&&e.x<1200&&e.y>-80&&e.y<700))bad.push(['widowpos',i,e.x,e.y,e.st])}
          mxW=Math.max(mxW,w);
          if(pl.rt>0&&pl.vx!==0&&hp>=hb&&tick!==tb)bad.push(['vx',i,pl.vx]);   /* hurt() sets the knockback vx at the end of a tick and hit-stop (tick frozen) keeps it for 4 ticks; the next real tick zeroes it before any movement */
          if(wb.filter(q=>!q.dy).length>5)bad.push(['cap',i]);
          for(const q of wb){const pf=P.find(p=>!p.t&&!p.fx&&q.y==p.y-30&&q.x>=p.x&&q.x+46<=p.x+p.w);if(!pf){bad.push(['patch',i,q.x,q.y]);break}}
          if(HE_ON==0){bad.push(['HE_OFF',i]);break}
        }
        return {bad:bad.slice(0,5),mxRt,mxI,mxWb,mxW,roots,tick,stage}}''', n)
        check('stage %d: invariants hold (root<=130, immunity<=150, alive patches<=5 & on static platforms, vx==0 while rooted, widows<=2, HE stays on); roots=%d, maxWidows=%d' % (n, r['roots'], r['mxW']),
              not r['bad'] and r['mxRt'] <= 130 and r['mxI'] <= 150 and r['mxWb'] <= 9 and r['mxW'] <= 2, r)
        check('stage %d: no page errors / warnings' % n, clean(pg), (pg._errs[:1], ev(pg, '__warns')[:1]))
        pg.context.close()
    br.close()

print('\nRESULT: %d passed, %d failed' % (PASS[0], len(FAIL)))
for f in FAIL: print('  FAILED:', f)
sys.exit(1 if FAIL else 0)

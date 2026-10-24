#!/usr/bin/env python3
"""Patch aria_v31.html -> aria_v32_p1.html  (HE part 1: foundation, no visible enemy).
Usage: python3 patch_v32_p1.py aria_v31.html aria_v32_p1.html
Every edit is an exact-string replacement that must match exactly once (assert), so the script
reproduces the output byte-for-byte from the untouched v31 and refuses to run on anything else."""
import sys, hashlib

src_path, out_path = sys.argv[1], sys.argv[2]
s = open(src_path, encoding='utf-8').read()
assert s.count('HE part') == 0, 'input already contains HE parts (must be the untouched v31)'

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, 'anchor count %d != %d: %r' % (c, n, old[:80])
    s = s.replace(old, new)

BLOCK = r'''/* ===== HE part 1: foundation ===== */
/* Hard-mode enemy framework: registry HEX, hooks HEH, spawn gating. NO enemy is registered here; parts 2-6 add t6..t10 with HEX[t]={...}.
   HE_ON=0 -> exact v31 behaviour (heFail() sets it on any exception in HE code). Active only when dif==2 (heOn()). Tunables: const HE.
   Hook semantics (see HANDOFF.md): pjHit[k] true = handled (the HANDLER removes pj[i] itself if it wants it gone; the loop then skips the generic hit test);
   blHit true = star consumed (the loop removes the star); every drawX hook runs inside its own c.save()/c.restore(). */
let HE_ON=1;
const HE_DEBUG=/[?&]hedebug/.test(location.search)?1:0;
const HE={maxNew:2,maxNewLate:3,lateStage:10,minDist:220,share:.3};
const HEX={};
const HEH={step:[],reset:[],drawBack:[],drawFront:[],drawPlayer:[],pjHit:{},blHit:[]};
const heSeen=new Set();let heDirty=0;
function heOn(){return HE_ON&&dif==2}
function heRun(){heSeen.clear()}
function heFail(err){
  if(!HE_ON)return;
  HE_ON=0;heDirty=1;
  try{console.warn('Hard enemies (HE) disabled:',err)}catch(_){}
  try{for(const e of E)if(HEX[e.t])e.a=0}catch(_){}
}
/* deferred clean-up (never reshuffles pj/bl while their loops run): HE enemies gone, HE projectiles gone, reset hooks run once */
function heSweep(){
  heDirty=0;
  try{for(const e of E)if(HEX[e.t])e.a=0}catch(_){}
  try{for(let i=pj.length-1;i>=0;i--){const q=pj[i];if(q.he||(q.k&&HEH.pjHit[q.k]))pj.splice(i,1)}}catch(_){}
  for(const f of HEH.reset){try{f()}catch(_){}}
}
function heReset(){if(heDirty)heSweep();if(!HE_ON)return;for(const f of HEH.reset){try{f()}catch(x){heFail(x)}}}
function heStep(px,py){
  if(heDirty)heSweep();
  if(!HE_ON||dif!=2)return;
  for(const f of HEH.step){try{f(px,py)}catch(x){heFail(x);return}}
}
function heBl(b,i){
  for(const f of HEH.blHit){let h=0;try{h=f(b,i)}catch(x){heFail(x);return false}if(h)return true}
  return false;
}
function heDrawH(arr,px,py){
  if(!HE_ON||!arr.length)return;
  for(const f of arr){c.save();try{f(px,py)}catch(x){heFail(x)}c.restore()}
}
/* painter of an HE enemy (called from dE2/dE2O; also with the death-dissolve snapshot, which carries a copy of every field of e plus fl=1,dd=1) */
function heDraw(e){
  if(!HE_ON)return;
  const r=HEX[e.t];c.save();
  try{if(e.fl>0)fGl(e.x+e.w/2,e.y+e.h/2,Math.max(e.w,e.h)*.9+8,'#ffffff',.28);r.draw(e)}catch(x){heFail(x)}
  c.restore();
}
/* one-time pop-up per run and type; optional registry fields: hint (text), col (colour) */
function heHint(t){if(heSeen.has(t))return;heSeen.add(t);const r=HEX[t];if(r)pop(W/2,130,r.hint||(r.name+'!'),r.col||'#ffd84d')}
function heAlive(t){let n=0;for(const q of E)if(q.a&&q.t===t)n++;return n}
function heNear(e){return Math.hypot(e.x+e.w/2-(pl.x+16),e.y+e.h/2-(pl.y+21))>=HE.minDist}
/* try to place e; true = e.x/e.y (and e.p for platform walkers) are set */
function hePlace(r,e){
  const px=pl.x+16,pk=r.place;
  if(pk=='ceiling'){e.x=clamp(px+(Math.random()<.5?-1:1)*rnd(200,360),30,W-30-e.w);e.y=-40;return true}
  if(pk=='air'){e.x=clamp(px+(Math.random()<.5?-1:1)*rnd(220,380),30,W-60);e.y=rnd(100,380);return true}
  if(pk=='platform'){
    const cs=P.filter(p=>!p.fx&&p.t!='f'&&(!p.t||r.moving)&&p.w>=e.w+8);
    if(!cs.length)return false;
    const p=cs[(Math.random()*cs.length)|0],x=rnd(p.x+4,p.x+p.w-e.w-4);
    if(p.y>=GY-1&&X.some(q=>x+e.w>q[0]-8&&x<q[0]+q[1]+8))return false;
    if(Math.abs(x+e.w/2-px)<=HE.minDist)return false;
    e.p=p;e.x=x;e.y=p.y-e.h;return true;
  }
  if(typeof pk=='function')return !!pk(e);
  return false;
}
function heMake(t){
  const r=HEX[t];if(!r)return null;
  const e={t,w:r.w,h:r.h,hp:r.hp(stage),a:1,fl:0,d:Math.random()<.5?-1:1,cd:80,id:Math.random()*9,born:tick,mn:100,tp:0,sp:(1+stage*.12)*D.es,st:0,tm:0};
  let ok=0;
  for(let k=0;k<6&&!ok;k++){e.p=undefined;ok=hePlace(r,e)&&heNear(e)}
  if(!ok)return null;
  if(!e.p)delete e.p;
  if(r.init)r.init(e);
  return e;
}
/* called first thing in spawn(); true = a new HE enemy was created (the legacy spawn is then skipped). No Math.random is consumed unless a type can actually spawn. */
function heSpawn(){
  try{
    if(!heOn()||bs||st!='play')return false;
    let tot=0;for(const q of E)if(q.a&&HEX[q.t])tot++;
    if(tot>=(stage>=HE.lateStage?HE.maxNewLate:HE.maxNew))return false;
    const cs=[];let sw=0;
    for(const k in HEX){const r=HEX[k];if(r.unlock<=stage&&heAlive(+k)<r.max){cs.push(+k);sw+=r.weight||1}}
    if(!cs.length||!(Math.random()<HE.share))return false;
    let u=Math.random()*sw,t=cs[0];
    for(const k of cs){u-=HEX[k].weight||1;if(u<0){t=k;break}}
    const e=heMake(t);if(!e)return false;
    E.push(e);
    if(!HEX[t].quiet){burst(e.x+e.w/2,e.y+e.h/2,'#9b5de5',8,3);heHint(t)}
    return true;
  }catch(x){heFail(x);return false}
}
/* debug (only with ?hedebug in the URL): __heSpawn(t,x,y) ignores every gate; __heHard() selects Hard */
if(HE_DEBUG){
  window.__heHard=()=>setDif(2);
  window.__heSpawn=(t,x,y)=>{
    const r=HEX[t];if(!r)return null;
    const e={t,w:r.w,h:r.h,hp:r.hp(stage),a:1,fl:0,d:1,cd:80,id:Math.random()*9,born:tick,mn:100,tp:0,sp:(1+stage*.12)*D.es,st:0,tm:0};
    e.x=x===undefined?pl.x+260:x;e.y=y===undefined?200:y;
    if(r.place=='platform'){let b=null;for(const p of P)if(e.x+e.w/2>=p.x&&e.x+e.w/2<=p.x+p.w&&p.y>=e.y&&(!b||p.y<b.y))b=p;if(b){e.p=b;e.y=b.y-e.h}}
    if(r.init)r.init(e);E.push(e);return e;
  };
}
/* ===== /HE part 1 ===== */
'''

# 1) block + spawn() gate -------------------------------------------------------------------
rep("function spawn(){\n  const pool=[0];",
    BLOCK + "function spawn(){\n  if(heOn()&&heSpawn())return;/*HE1*/\n  const pool=[0];")

# 2) hitE: per-type damage filter ---------------------------------------------------------
rep("function hitE(e,d){e.hp-=d;",
    "function hitE(e,d){const hr=HEX[e.t];if(hr&&hr.dmg){try{d=hr.dmg(e,d)}catch(x){heFail(x);return}if(!(d>0))return}/*HE1*/e.hp-=d;")

# 3) kill(): scores for t6..t10 + onKill ------------------------------------------------------
rep("const v=[85,100,170,255,340,500][e.t]", "const v=[85,100,170,255,340,500,420,520,380,600,450][e.t]/*HE1*/")
rep("  if(Math.random()<(e.t>1?.4:.26)*D.dr)drop(e.x+e.w/2,e.y);\n}",
    "  if(Math.random()<(e.t>1?.4:.26)*D.dr)drop(e.x+e.w/2,e.y);\n  const hk=HEX[e.t];if(hk&&hk.onKill){try{hk.onKill(e)}catch(x){heFail(x)}}/*HE1*/\n}")

# 4) enemy loop: dazed hook + AI dispatch -------------------------------------------------
rep("if(e.dz){e.y+=Math.sin(tick/5+e.id)*.3}else if(e.t==5){wizAI(e,px,py)}",
    "if(e.dz){const hz=HEX[e.t];if(hz&&hz.dazed){try{hz.dazed(e)}catch(x){heFail(x);continue}}else e.y+=Math.sin(tick/5+e.id)*.3}"
    "else if(HEX[e.t]){try{HEX[e.t].ai(e,px,py)}catch(x){heFail(x);continue}}/*HE1*/"
    "else if(e.t==5){wizAI(e,px,py)}")

# 5) shared contact test: per-type override ---------------------------------------------------
rep("    if(tick-e.born>14&&pl.x<e.x+e.w&&pl.x+pl.w>e.x&&pl.y<e.y+e.h&&bot>e.y){",
    "    let heHd=0;const heHc=HEX[e.t];if(heHc&&heHc.contact){try{heHd=heHc.contact(e,px,py,bot)}catch(x){heFail(x);continue}}/*HE1*/\n"
    "    if(!heHd&&tick-e.born>14&&pl.x<e.x+e.w&&pl.x+pl.w>e.x&&pl.y<e.y+e.h&&bot>e.y){")

# 6) HEH.step once per play tick after the enemy loop ----------------------------------------
rep("  for(const x of X)if(pl.x<x[0]+x[1]&&pl.x+pl.w>x[0]&&bot>GY-20){hurt(px<x[0]+20?-1:1);pl.vy=-9}",
    "  heStep(px,py);/*HE1*/\n"
    "  for(const x of X)if(pl.x<x[0]+x[1]&&pl.x+pl.w>x[0]&&bot>GY-20){hurt(px<x[0]+20?-1:1);pl.vy=-9}")

# 7) player stars vs HE objects (before rm is applied) -----------------------------------------
rep("    if(bs&&bs.a&&!bs.ghost&&!rm&&Math.abs(b.x-bs.x-35)<42",
    "    if(HE_ON&&!rm&&HEH.blHit.length&&heBl(b,i))rm=1;/*HE1*/\n"
    "    if(bs&&bs.a&&!bs.ghost&&!rm&&Math.abs(b.x-bs.x-35)<42")

# 8) enemy projectile kinds (before the generic hit test) --------------------------------------
rep("    if(Math.hypot(px-q.x,py-q.y)<q.r+14&&pl.inv==0&&iv<=0&&au<=0){pj.splice(i,1);hurt(q.vx>=0?1:-1)}",
    "    if(HE_ON&&q.k&&HEH.pjHit[q.k]){let heHh=0;try{heHh=HEH.pjHit[q.k](q,i,px,py)}catch(x){heFail(x);continue}if(heHh)continue}/*HE1*/\n"
    "    if(Math.hypot(px-q.x,py-q.y)<q.r+14&&pl.inv==0&&iv<=0&&au<=0){pj.splice(i,1);hurt(q.vx>=0?1:-1)}")

# 9) resets: load(n) (covers retry/respawn/new run) and clearStage ------------------------------
rep("gl=[];agRst();bloom=0;", "gl=[];agRst();heReset();/*HE1*/bloom=0;")
rep("st='clear';clearT=170;ad(stage*100);ulk='';pj=[];wn=[];pw=[];rc=[];",
    "st='clear';clearT=170;ad(stage*100);ulk='';pj=[];wn=[];pw=[];rc=[];heReset();/*HE1*/")
rep("function begin(){lv=1;", "function begin(){heRun();/*HE1*/lv=1;")
rep("function beginAt(d,n){runOn=0;", "function beginAt(d,n){heRun();/*HE1*/runOn=0;")

# 10) drawing: hooks ----------------------------------------------------------------------------
rep("  if(EN_ON)dEnTrk();for(const e of E)if(e.a)dEnemy(e);",
    "  heDrawH(HEH.drawBack);/*HE1*/\n  if(EN_ON)dEnTrk();for(const e of E)if(e.a)dEnemy(e);")
rep("  for(const q of pj)dPJ(q);\n  c.shadowBlur=0;\n  fxS();",
    "  for(const q of pj)dPJ(q);\n  heDrawH(HEH.drawFront);/*HE1*/\n  c.shadowBlur=0;\n  fxS();")
rep("if(PF_ON&&st=='play')dPlFx();dPlayer()}",
    "if(PF_ON&&st=='play')dPlFx();dPlayer();heDrawH(HEH.drawPlayer,pl.x+16,pl.y+21)/*HE1*/}")

# 11) painters: dispatch, quiet flag, tolerant snapshot -------------------------------------------
rep("function dE2(e){\n  if(!EN_ON)return dE2O(e);",
    "function dE2(e){\n  if(HEX[e.t])return heDraw(e);/*HE1*/\n  if(!EN_ON)return dE2O(e);")
rep("function dE2O(e){\n  const x=e.x",
    "function dE2O(e){\n  if(HEX[e.t])return heDraw(e);/*HE1*/\n  const x=e.x")
rep("const k=Math.min(1,(tick-e.born)/14),sc=k<1?1+2.7*(k-1)**3+1.7*(k-1)**2:1,cx=e.x+e.w/2,cy=e.y+e.h/2;",
    "const heQ=HEX[e.t]&&HEX[e.t].quiet/*HE1*/,k=heQ?1:Math.min(1,(tick-e.born)/14),sc=k<1?1+2.7*(k-1)**3+1.7*(k-1)**2:1,cx=e.x+e.w/2,cy=e.y+e.h/2;")
rep("  if(e.p&&e.t!=4)enSh(e);", "  if(e.p&&e.t!=4&&!heQ)enSh(e);/*HE1*/")
rep("  if(e.t!=4)fGl(cx,cy,Math.max(e.w,e.h)*.5+17,th.ec,.42);", "  if(e.t!=4&&!heQ)fGl(cx,cy,Math.max(e.w,e.h)*.5+17,th.ec,.42);/*HE1*/")
rep("let s=enM.get(e);if(!s){s={};enM.set(e,s)}s.x=e.x;",
    "let s=enM.get(e);if(!s){s={};enM.set(e,s)}if(HEX[e.t])Object.assign(s,e);/*HE1*/s.x=e.x;")
rep("c.shadowColor=th.ec;c.shadowBlur=e.t==4?0:11;dE2(e)",
    "c.shadowColor=th.ec;c.shadowBlur=e.t==4||(HEX[e.t]&&HEX[e.t].quiet)?0:11;dE2(e)")
rep("function dEnemyO(e){const k=Math.min(1,(tick-e.born)/14),sc=",
    "function dEnemyO(e){const k=HEX[e.t]&&HEX[e.t].quiet?1:Math.min(1,(tick-e.born)/14),sc=")

open(out_path, 'w', encoding='utf-8').write(s)
print('wrote', out_path, len(s.encode('utf-8')), 'bytes; sha256', hashlib.sha256(s.encode('utf-8')).hexdigest()[:8])

#!/usr/bin/env python3
"""Patch aria_v32_p1.html -> aria_v32_p2.html  (HE part 2: Player ROOT system + t6 Silk Widow + web patches).
Usage: python3 patch_v32_p2.py aria_v32_p1.html aria_v32_p2.html
Every edit is an exact-string replacement that must match exactly once (assert); the script refuses any input that is not p1."""
import sys

src_path, out_path = sys.argv[1], sys.argv[2]
s = open(src_path, encoding='utf-8').read()
assert s.count('===== HE part 1:') == 1, 'input must contain HE part 1'
assert s.count('HE part 2') == 0, 'input already contains HE part 2'


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, 'anchor count %d != %d: %r' % (c, n, old[:90])
    s = s.replace(old, new)


BLOCK = r'''/* ===== HE part 2: root + silk widow ===== */
/* Player ROOT status: pl.rt = root ticks left, pl.rtI = web-immunity ticks left (both 0 by default; reset by HEH.reset).
   While pl.rt>0 (patched in update(), lines tagged HE2): aiming, shooting and spells stay fully active; no walking acceleration, no jump, no dash, no drop-through; pl.vx=0; gravity applies.
   Mash alternating left/right (keys or touch stick, both go through act()) removes HE.root.mash ticks per edge; the timer runs out anyway; Aurora (au>0) burns the silk away.
   heRoot(n) is the ONE entry point for every later part: true = rooted (or the shield absorbed it), false = blocked (invulnerable / dashing / already rooted / immune).
   t6 SILK WIDOW: ceiling spider (DROP -> HANG -> TELL/REC shot | CLIMB -> SCUT trap | LOWER -> BITE punish), web ball pj k:'web' (HEH.pjHit.web), web patches wb[] (HEH.blHit, HEH.step, HEH.drawBack).
   All tunables: HE.root / HE.widow. Render code is deterministic (tick / e.id only, no Math.random). */
HE.root={ticks:130,mash:8,imm:150,shieldInv:70};
HE.widow={w:40,h:34,unlock:3,max:2,weight:1,hpBase:4,hpDiv:3,
  yMin:120,yMax:320,hover:[110,170],drop:50,hang:[60,90],sway:6,
  shootP:.65,tell:40,lock:18,ballSpd:5,ballR:9,hitPad:14,cool:150,rec:24,muzzle:16,aimExt:30,
  climb:25,ceilY:4,scut:60,scutSpd:5,scutMax:160,patchN:[1,2],patchW:46,patchH:30,patchMinDist:120,ghost:40,life:1500,maxPatches:5,fade:30,
  lowSpd:4,punishMin:90,biteTell:20,biteReach:46,lunge:12,strike:8,threadY:-10,corpse:46,col:'#8ffbff'};
const heRt={l:0,r:0,d:0,max:1};
let wb=[],wdDead=[],wdT=0;
function heRelease(){
  const x=pl.x+16,y=pl.y+21;pl.rt=0;pl.rtI=HE.root.imm;
  burst(x,y,'#8ffbff',18,5);burst(x,y,'#ffffff',8,4);ring(x,y,'#8ffbff',64);
  snd(900,.14,'triangle',.04,-500);noise(.1,.03,5200);
}
function heRoot(n){
  if(pl.rt>0||pl.rtI>0||pl.inv>0||tm.i>0||iv>0||au>0||pl.dt>0)return false;
  const x=pl.x+16,y=pl.y+21;
  if(sh>0){sh--;pl.inv=HE.root.shieldInv;burst(x,pl.y+20,'#7dff9e',16);sx('sp',x);return true}
  pl.rt=heRt.max=n;heRt.l=act('l')?1:0;heRt.r=act('r')?1:0;heRt.d=0;pl.vx=0;jb=0;dnq=0;
  burst(x,y,'#8ffbff',14,4);ring(x,y,'#8ffbff',70);snd(260,.2,'sine',.05,160);noise(.12,.04,3000);
  if(!heSeen.has('rt')){heSeen.add('rt');pop(W/2,150,'MASH \u2190\u2192 TO BREAK FREE','#8ffbff')}
  return true;
}
function heRtTick(Lk,Rk){
  if(!(pl.rt>0)){if(pl.rtI>0)pl.rtI--;return}
  const l=Lk?1:0,r=Rk?1:0,m=HE.root.mash;
  if(l&&!heRt.l&&heRt.d!=-1){pl.rt-=m;heRt.d=-1;burst(pl.x+10,pl.y+22,'#8ffbff',3,2);snd(1100,.03,'square',.02,300)}
  else if(r&&!heRt.r&&heRt.d!=1){pl.rt-=m;heRt.d=1;burst(pl.x+22,pl.y+22,'#8ffbff',3,2);snd(1100,.03,'square',.02,300)}
  heRt.l=l;heRt.r=r;
  if(au>0||--pl.rt<=0)heRelease();
}
function heRtU(Lk,Rk){try{heRtTick(Lk,Rk)}catch(x){heFail(x)}}
HEH.reset.push(function(){pl.rt=0;pl.rtI=0;heRt.l=heRt.r=heRt.d=0;wb.length=0;wdDead.length=0;wdT=0});

/* ---- web patches ---- */
function wdPlant(sp){
  const Q=HE.widow;let n=0;for(const q of wb)if(!q.dy)n++;
  if(n>=Q.maxPatches){for(const q of wb)if(!q.dy){q.dy=Q.fade;break}}   /* wb keeps creation order: the first live one is the oldest */
  wb.push({x:sp.x,y:sp.y,w:Q.patchW,h:Q.patchH,born:wdT,life:Q.life,dy:0});
  burst(sp.x+Q.patchW/2,sp.y+Q.patchH/2,'#8ffbff',6,2);snd(700,.06,'sine',.03,-200);
}
/* candidate patch spots: STATIC platforms only (no p.t, no p.fx), not over pits, >= patchMinDist from the player, not overlapping other patches */
function wdSpots(e,px,py,n){
  const Q=HE.widow,out=[],cs=P.filter(p=>!p.fx&&!p.t&&p.w>=Q.patchW+8);
  if(!cs.length)return out;
  for(let a=0;a<n;a++){
    let best=null,bd=1e9;
    for(let k=0;k<8;k++){
      const p=cs[(Math.random()*cs.length)|0],x=rnd(p.x+4,p.x+p.w-Q.patchW-4),y=p.y-Q.patchH;
      if(p.y>=GY-1&&X.some(q=>x+Q.patchW>q[0]-8&&x<q[0]+q[1]+8))continue;
      if(Math.hypot(x+Q.patchW/2-px,y+Q.patchH/2-py)<Q.patchMinDist)continue;
      let bad=0;
      for(const o of out)if(Math.abs(x-o.x)<Q.patchW+6&&Math.abs(y-o.y)<Q.patchH+6)bad=1;
      for(const o of wb)if(!o.dy&&Math.abs(x-o.x)<Q.patchW+6&&Math.abs(y-o.y)<Q.patchH+6)bad=1;
      if(bad)continue;
      const d=Math.abs(x+Q.patchW/2-(e.x+e.w/2));if(d<bd){bd=d;best={x,y}}
    }
    if(best)out.push(best);
  }
  out.sort((a,b)=>Math.abs(a.x-e.x)-Math.abs(b.x-e.x));
  return out;
}
/* player star vs patches (true = star consumed; pierce stars keep flying) */
HEH.blHit.push(function(b,i){
  const Q=HE.widow;let hit=0;
  for(let k=wb.length-1;k>=0;k--){
    const q=wb[k];if(q.dy||wdT-q.born<Q.ghost)continue;
    if(b.x>q.x-6&&b.x<q.x+q.w+6&&b.y>q.y-6&&b.y<q.y+q.h+6){
      wb.splice(k,1);hit=1;
      burst(q.x+q.w/2,q.y+q.h/2,'#8ffbff',12,4);burst(q.x+q.w/2,q.y+q.h/2,'#ffffff',5,3);ring(q.x+q.w/2,q.y+q.h/2,'#8ffbff',46);
      snd(1500,.07,'triangle',.04,-600);
      if(!(tm.p>0))break;
    }
  }
  return hit&&!(tm.p>0);
});
/* web ball: root on hit (removed either way), vanishes on the floor; never hurts */
HEH.pjHit.web=function(q,i,px,py){
  const Q=HE.widow;
  if(Math.hypot(px-q.x,py-q.y)<q.r+Q.hitPad){
    pj.splice(i,1);
    burst(q.x,q.y,'#8ffbff',10,4);
    if(!heRoot(HE.root.ticks)){burst(q.x,q.y,'#ffffff',4,3);snd(900,.05,'square',.02,-200)}
    return true;
  }
  if(q.y>=GY-6){pj.splice(i,1);burst(q.x,GY-6,'#8ffbff',6,3);return true}
  return true;
};
HEH.step.push(function(px,py){
  const Q=HE.widow;wdT++;
  for(let i=wb.length-1;i>=0;i--){
    const q=wb[i],age=wdT-q.born;
    if(q.dy){if(--q.dy<=0)wb.splice(i,1);continue}
    if(age>=Q.ghost+q.life){wb.splice(i,1);continue}
    if(age<Q.ghost)continue;
    if(pl.x<q.x+q.w&&pl.x+pl.w>q.x&&pl.y<q.y+q.h&&pl.y+pl.h>q.y){
      if(heRoot(HE.root.ticks)){burst(q.x+q.w/2,q.y+q.h/2,'#8ffbff',12,4);ring(q.x+q.w/2,q.y+q.h/2,'#8ffbff',50);wb.splice(i,1)}
    }
  }
  for(let i=wdDead.length-1;i>=0;i--){const d=wdDead[i];d.age++;d.vy+=.5;d.y+=d.vy;d.x+=d.vx;d.rot+=d.vr;if(d.age>Q.corpse||d.y>H+60)wdDead.splice(i,1)}
});

/* ---- Silk Widow AI. e.st: 0 DROP, 1 HANG, 2 TELL, 3 REC, 4 CLIMB, 5 SCUT, 6 LOWER (punish), 7 BITE tell, 8 STRIKE. e.tm counts down e.tl. ---- */
function wdPick(e,px,py){
  const Q=HE.widow,cs=P.filter(p=>!p.fx&&p.t!='f'),
    near=cs.map(p=>({p,d:Math.abs(clamp(px,p.x,p.x+p.w)-px)})).sort((a,b)=>a.d-b.d).slice(0,4);
  let bx=e.x+e.w/2,by=Q.yMin,bd=-1;
  for(let k=0;k<6;k++){
    let cx,cy;
    if(near.length){const p=near[(Math.random()*near.length)|0].p;cx=p.x+p.w*rnd(.2,.8);cy=clamp(p.y-rnd(Q.hover[0],Q.hover[1]),Q.yMin,Q.yMax)}
    else{cx=rnd(100,W-100);cy=rnd(Q.yMin,Q.yMax)}
    cx=clamp(cx,40,W-40);
    const d=Math.hypot(cx-px,cy+Q.h/2-py);
    if(d>bd){bd=d;bx=cx;by=cy}
    if(d>=HE.minDist)break;
  }
  e.hx=bx-e.w/2;e.hy=by;
}
function wdDrop(e,px,py){const Q=HE.widow;wdPick(e,px,py);e.x0=e.x;e.y0=e.y;e.st=0;e.tl=e.tm=Q.drop}
function wdClimb(e,nx){const Q=HE.widow;e.st=4;e.tl=e.tm=Q.climb;e.y0=e.y;e.nx=nx}
function wdPunish(e){e.st=6;e.pt=0;e.tl=e.tm=0}
function wdScut(e,px,py){
  const Q=HE.widow;e.st=5;e.sc=0;e.pi=0;e.d=e.x+e.w/2<W/2?1:-1;
  e.plan=wdSpots(e,px,py,Math.random()<.5?Q.patchN[0]:Q.patchN[1]);
}
function wdFire(e){
  const Q=HE.widow;if(pl.rt>0||pl.rtI>0)return;
  const mx=e.x+e.w/2,my=e.y+e.h/2+Q.muzzle,a=Math.atan2(e.ty-my,e.tx-mx),v=Q.ballSpd*D.ps;   /* aimed at the position locked during the tell: no lead */
  pj.push({x:mx,y:my,vx:Math.cos(a)*v,vy:Math.sin(a)*v,r:Q.ballR,c:Q.col,k:'web',he:1});
  e.cd=Math.round(Q.cool*D.bc);snd(520,.14,'sine',.05,-300);burst(mx,my,'#8ffbff',6,3);
}
function wdDecide(e,px,py){
  const Q=HE.widow;
  if(pl.rt>0){wdPunish(e);return}
  if(Math.random()<Q.shootP){
    if(e.cd<=0&&!(pl.rtI>0)){e.st=2;e.tl=e.tm=Q.tell;e.tx=px;e.ty=py;return}
    if(pl.rtI>0){wdClimb(e,'scut');return}
    e.st=1;e.tl=e.tm=Math.max(10,Math.min(40,e.cd));return;
  }
  wdClimb(e,'scut');
}
function wdAI(e,px,py){
  const Q=HE.widow,rooted=pl.rt>0;
  if(e.cd>0)e.cd--;
  switch(e.st){
  case 0:{
    const k=Math.min(1,1-(--e.tm)/e.tl),s=1-Math.pow(1-k,3);
    e.x=e.x0+(e.hx-e.x0)*s;e.y=e.y0+(e.hy-e.y0)*s;
    if(e.tm<=0){e.x=e.hx;e.y=e.hy;e.st=1;e.tl=e.tm=Math.round(rnd(Q.hang[0],Q.hang[1]))}
    break}
  case 1:
    e.x=e.hx+Math.sin(tick/18+e.id)*Q.sway;e.y=e.hy+Math.sin(tick/23+e.id*2)*3;
    if(rooted){wdPunish(e);break}
    if(--e.tm<=0)wdDecide(e,px,py);
    break;
  case 2:
    e.x=e.hx+Math.sin(tick/18+e.id)*Q.sway*.35;e.y=e.hy+Math.sin(tick/23+e.id*2)*1.5;
    if(rooted){wdPunish(e);break}
    if(pl.rtI>0){e.st=1;e.tl=e.tm=30;break}                 /* never webs a rooted or web-immune player */
    if(e.tm>Q.lock){e.tx=px;e.ty=py}                          /* aim follows the player, then locks for the last Q.lock ticks */
    if(--e.tm<=0){wdFire(e);e.st=3;e.tl=e.tm=Q.rec}
    break;
  case 3:
    e.x=e.hx+Math.sin(tick/18+e.id)*Q.sway*.5;e.y=e.hy+Math.sin(tick/23+e.id*2)*2;
    if(rooted){wdPunish(e);break}
    if(--e.tm<=0){e.st=1;e.tl=e.tm=Math.round(rnd(Q.hang[0],Q.hang[1])*.6)}
    break;
  case 4:{
    const k=Math.min(1,1-(--e.tm)/e.tl);e.y=e.y0+(Q.ceilY-e.y0)*k;
    if(e.tm<=0){e.y=Q.ceilY;if(e.nx=='scut')wdScut(e,px,py);else wdDrop(e,px,py)}
    break}
  case 5:{
    e.y=Q.ceilY+Math.sin(tick/5+e.id)*1.2;e.sc++;
    const tg=e.plan[e.pi];
    if(tg){
      const bx=tg.x+Q.patchW/2-e.w/2,dx=bx-e.x;
      if(Math.abs(dx)<=Q.scutSpd){e.x=bx;wdPlant(tg);e.pi++}else e.x+=Math.sign(dx)*Q.scutSpd;
    }else{
      e.x+=e.d*Q.scutSpd*.6;if(e.x<30||e.x>W-30-e.w){e.d*=-1;e.x=clamp(e.x,30,W-30-e.w)}
    }
    if((e.pi>=e.plan.length&&e.sc>=Q.scut)||e.sc>=Q.scutMax)wdDrop(e,px,py);
    break}
  case 6:{
    e.pt++;
    if(!rooted){wdClimb(e,'drop');break}
    const tx=pl.x+pl.w/2-e.w/2,ty=Math.max(Q.ceilY,pl.y-e.h-6),dx=tx-e.x,dy=ty-e.y,d=Math.hypot(dx,dy);
    if(d>Q.lowSpd){e.x+=dx/d*Q.lowSpd;e.y+=dy/d*Q.lowSpd}else{e.x=tx;e.y=ty}
    if(e.pt>=Q.punishMin&&d<=Q.lowSpd*2){e.st=7;e.tl=e.tm=Q.biteTell}
    break}
  case 7:{
    if(!rooted){wdClimb(e,'drop');break}                    /* mashed free during the tell: the bite is cancelled */
    const tx=pl.x+pl.w/2-e.w/2,ty=Math.max(Q.ceilY,pl.y-e.h-6);
    e.x+=(tx-e.x)*.25;e.y+=(ty-e.y)*.25;
    if(--e.tm<=0){
      e.st=8;e.tl=e.tm=Q.strike;e.by=e.y;
      if(Math.hypot(px-(e.x+e.w/2),py-(e.y+e.h/2+Q.lunge))<=Q.biteReach){hurt(px>e.x+e.w/2?-1:1);burst(px,py-10,'#ff6bd6',10,4)}
      snd(160,.12,'sawtooth',.06,-80);
    }
    break}
  case 8:{
    const k=1-e.tm/e.tl;e.y=e.by+Q.lunge*Math.sin(Math.min(1,k)*Math.PI);
    if(--e.tm<=0){e.y=e.by;wdClimb(e,'drop')}
    break}
  default:wdDrop(e,px,py)}
}
function wdKill(e){
  const Q=HE.widow,cx=e.x+e.w/2,cy=e.y+e.h/2;
  wdDead.push({x:e.x,y:e.y,vx:rnd(-1.2,1.2),vy:-2.5,rot:0,vr:rnd(-.12,.12),age:0,id:e.id,tx:cx,thY:cy-16,th:e.st!=5&&e.y>Q.threadY+8?1:0});
  burst(cx,cy,'#a98bff',18,5);burst(cx,cy,'#8ffbff',10,4);ring(cx,cy,'#8ffbff',70);
  snd(1300,.12,'triangle',.05,-900);noise(.1,.04,4200);
}

/* ---- painters (deterministic) ---- */
function wdDot(x,y,r){c.beginPath();c.arc(x,y,r,0,7);c.fill()}
function wdBody(o){
  const T=tick,f=o.f,dd=o.dd,id=o.id,knees=[];
  const KN=[[13,-15],[17,-7],[17,1],[13,9]],FT=[[27,-9],[31,3],[29,13],[21,20]],k=1-.5*(o.curl||0);
  c.lineCap='round';c.lineJoin='round';
  c.beginPath();
  for(let s=-1;s<=1;s+=2)for(let i=0;i<4;i++){
    const w=Math.sin(T/(6+i)+id*3+i*1.7+(s>0?0:1.3))*o.amp,hx=s*5,hy=-7+i*3.2,
      kx=s*(5+(KN[i][0]-5)*k)+s*w*.35,ky=hy+(KN[i][1]-hy)*k+w*.5,
      fx=kx+s*(FT[i][0]-KN[i][0])*k+s*w*.5,fy=ky+(FT[i][1]-KN[i][1])*k+w*.3;
    c.moveTo(hx,hy);c.lineTo(kx,ky);c.lineTo(fx,fy);knees.push(kx,ky);
  }
  c.strokeStyle=f?'#ffffff':'#2a1058';c.lineWidth=4.6;c.stroke();
  c.strokeStyle=f?'#ffffff':'#7a4cd0';c.lineWidth=2.6;c.stroke();
  if(!f){c.strokeStyle='#a98bff';c.lineWidth=.9;c.globalAlpha*=.75;c.stroke();c.globalAlpha/=.75}
  if(!dd&&!f)for(let i=0;i<knees.length;i+=2)eGl(knees[i],knees[i+1],6,'#a98bff',.7);
  c.fillStyle=f?'#ffffff':'#c8b6ff';for(let i=0;i<knees.length;i+=2)wdDot(knees[i],knees[i+1],2);
  /* abdomen */
  let g=c.createRadialGradient(-3,0,1,0,4,17);
  g.addColorStop(0,f?'#fff':'#8a5cdc');g.addColorStop(.55,f?'#fff':'#4a2290');g.addColorStop(1,f?'#fff':'#26104d');
  c.fillStyle=g;c.strokeStyle=f?'#fff':'#a98bff';c.lineWidth=1.6;
  c.beginPath();c.ellipse(0,4,12.5,13.5,0,0,7);c.fill();c.stroke();
  c.fillStyle=f?'#fff':'#8ffbff';
  c.beginPath();c.moveTo(-5.2,-1.5);c.lineTo(5.2,-1.5);c.lineTo(0,4.2);c.closePath();c.moveTo(0,4.2);c.lineTo(6.2,11);c.lineTo(-6.2,11);c.closePath();c.fill();
  /* spinneret orb: glows during the shot tell */
  const t=o.tell||0;
  if(!dd)eGl(0,16,8+t*20,'#8ffbff',.3+.65*t);
  c.fillStyle=f?'#fff':(t>0?'#e8ffff':'#8ffbff');wdDot(0,16.5,3.3+t*1.8);
  if(!f){c.strokeStyle='rgba(30,110,140,.85)';c.lineWidth=.8;c.beginPath();for(let i=0;i<3;i++){const a=i*1.0472,r=3.3+t*1.8;c.moveTo(-Math.cos(a)*r,16.5-Math.sin(a)*r);c.lineTo(Math.cos(a)*r,16.5+Math.sin(a)*r)}c.stroke()}
  /* head */
  g=c.createRadialGradient(-2,-11,1,0,-8,10);
  g.addColorStop(0,f?'#fff':'#8660d8');g.addColorStop(1,f?'#fff':'#2e1260');
  c.fillStyle=g;c.strokeStyle=f?'#fff':'#a98bff';c.lineWidth=1.5;
  c.beginPath();c.arc(0,-8,8.4,0,7);c.fill();c.stroke();
  if(!dd){
    const bk=((T+((id*40)|0))%210)<6,er=o.bite>0?'#ff3b5c':'#ff6bd6';
    if(!bk){
      eGl(-3.7,-9.6,5.6,er,.6);eGl(3.7,-9.6,5.6,er,.6);
      c.fillStyle=er;wdDot(-3.7,-9.6,3);wdDot(3.7,-9.6,3);wdDot(-7,-7.5,1.4);wdDot(7,-7.5,1.4);wdDot(-1.9,-13.2,1.2);wdDot(1.9,-13.2,1.2);
      c.fillStyle='#fff';wdDot(-4.5,-10.5,1);wdDot(2.9,-10.5,1);
    }else{c.strokeStyle=er;c.lineWidth=1.4;c.beginPath();c.moveTo(-6.5,-9.6);c.lineTo(-1,-9.6);c.moveTo(1,-9.6);c.lineTo(6.5,-9.6);c.stroke()}
  }
  c.strokeStyle=o.bite>0?'#ff9bd8':(f?'#fff':'#f0e6ff');c.lineWidth=1.7;
  c.beginPath();c.moveTo(-2.6,-1.6);c.quadraticCurveTo(-4.4,1,-3.2,3.4);c.moveTo(2.6,-1.6);c.quadraticCurveTo(4.4,1,3.2,3.4);c.stroke();
  if(o.bite>0&&!dd)eGl(0,1,8+10*o.bite,'#ff3b5c',.35+.5*o.bite);
}
function wdDraw(e){
  const Q=HE.widow,f=e.fl>0,dd=!!e.dd,cx=e.x+e.w/2,cy=e.y+e.h/2,T=tick,
    tell=!dd&&e.st==2?1-e.tm/Q.tell:0,bite=!dd&&e.st==7?1-e.tm/Q.biteTell:0;
  if(!dd&&e.st!=5){      /* silk thread from the ceiling */
    c.save();c.lineCap='round';
    c.strokeStyle='rgba(143,251,255,.18)';c.lineWidth=5;c.beginPath();c.moveTo(cx,Q.threadY);c.lineTo(cx,cy-16);c.stroke();
    c.strokeStyle='#bffcff';c.lineWidth=1.4;c.beginPath();c.moveTo(cx,Q.threadY);c.lineTo(cx,cy-16);c.stroke();
    c.restore();
  }
  if(tell>0){            /* dotted aim line + target ring (no lead aiming); brighter once the aim is locked */
    const mx=cx,my=cy+Q.muzzle,dx=e.tx-mx,dy=e.ty-my,d=Math.hypot(dx,dy)||1,L=d+Q.aimExt,lk=e.tm<=Q.lock;
    c.save();c.setLineDash([4,7]);c.lineDashOffset=-T*.9;c.lineCap='round';
    c.strokeStyle=lk?'#e8ffff':'#8ffbff';c.globalAlpha=Math.min(1,.3+.7*tell);c.lineWidth=lk?2.4:1.7;
    c.beginPath();c.moveTo(mx,my);c.lineTo(mx+dx/d*L,my+dy/d*L);c.stroke();
    c.setLineDash([]);c.strokeStyle='#ff6bd6';c.lineWidth=1.6;c.beginPath();c.arc(e.tx,e.ty,lk?15:19+Math.sin(T/3)*2,0,7);c.stroke();
    c.restore();
  }
  c.save();c.translate(cx+(bite>0?Math.sin(T*2.1)*1.2*bite:0),cy);
  wdBody({f,dd,id:e.id,amp:dd?.6:(e.st==5?3.6:e.st==6?2.4:1.5),curl:0,tell,bite});
  c.restore();
}
HEH.drawBack.push(function(){      /* web patches: ghost outline, then a shimmering net disc */
  const Q=HE.widow;
  for(const q of wb){
    const age=wdT-q.born,cx=q.x+q.w/2,cy=q.y+q.h/2,gh=!q.dy&&age<Q.ghost;
    let a;
    if(q.dy)a=q.dy/Q.fade*.6;
    else if(gh)a=.2+.12*Math.sin(age*.5);
    else{const rem=Q.ghost+q.life-age;a=rem<90?(.35+.4*Math.sin(rem*.5))*.9:.6+.2*Math.sin(wdT/9+q.x)}
    c.save();c.translate(cx,cy);c.scale(1,q.h/q.w);
    c.globalAlpha=Math.max(0,Math.min(1,a));
    if(!gh){c.fillStyle='rgba(143,251,255,.10)';c.beginPath();c.arc(0,0,q.w/2,0,7);c.fill()}
    eGl(0,0,q.w*.7,'#8ffbff',gh?.25:.45);
    c.strokeStyle='#8ffbff';c.lineWidth=1.2;c.lineCap='round';if(gh)c.setLineDash([3,4]);
    for(const r of[7,15,q.w/2]){c.beginPath();c.arc(0,0,r,0,7);c.stroke()}
    c.beginPath();for(let i=0;i<8;i++){const an=i*.7854;c.moveTo(0,0);c.lineTo(Math.cos(an)*q.w/2,Math.sin(an)*q.w/2)}c.stroke();
    c.restore();
  }
});
HEH.drawFront.push(function(){      /* web balls (the generic painter draws nothing for k:'web') + falling widow husks */
  const Q=HE.widow;
  for(const q of pj){
    if(q.k!=='web')continue;
    const sp=Math.hypot(q.vx,q.vy)||1;
    c.save();c.lineCap='round';
    c.strokeStyle='rgba(143,251,255,.35)';c.lineWidth=2;c.beginPath();c.moveTo(q.x,q.y);c.lineTo(q.x-q.vx/sp*22,q.y-q.vy/sp*22);c.stroke();
    eGl(q.x,q.y,q.r*3,'#8ffbff',.7);
    c.translate(q.x,q.y);c.rotate(tick*.15);
    c.fillStyle='#dffcff';c.strokeStyle='#8ffbff';c.lineWidth=1.5;wdDot(0,0,q.r);c.stroke();
    c.strokeStyle='#4aa3b8';c.lineWidth=1;c.beginPath();
    for(let i=0;i<3;i++){const a=i*1.0472;c.moveTo(-Math.cos(a)*q.r,-Math.sin(a)*q.r);c.lineTo(Math.cos(a)*q.r,Math.sin(a)*q.r)}
    c.stroke();c.beginPath();c.arc(0,0,q.r*.5,0,7);c.stroke();
    c.restore();
  }
  for(const d of wdDead){
    const a=1-d.age/Q.corpse;if(a<=0)continue;
    c.save();c.globalAlpha=Math.min(1,a*1.4);
    if(d.th){const ly=d.thY-d.age*9;if(ly>Q.threadY+1){c.strokeStyle='#bffcff';c.lineWidth=1.4;c.lineCap='round';c.beginPath();c.moveTo(d.tx,Q.threadY);c.lineTo(d.tx,ly);c.stroke()}}
    c.translate(d.x+Q.w/2,d.y+Q.h/2);c.rotate(d.rot);
    wdBody({f:0,dd:1,id:d.id,amp:.4,curl:1,tell:0,bite:0});
    c.restore();
  }
});
HEH.drawPlayer.push(function(px,py){      /* cocoon + cracks (grow as the timer drains) + shrinking timer ring above the head */
  if(!(pl.rt>0))return;
  if(px===undefined){px=pl.x+16;py=pl.y+21}
  const fr=Math.max(0,Math.min(1,pl.rt/heRt.max)),cr=1-fr,T=tick,rx=27,ry=37;
  if(fr<.25&&T%6<3)c.globalAlpha=.55;
  c.translate(px,py+1);
  c.fillStyle='rgba(143,251,255,'+(.10+.06*Math.sin(T/6))+')';c.beginPath();c.ellipse(0,0,rx,ry,0,0,7);c.fill();
  eGl(0,0,46,'#8ffbff',.28);
  c.strokeStyle='#8ffbff';c.lineWidth=2;c.beginPath();c.ellipse(0,0,rx,ry,0,0,7);c.stroke();
  c.lineWidth=1;c.globalAlpha*=.8;c.beginPath();
  for(let i=1;i<=3;i++){const kx=rx*i/4;c.moveTo(0,-ry);c.ellipse(0,0,kx,ry,0,-Math.PI/2,Math.PI/2);c.moveTo(0,-ry);c.ellipse(0,0,kx,ry,0,Math.PI/2,Math.PI*1.5)}
  for(let j=-1;j<=1;j++){const yy=j*ry*.5,hw=rx*Math.sqrt(1-(yy/ry)*(yy/ry));c.moveTo(-hw,yy);c.lineTo(hw,yy)}
  c.stroke();c.globalAlpha/=.8;
  const nc=Math.min(10,(cr*11)|0);
  c.strokeStyle='#ffffff';c.lineWidth=2.2;c.beginPath();
  for(let k=0;k<nc;k++){
    const a=k*2.399+.6,ex=Math.cos(a)*rx,ey=Math.sin(a)*ry,ln=7+(k%3)*3,ix=ex*(1-ln/rx*.9),iy=ey*(1-ln/ry*.9),mx=(ex+ix)/2+Math.sin(k*5.1)*3,my=(ey+iy)/2+Math.cos(k*3.7)*3;
    c.moveTo(ex,ey);c.lineTo(mx,my);c.lineTo(ix,iy);
  }
  c.stroke();
  c.globalAlpha=1;c.translate(0,-ry-13);
  const rr=3+6*fr;
  c.strokeStyle='rgba(143,251,255,.25)';c.lineWidth=2.5;c.beginPath();c.arc(0,0,rr,0,7);c.stroke();
  c.strokeStyle='#8ffbff';c.lineCap='round';c.beginPath();c.arc(0,0,rr,-Math.PI/2,-Math.PI/2+6.2832*fr);c.stroke();
});

HEX[6]={name:'Silk Widow',hint:'SILK WIDOW!',col:HE.widow.col,w:HE.widow.w,h:HE.widow.h,unlock:HE.widow.unlock,max:HE.widow.max,weight:HE.widow.weight,
  place:'ceiling',hp:s=>HE.widow.hpBase+(s>>3),quiet:false,
  init(e){e.plan=[];e.pi=0;e.sc=0;e.pt=0;e.tx=e.x;e.ty=e.y;wdDrop(e,pl.x+16,pl.y+21)},
  ai:wdAI,draw:wdDraw,onKill:wdKill};
/* ===== /HE part 2 ===== */
'''

# 1) the block, right after the part-1 block
rep('/* ===== /HE part 1 ===== */\n', '/* ===== /HE part 1 ===== */\n' + BLOCK)

# 2) update(): root tick (timer + mash + immunity countdown), right after the input snapshot of the play branch
rep("Fk=kf||md||Uk,Dk=act('d');\n",
    "Fk=kf||md||Uk,Dk=act('d');if(pl.rt>0||pl.rtI>0)heRtU(Lk,Rk);/*HE2*/\n")

# 3) update(): no dash while rooted
rep("if(Dk&&ups.dash&&pl.dc<=0&&pl.dt<=0){pl.dt=9;",
    "if(Dk&&ups.dash&&pl.dc<=0&&pl.dt<=0&&!(pl.rt>0)/*HE2*/){pl.dt=9;")

# 4) update(): no walking acceleration while rooted (vx=0); gravity line right below stays untouched
rep("    if(Lk&&!Rk){pl.vx-=.9;pl.d=-1}else if(Rk&&!Lk){pl.vx+=.9;pl.d=1}else pl.vx*=.78;\n"
    "    if(bs&&bs.pu>0)pl.vx+=(bs.x+35>pl.x+16?1:-1)*.55;pl.vx=clamp(pl.vx,-5,5);\n",
    "    if(pl.rt>0)pl.vx=0;else{/*HE2*/\n"
    "    if(Lk&&!Rk){pl.vx-=.9;pl.d=-1}else if(Rk&&!Lk){pl.vx+=.9;pl.d=1}else pl.vx*=.78;\n"
    "    if(bs&&bs.pu>0)pl.vx+=(bs.x+35>pl.x+16?1:-1)*.55;pl.vx=clamp(pl.vx,-5,5);\n"
    "    }\n")

# 5) update(): no jump / drop-through while rooted (buffers are flushed every rooted tick)
rep("  if(dnq>0){if(Fk)dnq=0;else if(--dnq==0)dropDown()}",
    "  if(pl.rt>0){jb=0;dnq=0}/*HE2*/\n  if(dnq>0){if(Fk)dnq=0;else if(--dnq==0)dropDown()}")

open(out_path, 'w', encoding='utf-8').write(s)
print('OK', len(s.encode('utf-8')), 'bytes')

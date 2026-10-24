#!/usr/bin/env python3
"""Patch aria_v32_p2.html -> aria_v32_p3.html  (HE part 3: t8 NIGHT-FANG).
Usage: python3 patch_v32_p3.py aria_v32_p2.html aria_v32_p3.html
Pure registry/hook usage (HEX[8], HEH.pjHit.cw, HEH.drawFront): NO edit inside existing game functions.
The script refuses any input that is not p2 (assert on unique anchors)."""
import sys

src_path, out_path = sys.argv[1], sys.argv[2]
s = open(src_path, encoding='utf-8').read()
assert s.count('===== HE part 2:') == 1, 'input must contain HE part 2'
assert s.count('HE part 3') == 0, 'input already contains HE part 3'

BLOCK = r'''/* ===== HE part 3: night-fang ===== */
/* t8 NIGHT-FANG: shadow hound. st: 0 PATROL/HUNT, 1 CROUCH (tell, e.tm), 2 HOP (feint hop back), 3 CROUCH2 (feint, WHITE eyes), 4 LEAP (airborne, e.p=null), 6 DAZED.
   LEAP = ballistic arc with the player's gravity HE.fang.g, launch speed <= HE.fang.maxV (a crouch only STARTS when the solution needs <= HE.fang.startV), solved by fgSolve() for the player's FEET position at the moment the crouch ends (no tracking afterwards).
   fgLand() simulates the arc with the same integrator as the runtime and refuses (-> no crouch / whiff) any landing on a pit (no platform), spike strip X[], lava, a moving platform, a fading / p.fx platform or within HE.fang.edge px of an edge.
   LAND = two low claw-wave shocks pj{k:'cw'} (HEH.pjHit.cw, height aware, must be jumped) then DAZED (double damage via dmg). Airborne = not stompable (contact() falls to hurt), always shootable.
   Public: fgSolve, fgLand, fgAI, fgDraw, HE.fang. Render code is deterministic (tick / e.id only). */
HE.fang={w:44,h:28,unlock:4,max:2,weight:1,hpBase:3,
  patrolMul:1.5,huntX:380,huntY:200,minDist:40,
  crouch:28,feintP:.3,hop:12,hopDist:30,hopH:9,crouch2:18,whiff:50,
  maxV:11,startV:10,g:.62,tMin:12,tMax:70,edge:10,trail:4,
  waveSpd:4.2,waveReach:160,waveH:14,waveW:18,dazed:45,dmgMul:2,after:90,col:'#ff5a3c'};
/* simulate the leap exactly like fgFly() does; returns {p,x,y} (landing platform, fang x/y at landing) or null when the landing is not acceptable; pts (optional) receives the feet path [x,y,...] */
function fgLand(e,vx,vy,pts){
  const Q=HE.fang;let x=e.x,y=e.y,v=vy;
  for(let n=0;n<Q.tMax+90;n++){
    const of=y+e.h;v+=Q.g;x=clamp(x+vx,0,W-e.w);y+=v;
    const cx=x+e.w/2,nf=y+e.h;
    if(pts&&n%2==0)pts.push(cx,nf);
    if(v>0){
      let hit=null;
      for(const p of P){
        if(p.t=='f'||p.fx)continue;
        if(of<=p.py+6&&nf>=p.y&&cx>p.x&&cx<p.x+p.w&&(!hit||p.y<hit.y))hit=p;
      }
      if(hit){
        if(pts)pts.push(cx,hit.y);
        if(lava&&hit.y>=GY-20)return null;                                    /* lava stage: floor level is lava */
        if(hit.t)return null;                                                 /* moving platform: landing is unpredictable */
        if(cx<hit.x+Q.edge||cx>hit.x+hit.w-Q.edge)return null;               /* too close to an edge */
        if(hit.y>=GY-1&&X.some(q=>cx>q[0]-14&&cx<q[0]+q[1]+14))return null;   /* spike strip on the floor */
        return {p:hit,x:x,y:hit.y-e.h};
      }
    }
    if(nf>H+40)return null;                                                   /* falls into a pit */
  }
  return null;
}
/* minimum-speed ballistic solution to the target feet position (tx,ty); null = out of range (> maxV) or unacceptable landing */
function fgSolve(e,tx,ty){
  const Q=HE.fang,fx=e.x+e.w/2,fy=e.y+e.h,dx=tx-fx,dy=ty-fy;
  let b=null;
  for(let T=Q.tMin;T<=Q.tMax;T++){
    const vx=dx/T,vy=(dy-Q.g*T*(T+1)/2)/T,sp=Math.hypot(vx,vy);
    if(sp<=Q.maxV&&(!b||sp<b.s))b={vx,vy,T,s:sp};
  }
  if(!b)return null;
  const pts=[fx,fy],L=fgLand(e,b.vx,b.vy,pts);
  if(!L)return null;
  b.p=L.p;b.mx=L.x+e.w/2;b.my=L.p.y;b.pts=pts;
  return b;
}
function fgRescue(e){   /* failsafe: never leave a hound stuck / falling forever */
  const Q=HE.fang;let b=null,bd=1e9;
  for(const p of P){if(p.t||p.fx||p.w<e.w+8)continue;if(lava&&p.y>=GY-20)continue;const d=Math.abs(p.x+p.w/2-(e.x+e.w/2));if(d<bd){bd=d;b=p}}
  if(!b){e.a=0;return}
  e.p=b;e.x=clamp(e.x,b.x+4,b.x+b.w-e.w-4);e.y=b.y-e.h;e.vx=e.vy=0;e.st=0;e.cd=Q.after;e.tr=[];e.arc=null;
  burst(e.x+e.w/2,e.y+e.h,'#8a5cf0',10,3);
}
function fgWaves(e,p){
  const Q=HE.fang,cx=e.x+e.w/2;
  for(const dir of[-1,1])pj.push({x:cx+dir*10,y:p.y-7,vx:dir*Q.waveSpd,vy:0,r:8,c:Q.col,k:'cw',he:1,x0:cx,pf:p,sy:p.y,hw:Q.waveW/2,dir});
}
function fgLandOn(e,p){
  const Q=HE.fang,cx=e.x+e.w/2;
  e.y=p.y-e.h;e.vx=e.vy=0;e.p=p;e.st=6;e.tm=Q.dazed;e.sq=10;e.sol=null;e.arc=null;e.tr=[];
  burst(cx,p.y,'#8a5cf0',12,4);burst(cx,p.y,'#ffffff',4,3);ring(cx,p.y,'#ff5a3c',70);snd(90,.22,'sine',.08,-50);noise(.1,.06,900);
  fgWaves(e,p);
}
function fgFly(e){
  const Q=HE.fang,of=e.y+e.h;
  e.vy+=Q.g;e.x=clamp(e.x+e.vx,0,W-e.w);e.y+=e.vy;
  if(tick%2==0){e.tr.unshift(e.x,e.y);if(e.tr.length>Q.trail*2)e.tr.length=Q.trail*2}
  if(e.vy>0){
    const cx=e.x+e.w/2,nf=e.y+e.h;let hit=null;
    for(const p of P){
      if(p.t=='f'||p.fx)continue;
      if(lava&&p.y>=GY-20)continue;
      if(of<=p.py+6&&nf>=p.y&&cx>p.x&&cx<p.x+p.w&&(!hit||p.y<hit.y))hit=p;
    }
    if(hit){fgLandOn(e,hit);return}
  }
  if(e.y>H+30)fgRescue(e);
}
function fgLaunch(e){
  const s=e.sol;
  e.vx=s.vx;e.vy=s.vy;e.st=4;e.p=null;e.tr=[];e.arc=null;e.mx=s.mx;e.my=s.my;
  if(Math.abs(s.vx)>.4)e.d=s.vx>0?1:-1;
  burst(e.x+e.w/2,e.y+e.h,'#cfc8e8',8,3);snd(320,.16,'sawtooth',.05,260);
}
/* a feint is only chosen when the leap is still possible after the hop back (otherwise it would always end in a whiff at the edge of the range) */
function fgFeintOK(e,tx,ty){
  const Q=HE.fang,ox=e.x;
  e.x=clamp(e.x-e.d*Q.hopDist,e.p.x,e.p.x+e.p.w-e.w);
  const s=fgSolve(e,tx,ty);e.x=ox;
  return !!s&&s.s<=Q.maxV;
}
function fgAI(e,px,py){
  const Q=HE.fang,cx=e.x+e.w/2,bot=py+21,dx=px-cx;
  if(e.cd>0)e.cd--;if(e.sq>0)e.sq--;
  if(e.st!=4&&!e.p){fgRescue(e);return}
  switch(e.st){
  case 0:{
    e.y=e.p.y-e.h;
    const hunt=Math.abs(dx)<Q.huntX&&Math.abs(py-(e.y+e.h/2))<Q.huntY,lo=e.p.x,hi=e.p.x+e.p.w-e.w;
    e.hu=hunt?1:0;
    if(hunt){e.d=dx>=0?1:-1;e.x=clamp(e.x+e.d*e.sp*Q.patrolMul,lo,hi)}   /* hunting: face the player, wait at the platform edge */
    else{e.x+=e.d*e.sp*Q.patrolMul;if(e.x<lo||e.x>hi){e.d*=-1;e.x=clamp(e.x,lo,hi)}}
    if(hunt&&e.cd<=0&&Math.abs(dx)>=Q.minDist){
      const sl=fgSolve(e,px,bot+1);
      if(sl&&sl.s<=Q.startV){                                                /* start with a comfortable margin below maxV so a feint hop back stays in range */
        e.sol=sl;e.arc=sl.pts;e.st=1;e.tm=Q.crouch;e.d=dx>=0?1:-1;
        e.ft=Math.random()<Q.feintP&&fgFeintOK(e,px,bot+1)?1:0;
        snd(90,.28,'sawtooth',.05,-20);burst(cx,e.y+e.h,'#cfc8e8',5,2);
      }
    }
    break}
  case 1:case 3:{
    e.y=e.p.y-e.h;e.d=dx>=0?1:-1;
    e.sol=fgSolve(e,px,bot+1);e.arc=e.sol?e.sol.pts:null;      /* preview follows the player; it is frozen by the lock on the LAST tick of the crouch */
    if(tick%5==0)burst(cx-e.d*14,e.y+e.h,'#cfc8e8',1,1.4);
    if(--e.tm<=0){
      if(!e.sol){e.st=0;e.cd=Q.whiff;e.arc=null;snd(70,.2,'sawtooth',.04,-30);burst(cx,e.y+e.h,'#cfc8e8',6,2);break}
      if(e.st==1&&e.ft){e.ft=0;e.st=2;e.tm=Q.hop;e.hd=-e.d;e.arc=null;snd(200,.1,'triangle',.04,-80);break}
      fgLaunch(e);
    }
    break}
  case 2:{
    const lo=e.p.x,hi=e.p.x+e.p.w-e.w;
    e.tm--;e.x=clamp(e.x+e.hd*Q.hopDist/Q.hop,lo,hi);
    e.y=e.p.y-e.h-Q.hopH*Math.sin(Math.PI*(1-e.tm/Q.hop));
    if(e.tm<=0){e.y=e.p.y-e.h;e.st=3;e.tm=Q.crouch2;burst(cx,e.y+e.h,'#cfc8e8',5,2)}
    break}
  case 4:
    fgFly(e);break;
  case 6:
    e.y=e.p.y-e.h;
    if(--e.tm<=0){e.st=0;e.cd=Q.after;e.d=dx>=0?1:-1}
    break;
  default:e.st=0}
}
function fgDazed(e){if(e.st==4)fgFly(e);else e.y+=Math.sin(tick/5+e.id)*.3}
function fgDmg(e,d){return e.st==6?d*HE.fang.dmgMul:d}
function fgContact(e,px,py,bot){
  if(e.st!=4)return false;                                                    /* legacy test: stomp / invincible kill / hurt */
  if(tick-e.born>14&&pl.x<e.x+e.w&&pl.x+pl.w>e.x&&pl.y<e.y+e.h&&bot>e.y){
    if(tm.i>0)hitE(e,3);else if(!e.dz)hurt(e.x+e.w/2>px?-1:1);               /* airborne: a stomp falls through to hurt */
  }
  return true;
}
function fgKill(e){
  const cx=e.x+e.w/2,cy=e.y+e.h/2;
  burst(cx,cy,'#8a5cf0',16,5);burst(cx,cy,'#ff5a3c',8,4);ring(cx,cy,'#8a5cf0',66);snd(140,.2,'sawtooth',.06,-90);noise(.1,.04,2400);
}
/* claw wave: handled here every tick (true = keep flying unless removed here) */
HEH.pjHit.cw=function(q,i,px,py){
  const Q=HE.fang,p=q.pf;
  if(p&&p.t){q.x+=p.dx;q.x0+=p.dx;q.sy=p.y;q.y=p.y-7}
  if((p&&(q.x<p.x||q.x>p.x+p.w))||Math.abs(q.x-q.x0)>=Q.waveReach){pj.splice(i,1);burst(q.x,q.sy,Q.col,3,2);return true}
  const bot=pl.y+pl.h;
  if(pl.x<q.x+q.hw&&pl.x+pl.w>q.x-q.hw&&bot>q.sy-Q.waveH&&pl.y<q.sy){      /* height aware: only a player whose feet are below the wave top is hit */
    if(pl.inv>0||tm.i>0||iv>0||au>0)return true;                            /* i-frames / dash: the wave passes through */
    pj.splice(i,1);burst(q.x,q.sy-6,Q.col,8,4);hurt(q.dir);return true;
  }
  return true;
};
/* ---- painters (deterministic) ---- */
function fgBody(o){      /* origin = feet centre, facing +x */
  const T=tick,f=o.f,gh=o.gh,E=o.ear||0;
  c.save();
  c.scale(1+.1*o.cr+(o.sq>0?.12*o.sq/10:0),1-.4*o.cr-(o.dz?.16:0)-(o.sq>0?.1*o.sq/10:0));
  if(o.ang){c.translate(0,-12);c.rotate(o.ang);c.translate(0,12)}
  c.lineCap='round';c.lineJoin='round';
  const lc=f?'#ffffff':gh?'rgba(138,92,240,.3)':'#1a0c3a',lo=f?'#ffffff':gh?'rgba(138,92,240,.3)':'#8a5cf0',sw=o.wk?Math.sin(T*.45+o.id)*3.4:0;
  /* tail (smoky violet) */
  const tw=Math.sin(T/9+o.id)*2.2;
  if(!gh&&!o.dd){eGl(-31,-27+tw,9,'#8a5cf0',.5)}
  c.strokeStyle=f?'#fff':gh?'rgba(138,92,240,.3)':'rgba(138,92,240,.35)';c.lineWidth=7;c.beginPath();c.moveTo(-22,-15);c.quadraticCurveTo(-36,-14,-31,-27+tw);c.stroke();
  c.strokeStyle=f?'#fff':gh?'rgba(138,92,240,.3)':'#8a5cf0';c.lineWidth=3.4;c.stroke();
  if(!gh&&!f&&!o.dd){c.fillStyle='rgba(168,139,255,.8)';for(let k=0;k<3;k++){const a=T/11+k*2.1;c.beginPath();c.arc(-33-k*3+Math.sin(a)*1.5,-30-k*3.4+Math.cos(a)*1.5,2.2-k*.5,0,7);c.fill()}}
  /* legs */
  const legs=o.air?[[5,-7,15,-3],[1,-7,11,-6],[-11,-6,-22,-3],[-8,-6,-18,-7]]:[[6,-7,8+sw,0],[1,-7,2-sw,0],[-12,-6,-14+sw,0],[-7,-6,-5-sw,0]];
  for(let i=0;i<4;i++){const l=legs[i];c.strokeStyle=lo;c.lineWidth=i%2?5.2:6.4;c.beginPath();c.moveTo(l[0],l[1]);c.lineTo(l[2],l[3]);c.stroke();c.strokeStyle=lc;c.lineWidth=i%2?2.8:3.8;c.stroke()}
  if(!gh&&!f&&!o.air){c.fillStyle='#e8e0ff';for(const l of[legs[0],legs[2]]){c.beginPath();c.moveTo(l[2]-1,l[3]);c.lineTo(l[2]+4,l[3]);c.lineTo(l[2]+1.4,l[3]-2.6);c.fill()}}
  /* body + haunch */
  let g;
  if(f)g='#fff';else if(gh)g='rgba(138,92,240,.3)';else{g=c.createLinearGradient(0,-24,0,0);g.addColorStop(0,'#3b1d7a');g.addColorStop(1,'#1a0c3a')}
  c.fillStyle=g;c.strokeStyle=f?'#fff':gh?'rgba(138,92,240,.4)':'#8a5cf0';c.lineWidth=1.6;
  c.beginPath();c.ellipse(-12,-12,10,10,0,0,7);c.fill();c.stroke();
  c.beginPath();c.ellipse(-1,-12,17,9,0,0,7);c.fill();c.stroke();
  /* spine spikes */
  if(!gh){
    c.fillStyle=f?'#fff':'#2a1458';c.strokeStyle=f?'#fff':'#a98bff';c.lineWidth=1.1;
    for(let i=0;i<8;i++){const x=-14+i*3.4,yb=-12-9*Math.sqrt(Math.max(0,1-((x+1)/17)*((x+1)/17)));c.beginPath();c.moveTo(x-2.4,yb+1.2);c.lineTo(x+.7,yb-5.8);c.lineTo(x+2.6,yb+1.2);c.closePath();c.fill();c.stroke()}
  }
  /* head */
  c.fillStyle=g;c.strokeStyle=f?'#fff':gh?'rgba(138,92,240,.4)':'#8a5cf0';c.lineWidth=1.6;
  c.beginPath();c.moveTo(8,-19);c.lineTo(11-6*E,-27+8*E);c.lineTo(14,-21);c.lineTo(18-6*E,-26+8*E);c.lineTo(20,-19);c.lineTo(26,-11);c.lineTo(24,-7);c.lineTo(14,-5);c.lineTo(8,-8);c.closePath();c.fill();c.stroke();
  if(!gh&&!o.dd){
    /* shoulder star scar */
    fGl(4,-13,12,'#ffd84d',.5);c.fillStyle='#ffd84d';star(4,-13,4.2,T/60);c.fill();
    /* teeth */
    c.strokeStyle='#0b0618';c.lineWidth=1.4;c.beginPath();c.moveTo(14.5,-7.2);c.lineTo(25,-10);c.stroke();
    c.fillStyle='#f5f0ff';for(let i=0;i<4;i++){const x=16+i*2.5,y=-7.2-(x-14.5)*.267;c.beginPath();c.moveTo(x,y);c.lineTo(x+1.7,y-.4);c.lineTo(x+.7,y+2.6);c.fill()}
    /* eye */
    if(o.closed){c.strokeStyle='#ff5a3c';c.lineWidth=1.6;c.beginPath();c.moveTo(14.5,-14.6);c.lineTo(19.5,-14.6);c.stroke()}
    else{
      eGl(17,-15,7+o.eg*8,o.eye,.55+.4*o.eg);
      c.fillStyle=o.eye;c.beginPath();c.ellipse(17,-15,3+o.eg*1.5,2.5+o.eg*1.3,0,0,7);c.fill();
      c.fillStyle='#0b0618';c.beginPath();c.ellipse(17.7,-15,.9,2.1+o.eg*.8,0,0,7);c.fill();
      c.fillStyle='#fff';c.beginPath();c.arc(16,-16.1,.8,0,7);c.fill();
    }
  }
  c.restore();
}
function fgDraw(e){
  const Q=HE.fang,f=e.fl>0,dd=!!e.dd,cx=e.x+e.w/2,fy=e.y+e.h,d=e.d>0?1:-1,T=tick;
  const crouching=e.st==1||e.st==3,pr=e.st==1?1-e.tm/Q.crouch:e.st==3?1-e.tm/Q.crouch2:0,cr=crouching?Math.min(1,pr*1.8):e.st==2?.45:0;
  if(!dd&&crouching&&e.arc&&e.arc.length>3){      /* tell: dotted leap arc + landing mark (aims where you WERE) */
    c.save();c.setLineDash([5,6]);c.lineDashOffset=-T*.7;c.lineCap='round';
    c.strokeStyle=Q.col;c.globalAlpha=.3+.55*pr;c.lineWidth=2;c.beginPath();c.moveTo(e.arc[0],e.arc[1]);
    for(let i=2;i<e.arc.length;i+=2)c.lineTo(e.arc[i],e.arc[i+1]);c.stroke();
    c.restore();
  }
  if(!dd&&(e.st==4&&e.mx!==undefined||crouching&&e.sol)){
    const mx=e.st==4?e.mx:e.sol.mx,my=e.st==4?e.my:e.sol.my,s=7+Math.sin(T/4)*1.2;
    c.save();c.strokeStyle=Q.col;c.lineWidth=2.6;c.lineCap='round';c.globalAlpha=.85;
    c.beginPath();c.moveTo(mx-s,my-s);c.lineTo(mx+s,my+s);c.moveTo(mx+s,my-s);c.lineTo(mx-s,my+s);c.stroke();c.restore();
  }
  if(!dd&&e.st==4&&e.tr){      /* shadow after-images */
    const n=e.tr.length/2;
    for(let k=n-1;k>=0;k--){
      c.save();c.globalAlpha=.34*(1-k/(n+.5));c.translate(e.tr[k*2]+e.w/2,e.tr[k*2+1]+e.h);c.scale(d,1);
      fgBody({gh:1,air:1,cr:0,id:e.id,eg:0,eye:'#000'});c.restore();
    }
  }
  const air=e.st==4,ang=air?Math.atan2(e.vy,Math.abs(e.vx)+1)*.55:0;
  c.save();c.translate(cx,fy);c.scale(d,1);
  fgBody({f,dd,id:e.id,cr:dd?0:cr,ear:dd?0:(crouching?Math.min(1,pr*2):e.st==6?.7:0),air,ang,wk:e.st==0&&!dd,sq:e.sq||0,dz:e.st==6,closed:e.st==6,
    eye:e.st==3?'#ffffff':Q.col,eg:dd?0:crouching?Math.min(1,pr*1.6):air?.8:e.st==0&&e.hu?.35:.15});
  c.restore();
  if(!dd&&e.st==6){      /* dazed: orbiting stars */
    c.save();c.fillStyle='#ffd84d';
    for(let k=0;k<3;k++){const a=T/10+k*2.094,sx=cx+d*14+Math.cos(a)*13,sy=fy-30+Math.sin(a)*3.6;fGl(sx,sy,8,'#ffd84d',.5);star(sx,sy,3.6,T/14+k);c.fill()}
    c.restore();
  }
}
HEH.drawFront.push(function(){      /* claw waves (the generic painter draws nothing for k:'cw') */
  const Q=HE.fang;
  for(const q of pj){
    if(q.k!=='cw')continue;
    const h=Q.waveH;
    for(let k=3;k>=0;k--){
      c.save();c.translate(q.x-q.dir*k*7,q.sy);c.scale(q.dir,1);c.globalAlpha=(k==0?1:.5/k);
      c.lineCap='round';
      c.strokeStyle='rgba(255,90,60,.35)';c.lineWidth=7;c.beginPath();c.ellipse(-4,0,12,h,0,-Math.PI/2,0);c.stroke();
      c.strokeStyle=k==0?'#ffb08a':'#ff5a3c';c.lineWidth=3;c.stroke();
      c.restore();
    }
    eGl(q.x,q.sy-5,13,'#ff5a3c',.3);
  }
});
HEX[8]={name:'Night-Fang',hint:'NIGHT-FANG!',col:HE.fang.col,w:HE.fang.w,h:HE.fang.h,unlock:HE.fang.unlock,max:HE.fang.max,weight:HE.fang.weight,
  place:'platform',moving:true,hp:s=>HE.fang.hpBase+(s>>3),quiet:false,
  init(e){e.tr=[];e.arc=null;e.sol=null;e.ft=0;e.hu=0;e.sq=0;e.vx=0;e.vy=0},
  ai:fgAI,dazed:fgDazed,dmg:fgDmg,contact:fgContact,draw:fgDraw,onKill:fgKill};
/* ===== /HE part 3 ===== */
'''

old = '/* ===== /HE part 2 ===== */\n'
assert s.count(old) == 1
s = s.replace(old, old + BLOCK)
open(out_path, 'w', encoding='utf-8').write(s)
print('OK', len(s.encode('utf-8')), 'bytes')

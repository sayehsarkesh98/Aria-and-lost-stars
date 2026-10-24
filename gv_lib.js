/* gv_lib.js — Track B reference algorithms (pure, DOM-free, unit-tested in gv_lib.test.mjs).
   Paste the body (without the UMD wrapper) into the game inside the "GV part 8: core" marker block, keep names, adapt only glue.
   Everything here is deterministic: no Math.random, no Date, no performance.now. Time = integer sim ticks (60/s). */
(function(root,f){if(typeof module=='object'&&module.exports)module.exports=f();else root.GVLIB=f()})(this,function(){
'use strict';
const clamp=(v,a,b)=>v<a?a:v>b?b:v, lerp=(a,b,t)=>a+(b-a)*t;
/* ---------- easing: every ez[k](0)==0 and ez[k](1)==1 (pulse: 0 -> 1 at .5 -> 0). t is clamped. ---------- */
const ez={
  lin:t=>clamp(t,0,1),
  inQuad:t=>(t=clamp(t,0,1))*t,
  outQuart:t=>1-Math.pow(1-clamp(t,0,1),4),
  inOutCubic:t=>(t=clamp(t,0,1))<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,
  inOutSine:t=>-(Math.cos(Math.PI*clamp(t,0,1))-1)/2,
  outBack:t=>{t=clamp(t,0,1);const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2)},
  outElastic:t=>{t=clamp(t,0,1);return t==0||t==1?t:Math.pow(2,-10*t)*Math.sin((t*10-.75)*(2*Math.PI/3))+1},
  outBounce:t=>{t=clamp(t,0,1);const n=7.5625,d=2.75;if(t<1/d)return n*t*t;if(t<2/d)return n*(t-=1.5/d)*t+.75;if(t<2.5/d)return n*(t-=2.25/d)*t+.9375;return n*(t-=2.625/d)*t+.984375},
  pulse:t=>Math.sin(Math.PI*clamp(t,0,1)),
};
/* ---------- critically-ish damped spring (fixed step; k in (0,1), d in (0,1)) ---------- */
function spring(s,target,k,d){s.v+=(target-s.x)*k;s.v*=d;s.x+=s.v;return s}
/* ---------- hashing / noise (deterministic, seedable) ---------- */
const hash2=(i,j,seed)=>{let h=Math.imul(i|0,374761393)+Math.imul(j|0,668265263)+Math.imul(seed|0,1274126177);h=Math.imul(h^(h>>>13),1274126177);return((h^(h>>>16))>>>0)/4294967296};
const vnoise=(x,seed)=>{const i=Math.floor(x),f=x-i,u=f*f*(3-2*f);return lerp(hash2(i,0,seed),hash2(i+1,0,seed),u)};          // [0,1)
const fbm=(x,seed,oct)=>{let a=.5,s=0,n=0;for(let o=0;o<(oct||3);o++){s+=a*vnoise(x*(1<<o),seed+o*31);n+=a;a*=.5}return s/n};
const fnv=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0};
/* identical to the game's rng(s) (v31 L902) so streams can be mixed with game code */
function rng(s){return()=>{s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const stream=(name,seed)=>rng((fnv(name)^Math.imul(seed|0,2654435761))|0);   // independent named streams: stream('storm',stage*977+retry)
/* ---------- struct-of-arrays particle pool: zero allocation per frame ---------- */
function Pool(cap,fields){const P={cap,n:0,f:{}};for(const k of fields)P.f[k]=new Float32Array(cap);
  P.add=function(){return this.n<this.cap?this.n++:-1};
  P.kill=function(i){const l=--this.n;if(i!==l)for(const k in this.f)this.f[k][i]=this.f[k][l]};   // swap-remove: iterate BACKWARDS when killing
  P.clear=function(){this.n=0};return P}
/* ---------- keyframe timeline: keys=[[t,v,ease?],…] sorted by t; ease applies to the segment ENDING at that key ---------- */
function tl(keys,t){if(t<=keys[0][0])return keys[0][1];for(let i=1;i<keys.length;i++){const[t1,v1,e]=keys[i];if(t<=t1){const[t0,v0]=keys[i-1];const u=(t-t0)/(t1-t0||1);return lerp(v0,v1,(e||ez.lin)(u))}}return keys[keys.length-1][1]}
/* ---------- tiny table-driven FSM (data + validator). def={name:{dur,next,on:{evt:state}}} ; dur 0/undefined = wait for event ---------- */
function fsmValidate(def,start){const names=Object.keys(def),err=[];
  for(const n of names){const s=def[n];if(s.dur!==undefined&&!(s.dur>=0))err.push(n+': bad dur');if(s.dur>0&&!def[s.next])err.push(n+': timed state needs valid next');for(const e in(s.on||{}))if(!def[s.on[e]])err.push(n+':'+e+' -> unknown '+s.on[e])}
  const seen=new Set([start]),q=[start];while(q.length){const s=def[q.pop()];if(!s)continue;for(const t of[s.next,...Object.values(s.on||{})])if(t&&!seen.has(t)){seen.add(t);q.push(t)}}
  for(const n of names)if(!seen.has(n))err.push(n+': unreachable');return err}
/* ================= CAPACITOR SLAB ================= */
const SLAB={chargeT:540,warnT:48,liveT:150,dischT:24,rest:90};
const slabNew=(q0)=>({s:'c',t:0,ch:q0||0});
function slabStep(q,c,add){switch(q.s){
  case'c':q.ch+=1/c.chargeT+(add||0);if(q.ch>=1){q.ch=1;q.s='w';q.t=0;return'warn'}break;
  case'w':if(++q.t>=c.warnT){q.s='l';q.t=0;return'live'}break;
  case'l':if(++q.t>=c.liveT){q.s='d';q.t=0;return'disch'}break;
  case'd':if(++q.t>=c.dischT){q.s='c';q.t=0;q.ch=-c.rest/c.chargeT;return'rest'}break}return null}
function slabGround(q,c,ins){if(ins||(q.s!='w'&&q.s!='l'))return false;q.s='d';q.t=0;return true}
const slabJar=q=>clamp(q.ch,0,1);                         // what the jar shows
/* ================= POOL ================= */
const POOL={tellT:40,liveT:36};
const poolNew=()=>({s:'i',t:0});
function poolTrigger(p){if(p.s!='i')return false;p.s='t';p.t=0;return true}
function poolStep(p,c){if(p.s=='t'&&++p.t>=c.tellT){p.s='l';p.t=0;return'live'}if(p.s=='l'&&++p.t>=c.liveT){p.s='i';p.t=0;return'idle'}return null}
/* ================= CHARGED ENEMY ================= */
function chargedExtra(dx,dy,spd){return[dx*spd,dy*spd]}
function clampToPlatform(x,w,p){return clamp(x,p.x,p.x+p.w-w)}
/* ================= SINKING GRAVE ================= */
const SINK={v:.55,up:.9,max:56,swallowT:240};
const sinkNew=(w)=>({sk:0,ss:'n',gt:0,w:w,w0:w});          // ss: n normal | g gone
function sinkStep(p,occ,c){let ev=null;
  if(p.ss=='g'){if(--p.gt<=0){p.ss='n';p.w=p.w0;p.sk=c.max;ev='emerge'}return ev}
  if(occ)p.sk=Math.min(c.max,p.sk+c.v);else p.sk=Math.max(0,p.sk-c.up);
  if(occ&&p.sk>=c.max){p.ss='g';p.gt=c.swallowT;p.w=0;ev='swallow'}return ev}
/* ================= SOUL LANTERN ================= */
const LAMP={litT:420,flickerT:70};
const lampNew=()=>({lit:0});
const lampHit=(l,c)=>{l.lit=c.litT};
const lampStep=l=>{if(l.lit>0)l.lit--};
const lampSolid=l=>l.lit>0;
const lampPhase=(l,c)=>l.lit<=0?'dark':l.lit<=c.flickerT?'flicker':'lit';
/* ================= CANTOR BRIDGE ================= */
const CANTOR={hold:150,tell:36,anim:18};
const CSEQ=[0,1,2,1];
/* cell i of a 3^k-cell bridge is present at iteration n iff none of its top-n ternary digits equals 1 */
function cantorPresent(i,n,digits){digits=digits||2;const ds=[];let v=i;for(let q=0;q<digits;q++){ds.unshift(v%3);v=(v/3)|0}for(let q=0;q<n;q++)if(ds[q]==1)return false;return true}
function cantorSched(t,c,ph){const L=c.hold+c.tell+c.anim,cyc=4*L,tau=(((t+(ph||0))%cyc)+cyc)%cyc,k=(tau/L)|0,r=tau-k*L,cur=CSEQ[k],nxt=CSEQ[(k+1)%4];
  return r<c.hold?{cur,nxt,ph:'hold',u:0}:r<c.hold+c.tell?{cur,nxt,ph:'tell',u:(r-c.hold)/c.tell}:{cur,nxt,ph:'anim',u:(r-c.hold-c.tell)/c.anim}}
/* collision width factor (0..1) of cell i — the ONLY thing the sim writes to p.w; visuals may overshoot separately */
function cantorW(i,s){const a=cantorPresent(i,s.cur),b=cantorPresent(i,s.nxt);if(a&&b)return 1;if(!a&&!b)return 0;
  if(s.ph!='anim')return a?1:0;return a?1-ez.inOutCubic(s.u):clamp(ez.outBack(s.u),0,1)}
/* ================= FLASH LIMITER ================= */
function flashNew(max,minGap){return{max,minGap,last:-1e9}}
function flashReq(f,a,t){if(t-f.last<f.minGap)return 0;f.last=t;return Math.min(a,f.max)}
/* ================= STORM DIRECTOR ================= */
function stormNew(seed,rods,every,grace){const R=stream('storm',seed);let t=grace,prev=-1;
  return{next(){let r;do{r=(R()*rods)|0}while(rods>1&&r==prev);prev=r;const at=t;t+=Math.round(every*(.85+R()*.3));return{at,rod:r}}}}
/* ================= LIGHTNING TELL GEOMETRY (deterministic fractal leader) ================= */
function leader(x0,y0,x1,y1,seed,depth,jit){const R=rng(seed),pts=[[x0,y0],[x1,y1]];
  for(let d=0;d<depth;d++){const o=[pts[0]],s=jit/Math.pow(2,d);for(let i=1;i<pts.length;i++){const a=pts[i-1],b=pts[i],mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2,dx=b[0]-a[0],dy=b[1]-a[1],L=Math.hypot(dx,dy)||1,n=(R()-.5)*2*s;o.push([mx-dy/L*n,my+dx/L*n],b)}pts.length=0;pts.push(...o)}return pts}
/* ================= CABLES (fractal power lines) + pulse lookup ================= */
function cableBuild(pts){const n=pts.length,cum=new Float32Array(n);for(let i=1;i<n;i++)cum[i]=cum[i-1]+Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);return{pts,cum,len:cum[n-1]}}
function cablePos(c,s,out){out=out||[0,0];s=clamp(s,0,c.len);let lo=0,hi=c.cum.length-1;while(hi-lo>1){const m=(lo+hi)>>1;if(c.cum[m]<=s)lo=m;else hi=m}
  const u=(s-c.cum[lo])/((c.cum[hi]-c.cum[lo])||1);out[0]=lerp(c.pts[lo][0],c.pts[hi][0],u);out[1]=lerp(c.pts[lo][1],c.pts[hi][1],u);return out}
/* binary-branching roots/trees: returns flat segments [x0,y0,x1,y1,depth]; 2^(d+1)-1 segments; deterministic */
function rootSegs(x,y,len,ang,depth,seed,spread,shrink){const R=rng(seed),out=[];spread=spread||.38;shrink=shrink||.72;
  (function rec(x,y,len,ang,d){const x1=x+Math.cos(ang)*len,y1=y+Math.sin(ang)*len;out.push([x,y,x1,y1,d]);if(d<=0)return;
    rec(x1,y1,len*shrink*(.9+R()*.2),ang-spread*(.7+R()*.6),d-1);rec(x1,y1,len*shrink*(.9+R()*.2),ang+spread*(.7+R()*.6),d-1)})(x,y,len,ang,depth);return out}
/* strike damage zone: disc around the rod tip OR the vertical bolt column above it */
function strikeHit(px,py,rod,r,colHalf){const dx=px-rod.x,dy=py-rod.tipY;return dx*dx+dy*dy<=r*r||(Math.abs(dx)<=colHalf&&py<=rod.tipY)}
return{cableBuild,cablePos,rootSegs,strikeHit,clamp,lerp,ez,spring,hash2,vnoise,fbm,fnv,rng,stream,Pool,tl,fsmValidate,SLAB,slabNew,slabStep,slabGround,slabJar,POOL,poolNew,poolTrigger,poolStep,chargedExtra,clampToPlatform,SINK,sinkNew,sinkStep,LAMP,lampNew,lampHit,lampStep,lampSolid,lampPhase,CANTOR,CSEQ,cantorPresent,cantorSched,cantorW,flashNew,flashReq,stormNew,leader}});

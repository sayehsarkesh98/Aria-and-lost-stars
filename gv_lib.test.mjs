import assert from 'node:assert/strict';
import {createRequire} from 'module';
const require=createRequire(import.meta.url);
const L=require('./gv_lib.js'), M=require('./gv_migrate.js');
let n=0;const T=(name,f)=>{try{f();n++;console.log('ok  ',name)}catch(e){console.log('FAIL',name,'\n    ',e.message);process.exitCode=1}};
const R=L.rng(12345);

T('easing endpoints + monotone + clamp',()=>{
  for(const k of ['lin','inQuad','outQuart','inOutCubic','inOutSine','outBack','outElastic','outBounce']){
    assert.ok(Math.abs(L.ez[k](0))<1e-9,k+'(0)');assert.ok(Math.abs(L.ez[k](1)-1)<1e-9,k+'(1)');assert.equal(L.ez[k](-5),L.ez[k](0));assert.equal(L.ez[k](9),L.ez[k](1))}
  for(const k of ['lin','inQuad','outQuart','inOutCubic','inOutSine']){let p=-1;for(let i=0;i<=200;i++){const v=L.ez[k](i/200);assert.ok(v>=p-1e-12,k+' monotone');p=v}}
  assert.ok(Math.max(...Array.from({length:101},(_,i)=>L.ez.outBack(i/100)))>1.05,'outBack overshoots');
  assert.ok(Math.abs(L.ez.pulse(.5)-1)<1e-9&&L.ez.pulse(0)<1e-9&&L.ez.pulse(1)<1e-9)});
T('spring converges, finite, bounded',()=>{for(const k of[.05,.1,.2,.4])for(const d of[.7,.8,.9]){const s={x:0,v:0};let mx=0;for(let i=0;i<600;i++){L.spring(s,10,k,d);assert.ok(Number.isFinite(s.x));mx=Math.max(mx,Math.abs(s.x))}assert.ok(Math.abs(s.x-10)<1e-3,`k${k} d${d}`);assert.ok(mx<25)}});
T('rng deterministic, [0,1), streams independent',()=>{const a=L.rng(7),b=L.rng(7);for(let i=0;i<1000;i++){const x=a();assert.equal(x,b());assert.ok(x>=0&&x<1)}
  const s1=L.stream('storm',5),s2=L.stream('storm',5),s3=L.stream('rain',5),s4=L.stream('storm',6);let same=0,eq=0;for(let i=0;i<200;i++){const v=s1();if(v===s2())eq++;if(v===s3()||v===s4())same++}assert.equal(eq,200);assert.equal(same,0)});
T('noise in range, deterministic, continuous',()=>{let p=L.vnoise(0,3);for(let i=1;i<2000;i++){const x=i*.02,v=L.vnoise(x,3);assert.ok(v>=0&&v<1);assert.ok(Math.abs(v-p)<.12);assert.equal(v,L.vnoise(x,3));p=v}for(let i=0;i<500;i++){const v=L.fbm(i*.3,9,4);assert.ok(v>=0&&v<1)}});
T('pool: capacity, swap-remove integrity',()=>{const P=L.Pool(64,['a','b']);for(let i=0;i<64;i++){const j=P.add();assert.equal(j,i);P.f.a[j]=i;P.f.b[j]=i*2}assert.equal(P.add(),-1);
  const alive=new Set(Array.from({length:64},(_,i)=>i));for(let r=0;r<40;r++){const i=(R()*P.n)|0,v=P.f.a[i];alive.delete(v);P.kill(i)}
  assert.equal(P.n,24);const got=new Set();for(let i=0;i<P.n;i++){got.add(P.f.a[i]);assert.equal(P.f.b[i],P.f.a[i]*2)}assert.deepEqual([...got].sort((a,b)=>a-b),[...alive].sort((a,b)=>a-b))});
T('timeline exact at keys, clamped, eased',()=>{const k=[[0,0],[10,5,L.ez.inOutCubic],[30,1,L.ez.outBack]];assert.equal(L.tl(k,-3),0);assert.equal(L.tl(k,10),5);assert.ok(Math.abs(L.tl(k,30)-1)<1e-9);assert.equal(L.tl(k,99),1);assert.ok(Math.abs(L.tl(k,5)-2.5)<1e-9)});
T('fsm validator',()=>{const ok={c:{dur:60,next:'w'},w:{dur:10,next:'l'},l:{dur:20,next:'c',on:{ground:'c'}}};assert.deepEqual(L.fsmValidate(ok,'c'),[]);
  const bad={a:{dur:5,next:'zzz'},b:{dur:0}};const e=L.fsmValidate(bad,'a');assert.ok(e.length>=2)});
T('slab: phase lengths + full cycle + boost + ground',()=>{const c=L.SLAB;const q=L.slabNew(0),ev=[];let t=0;while(ev.length<4&&t<5000){const e=L.slabStep(q,c);t++;if(e)ev.push([e,t])}
  assert.deepEqual(ev.map(x=>x[0]),['warn','live','disch','rest']);
  assert.ok(Math.abs(ev[0][1]-c.chargeT)<=1);assert.equal(ev[1][1]-ev[0][1],c.warnT);assert.equal(ev[2][1]-ev[1][1],c.liveT);assert.equal(ev[3][1]-ev[2][1],c.dischT);
  // second cycle includes the rest delay
  let t2=0,w=false;while(!w&&t2<5000){if(L.slabStep(q,c)=='warn')w=true;t2++}assert.ok(Math.abs(t2-(c.chargeT+c.rest))<=1);
  const b=L.slabNew(0);let tb=0;while(L.slabStep(b,c,.002)!='warn')tb++;assert.ok(tb<c.chargeT);
  const g=L.slabNew(0);g.s='l';assert.ok(L.slabGround(g,c,false)&&g.s=='d');const i2=L.slabNew(0);i2.s='l';assert.ok(!L.slabGround(i2,c,true)&&i2.s=='l');const cc=L.slabNew(0);assert.ok(!L.slabGround(cc,c,false));
  const j=L.slabNew(0);let pj=-1;for(let i=0;i<300;i++){L.slabStep(j,c);assert.ok(L.slabJar(j)>=pj);pj=L.slabJar(j)}});
T('slab: staggered start charges never sync',()=>{const c=L.SLAB,a=L.slabNew(.15),b=L.slabNew(.55);let ta=0,tb=0;while(L.slabStep(a,c)!='warn')ta++;while(L.slabStep(b,c)!='warn')tb++;assert.ok(Math.abs(ta-tb)>100)});
T('pool fsm',()=>{const p=L.poolNew(),c=L.POOL;assert.ok(L.poolTrigger(p));assert.ok(!L.poolTrigger(p));let t=0,ev=[];while(ev.length<2&&t<500){const e=L.poolStep(p,c);t++;if(e)ev.push([e,t])}assert.deepEqual(ev,[['live',c.tellT],['idle',c.tellT+c.liveT]]);assert.ok(L.poolTrigger(p))});
T('sink: swallow time, no teleports, w in {0,w0}, emerge',()=>{const c=L.SINK,p=L.sinkNew(100);let t=0,prev=0,ev=[];while(ev.length<1&&t<1000){const e=L.sinkStep(p,true,c);t++;assert.ok(Math.abs(p.sk-prev)<=c.v+1e-9);prev=p.sk;assert.ok(p.w==0||p.w==100);if(e)ev.push([e,t])}
  assert.equal(ev[0][0],'swallow');assert.equal(ev[0][1],Math.ceil(c.max/c.v));
  let t2=0,e2=null;while(!e2&&t2<1000){e2=L.sinkStep(p,false,c);t2++}assert.equal(e2,'emerge');assert.equal(t2,c.swallowT);assert.equal(p.w,100);assert.equal(p.sk,c.max);
  for(let i=0;i<100;i++){L.sinkStep(p,false,c)}assert.equal(p.sk,0);
  const q=L.sinkNew(100);for(let i=0;i<60;i++)L.sinkStep(q,true,c);const mid=q.sk;for(let i=0;i<200;i++)L.sinkStep(q,false,c);assert.ok(mid>0&&q.sk==0&&q.ss=='n')});
T('lamp phases',()=>{const l=L.lampNew(),c=L.LAMP;assert.equal(L.lampPhase(l,c),'dark');L.lampHit(l,c);assert.ok(L.lampSolid(l));assert.equal(L.lampPhase(l,c),'lit');let f=0,s=0;while(L.lampSolid(l)){if(L.lampPhase(l,c)=='flicker')f++;L.lampStep(l);s++}assert.equal(s,c.litT);assert.equal(f,c.flickerT)});
T('cantor sets (ternary rule)',()=>{const set=n=>[...Array(9).keys()].filter(i=>L.cantorPresent(i,n));assert.deepEqual(set(0),[0,1,2,3,4,5,6,7,8]);assert.deepEqual(set(1),[0,1,2,6,7,8]);assert.deepEqual(set(2),[0,2,6,8])});
T('cantor: permanent anchors, width in [0,1], periodic, changes only in anim',()=>{const c=L.CANTOR,cyc=4*(c.hold+c.tell+c.anim);
  for(const ph of[0,77,311])for(let t=0;t<cyc*2;t++){const s=L.cantorSched(t,c,ph);for(const i of[0,2,6,8])assert.equal(L.cantorW(i,s),1);for(let i=0;i<9;i++){const w=L.cantorW(i,s);assert.ok(w>=0&&w<=1);if(s.ph!='anim')assert.ok(w==0||w==1)}
    const s2=L.cantorSched(t+cyc,c,ph);assert.deepEqual(s,s2)}
  // tell always precedes a width change by >= tell ticks
  let lastW=null,tellRun=0;for(let t=0;t<cyc;t++){const s=L.cantorSched(t,c,0);const w=L.cantorW(4,s);if(lastW!==null&&w!==lastW&&s.ph=='anim'&&tellRun<c.tell)assert.fail('width changed without full tell');tellRun=s.ph=='tell'?tellRun+1:(s.ph=='hold'?0:tellRun);lastW=w}});
T('flash limiter: <=3 per second, alpha<=max',()=>{const f=L.flashNew(.5,20);let acc=[];for(let t=0;t<20000;t++){if(R()<.25){const a=L.flashReq(f,R()*2,t);if(a>0){assert.ok(a<=.5);acc.push(t)}}}
  for(let i=0;i<acc.length;i++){const w=acc.filter(x=>x>=acc[i]&&x<acc[i]+60).length;assert.ok(w<=3,'window '+w)}});
T('storm director: deterministic, no repeats, spacing, grace',()=>{const a=L.stormNew(977*13+2,3,420,180),b=L.stormNew(977*13+2,3,420,180);let prev=-1,last=null;for(let i=0;i<500;i++){const x=a.next(),y=b.next();assert.deepEqual(x,y);assert.notEqual(x.rod,prev);prev=x.rod;if(i==0)assert.ok(x.at>=180);if(last!==null){const g=x.at-last;assert.ok(g>=Math.round(420*.85)&&g<=Math.round(420*1.15)+1)}last=x.at}
  const c=L.stormNew(1,1,420,0);assert.equal(c.next().rod,0);assert.equal(c.next().rod,0)});
T('leader fractal: endpoints, count, determinism',()=>{const a=L.leader(100,0,140,300,42,6,40),b=L.leader(100,0,140,300,42,6,40);assert.deepEqual(a,b);assert.equal(a.length,(1<<6)+1);assert.deepEqual(a[0],[100,0]);assert.deepEqual(a[a.length-1],[140,300]);for(const p of a)assert.ok(Number.isFinite(p[0])&&Number.isFinite(p[1]))});
T('cables: cumulative length, position lookup, endpoints',()=>{const pts=L.leader(0,0,300,400,5,5,30),c=L.cableBuild(pts);let len=0;for(let i=1;i<pts.length;i++)len+=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);assert.ok(Math.abs(c.len-len)<.01);
  assert.deepEqual(L.cablePos(c,0).map(Math.round),[0,0]);assert.deepEqual(L.cablePos(c,c.len).map(Math.round),[300,400]);assert.deepEqual(L.cablePos(c,-9).map(Math.round),[0,0]);assert.deepEqual(L.cablePos(c,1e9).map(Math.round),[300,400]);
  let prev=0;for(let s=0;s<=c.len;s+=c.len/200){const q=L.cablePos(c,s);const d=Math.hypot(q[0]-pts[0][0],q[1]-pts[0][1]);assert.ok(Number.isFinite(d));}
  for(let s=0;s<c.len-5;s+=7){const a=L.cablePos(c,s),b=L.cablePos(c,s+5);assert.ok(Math.hypot(a[0]-b[0],a[1]-b[1])<=5.001)}});
T('roots: segment count 2^(d+1)-1, deterministic, finite',()=>{for(const d of[1,3,5]){const a=L.rootSegs(100,100,40,Math.PI/2,d,9),b=L.rootSegs(100,100,40,Math.PI/2,d,9);assert.equal(a.length,Math.pow(2,d+1)-1);assert.deepEqual(a,b);for(const s of a)for(const v of s)assert.ok(Number.isFinite(v))}});
T('strike zone: disc + column above tip only',()=>{const rod={x:100,tipY:200};assert.ok(L.strikeHit(100,200,rod,38,14));assert.ok(L.strikeHit(130,215,rod,38,14));assert.ok(!L.strikeHit(160,200,rod,38,14));assert.ok(L.strikeHit(105,20,rod,38,14));assert.ok(!L.strikeHit(105,260,rod,38,14));assert.ok(!L.strikeHit(140,20,rod,38,14))});
/* ---------- migration ---------- */
T('migration: mapping, idempotent, monotone, immutability',()=>{
  for(const clr of[[0,0,0],[10,10,10],[11,12,13],[14,14,14],[3,11,14]]){const p={fin:[0,0,0],clr};const q=M.migProg(p);assert.deepEqual(p.clr,clr,'input untouched');assert.equal(q.cv,2);for(let i=0;i<3;i++){assert.equal(q.clr[i],clr[i]>=11?clr[i]+3:clr[i])}assert.equal(M.migProg(q),q,'idempotent (same ref)')}
  for(let a=0;a<=14;a++)for(let b=a;b<=14;b++){assert.ok(M.mig(a)<=M.mig(b))}
  assert.equal(M.mig(14),17);assert.equal(M.mig(10),10);assert.equal(M.mig(11),14);
  const r={v:1,d:2,st:12,cp:11,cs:5000,sc:9000,hp:3,mh:5,lv:4,xp:7,nx:1e4,gt:99,ups:{dj:1,dash:1,dmg:2}};const r2=M.migRun(r);assert.equal(r2.st,15);assert.equal(r2.cp,14);assert.equal(r2.cs,5000);assert.deepEqual(r2.ups,r.ups);assert.equal(M.migRun(r2),r2);assert.equal(r.st,12);
  const low={v:1,st:7,cp:7};assert.deepEqual(M.migRun(low),{v:1,st:7,cp:7,cv:2});
  assert.ok(M.migRun(Object.assign({},r,{st:14})).st<=17)});
T('migration: bad data untouched; store wrapper',()=>{
  assert.equal(M.migProg(null),null);assert.deepEqual(M.migProg({fin:1}),{fin:1});assert.equal(M.migRun('x'),'x');assert.deepEqual(M.migRun({v:2,st:12}),{v:2,st:12});
  const mem=new Map([['aria_prog','{"fin":[1,0,0],"clr":[14,3,0]}'],['aria_run','{"v":1,"d":0,"st":13,"cp":11}'],['aria_best2_0','500']]);const st={getItem:k=>mem.has(k)?mem.get(k):null,setItem:(k,v)=>mem.set(k,v)};
  assert.equal(M.migStore(st),2);assert.deepEqual(JSON.parse(mem.get('aria_prog')),{fin:[1,0,0],clr:[17,3,0],cv:2});assert.deepEqual(JSON.parse(mem.get('aria_run')),{v:1,d:0,st:16,cp:14,cv:2});assert.equal(mem.get('aria_best2_0'),'500');assert.equal(M.migStore(st),0);
  const bad=new Map([['aria_prog','{oops'],['aria_run','null']]);const st2={getItem:k=>bad.has(k)?bad.get(k):null,setItem:(k,v)=>bad.set(k,v)};assert.equal(M.migStore(st2),0);assert.equal(bad.get('aria_prog'),'{oops');
  const th={getItem(){throw new Error('x')},setItem(){throw new Error('y')}};assert.equal(M.migStore(th),0)});
T('migration: bag (imported save file)',()=>{const bag={aria_prog:{fin:[0,1,0],clr:[0,13,10]},aria_run:{v:1,st:11,cp:11},aria_best2_1:700,aria_costumes:['cosmic']};const o=M.migBag(bag);assert.deepEqual(o.aria_prog.clr,[0,16,10]);assert.equal(o.aria_run.st,14);assert.equal(o.aria_best2_1,700);assert.deepEqual(o.aria_costumes,['cosmic']);assert.equal(bag.aria_prog.cv,undefined);assert.deepEqual(M.migBag(o),o)});
console.log(`\n${n} test groups passed`);

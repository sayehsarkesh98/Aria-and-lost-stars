#!/usr/bin/env node
// gv_reach.mjs — physics-accurate platform reachability for Aria stages (v31 player physics, verified from update()).
// Usage:  node gv_reach.mjs seeds [11|12|13]          -> check tools/gv_seeds.json
//         node gv_reach.mjs html path/to/aria.html    -> extract `const GVL={...}` from the game and check stages 11-13
// Options: --nodash  --nodj  (default: double jump + dash available, i.e. stage >= 5)
// Model: a policy search (direction, jump-hold length, double-jump tick, dash tick) simulated tick-by-tick with the REAL constants;
//        movers are sampled at 3 phases; Cantor cells are checked in each of the 3 Cantor states; spectral slabs are treated as ABSENT
//        (shortcut-only rule) and sinking graves/capacitors as normal solids. A start position is any x on the source platform.
import fs from 'fs';
const W=1000,H=600,GY=560,PW=32,PH=42;
const args=process.argv.slice(2),flags=new Set(args.filter(a=>a.startsWith('--')));
const dj=!flags.has('--nodj'),dash=!flags.has('--nodash');
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
// ---- exact player integrator (mirrors update(): accel .9, friction .78, clamp ±5, g .62 (max 14), jump -13, double -12, cut -4, dash 9 ticks @13, coyote 7, buffer 8)
function simulate(P,sx,sy,gp,pol){
  let x=sx,y=sy,vx=0,vy=0,g=gp,cy=7,used=0,jb=0,dt=0,d=pol.dir||1,landed=null;
  const dc0=0;let dcd=0;
  for(let t=0;t<pol.T;t++){
    const dir=t>=pol.dirFrom?(t<pol.dirTo?pol.dir:0):0;
    const holdJump=t<pol.hold;
    if(t==0&&pol.jump)jb=8;
    if(pol.dj>=0&&t==pol.dj)jb=8;
    dcd--;
    if(dash&&pol.dash>=0&&t==pol.dash&&dcd<=0&&dt<=0){dt=9;dcd=55}
    if(dt>0){dt--;vx=d*13;vy=0}
    else{ if(dir<0){vx-=.9;d=-1}else if(dir>0){vx+=.9;d=1}else vx*=.78; vx=clamp(vx,-5,5); vy=Math.min(14,vy+.62) }
    cy=g?7:cy-1; if(jb>0)jb--;
    if(jb>0&&cy>0){vy=-13;cy=0;jb=0;g=null}
    else if(jb>0&&dj&&!g&&!used){used=1;jb=0;vy=-12}
    if(!holdJump&&vy<-4&&dt<=0)vy=-4;
    const pb=y+PH; x=clamp(x+vx,0,W-PW); y+=vy; g=null;
    if(vy>=0)for(const p of P){ if(x+PW>p.x&&x<p.x+p.w&&pb<=p.y+6&&y+PH>=p.y){y=p.y-PH;vy=0;g=p;used=0;break} }
    if(g&&t>2){landed=g;break}
    if(y>H+80)break;
  }
  return landed;
}
function policies(){
  const out=[];
  for(const dir of[-1,1])for(const jump of[0,1])for(const hold of jump?[3,6,10,15,21,60]:[0])
   for(const dirFrom of[0,3,8])for(const dirTo of[14,24,34,48,80])
    for(const djT of(dj&&jump?[-1,8,14,20,26,32]:[-1]))for(const dashT of(dash&&jump?[-1,6,16,26]:[-1]))
     out.push({dir,jump,hold,dirFrom,dirTo,dj:djT,dash:dashT,T:130});
  return out;
}
const POL=policies();
function expand(stage,cantorState){
  const P=[];const idx=[];
  stage.plats.forEach((p,i)=>{
    if(p.fx=='l')return;                       // spectral: shortcut only -> absent
    if(p.fx=='u'){const cw=p.cw,n=p.cells;for(let k=0;k<n;k++){ // present(k, iter) = none of the top `iter` ternary digits is 1
        let ok=true,v=k,digs=[];for(let q=0;q<2;q++){digs.unshift(Math.floor(v%3));v=Math.floor(v/3)}
        for(let q=0;q<cantorState;q++)if(digs[q]==1)ok=false;
        if(ok){P.push({x:p.x+k*cw,y:p.y,w:cw,src:i,cell:k});idx.push(i)}}return}
    if(p.t=='h'){for(const o of[-p.r,0,p.r])P.push({x:p.x+o,y:p.y,w:p.w,src:i,mover:1});return}
    P.push({x:p.x,y:p.y,w:p.w,src:i});
  });
  return P;
}
function reachFrom(P,start){
  const seen=new Set(),q=[...start];start.forEach(s=>seen.add(s));
  while(q.length){const a=q.pop(),A=P[a];
    const xs=[];for(let x=A.x;x<=A.x+A.w-PW;x+=Math.max(6,(A.w-PW)/8))xs.push(x);xs.push(A.x+A.w-PW,A.x);
    for(const sx of xs)for(const pol of POL){
      const L=simulate(P,sx,A.y-PH,A,pol); if(!L)continue; const b=P.indexOf(L);
      if(b>=0&&!seen.has(b)){seen.add(b);q.push(b)}
    }
    // walking off a ledge: covered by pol.jump=0 policies (dir held, no jump)
  }
  return seen;
}
function check(num,stage){
  const res=[];
  for(const cs of(stage.plats.some(p=>p.fx=='u')?[0,1,2]:[0])){
    const P=expand(stage,cs);
    // starting platform = the one containing the spawn (feet at rs.y+PH); floor y=560 also reachable by falling
    const [rx,ry]=stage.rs;let start=P.map((p,i)=>[p,i]).filter(([p])=>rx+16>=p.x&&rx+16<=p.x+p.w&&Math.abs(p.y-(ry+PH))<2).map(([,i])=>i);
    const seen=reachFrom(P,start);
    const srcSeen=new Set([...seen].map(i=>P[i].src));
    const need=[];stage.plats.forEach((p,i)=>{if(p.fx=='l'||p.fx=='u')return; if(!srcSeen.has(i))need.push(i)});
    const cellsMissing=[];if(cs>=0)stage.plats.forEach((p,i)=>{if(p.fx=='u'){const pr=P.filter(q=>q.src==i);const reached=pr.filter(q=>seen.has(P.indexOf(q))).length;cellsMissing.push(`${reached}/${pr.length} cells reachable`)}});
    res.push({cantorState:cs,start,unreachableStarEligible:need,bridge:cellsMissing});
  }
  return res;
}
let seeds;
if(args[0]=='html'){const t=fs.readFileSync(args[1],'utf8');let G=null,pos=-1;
  while((pos=t.indexOf('const GVL=',pos+1))>=0){let d=0,j=t.indexOf('{',pos),s0=j;for(;j<t.length;j++){if(t[j]=='{')d++;else if(t[j]=='}'){d--;if(!d)break}}
    try{G=new Function('return ('+t.slice(s0,j+1)+')')();if(G&&G[11])break;G=null}catch(e){G=null}}   // skip comment/schematic occurrences, take the first that evaluates
  if(!G)throw new Error('no evaluable `const GVL={...}` found');
  seeds={};for(const n in G){const g=G[n];seeds[n]={n:g.n,rs:g.rs,plats:g.p.map(a=>Object.assign({x:a[0],y:a[1],w:a[2],t:a[3]||0,r:a[4]||0,s:a[5]||0},a[7]||{}))}}}
else seeds=JSON.parse(fs.readFileSync(new URL('./gv_seeds.json',import.meta.url)));
const want=args.find(a=>/^\d+$/.test(a));let bad=0;
for(const n of Object.keys(seeds)){ if(want&&n!=want)continue; const r=check(n,seeds[n]);
  console.log(`stage ${n} ${seeds[n].n}`);for(const x of r){console.log(`  cantor state ${x.cantorState}: unreachable star-eligible platforms: [${x.unreachableStarEligible}] ${x.bridge.join(' ')}`);if(x.unreachableStarEligible.length)bad++}}
process.exit(bad?1:0);

/* gv_migrate.js — one-time stage-number migration for the 14 -> 17 stage campaign (old 11-14 become 14-17).
   Per-OBJECT version stamp `cv:2` (no new localStorage key): idempotent per object, robust if an old build overwrites a key,
   and works for localStorage reads, imported save files (`sane()`), save-folder restores and exports alike. Pure functions. */
(function(root,f){if(typeof module=='object'&&module.exports)module.exports=f();else root.GVMIG=f()})(this,function(){
'use strict';
const CV=2,SHIFT=3,FIRST=11;
const mig=n=>(typeof n=='number'&&isFinite(n)&&n>=FIRST)?n+SHIFT:n;
function migProg(p){if(!p||typeof p!='object'||!Array.isArray(p.clr)||!Array.isArray(p.fin))return p;if(p.cv===CV)return p;
  return Object.assign({},p,{clr:p.clr.map(mig),cv:CV})}
function migRun(r){if(!r||typeof r!='object'||r.v!==1)return r;if(r.cv===CV)return r;
  return Object.assign({},r,{st:mig(r.st),cp:mig(r.cp),cv:CV})}
function migBag(bag){if(!bag||typeof bag!='object')return bag;const o=Object.assign({},bag);if('aria_prog' in o)o.aria_prog=migProg(o.aria_prog);if('aria_run' in o)o.aria_run=migRun(o.aria_run);return o}
/* boot wrapper over a localStorage-like store {getItem,setItem}; never throws, never touches unparsable values */
function migStore(st){let n=0;for(const[k,f]of[['aria_prog',migProg],['aria_run',migRun]]){let raw;try{raw=st.getItem(k)}catch(e){continue}if(raw==null)continue;let v;try{v=JSON.parse(raw)}catch(e){continue}const w=f(v);if(w!==v){try{st.setItem(k,JSON.stringify(w));n++}catch(e){}}}return n}
return{CV,SHIFT,mig,migProg,migRun,migBag,migStore}});

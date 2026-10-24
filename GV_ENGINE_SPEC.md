# GV ENGINE SPEC — engineering contract for Track B (Fractal Necropolis)
Every Track B session reads **§1–§4 completely** and the sections its part cites. Nothing here changes Track B's scope; it makes the logic exact. Verified facts come from `aria_v31.html` (line numbers drift: re-grep). Reference algorithms live in `tools/` and are **unit-tested** (`node tools/gv_lib.test.mjs` → all groups must pass before AND after your patch).

## §1 Verified runtime facts (v31)
**1.1 Loop.** `frame(t)`: `acc+=min(100,dt)`; `while(acc>=16.667){update();acc-=16.667}` ⇒ 0…6 `update()` calls per animation frame, then `RA=acc/16.667` (render alpha 0…1), `ipOn(); draw0(); post(); ipOff()`. Display refresh can exceed 60 Hz, so draw runs several times per update.
**1.2 Clocks.** `update()` order: `ipSnap(); voS(); if(st=='cut'){cutU();return} if(hs>0){hs--;return} tick++ …`. Therefore `tick` **keeps advancing in menu, pause, clear and over states** and **freezes during hit-stop (`hs`) and cutscenes**. ⇒ *Gameplay timers must never use `tick`.* Track B introduces its own simulation clock `gv.t`, incremented once per tick **inside `GVH.step` only** (which runs only when `st=='play'` and not in hit-stop). `tick` is for decor that may keep moving in pause; `gv.t+RA` (fractional) is for sim-coupled visuals.
**1.3 Play-tick order (update):** particles/rings → `clear` branch → `if(st!='play')return` → `gt++; music(); movP()` → input & shooting → dash/accel/gravity → jump logic → *player integration + platform landing* → pit/lava `hurt(0,true)` → enemy loop (AI by `e.t`, carry `e.p.t`, contact) → `bl[]` stars → `pj[]` shots → boss. **Insert `GVH.kin` right after `movP()`** (platform kinematics must precede the player, exactly like `movP`); **`GVH.step` after the enemy loop**.
**1.4 Player integrator (exact).** Per tick: dash active (`pl.dt>0`): `vx=d*13, vy=0`; else `vx+=±.9` (input) or `vx*=.78`, clamp ±5, `vy=min(14,vy+.62)`; `pl.cy=pl.g?7:pl.cy-1` (coyote 7); jump buffer `jb=8` on key press; `if(jb>0&&cy>0){vy=-13}` else `if(jb>0&&ups.dj&&!pl.g&&!pl.used){vy=-12}`; variable height `if(!Jk&&vy<-4&&dt<=0)vy=-4`; dash `dt=9`, cooldown `dc=55`, i-frames `pl.inv=max(pl.inv,6)`. Max single jump ≈ 143 px, double jump adds ≈ 122 px, horizontal reach ≈ 205 px (+≈117 with dash). Player box 32×42.
**1.5 Landing rule (exact).** `if(pl.vy>=0)for p of P{ if(p.t=='f'&&p.al<.5)continue; if(pl.dd>0&&p===pl.dp)continue; if(x+32>p.x&&x<p.x+p.w&&pb<=p.py+6&&y+42>=p.y){land} }` where `pb` = feet **before** the move and `p.py` = the platform's previous-tick y. ⇒ any platform that changes `y` must maintain `p.py` (previous) and `p.dy`; a platform with `p.w==0` can never be landed on (this is how GV disables platforms — no collision-loop patch). Rider carry: `if(pl.g){pl.x+=pl.g.dx;pl.y+=pl.g.dy}` at the start of the next player update.
**1.6 `hurt(dir,fall)`.** Returns early if `!fall&&(pl.inv>0||tm.i>0||iv>0||au>0)`; shield `sh>0` → `sh--; pl.inv=70`; else `hp--; pl.inv=100; shake=12; hs=4 (hit-stop); zm=.04; ring+burst`, and **knockback is built in**: `pl.vy=-7; pl.vx=dir*6` (dir = −1 pushes left). `fall=true` = pit/lava: ignores i-frames, respawns at `rs`. ⇒ **Every electric hit is exactly `hurt(dir)`** — no extra impulse, no extra i-frame logic (the 100-tick `pl.inv` is the grace window; dash i-frames come for free).
**1.7 Interpolation.** `ipSnap()` stores previous `x,y` only for `pl, E, bs, bl, pj, S(non-'*' or riding), P where p.t`, and `ipOn()` lerps them by `RA` before `draw0`. ⇒ **Platforms with `fx` that change `x/y` (sinking grave, movers you add) must be registered**: patch both loops to `if(p.t||p.fx=='s')`. Width changes (Cantor) are not interpolated by the engine: the painter evaluates the closed-form schedule at `gv.t+RA` instead of reading `p.w`.
**1.8 Juice variables.** `shake` (counter, coherent sine camera, decays 1/tick), `zm` (zoom punch, `*=.86`/tick), `hs` (hit-stop ticks), `fl` (white flash counter: drawn as `fillRect` with alpha `min(1,fl/30)*.9` in `dFlash`; decays 1/tick). **A flash of `fl=16` ≈ alpha .48** → `GV.flash.maxFl=16`.
**1.9 Helpers (signatures).** `burst(x,y,col,n=12,sp=5)` and `rnd` use `Math.random` (sim-side, cosmetic only); `ring(x,y,col,m=60)`; `pop(x,y,text,col)`; `snd(f,d=.1,type='square',vol=.05,slide=0,det,lp,at,px)`; `noise(d,vol,freq,at,px)`; `sx(name,x)` positional sfx; `lgBolt(x1,y1,x2,y2,seedMain,seedBranch,{j,d,nb,bl})` returns a bolt, `lgDraw(bolt,[colA,colB],width,alpha)` draws it additively; `sgd(px,py,x1,y1,x2,y2)` point-segment distance; `gsp(col)/fGl(x,y,r,col,a)` cached glow sprites; `star(x,y,r,rot)`, `rr(x,y,w,h,r)`; particles `pt` = `{x,y,vx,vy,l,m,c,s}` (`s` = text), rings `rg`. `AQ` (0.6…1, adaptive) and `FXON` (0/1/2): follow the existing low-quality test `AQ<.75||FXON==0`.

## §2 Architecture contract
**2.1 Hook phases (final).** `GVH.kin` (after `movP()`, before input) · `GVH.step` (after enemy loop; increments `gv.t`; flushes events) · `GVH.blHit` (in `bl` loop before `rm`) · `GVH.pjHit[k]` · draw: `drawBack` (after `bg()`/`dLava()`) → platform loop + `drawPlat` → `dSpk` → pickups → enemies → `drawFront` → boss/shots → player → **`gvDark()`** → `gvRim()` → additive particles → text pops → HUD.
**2.2 Single-writer ownership** (violations = bug): `p.x/p.y/p.w/p.py/p.dx/p.dy` of fx platforms ← only `GVX[fx].kin`; `p.q/p.sk/p.ss/lamp.lit/pool.s/gv.storm` ← only their `step`; `e.chg` ← only `gvCharge()`; `pl.*`, `hp`, `sh` ← only game code via `hurt()`; `fl/shake/zm/hs` ← only `gvJuice()` (central; applies caps and the flash limiter). Everything else reads.
**2.3 RNG.** Simulation uses named streams `stream(name,seed)` from `tools/gv_lib.js` (`stream('storm',stage*977+retry)`); draw uses `hash2/vnoise` only. Cosmetic one-shots (`burst`, sound jitter) may use `Math.random` but must never feed back into state.
**2.4 Event bus** (decouples logic from juice/audio/hints; no re-entrancy; ≤64 events per tick):
```js
const gvQ=[],gvSub={};
function gvOnEv(t,f){(gvSub[t]||(gvSub[t]=[])).push(f)}
function gvEmit(t,a,b){if(gvQ.length<192)gvQ.push(t,a,b)}
function gvFlush(){for(let i=0;i<gvQ.length&&i<192;i+=3){const h=gvSub[gvQ[i]];if(h)for(const f of h)gvTry('ev:'+gvQ[i],f,gvQ[i+1],gvQ[i+2])}gvQ.length=0}
```
Event names (stable API): `slab:warn|live|disch|ground`, `pool:tell|live|idle`, `zap` (kind,srcX), `charge:on|off`, `chain`, `cantor:tell|anim`, `grave:tremble|swallow|emerge`, `lamp:lit|flicker|dark`, `strike:tell|hit|pulse`, `hint:<key>`.
**2.5 Error isolation.** `function gvTry(name,f,a,b){try{return f(a,b)}catch(e){if((gvErr[name]=(gvErr[name]||0)+1)>=3)gvFail(e,name);if(GV_DEBUG)console.error('[GV]',name,e)}}` — every hook body runs inside it; `gvFail` is global fail-soft (fx platforms become plain, darkness/ambience off, game continues).
**2.6 Reset matrix** `gvReset(reason)`:
| reason | clears | keeps |
|---|---|---|
| `load` (new stage / retry / respawn) | everything: `gv` rebuilt from `GVL[n]`, `gv.t=0`, queues, caches of *state* | baked art caches (keyed by stage) |
| `death` (`st=='over'`) | nothing (frozen) | all |
| `clear` | live timers frozen, pools/slabs forced to idle visuals (no damage after clear) | art |
Hint flags (`gvHint`) persist per **run** (reset in `begin()/beginAt()`), not per stage.
**2.7 Zap — one entry point.**
```js
function gvZap(kind,srcX){ if(gv.t<gv.zapT)return false;
  const h0=hp,s0=sh;hurt(pl.x+16<srcX?-1:1);const took=hp<h0||sh<s0;
  if(took){gv.zapT=gv.t+GV.zap.cd;gv.zaps++;gvEmit('zap',kind,srcX)}return took}
```
Callers: slab/pool/strike steps. Never call `hurt` elsewhere in GV code. Idempotent within `GV.zap.cd` (12 ticks) even if two sources fire in the same tick.
**2.8 Previews.** Stage-select calls `genLayout` + `dPlat` on cached layouts with swapped globals: painters must derive everything from `p` + static options (no `gv`), draw a deterministic "showcase" pose (slab 60 % charged, grave half-sunk, Cantor state 1, lantern lit).
**2.9 Fixed budgets.** `GV.maxLights=32`, `gvQ` ≤ 64 events/tick, particle pool 512, cables ≤ 12, rain streaks ≤ 90, splashes ≤ 8/frame.

## §3 Reference library (`tools/gv_lib.js` — paste, don't rewrite)
`ez` (easing set) · `spring` · `hash2/vnoise/fbm` · `rng/stream` (bit-identical to the game's `rng`) · `Pool` (struct-of-arrays, swap-remove: iterate backwards) · `tl` (keyframe timeline) · `fsmValidate` · **mechanic cores**: `slabStep/slabGround/slabJar`, `poolTrigger/poolStep`, `chargedExtra/clampToPlatform`, `sinkStep`, `lampHit/lampStep/lampPhase`, `cantorPresent/cantorSched/cantorW`, `stormNew`, `leader` (midpoint-displacement bolt/cable), `cableBuild/cablePos`, `rootSegs` (fractal roots/trees), `strikeHit`, `flashNew/flashReq`. Defaults in `SLAB/POOL/SINK/LAMP/CANTOR`. The game's `GV` tunables **must default to those values** (then diverge per stage/difficulty through data, never by editing logic). Migration: `tools/gv_migrate.js` (`migProg/migRun/migBag/migStore`).

## §4 Formal mechanic specs
**4.1 Capacitor slab** (`slabStep`, ticks): `c`(charge) —ch≥1→ `w`(warn, warnT) —→ `l`(live, liveT) —→ `d`(disch, dischT) —→ `c` with `ch=-rest/chargeT`. Events returned: `warn|live|disch|rest`. Damage predicate: `pl.g===p && q.s=='l'` evaluated in `GVH.step` **after** the player has landed this tick. Invariants: `q.s∈{c,w,l,d}`; `0<=t<=dur`; `slabJar` monotone in `c`; cycle length = `chargeT+warnT+liveT+dischT` (+`rest` after the first cycle). Grounding: only in `w|l`, not `ins`. Difficulty: `chargeT*=D.bc`, `warnT*=dif==0?1.4:dif==2?.85:1` (never < 30).
**4.2 Pool** (`i→t→l→i`): trigger ignored unless idle (no stacking). Player damage if `pl.g&&pl.g.y==GY&&x∈zone&&pool.s=='l'`.
**4.3 Charge** `e.chg`: set to `GV.chg.T` while overlapping a LIVE slab rect (expanded 14 px up) or live pool; else `--`. Extra move = `(dx,dy)*spd` then `clampToPlatform` for `e.p` enemies. Invariant: charged ground enemy never leaves its platform bounds; `e.chg>0` ⇒ not stompable (legacy path).
**4.4 Cantor** (closed form, no accumulated state): `cantorSched(gv.t,cfg,ph)` → `{cur,nxt,ph:'hold'|'tell'|'anim',u}`; width `cantorW(i,s)∈[0,1]` is the **only** thing the sim writes (`p.w=p.w0*W; p.x=p.ox+(p.w0-p.w)/2; p.dx=0`). **Anchor invariant:** cells 0,2,6,8 (the permanent Cantor points) always have `W==1`; width changes only during `anim`, always preceded by ≥ `tell` ticks. Cycle `4*(hold+tell+anim)`, periodic and phase-offset by `cph`.
**4.5 Sinking grave** (`sinkStep(p,occ,cfg)`): `occ = pl.g===p`. `p.y=p.oy+p.sk`; each tick set `p.py=prevY`, `p.dy=p.y-p.py` **before** the player update (in `kin`); swallow sets `p.w=0`; emerge restores `w0` at `sk=max` and rises at `up`. Invariant: `|Δsk|≤max(v,up)` except the discrete `emerge`.
**4.6 Lantern/spectral:** `lampHit` on star contact (radius 20); `p.w = lampSolid(any linked lamp)?p.w0:0` in `kin`; flicker = last `flickerT` ticks; ≥ 30 ticks "unstable" shimmer before `w` drops to 0.
**4.7 Storm:** `stormNew(seed,rods,every,grace).next()` yields `{at,rod}` (deterministic, never the same rod twice, gap ∈ every·[.85,1.15]). Timeline per strike (ticks from `at`): `tell` 54 (leader grows: `leader(cloudX,-20,rod.x,rod.tipY,seed,6,jit)` revealed by `ez.inQuad(t/54)` of its length) → `hit` 8 (damage if `strikeHit(pl centre,rod,r,14)`) → `after` 30 (afterglow, scorch). Pulses along `cableBuild` polylines travel at `GV.rod.pulse` px/tick: arrival tick = `at+tell+len/pulse`; apply `+addCharge` only if slab `s=='c'`; pools trigger on arrival.
**4.8 Darkness** (per frame, half-res offscreen): fill α; for each light (≤32, culled by `x±r` vs screen, sorted by priority) `destination-out` its sprite scaled to `r*(1+breath)`; α·`(1-fl/16)`; `gvRim()` afterwards. Low tier (`AQ<.75||FXON==0`): player-only radial gradient.
**4.9 Flash/juice** `gvJuice({shake,fl,zm,hs})`: `fl=max(fl,min(req,GV.flash.maxFl))` but only if `gv.t-lastFlash>=GV.flash.minGap` (20) and not reduced-motion/FXON==0 (then `fl` ≤ 4 and add a 6-tick dim instead). `hs≤4`, `zm≤.06`, `shake≤24`.

## §5 Performance engineering
| subsystem | budget (avg ms/frame, dev machine) | rule |
|---|---|---|
| darkness | ≤ 1.5 | half-res offscreen, cached light sprites, ≤ 32 lights |
| fx platform overlays | ≤ 0.6 | cached sprites per state bucket (jar levels quantised to 16 steps), no gradients per frame |
| particles (GV pool) | ≤ 0.5 | `Pool(512)`, additive batches, no `shadowBlur` |
| animated backdrop overlays | ≤ 0.8 | baked layers + ≤ 24 animated sprites |
| director/FSM/events | ≤ 0.1 | integer math, no allocation |
Rules: no allocation inside per-tick/per-frame loops (reuse arrays/objects); no `ctx.filter`, no `shadowBlur`; no gradient creation per frame (cache by key); offscreen caches keyed by `(stage,quality,scale)` with explicit `dispose` (set canvas size to 1) when the key changes; at most 2 baked backdrops alive (follow `bgCa`). Instrument with `GV.perf` (rolling mean of `performance.now()` deltas per subsystem, **debug only**) and report the numbers.

## §6 Test architecture (what "tested" means)
**L1 pure logic:** `node tools/gv_lib.test.mjs` (23 groups incl. migration) — must pass before and after.
**L2 reachability:** `node tools/gv_reach.mjs html <your file>` — real-physics policy search over every Cantor state; spectral slabs counted absent; exit code 1 if a star-eligible platform is unreachable. (It proves *reachable*; it cannot prove *unreachable*.)
**L3 in-page harness** (debug only, behind `?gvdebug`): `window.__gv={seed(n),go(stage,dif),step(n,keys),snap(),hash(),inv(),force(evt,arg),perf()}`. `step` runs `update()` n times with a synthetic key map (`K[code]=1`) and **no rendering**; `snap()` returns JSON of `{t,stage,pl:{x,y,vx,vy,g},hp,sh,slabs,pools,graves,lamps,storm,E:[ids,x,y,chg]}`; `hash()` hashes it (FNV-1a); `inv()` evaluates the invariants below and returns the list of violations.
**L4 fuzz/property:** for stages 11-13 × dif 0-2 × 20 seeds: random input traces (seeded; mixes hold-right, jump spam, dash, shoot) for 20 000 ticks, calling `inv()` every tick. Plus determinism: same seed+trace ⇒ identical `hash()` sequence twice; plus `step(1)` vs 6×`step(1)` equivalence (no dependence on frame batching).
**L5 visual:** canvas screenshots + `hash` of the canvas bytes twice at the same `tick`/`gv.t` (determinism), parity screenshots of stages 1-10 and 14-17 against the previous build.
If no browser automation exists, run L1+L2 and static checks and **say clearly** that L3-L5 were not run.

**Invariants (`inv()`):**
INV-1 no NaN/Infinity in `pl`, `E`, `P`, `gv` · INV-2 `0<=p.w<=p.w0` for every fx platform and `p.w==0 ⇒` player not grounded on it · INV-3 anchors 0,2,6,8 of every bridge have `w==w0` · INV-4 slab state ∈ {c,w,l,d} and `t<=dur` · INV-5 ≤ 1 successful zap per `GV.zap.cd` ticks and never during `pl.inv>0` · INV-6 `sh`/`hp` change only through `hurt` (compare before/after each tick) · INV-7 flashes: sliding 60-tick window has ≤ 3 flash starts and `fl<=GV.flash.maxFl` · INV-8 charged enemies stay inside their platform x-range · INV-9 no enemy/star/power-up on a platform with `!gvOkPlat(p)` · INV-10 `gvQ.length==0` at the end of each tick · INV-11 particle pool `n<=cap`, lights `<=32` · INV-12 non-GV stages: `gv==null` and zero GV draw calls · INV-13 sink platforms: `p.py+p.dy==p.y` every tick · INV-14 strike never happens within `grace` ticks of load/respawn · INV-15 `gv.t` strictly increases by 1 per play tick and is frozen in pause/hit-stop.

# ARIA → v33 · THE FRACTAL NECROPOLIS (3 new dark stages after stage 10) · PART 10/13 · TRACK B 3/6 — Electric system: Capacitor Slabs, charged enemies, pools, cables

You are ONE of several Claude Code sessions (possibly on different accounts) that build the same feature **in sequence**. You have NO memory of earlier sessions: everything you need is in this file, `HANDOFF.md`, the reference images and the game file. Stay strictly inside this part's scope.

**Project:** *Aria and the Lost Stars* — heavily customised single-file HTML5 Canvas platformer (~5000 lines, ~835 KB, 1000×600 logical canvas, stages 1-14 today: bosses on 5 / 10 and the Void Singularity final boss on 14; the UI/docs sometimes call it "13 stages + finale"). **Track B** inserts THREE new stages right after the Crimson Reaper (stage 10): **11 THE WEEPING CEMETERY · 12 THE FRACTAL CRYPT · 13 THE STORM MAUSOLEUM** — dark, frightening, *graveyard + fractal*. The old stages 11-14 become **14-17** (campaign = 17 stages). Track A (5 Hard-mode enemies, Parts 1-7) is independent and runs first: Track B's input is `aria_v32.html`. If Track A was skipped the input is `aria_v31.html` and every "HE" note below is N/A.

## Session protocol
**START**
1. Read `HANDOFF.md` completely (Track B sections included), **`GV_ENGINE_SPEC.md` §1-§4** (verified runtime facts + engineering contract) and the **`GV_ANIMATION_BIBLE.md`** entries cited in this part. Open the reference images listed in this part (blueprints = seed layouts + palette). Run `node tools/gv_lib.test.mjs` (must pass: it proves the reference algorithms you will paste) and, once a game file exists, `node tools/gv_reach.mjs html <file>`.
2. Input file: `aria_v33_g2.html`. Verify earlier Track B parts are really in it: for each K in 8, 9 run `grep -c "===== GV part K:" aria_v33_g2.html` (each must be ≥ 1). If something is missing → STOP and tell the user (in Persian) which part must run first.
3. If `HANDOFF.md` marks this part as **WIP**, resume from its remaining checklist instead of starting over (input = the `_WIP` file it names).

**BUDGET (the pack is designed to fit daily limits)**
- Never `cat` the game file. Use `grep -n` and `sed -n 'a,bp'` ranges. All anchors below were verified on v31; **line numbers drift** (Track A shifted them) — re-grep every anchor.
- Work in small verified patches (a patch script with assertions on unique anchors); re-read every modified region; check duplicate functions / unmatched delimiters / template literals.
- If you are about to run out of budget: reach a clean LOADABLE state, save `aria_v33_g3_WIP.html`, write the exact remaining checklist into `HANDOFF.md` (status: WIP). Never leave a half-edited file as "the output".

**END**
1. Save the result as a NEW file `aria_v33_g3.html` (never overwrite earlier files).
2. Append a ≤30-line section `## Part 10` to `HANDOFF.md`: status DONE, output filename, functions/vars/`GV` keys added, hooks used, runtime fields, known issues, tests run.
3. Final report **in Persian**: (a) file produced (b) behaviour changed (c) functions/systems touched (d) tests actually run + results — never claim untested results; separate *design hypothesis* from *playtest evidence* (e) limitations / notes for the next part.

## Track B rules (these override Track A's "keep the 13-stage campaign / no save-schema change" — see rule 1)
1. **Allowed structural changes:** the campaign grows to 17 stages (Part 8 only) and `aria_prog` / `aria_run` get a one-time, idempotent stage-number **migration**. Nothing else in the save schema changes. Stages 1-10 and the old 11-14 (now 14-17) keep byte-identical layouts, bosses, enemy stats, controls, themes and options.
2. Everything new sits behind `GV_ON`. Any exception in new code → `gvFail(err)`: `GV_ON=0`, `gv=null`; effect platforms degrade to plain static platforms, darkness/ambience switch off, the game continues (stages 11-13 stay playable and completable).
3. All tunables live in one `const GV={…}` block (each part adds its own sub-object). No magic numbers in logic. Markers: `/* ===== GV part N: name ===== */ … /* ===== /GV part N ===== */`, one-line patches inside existing functions tagged `/*GV<N>*/`.
4. **`p.t` is reserved for movement** (truthy = "moving platform": star riding, enemy carry, `movP`, webs, spawn filters all test it; `'f'` = fading). Every new platform behaviour lives in **`p.fx`** (+ its own state object). Moving effect platforms (sinking, Cantor cells) must keep `p.px/p.py/p.dx/p.dy` correct so riders are carried (player: `pl.g.dx/dy`; enemies: patch the carry line to `e.p&&(e.p.t||e.p.fx)`).
5. Render is deterministic: no `Math.random()` and no gameplay mutation in draw code (use `gv.t`+`RA`, ids, `hash2/fbm`); simulation randomness only through named seeded streams (`stream('storm',seed)`). **Gameplay timers use the sim clock `gv.t`, never `tick`** (`tick` keeps running in pause/menu/clear and freezes in hit-stop — SPEC §1.2). Bake backgrounds/skins into offscreen caches (follow `bgBuild`/`pcBake` style); per-frame work bounded; honour `FXON`, `AQ`, `BG_ON`, `PL_ON`; interpolation (`ipSnap/ipP`): GV-owned moving objects are drawn from state or registered.
6. Don't change player physics/hitbox (g .62, jump vy -13, double jump -12, vx clamp ±5, dash i-frames). `hurt(dir)` already applies knockback, 100-tick i-frames and hit-stop: electric damage is **exactly** `gvZap()` → `hurt(dir)`, nothing more.
7. **Fairness (Aria design principles):** every damaging mechanic = tell → active → recovery → counterplay → failure feedback; no unavoidable damage, no hidden collision traps, no stacking of two control effects, hazards stay visible in darkness, nothing spawns on top of the player (≥220 px). Teach one mechanic at a time: stage 11 = capacitors; stage 12 = fractal / grave / spectral; stage 13 = recombination + storm. Easy/Normal/Hard must all be meaningful (scale with `D.bc`, `D.nd`, `D.ps`, `D.es`; never inflate HP/speed as the only difficulty).
8. **Photosensitivity safety:** no full-screen flash brighter than `GV.flash.max` (.5 alpha) and no more than 3 flashes per second; honour `prefers-reduced-motion` and `FXON==0` (replace flashes with a short darkening dip).
9. Single file, no dependencies, no network, no remote assets. Time unit: 60 ticks = 1 s ("f" = ticks).
10. **Reference code is authoritative:** `tools/gv_lib.js` (tested) holds the mechanic cores (`slabStep`, `sinkStep`, `cantorSched/cantorW`, `stormNew`, `leader`, `cableBuild`, flash limiter…). Paste it, keep the names, adapt only glue; if you must change an algorithm, change the lib + its test first. Part prompts cite spec sections instead of repeating them.
11. **Definition of done (per part):** L1 tests pass; L2 reachability passes; invariants INV-* implemented for this part's systems and clean over a 20 000-tick fuzz run (if browser automation exists; otherwise say it was NOT run); each animation of this part meets the bible's Definition of Done; measured ms/frame reported.

## Campaign renumber map (fixed facts)
| old | new | stage |
|---|---|---|
| 1-10 | 1-10 | unchanged (5 = Shadow Witch, 10 = Crimson Reaper) |
| — | **11** | **THE WEEPING CEMETERY** (theme `TH[6]`) |
| — | **12** | **THE FRACTAL CRYPT** (theme `TH[7]`) |
| — | **13** | **THE STORM MAUSOLEUM** (theme `TH[8]`) |
| 11 | 14 | THE MAGMA GAUNTLET (lava) |
| 12 | 15 | THE FORGE OF STARS (lava) |
| 13 | 16 | THE FADING ROAD (void) |
| 14 | 17 | Void Singularity final boss |
Helpers (Part 8): `FIN=17`, `isBoss(n)=n==5||n==10`, `isMag(n)=n>=14&&n<=16`, `isGV(n)=n>=11&&n<=13`. **Never use `n%5==0` as a boss test** (stage 15 would become a boss). The literal `stage>=11` used for the Wizard spawn and the enemy cap stays as is: it now means "after the Reaper" (graveyard + magma + void).

## GV API (contract; Part 8 implements, later parts only USE it)
```js
GV_ON, GV_DEBUG(?gvdebug), const GV={…tunables…}; let gv=null;   // gv = runtime state of the current GV stage (null elsewhere)
const GVL={11:{n,rs,dark,need,p:[[x,y,w,t,r,s,ph,{fx,…}],…],x:[[x,w],…],pools:[[x0,x1],…],rods:[{x,p,slabs:[],pool}],lamps:[{x,y,link:[]}]},12:{…},13:{…}};
const GVX={};   // registry by fx code: 'q' capacitor slab, 's' sinking grave, 'u' Cantor-bridge cell, 'l' spectral slab
GVX[fx]={init(p,G), step(p), draw(p), reset?(p)};          // p = platform object, G = GVL entry
const GVH={kin:[],step:[],reset:[],drawBack:[],drawPlat:[],drawFront:[],lights:[],blHit:[],pjHit:{}};
//  kin         right after movP(), BEFORE the player update (platform kinematics: p.x/y/w/py/dx/dy)
//  step        once per play tick, after the enemy loop (gv.t++, logic, zaps, events flush)     reset  load(n), retry/death, clearStage
//  drawBack    after bg(), before platforms (cables, pools)       drawPlat inside the platform loop, right after dPlat(p) (fx overlays)
//  drawFront   after enemies/pickups, before the player           lights   push({x,y,r,c,a}) light sources for the darkness pass
//  blHit       player star b=bl[i] vs GV objects (true = consumed, respect tm.p pierce)      pjHit[k] enemy projectile kinds
function gvOn(){return GV_ON&&gv}  function gvFail(err,name)  function gvTry(name,f,a,b)  function gvHint(key,text)   // one-time pop() per run per key
function gvEmit(t,a,b) / gvOnEv(t,f) / gvFlush()   // event bus (SPEC §2.4)   function gvZap(kind,srcX)  // the ONLY way GV hurts the player (SPEC §2.7)
function gvJuice({shake,fl,zm,hs})   // the ONLY writer of shake/fl/zm/hs inside GV: caps + photosensitivity limiter (SPEC §4.9)
function gvOkPlat(p){return !p.fx||p.fx=='q'}   // platforms enemies/stars/power-ups/webs may use
```
Platform data tuple = `[x,y,w,t,r,s,ph,{opts}]` (same as `HMX`, plus an options object that is `Object.assign`-ed onto `mk(...)`). Seed layouts (the blueprints) are the starting point — **re-verify reachability with the real physics** (jump ≈136 px up, ≈210 px across at vx 5; a conservative envelope of 120 up / 150 across was used for the seeds). Stage-select previews call `genLayout` + `dPlat` on cached layouts with temporarily swapped globals: effect painters must also work from static layout data (draw a "60 % charged" slab, a half-sunk grave…) without touching `gv`.

## Scope of THIS part (G3): the ELECTRIC SYSTEM — Capacitor Slabs, charged enemies, conductive pools, fractal cables — wired into STAGE 11
Read first: SPEC §2.7 (`gvZap`), §4.1-§4.3, §4.9; Bible **A01-A08, A19, P1-P3**. Reference: `gv11_blueprint.png` (slabs #2 linked to pool 0, #4, #11, #15; pool x 300-560) and `gv13_blueprint.png`. Core logic is **already written and tested** in `tools/gv_lib.js`: `slabNew/slabStep/slabGround/slabJar`, `poolNew/poolTrigger/poolStep`, `chargedExtra/clampToPlatform`, `leader`, `cableBuild/cablePos`. Paste, wire, animate.

### 1. Data model
`gv.slabs=[p…]` for platforms with `fx:'q'` (`p.q=slabNew(p.q0)`, `p.add=0` charge injected this tick, `p.link` pool index, `p.ins`); `gv.pools=[{x0,x1,…poolNew()}]`; `gv.cabs=[{cab:cableBuild(leader(...)),from,to,kind}]`; `gv.pulses=Pool(24,['cab','s','spd','kind','to'])`.
Per-slab config = `GV.slab` defaults overridden by stage data (`GV.q11={chargeT:600,liveT:130}`) and difficulty (`chargeT*=D.bc`, `warnT*=dif==0?1.4:dif==2?.85:1`, min 30).

### 2. Step order (inside one `GVH.step` entry `gvElec()`; order is a contract)
```js
function gvElec(){
  for(const p of gv.slabs){const ev=slabStep(p.q,cfg(p),p.add);p.add=0;if(ev)slabEvt(p,ev)}      // 1 slab FSMs
  for(const o of gv.pools){const ev=poolStep(o,GV.pool);if(ev)gvEmit('pool:'+ev,o)}               // 2 pools
  gvCharge();                                                                                      // 3 e.chg from live slabs / live pools
  for(const p of gv.slabs)if(p.q.s=='l'&&pl.g===p)gvZap('slab',p.x+p.w/2);                          // 4 zaps (player has already landed this tick)
  for(const o of gv.pools)if(o.s=='l'&&gvOnFloorIn(o))gvZap('pool',(o.x0+o.x1)/2);
  gvPulses();                                                                                      // 5 cable pulses -> arrival effects
}
```
`slabEvt`: `warn` → hint + `gvEmit('slab:warn')`; `live` → light + event; `disch` → `poolTrigger(gv.pools[p.link])` if linked, ring, `gvJuice({fl:10,shake:6})`, pulse along the cable. `gvOnFloorIn(o)` = `pl.g&&pl.g.y==GY&&pl.x+16∈[o.x0,o.x1]` (airborne/dashing/on a platform ⇒ safe; dash i-frames come free from `hurt`).
**Zap = `gvZap` only** (`hurt(dir)` brings knockback `vy -7, vx dir·6`, 100-tick i-frames, hit-stop 4, ring, burst). Never zap during WARN; never when `pl.inv>0` (hurt itself returns).
**Counterplay:** a player star hitting a `w|l` slab → `slabGround(q,cfg,p.ins)` (star consumed unless piercing; `rest` 120); hitting a charging slab → `p.add+=GV.slab.starCharge` (.12). `GV.slab.groundable` per stage `[1,1,0]`.

### 3. Charged enemies — no deep AI patch needed
Two hooks bracket the enemy loop: in `GVH.kin` (before AI) store `e.ox=e.x,e.oy=e.y` for every enemy; in `GVH.step` (after AI) for `e.chg>0 && !e.noChg`: `[ex,ey]=chargedExtra(e.x-e.ox,e.y-e.oy,spd)`; `e.x+=ex;e.y+=ey`; if `e.p&&!e.p.t` (patrolling a static platform) → `e.x=clampToPlatform(e.x,e.w,e.p)`. `spd`=`GV.chg.spd` (.45; ×.8 Easy). Shooters: `e.cd-=GV.chg.fire-1` per tick. The engine's interpolation sees it as ordinary motion. `gvCharge()`: overlap test of each enemy rect with each LIVE slab rect expanded 14 px up (≤ 8 slabs × ≤ 12 enemies: no spatial structure needed) + pool zones; `e.chg=GV.chg.T` or `--`. Skips `bs` (bosses) and Track-A enemies with `noChg`.
**One-line patch** in the enemy contact/stomp test: treat `e.chg>0` like the spiked brute (`t==3`): stomp hurts the player; shooting always works. **Overload chain:** a 1-line patch at the top of `kill(e)`: `if(e.chg>0&&!e.chained)gvChain(e)`; `gvChain` finds the nearest other enemy within `GV.chg.chain` (160), marks it `chained=1`, `hitE(o,1)`, draws A05 — depth-limited by the flag (no recursion).

### 4. Cables and pulses (data → visuals → gameplay)
Build at `gvLoad`: for each link `cable=cableBuild(leader(x0,y0,x1,y1,seed,3,jit))`. `gvPulses()` advances pulses (`s+=spd`), arrival at `s>=cab.len`: slab `p.add+=…`, pool `poolTrigger`. Slab→pool pulse speed 6 px/f, charging pulse 1.2 px/f (cosmetic). Cables are drawn from a baked layer (`gvBake`) in `GVH.drawBack`; pulses from the pool with `cablePos` (A07).

### 5. Pools (floor)
`G.pools` (≤ 3, each ≤ `GV.pool.maxW` 220 px on stage 11, never within 160 px of spawn/respawn, never covering the only crossing of spikes). States and visuals: A06. `gvHint('pool',…)` on the first tell.

### 6. Animation deliverables (Bible)
A01 jar/liquid · A02 WARN/LIVE/DISCHARGE · A03 player zap · A04 charged enemy (aura, orbit sparks, afterimages) · A05 chain · A06 pools · A07 cables · A08 landing squash. Draw rules: slab painters read `p.q` + `gv.t+RA`; a state-bucketed sprite cache (jar level 16 steps × 4 states) keeps cost ≤ 0.6 ms; all particles via `Pool`; lights via `GVH.lights` (live slab r150 `#bfe9ff`, live pool r = half width); previews draw "60 % charged".

### 7. Stage 11 tuning (the teaching stage)
4 slabs (`#2,#4,#11,#15`), only #2 linked to the pool, all groundable, no rods. `chargeT` 600, `liveT` 130, pool tell 48. Slab #2 is visible from the spawn at `q0` .15 so the jar visibly fills before it ever flashes. Enemy density unchanged.

### 8. Invariants added (`inv()`): INV-2 (`p.w` untouched by slabs), INV-4, INV-5, INV-6, INV-8, INV-10, INV-11 plus: INV-16 pool states ∈ {i,t,l} and a pool never retriggers while not idle; INV-17 `e.chg>=0`, and a charged enemy is never killed by a stomp (the contact patch holds); INV-18 pulses ≤ 24, each `s<=len+spd`.

## Tests
L1 + L2 + fuzz (L4, if available). (a) Timing per difficulty (measure ticks between `slab:warn/live/disch` events from `snap()`), shield/dash/inv honoured, airborne safe, landing exactly on the WARN→LIVE boundary hurts at most once. (b) Star grounding: groundable vs `ins`; pierce. (c) Charged enemy: speed bonus bounded to its platform, not stompable, chain on kill (depth 1), `chg` expires, boss/Track-A exceptions. (d) Pool: tell visible before live, jumping avoids it, spawn never inside. (e) Retry/death/clear/next-stage reset every new field. (f) Determinism hash twice; `step(1)`×6 == `step(6)`; FX tiers; perf with 4 slabs + pool + 6 enemies (numbers). (g) Easy/Normal/Hard differences measured. (h) Screenshots of each state (A02 ×4, A04, A06 ×3) inspected.

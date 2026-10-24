# ARIA → v33 · THE FRACTAL NECROPOLIS (3 new dark stages after stage 10) · PART 12/13 · TRACK B 5/6 — Lightning rods, storm director, fractal lightning — STAGE 13

You are ONE of several Claude Code sessions (possibly on different accounts) that build the same feature **in sequence**. You have NO memory of earlier sessions: everything you need is in this file, `HANDOFF.md`, the reference images and the game file. Stay strictly inside this part's scope.

**Project:** *Aria and the Lost Stars* — heavily customised single-file HTML5 Canvas platformer (~5000 lines, ~835 KB, 1000×600 logical canvas, stages 1-14 today: bosses on 5 / 10 and the Void Singularity final boss on 14; the UI/docs sometimes call it "13 stages + finale"). **Track B** inserts THREE new stages right after the Crimson Reaper (stage 10): **11 THE WEEPING CEMETERY · 12 THE FRACTAL CRYPT · 13 THE STORM MAUSOLEUM** — dark, frightening, *graveyard + fractal*. The old stages 11-14 become **14-17** (campaign = 17 stages). Track A (5 Hard-mode enemies, Parts 1-7) is independent and runs first: Track B's input is `aria_v32.html`. If Track A was skipped the input is `aria_v31.html` and every "HE" note below is N/A.

## Session protocol
**START**
1. Read `HANDOFF.md` completely (Track B sections included), **`GV_ENGINE_SPEC.md` §1-§4** (verified runtime facts + engineering contract) and the **`GV_ANIMATION_BIBLE.md`** entries cited in this part. Open the reference images listed in this part (blueprints = seed layouts + palette). Run `node tools/gv_lib.test.mjs` (must pass: it proves the reference algorithms you will paste) and, once a game file exists, `node tools/gv_reach.mjs html <file>`.
2. Input file: `aria_v33_g4.html`. Verify earlier Track B parts are really in it: for each K in 8, 9, 10, 11 run `grep -c "===== GV part K:" aria_v33_g4.html` (each must be ≥ 1). If something is missing → STOP and tell the user (in Persian) which part must run first.
3. If `HANDOFF.md` marks this part as **WIP**, resume from its remaining checklist instead of starting over (input = the `_WIP` file it names).

**BUDGET (the pack is designed to fit daily limits)**
- Never `cat` the game file. Use `grep -n` and `sed -n 'a,bp'` ranges. All anchors below were verified on v31; **line numbers drift** (Track A shifted them) — re-grep every anchor.
- Work in small verified patches (a patch script with assertions on unique anchors); re-read every modified region; check duplicate functions / unmatched delimiters / template literals.
- If you are about to run out of budget: reach a clean LOADABLE state, save `aria_v33_g5_WIP.html`, write the exact remaining checklist into `HANDOFF.md` (status: WIP). Never leave a half-edited file as "the output".

**END**
1. Save the result as a NEW file `aria_v33_g5.html` (never overwrite earlier files).
2. Append a ≤30-line section `## Part 12` to `HANDOFF.md`: status DONE, output filename, functions/vars/`GV` keys added, hooks used, runtime fields, known issues, tests run.
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

## Scope of THIS part (G5): the STORM — lightning rods, strikes, bell, pulses, fractal lightning — STAGE 13, THE STORM MAUSOLEUM
Read first: SPEC §4.7, §4.9; Bible **A07 (storm pulses), A13, A14, A15 (stage 13), A16, A17, A19**. Reference: `gv13_blueprint.png` (3 rods on the top tier, 2 wide pools, slabs #2/#4/#6/#9(ins)/#15/#17, sinking grave #7, Cantor bridge #16, mover #12). Tested core in `tools/gv_lib.js`: `stormNew`, `leader`, `strikeHit`, `cableBuild/cablePos`, `flashNew/flashReq`.

### 1. Data and director
Tunables: `GV.rod={r:38,every:420,tell:54,hit:8,after:30,pulse:12,addCharge:.35,grace:180}` (difficulty scales `every`, tells never < 30 f).
`G.rods=[{x,p,slabs:[],pool}]`: iron cross/obelisk on platform `p` (60 px tall, copper tip; `tipY=P[p].y-60`). Cables rod→slabs (+pool) via `cableBuild(leader(...))` (Part 10 machinery). Director: `gv.storm={dir:stormNew(stage*977+retryCount,rods.length,every,grace),nxt:dir.next(),ph:'idle',t0:0,delay:0}` with `every`=420 (×1.3 Easy, ×.85 Hard), `grace`=180 (no strike within 180 f of load/respawn). Deterministic: same `retryCount` ⇒ same sequence (L1 proves it).
```js
function gvStorm(){const S=gv.storm;
  if(S.ph=='idle'&&gv.t>=S.nxt.at+S.delay){ if(stormBlocked(S.nxt.rod)&&S.delay<90){S.delay++;return}        // SPEC §4.7 fairness delay (≤90 f)
     S.ph='tell';S.t0=gv.t;S.rod=S.nxt.rod;S.delay=0;gvEmit('strike:tell',S.rod)}
  else if(S.ph=='tell'&&gv.t-S.t0>=54){S.ph='hit';S.t0=gv.t;strikeNow(S.rod)}                              // damage zone + pulses spawn
  else if(S.ph=='hit'){ if(gv.t-S.t0<8&&strikeHit(pl.x+16,pl.y+21,rodOf(S.rod),GV.rod.r,14))gvZap('strike',rodOf(S.rod).x);
                         if(gv.t-S.t0>=8){S.ph='after';S.t0=gv.t} }
  else if(S.ph=='after'&&gv.t-S.t0>=30){S.ph='idle';S.nxt=S.dir.next()}}
```
`stormBlocked(rod)` = a linked slab is in `w|l` **or** a slab discharge/zap happened < 90 f ago (A19: one big event per 90 f). `strikeNow` emits `strike:hit`, calls `gvJuice({fl:16,shake:18,zm:.05,hs:3})`, spawns one pulse per cable (`spd` 12 px/f); pulse arrival (Part 10 `gvPulses`): slab `p.add+=.35` (consumed only in the `c` state by `slabStep`), pool `poolTrigger`.

### 2. Fractal lightning rendering (reuse, don't reinvent)
**Tell:** leader polyline `leader(cloudX,-20,rod.x,tipY,seedStrike,6,jit)` (seed `S.rod*1009+strikeIndex`), revealed fraction `ez.inQuad(u)`; first 60 % of vertices fixed, tail reseeded every 3 f. **Hit:** the game's own `lgBolt/lgDraw` with `{j:.09,d:7,nb:8}`, three passes (white core w5, cyan w16, violet w30 α .25). Cache the bolt object per strike id (no per-frame generation). **After:** afterimage + scorch decal (≤ 6 kept) + ring + ground ripple through pools. Full frame timing: Bible A13.

### 3. Stage 13 look (`TH[8]`, `w=8`, dark .60 + strike reveal) — A14, A15 (stage 13), A16, A17
Backdrop (`bgBuildGV(8)`): three drifting cloud layers (internal glow `fbm`, α ≤ .15, never a ground bolt), a **huge Julia-set moon** (baked, veined, behind torn clouds), a far mausoleum with a bell tower (bell = damped pendulum, amplitude set by `strike:tell|hit`), jagged hills with crosses. **Rain:** two cached streak tiles scrolled at 14/9 px/f (shear 12°) + ≤ 8 hashed splash crowns per frame + pool ripples; wet platform rims. Platforms (`dGPlat` for `TH[8]`): wet black marble, copper rod inlays, dark rain-glossed tops; rods with a faint corona. Enemies `th.ec` red. **Music:** final `MU[12]` (faster `tk:7`, `kk`, `sn`, `bell`, `pd`); thunder/bell stingers come from events, not from the track. Clear variant A17 (slab cascade, rising souls, darkness fades out).

### 4. Combined rules
Seed `GVL[13]`; `GV.need[2]=11`; capacitor `chargeT` 480 (slabs also charge from pulses); Cantor `hold` 120; one sinking grave; mover #12. **Fairness:** the strike point is telegraphed ≥ 54 f ahead (> time to run 270 px); at least one safe standing platform exists in every strike/pool configuration (assert in the BFS tool by removing pools+strike zones in turn — never a "whole screen is lethal" moment); no strike inside the grace window; the director delay rule prevents strike+discharge stacking. Difficulty: Easy = longer tells/holds; Hard = ×.85 intervals and charged-enemy `spd` 1.0×.

### 5. Photosensitivity and performance
Every flash through `gvJuice` (INV-7: ≤ 3 flash starts per 60 f, `fl≤16`); when a strike and a discharge coincide the limiter drops the weaker one. `prefers-reduced-motion`/`FXON==0` → dim instead of white. Budget: ≤ +15 % ms/frame vs stage 12; rain tiles/sprites cached; bolt arrays reused; ≤ 6 scorch decals; ≤ 24 pulses.

### 6. Invariants added: INV-14 (no strike inside grace), INV-22 strike phase ∈ {idle,tell,hit,after} with legal transitions only, INV-23 ≥ 1 solid static platform outside every active strike disc, INV-24 director sequence equals `stormNew` replay for the same seed.

## Tests
L1 (director determinism/no-repeat/spacing) + L2 + fuzz. (a) Seeded sequence identical across runs; interval per difficulty; grace after respawn; no strike in pause/cutscene/clear. (b) Tell/strike timing from `snap()`, damage zone vs dash/shield/inv, ring readable at α .78. (c) Pulses: charge only in `c`, pool tell on arrival, combos with slab WARN/LIVE and the delay rule. (d) Flash limiter under overlapping events + reduced-motion + `FXON=0`. (e) Full-stage input-trace playthrough on all three difficulties (collect stars, 3 deaths/retries, clear → stage 14 loads with checkpoint 14). (f) 8 screenshots (tell, hit, after, rain, bell, pools live, backdrop, title card) inspected + determinism hash + perf numbers.

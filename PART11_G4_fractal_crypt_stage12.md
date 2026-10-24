# ARIA → v33 · THE FRACTAL NECROPOLIS (3 new dark stages after stage 10) · PART 11/13 · TRACK B 4/6 — Cantor bridge, Sinking Graves, Spectral slabs — STAGE 12

You are ONE of several Claude Code sessions (possibly on different accounts) that build the same feature **in sequence**. You have NO memory of earlier sessions: everything you need is in this file, `HANDOFF.md`, the reference images and the game file. Stay strictly inside this part's scope.

**Project:** *Aria and the Lost Stars* — heavily customised single-file HTML5 Canvas platformer (~5000 lines, ~835 KB, 1000×600 logical canvas, stages 1-14 today: bosses on 5 / 10 and the Void Singularity final boss on 14; the UI/docs sometimes call it "13 stages + finale"). **Track B** inserts THREE new stages right after the Crimson Reaper (stage 10): **11 THE WEEPING CEMETERY · 12 THE FRACTAL CRYPT · 13 THE STORM MAUSOLEUM** — dark, frightening, *graveyard + fractal*. The old stages 11-14 become **14-17** (campaign = 17 stages). Track A (5 Hard-mode enemies, Parts 1-7) is independent and runs first: Track B's input is `aria_v32.html`. If Track A was skipped the input is `aria_v31.html` and every "HE" note below is N/A.

## Session protocol
**START**
1. Read `HANDOFF.md` completely (Track B sections included), **`GV_ENGINE_SPEC.md` §1-§4** (verified runtime facts + engineering contract) and the **`GV_ANIMATION_BIBLE.md`** entries cited in this part. Open the reference images listed in this part (blueprints = seed layouts + palette). Run `node tools/gv_lib.test.mjs` (must pass: it proves the reference algorithms you will paste) and, once a game file exists, `node tools/gv_reach.mjs html <file>`.
2. Input file: `aria_v33_g3.html`. Verify earlier Track B parts are really in it: for each K in 8, 9, 10 run `grep -c "===== GV part K:" aria_v33_g3.html` (each must be ≥ 1). If something is missing → STOP and tell the user (in Persian) which part must run first.
3. If `HANDOFF.md` marks this part as **WIP**, resume from its remaining checklist instead of starting over (input = the `_WIP` file it names).

**BUDGET (the pack is designed to fit daily limits)**
- Never `cat` the game file. Use `grep -n` and `sed -n 'a,bp'` ranges. All anchors below were verified on v31; **line numbers drift** (Track A shifted them) — re-grep every anchor.
- Work in small verified patches (a patch script with assertions on unique anchors); re-read every modified region; check duplicate functions / unmatched delimiters / template literals.
- If you are about to run out of budget: reach a clean LOADABLE state, save `aria_v33_g4_WIP.html`, write the exact remaining checklist into `HANDOFF.md` (status: WIP). Never leave a half-edited file as "the output".

**END**
1. Save the result as a NEW file `aria_v33_g4.html` (never overwrite earlier files).
2. Append a ≤30-line section `## Part 11` to `HANDOFF.md`: status DONE, output filename, functions/vars/`GV` keys added, hooks used, runtime fields, known issues, tests run.
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

## Scope of THIS part (G4): fractal + grave + spectral platforms — STAGE 12, THE FRACTAL CRYPT
Read first: SPEC §1.5, §1.7, §4.4-§4.6; Bible **A09-A12, A15 (stage 12), A16, A19**. Reference: `gv12_blueprint.png` (2 sinking graves over spike strips, slab #7 + insulated #17, 9-cell Cantor bridge, 3 spectral slabs, 2 lanterns). Core logic is already written and tested in `tools/gv_lib.js`: `cantorPresent/cantorSched/cantorW`, `sinkNew/sinkStep`, `lampNew/lampHit/lampStep/lampSolid/lampPhase`, `rootSegs`.

### 1. Kinematics contract (`GVH.kin` — runs right after `movP()`, before the player)
```js
function gvKinFx(){
  for(const p of gv.cells){const s=cantorSched(gv.t,GV.cantor,p.cph),W=cantorW(p.ci,s);   // closed form: no accumulated state, previews & tests can call it for any t
    p.py=p.y;p.w=p.w0*W;p.x=p.ox+(p.w0-p.w)/2;p.dx=0;p.dy=0}
  for(const p of gv.graves){p.py=p.y;sinkStep(p,pl.g===p,GV.sink);p.y=p.oy+p.sk;p.dy=p.y-p.py}     // p.w switched to 0 / w0 inside sinkStep
  for(const p of gv.spec){p.py=p.y;p.w=p.lamps.some(l=>lampSolid(l))?p.w0:0}                       // lantern timers tick in GVH.step
}
```
**Why here:** the landing rule uses `p.py` and rider carry uses `p.dy`; platform geometry must be final before the player integrates (same reason `movP` runs first). INV-13 (`p.py+p.dy==p.y`) and INV-2 (`0<=p.w<=p.w0`) are checked every tick. Sinking graves are registered for interpolation (`p.fx=='s'`, Part 8 patch); Cantor/spectral painters evaluate their schedule at `gv.t+RA` (no stored-`w` reads).

### 2. CANTOR BRIDGE (`fx:'u'`)
Data `{fx:'u',cells:9,cw:40,cph}`; **expand in `genLayout`** into 9 real platform objects (`mk(x+i*cw,y,cw)`; `fx:'u',ci:i,w0:cw,ox:x,grp`) — all collision/carry/preview paths keep working. Closed-form schedule (SPEC §4.4): `hold` 150 f (120 on stage 13) → `tell` 36 → `anim` 18; states 0→1→2→1. **Anchor cells 0,2,6,8 are permanent** (a design guarantee *and* INV-3): even in state 2 the bridge is four 40 px keystone pads, never empty. Cells with `w==0` are non-solid through the existing overlap test. Enemies, stars, power-ups and webs never use `'u'` (`gvOkPlat`).
Animation: A09 (hinge fold with `scaleX=|cos θ|`, tell shimmer + cracks, chimes by cell, rune wave, keystone gems, cascade delay `|i-4|·2`, Sierpiński under-glow that deepens per state). `gvHint('cantor','FRACTAL BRIDGE: it folds in thirds.')`.

### 3. SINKING GRAVE (`fx:'s'`)
`Object.assign(p,sinkNew(p.w))` at load; `p.oy=p.y`. SPEC §4.5 (sink .55 px/f to 56 px ⇒ swallow after ⌈56/.55⌉=102 f; gone 240 f; emerge at max depth then rises .9 px/f). Seed puts graves over spike strips so ignoring the tell hurts — the warning is ≥ 100 f of visibly increasing tremble. Animation A10 (tremble, dirt trickle, glowing cracks, skeletal hands, swallow suction, rune progress ring while gone, dome + fountain on emerge). Never used by enemies. `gvHint('sink',…)`.

### 4. SPECTRAL SLABS + SOUL LANTERNS (`fx:'l'`, `G.lamps=[{x,y,link:[platformIdx…]}]`)
`gv.lamps=[{x,y,...lampNew(),swing:{x:0,v:0}}]`; star contact (`GVH.blHit`, r 20) → `lampHit(l,GV.lamp)`, pendulum impulse, star consumed unless piercing. `gvLampStep` (in `GVH.step`) → `lampStep`; emits `lamp:lit|flicker|dark` on phase changes. Slab solidity in `kin` (above). Fair-play: the last 70 f flicker + 30 f "unstable shimmer" before `w→0`; a player still standing falls (fair, telegraphed). **Spectral slabs are shortcuts only** — L2 treats them as absent and must still pass. Animation A11 (lantern) + A12 (materialise/dematerialise). Light r 180 via `GVH.lights`. `gvHint('lamp',…)`.

### 5. STAGE 12 look (`TH[7]`, `w=7`, dark .72) — Bible A15 (stage 12), A16
Backdrop (`bgBuildGV(7)`, cached): vaulted crypt, deep indigo; **Sierpiński arches** (baked, depth 5, cyan hairlines α .12-.25: great central arch + two side arches); **ossuary wall** — recursive niche grid with skull piles, every 3rd niche amber; **Julia-set rose window** (160×160 sprite baked once, ≤ 30 iterations, cyan→violet) rotating slowly with additive breath; chains + **fractal chandeliers** (Koch-style candle rings, swinging .03 rad, `fbm` flames); **vein cracks** (L-system depth 5) with a travelling signal; dust motes; cobwebs. Platforms (`dGPlat` for `TH[7]`): blue-violet stone with a carved **Cantor-pattern band** (3 notch levels) and hinge ornaments; graves = earth mound over a leaning tombstone; floor = bone-and-dust grating; spikes as ribs/fangs. Enemies: `th.ec` amber. **Music:** final `MU[11]`: melody from the **Thue–Morse sequence** mapped onto scale degrees (`mt[i]=tm(i)?sc[(i>>2)%4]:null` style; build once at load, verify no `NaN` notes); keep `bell`,`pd`,`ar`. **Grade:** cold teal-violet `GD` row.

### 6. Layout, capacitors, difficulty
Seed `GVL[12]`; slab #7 normal, #17 insulated (`ins`), `chargeT` 540, `liveT` 150 (Part 10 code, stage-12 data). Run L2 on the real file: every platform reachable in every Cantor state (the tool checks 0/1/2) with spectral slabs absent. Difficulty: `hold`, `litT` ×1.25 Easy, ×.85 Hard (never `tell` < 30 f).

### 7. Invariants added: INV-3 (anchors), INV-13, INV-19 `lamp.lit>=0`, INV-20 a grave is swallowed only after ≥ ⌈max/v⌉ occupied ticks since its last full rise (no instant swallow), INV-21 no star/enemy/power-up on `'u'|'s'|'l'`.

## Tests
L1 + L2 + fuzz. (a) Cantor: all three states, tell/anim timing from `snap()`, riders on vanishing cells (≥ 54 f warning), dash through gaps, keystones never vanish (sample 2 cycles × 3 phases), `step(1)×6==step(6)`. (b) Sinking: swallow tick == 102 under constant occupancy, rise/emerge timing, carry correctness (no jitter, never falls through — assert `pl.y+42<=p.y+6` after landing), retry/clear reset, spikes below. (c) Lantern/spectral: star lights, refresh, flicker tell, fall when expired, pierce, light radius in the dark pass, shortcut-only rule. (d) Visuals: 8 screenshots (each mechanic in tell/active states) inspected + preview + `FXON=0`; determinism hash; perf with bridge + 2 graves + 3 ghosts + capacitors (numbers). (e) Stage 12 start/retry/death/clear → stage 13; checkpoint 11 respawn; `GV_ON=0` fallback (cells stay plain platforms; stage completable).

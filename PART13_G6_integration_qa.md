# ARIA → v33 · THE FRACTAL NECROPOLIS (3 new dark stages after stage 10) · PART 13/13 · TRACK B 6/6 — Integration, balance, QA, final build

You are ONE of several Claude Code sessions (possibly on different accounts) that build the same feature **in sequence**. You have NO memory of earlier sessions: everything you need is in this file, `HANDOFF.md`, the reference images and the game file. Stay strictly inside this part's scope.

**Project:** *Aria and the Lost Stars* — heavily customised single-file HTML5 Canvas platformer (~5000 lines, ~835 KB, 1000×600 logical canvas, stages 1-14 today: bosses on 5 / 10 and the Void Singularity final boss on 14; the UI/docs sometimes call it "13 stages + finale"). **Track B** inserts THREE new stages right after the Crimson Reaper (stage 10): **11 THE WEEPING CEMETERY · 12 THE FRACTAL CRYPT · 13 THE STORM MAUSOLEUM** — dark, frightening, *graveyard + fractal*. The old stages 11-14 become **14-17** (campaign = 17 stages). Track A (5 Hard-mode enemies, Parts 1-7) is independent and runs first: Track B's input is `aria_v32.html`. If Track A was skipped the input is `aria_v31.html` and every "HE" note below is N/A.

## Session protocol
**START**
1. Read `HANDOFF.md` completely (Track B sections included), **`GV_ENGINE_SPEC.md` §1-§4** (verified runtime facts + engineering contract) and the **`GV_ANIMATION_BIBLE.md`** entries cited in this part. Open the reference images listed in this part (blueprints = seed layouts + palette). Run `node tools/gv_lib.test.mjs` (must pass: it proves the reference algorithms you will paste) and, once a game file exists, `node tools/gv_reach.mjs html <file>`.
2. Input file: `aria_v33_g5.html`. Verify earlier Track B parts are really in it: for each K in 8, 9, 10, 11, 12 run `grep -c "===== GV part K:" aria_v33_g5.html` (each must be ≥ 1). If something is missing → STOP and tell the user (in Persian) which part must run first.
3. If `HANDOFF.md` marks this part as **WIP**, resume from its remaining checklist instead of starting over (input = the `_WIP` file it names).

**BUDGET (the pack is designed to fit daily limits)**
- Never `cat` the game file. Use `grep -n` and `sed -n 'a,bp'` ranges. All anchors below were verified on v31; **line numbers drift** (Track A shifted them) — re-grep every anchor.
- Work in small verified patches (a patch script with assertions on unique anchors); re-read every modified region; check duplicate functions / unmatched delimiters / template literals.
- If you are about to run out of budget: reach a clean LOADABLE state, save `aria_v33_WIP.html`, write the exact remaining checklist into `HANDOFF.md` (status: WIP). Never leave a half-edited file as "the output".

**END**
1. Save the result as a NEW file `aria_v33.html` (never overwrite earlier files).
2. Append a ≤30-line section `## Part 13` to `HANDOFF.md`: status DONE, output filename, functions/vars/`GV` keys added, hooks used, runtime fields, known issues, tests run.
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

## Scope of THIS part (G6): integration, balance, QA, final build — no new features
Input `aria_v33_g5.html` → output **`aria_v33.html`** + **`GV_TUNING.md`**. Read SPEC §5-§6 and the invariant list. Your job is to *break* the build, then fix what you find, keeping every fix inside GV code.

### 1. Global audit (static)
Re-run the Part 8 stage-literal grep: every `==14|>=14|<=14|/14|,13\)|==13|%5==0|=14\b` hit justified; `FIN/isBoss/isMag/isGV` are the only stage-range tests; `stage>=11` (Wizard + enemy cap) intentionally unchanged. Duplicate functions, unmatched delimiters, template literals. Marker audit (`===== GV part N:` for N = 8…12 present once each); every one-line patch tagged `/*GV<N>*/`. Ownership audit (SPEC §2.2): grep that only `gvJuice` writes `shake/fl/zm/hs` inside GV code, only `gvZap` calls `hurt`, only `kin` writes fx platform geometry.
Fail-soft: inject a throw into each of `GVX.q/s/u/l`, `gvDark`, `gvAmb`, `gvStorm`, `gvElec`, each draw hook → after 3 errors `gvFail`, game continues, stages 11-13 still start and are completable.

### 2. Layered tests (SPEC §6)
**L1** `node tools/gv_lib.test.mjs` (all groups). **L2** `node tools/gv_reach.mjs html aria_v33.html` (+ variants `--nodash`, `--nodj` for information). **L3/L4** with browser automation (Playwright/puppeteer if present; if not, say so explicitly and list what was not run): `window.__gv` harness; for stages 11-13 × dif 0-2 × 20 seeds: seeded random input traces, 20 000 ticks, `inv()` every tick, **zero violations**; determinism (same seed + trace ⇒ identical `hash()` sequence twice); batching equivalence (`step(1)×6 == step(6)`); pause/resume mid-WARN / mid-tell (`gv.t` frozen, no event fires); hit-stop (`gv.t` frozen); stage clear mid-LIVE (no damage after clear). **L5** screenshots: every mechanic in tell+active states, stage-select previews, `FXON` 0/1/2, mobile landscape; parity screenshots of stages 1-10 and 14-17 vs the previous build.

### 3. Gameplay matrix (Aria test matrix — state what you could not run)
Low vs high skill traces (idle/camping, constant movement, speed-run), Easy/Normal/Hard, ground vs airborne, ranged vs close; checkpoint/retry (11→11, 12→11, 13→11, 14-16→14), death, clear, next stage; keyboard/mouse/gamepad/touch; stage select 17 slots; wardrobe + cosmic costume unlock at stage 17. Search for forced damage, stuck states, uncollectable stars, softlocks (sinking grave swallowed under the player, Cantor states, expired lanterns, strike + pool + slab coincidence). A bot that never jumps over pools must still be survivable on Easy (damage ≤ 1 heart per pool cycle).

### 4. Balance evidence
Instrument counters (debug only): zaps by source (slab/pool/strike), hits by enemy type, time per stage, deaths per stage, charged-enemy kills, grounding uses, lantern uses. With a simple bot, report medians per difficulty. Present as **design hypotheses** until a human playtests; give the first 5 things a playtester should watch (camping on insulated slabs, ignoring lanterns, pool deaths on Hard, Cantor state-2 crossings, strike/discharge overlap).

### 5. Performance and quality
Avg and p95 ms/frame on stages 10, 11, 12, 13, 14 at `FXON` 0/1/2 and low `AQ`; per-subsystem `GV.perf` (dark, platforms fx, particles, backdrop overlays, director) vs SPEC §5 budgets; memory: caches disposed on stage change (count live offscreen canvases ≤ 8). Fix budget overruns by lowering resolution/counts, not by removing animations.

### 6. Saves and compatibility
Migration tests on the final file (old v31/v32 saves, imports, save-folder restore, fresh profile playing to 14+ and reloading); `grep` confirms **no new localStorage key**; `?dev` and `?gvdebug` behave; debug hooks inert without the flag.

### 7. Deliverables
`aria_v33.html`; `GV_TUNING.md` (every `GV` knob: default, effect, owner part, first knobs to change after playtests, difficulty multipliers); `tools/` updated if you changed the lib (tests included); updated `HANDOFF.md` (final status board, measured numbers, known issues). Final report in Persian: files, behaviour changed, systems touched, tests actually run + results (numbers), limitations, and a quick-test recipe (`?dev` + stage select; `?gvdebug` helpers: `__gv.go(12,1)`, `__gv.force('slab:warn')`).

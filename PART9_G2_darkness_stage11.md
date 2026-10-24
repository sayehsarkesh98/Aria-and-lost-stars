# ARIA → v33 · THE FRACTAL NECROPOLIS (3 new dark stages after stage 10) · PART 9/13 · TRACK B 2/6 — Darkness + ambience engine, fractal helpers, STAGE 11 look

You are ONE of several Claude Code sessions (possibly on different accounts) that build the same feature **in sequence**. You have NO memory of earlier sessions: everything you need is in this file, `HANDOFF.md`, the reference images and the game file. Stay strictly inside this part's scope.

**Project:** *Aria and the Lost Stars* — heavily customised single-file HTML5 Canvas platformer (~5000 lines, ~835 KB, 1000×600 logical canvas, stages 1-14 today: bosses on 5 / 10 and the Void Singularity final boss on 14; the UI/docs sometimes call it "13 stages + finale"). **Track B** inserts THREE new stages right after the Crimson Reaper (stage 10): **11 THE WEEPING CEMETERY · 12 THE FRACTAL CRYPT · 13 THE STORM MAUSOLEUM** — dark, frightening, *graveyard + fractal*. The old stages 11-14 become **14-17** (campaign = 17 stages). Track A (5 Hard-mode enemies, Parts 1-7) is independent and runs first: Track B's input is `aria_v32.html`. If Track A was skipped the input is `aria_v31.html` and every "HE" note below is N/A.

## Session protocol
**START**
1. Read `HANDOFF.md` completely (Track B sections included), **`GV_ENGINE_SPEC.md` §1-§4** (verified runtime facts + engineering contract) and the **`GV_ANIMATION_BIBLE.md`** entries cited in this part. Open the reference images listed in this part (blueprints = seed layouts + palette). Run `node tools/gv_lib.test.mjs` (must pass: it proves the reference algorithms you will paste) and, once a game file exists, `node tools/gv_reach.mjs html <file>`.
2. Input file: `aria_v33_g1.html`. Verify earlier Track B parts are really in it: for each K in 8 run `grep -c "===== GV part K:" aria_v33_g1.html` (each must be ≥ 1). If something is missing → STOP and tell the user (in Persian) which part must run first.
3. If `HANDOFF.md` marks this part as **WIP**, resume from its remaining checklist instead of starting over (input = the `_WIP` file it names).

**BUDGET (the pack is designed to fit daily limits)**
- Never `cat` the game file. Use `grep -n` and `sed -n 'a,bp'` ranges. All anchors below were verified on v31; **line numbers drift** (Track A shifted them) — re-grep every anchor.
- Work in small verified patches (a patch script with assertions on unique anchors); re-read every modified region; check duplicate functions / unmatched delimiters / template literals.
- If you are about to run out of budget: reach a clean LOADABLE state, save `aria_v33_g2_WIP.html`, write the exact remaining checklist into `HANDOFF.md` (status: WIP). Never leave a half-edited file as "the output".

**END**
1. Save the result as a NEW file `aria_v33_g2.html` (never overwrite earlier files).
2. Append a ≤30-line section `## Part 9` to `HANDOFF.md`: status DONE, output filename, functions/vars/`GV` keys added, hooks used, runtime fields, known issues, tests run.
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

## Scope of THIS part (G2): darkness engine, ambience, bake/cache helpers, and the full look of STAGE 11 — THE WEEPING CEMETERY
No electric mechanics yet (Part 10). Read first: SPEC §4.8-§4.9, §5; Bible **A15 (stage 11), A16, A20, A19, P1-P8**. Reference: `reference_images/gv11_blueprint.png` (palette + seed layout). The stage must feel dark and frightening while staying readable and in the game's neon-cartoon style (soft glows, rim light, rounded shapes) — not photoreal grit.

### 1. Lighting pass `gvDark()` (stages 11-13)
**Where:** in `draw0()` after the player/aim draw and **before** the additive particle loop (`c.globalCompositeOperation='lighter'`/`for(const p of pt)`), so sparks and pop text stay bright; the HUD is never darkened. Same transform as the world (shake/zoom aware).
**Algorithm (per frame):**
1. `α=GV.dark[stage]` (11: .58, 12: .72, 13: .60), hard cap .78, `α*=1-min(1,fl/GV.flash.maxFl)` (lightning reveals the scene).
2. Offscreen `dk` canvas at **half resolution** (500×300), allocated once per stage (key `(stage,quality)`), disposed on change. `dk.fillStyle='rgba(2,3,10,α)'; fillRect`.
3. Collect lights into the preallocated registry (cap `GV.maxLights`=32; **priority order** player → strike/rod → live slabs/pools → lit lanterns → stars → power-ups → enemy eyes; cull when `x±r` is off-screen; ease newly visible lights in over 10 f).
4. `globalCompositeOperation='destination-out'`; for each light draw the cached soft radial sprite (radius quantised to 16 px buckets, built once) scaled to `r·(1+breath)`; `breath` = A20 (`.02·sin(gv.t*.07)` + `fbm` shimmer ±.015; heartbeat when `hp==1`).
5. Draw `dk` scaled to 1000×600 (`imageSmoothingEnabled=true`).
6. **Glow pass** (additive, after the overlay): for lights that carry a colour, `fGl` at `a*.35` so a live slab/lantern/eye glows in colour instead of merely cutting a hole.
7. `gvRim()`: 2 px top rim on every platform (`th.a`, α .35) + outline on spikes `X` (α .5) + ghost outlines of non-solid fx platforms; drawn after the glow pass so hazards never vanish at α .78.
**Light sources:** player r 210; stage stars `S[k=='*']` r 70; power-ups r 40; enemy eyes r 28 (tint `th.ec`); Part 10-12 push theirs via `GVH.lights`.
**Tiers:** `FXON==0||AQ<.75` → one radial vignette around the player (α .45, no offscreen, no glow pass). **Budget ≤ 1.5 ms** (measure, report).

### 2. Ambience `gvAmb()` (stages 11-13, inside the play step)
Scheduler on a named stream `stream('amb',stage*131+retry)`: wind swell (very low-passed `noise`, every 80-120 f), distant bell or crow every 900-1500 f (positional `px` from a hashed side), heartbeat pair `snd(55,.12,'sine',.1)` every 50 f **only while `hp==1`**; honour `mute`, `musOn`, pause (`st!='play'` ⇒ nothing). Optional storytelling: 6 epitaph lines per stage (`HERE LIES A STAR`, `DON'T LOOK BACK`…) shown once via `pop()` when the player passes within 60 px of the matching decor tombstone (decor positions deterministic from the stage seed).

### 3. Bake/cache helpers (reused by Parts 11-12)
`gvBake(key,w,h,fn)` — returns an offscreen canvas for `key`, drawing it once with `fn(ctx)`; LRU of 6 entries; evicted canvases get `width=height=1`. Fractal geometry comes from `rootSegs(x,y,len,ang,depth,seed,spread,shrink)` (tested): trees are baked as **two layers** (trunk + coarse branches / fine branches depth ≥ 4) so the fine layer can sway (A15). Seeds: `stage*131+layer*17+7`.

### 4. STAGE 11 visual brief (`TH[6]`, background index `w=6`) — with animation hooks
**Backdrop layers** (`bgBuildGV(6)`, cached): near-black teal gradient; pale cracked moon `#cfe9df` (thin dark cracks, torn cloud bands); **far** — 9 dead trees from `rootSegs` (depth 6, two layers); **mid** — graveyard rows (crooked crosses, obelisks, a weeping-angel statue with broken wings, a leaning iron fence with spear tips, a tiny far chapel with one flickering window); **near** — 3 additive fog bands (tiled noise).
**Animated overlays (A15):** tree fine-layer sway with gusts, fog scroll, 12 reactive wisps, eyes FSM in tree hollows (never jump-scare, never damaging), chapel window flicker, drifting ash points (24, deterministic).
**Platforms** (`dGPlat`, cached per width/seed): mossy tomb slabs — stone gradient `#2c3a36→#1b2523`, bevel, carved cross/skull/rune by seed, hairline cracks, moss tufts in `th.pt`, hanging **fractal roots** (`rootSegs` depth 3), mint rim light. **Ground:** black soil, bone fragments, rib arcs, grave mounds; flat top edge at `GY` (pool-ready).
**Spikes:** re-skin `dSpk` as bone/iron-fence spikes when `isGV(stage)` (same hitbox). **Foreground:** cached cobwebs + grass blades + soft vignette before the lighting pass.
**Title card (A16)** for stage 11 and a reusable `gvTitle(name,num,th)` for 12-13.
**Music/grade:** final `MU[10]` (slow, bell-like, minor, pad; may add a 32-step `mt`); tune the `GD` row for `TH[6]` (cool, slightly green, low saturation). Enemies: unchanged sprites, `th.ec` lime glow, stats untouched.

### 5. Stage 11 gameplay (no new mechanics)
Seed layout `GVL[11]`; run L2 (`gv_reach.mjs`) on the actual file; adjust ≤ 20 px if needed. Standard enemy pool + Wizard (stage ≥ 11 rule). Verify stars glow enough in the dark and no platform edge is ever invisible.

### 6. Engineering contract for this part
Add to `inv()`: INV-7 (flash), INV-11 (lights ≤ 32). `GV.perf` rolling means for `dark`, `bgOverlay`, `amb`. All draw code reads only `gv.t`, `RA`, `tick` (decor), `hash2/fbm`. Preview path (`dScene`) must render stage 11 without touching `gv`.

## Tests
L1 + L2. (a) 6 screenshots (start, mid, near a platform edge, with an enemy, `FXON=0`, stage-select preview) — inspect them. (b) Determinism: `draw0()` twice at the same `tick`,`gv.t` ⇒ identical canvas hash. (c) Perf: ms/frame over 600 ticks vs stage 10 (numbers). (d) Darkness never hides spikes/platform tops/stars/enemies/power-ups at α .78 (pixel-sample test: each feature's pixel luminance > threshold). (e) `gvAmb` silent on stages ≠ 11-13, in pause and when muted. (f) Parity: stages 1-10 and 14-17 render identically to the previous build. (g) `GV_ON=0` keeps stage 11 playable. (h) Title card does not block input; light pass survives `AQ` drops.

# ARIA → v33 · THE FRACTAL NECROPOLIS (3 new dark stages after stage 10) · SINGLE-ACCOUNT VERSION (all 6 phases in one go)

You are ONE of several Claude Code sessions (possibly on different accounts) that build the same feature **in sequence**. You have NO memory of earlier sessions: everything you need is in this file, `HANDOFF.md`, the reference images and the game file. Stay strictly inside this part's scope.

**Project:** *Aria and the Lost Stars* — heavily customised single-file HTML5 Canvas platformer (~5000 lines, ~835 KB, 1000×600 logical canvas, stages 1-14 today: bosses on 5 / 10 and the Void Singularity final boss on 14; the UI/docs sometimes call it "13 stages + finale"). **Track B** inserts THREE new stages right after the Crimson Reaper (stage 10): **11 THE WEEPING CEMETERY · 12 THE FRACTAL CRYPT · 13 THE STORM MAUSOLEUM** — dark, frightening, *graveyard + fractal*. The old stages 11-14 become **14-17** (campaign = 17 stages). Track A (5 Hard-mode enemies, Parts 1-7) is independent and runs first: Track B's input is `aria_v32.html`. If Track A was skipped the input is `aria_v31.html` and every "HE" note below is N/A.

## Session protocol
**START**
1. Read `HANDOFF.md` completely (Track B sections included), **`GV_ENGINE_SPEC.md` §1-§4** (verified runtime facts + engineering contract) and the **`GV_ANIMATION_BIBLE.md`** entries cited in this part. Open the reference images listed in this part (blueprints = seed layouts + palette). Run `node tools/gv_lib.test.mjs` (must pass: it proves the reference algorithms you will paste) and, once a game file exists, `node tools/gv_reach.mjs html <file>`.
2. Input file: `aria_v32.html (or aria_v31.html if Track A was skipped)`. Run the Part-8 Track A check (informational) and make sure `grep -c "===== GV part"` is 0.
3. If `HANDOFF.md` marks this part as **WIP**, resume from its remaining checklist instead of starting over (input = the `_WIP` file it names).

**BUDGET (the pack is designed to fit daily limits)**
- Never `cat` the game file. Use `grep -n` and `sed -n 'a,bp'` ranges. All anchors below were verified on v31; **line numbers drift** (Track A shifted them) — re-grep every anchor.
- Work in small verified patches (a patch script with assertions on unique anchors); re-read every modified region; check duplicate functions / unmatched delimiters / template literals.
- If you are about to run out of budget: reach a clean LOADABLE state, save `aria_v33_WIP.html`, write the exact remaining checklist into `HANDOFF.md` (status: WIP). Never leave a half-edited file as "the output".

**END**
1. Save the result as a NEW file `aria_v33.html` (never overwrite earlier files).
2. Append a ≤30-line section `## Track B` to `HANDOFF.md`: status DONE, output filename, functions/vars/`GV` keys added, hooks used, runtime fields, known issues, tests run.
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


> Use this only if one account can do everything in one go. Otherwise use the split PART8…PART13 prompts. Work phase by phase in the order below, commit a loadable intermediate file after each phase (e.g. `aria_v33_phase1.html`), and ignore the intermediate filenames mentioned inside the phase texts: the only final output is `aria_v33.html` + `GV_TUNING.md`.


# PHASE 1 — scope (G1): campaign expansion + shared plumbing
After this part the campaign has 17 stages, stages 11-13 exist as **playable, plain, dark-themed placeholders** (seed layouts, no electric / fractal mechanics yet), saves migrate safely, and every hook later parts need is wired. Reference: `reference_images/gv11_blueprint.png`, `gv12_blueprint.png`, `gv13_blueprint.png`.

### 1. Renumber pass — do this FIRST, verify, only then continue
Constants (one block next to `thI`): `const FIN=17,isBoss=n=>n==5||n==10,isMag=n=>n>=14&&n<=16,isGV=n=>n>=11&&n<=13;`
**Order matters:** (a) rekey the old tables, (b) switch the `n>=11` branches to `isMag`, (c) only then add the new stages — otherwise `HM[11]` is undefined and `genLayout` throws.
Verified v31 audit list (re-grep each literal; "L" = v31 line):
- `thI` (L100): `n<=3?0:n<=6?1:n<=10?2:n==11?6:n==12?7:n==13?8:n<=15?3:n==16?4:5`.
- `TH` (L85): **append** `TH[6..8]` (palettes below). Never insert: `th===TH[5]` (void) and `TH.indexOf(th)` are used all over (`dPlat`, `bg`, `bgGet`, `gdIdx`).
- `HM` (L1250) and `HMX` (L1260): rename keys 11→14, 12→15, 13→16 (data byte-identical; `HMX[11]` = MAGMA GAUNTLET, `[12]` = FORGE OF STARS, `[13]` = FADING ROAD).
- `genLayout` (L907-923): `boss=isBoss(n)`; `lava=isMag(n)?1:0`; `rs=isMag(n)?[60,428]:[60,480]`; `if(n>=11){P=HM[n]…}` → `if(isMag(n))`; the random-spike line (`n<11`) stays. Add the `GVL` branch (section 4).
- `load(n)` (L925-935): checkpoint list `n==1||n==4||n==6||n==7||n==11` → append `||n==14`; `boss=isBoss(n)`; `bs&&n%5==0` → `bs&&isBoss(n)`; star `need`: `n>=11?n-3:` → `isMag(n)?n-6:isGV(n)?GV.need[n-11]:` (old magma values 8/9/10 preserved; `GV.need=[9,10,11]`); `if(n==14){need=tot=0;mkBH();return}` → `n==FIN`; `if(HMX[n])pop(…)` → `if(HMX[n]||GVL[n])pop(W/2,200,(HMX[n]||GVL[n]).n,th.a)`.
- `clearStage` (L966-974): stage 10 text → `'+1 Max Heart! But the graveyard stirs...'`; **new** stage 13 → `'The Magma Abyss awaits...'`; stage 16 (old 13) → `'The Event Horizon awaits... the final boss is next!'`; costume unlock `stage==14` → `stage==FIN`.
- `update()` clear branch (L1650): `if(stage==14)win()` → `stage==FIN`. **Also** `win()` (L962) and the `'vd'` cutscene (L4324) both write `prog.clr[dif]=14` → `prog.clr[dif]=FIN` (missed by simple greps; with 17 stages a clr of 14 would lock the finale's neighbours).
- HUD (L3957 + L3997) `Stage ${stage}/14` and the saved-run label (L3775) `Stage ${r.st}/14` → `/${FIN}`. Clear banner (L4061) `stage==14` → `FIN`.
- `TIPS` (L88): re-key 11→14, 12→15, 13→16, 14→17 and add `11:'WEEPING CEMETERY: the dark hides nothing that glows. Stay off slabs that flash!'`, `12:'FRACTAL CRYPT: bridges fold in thirds, graves sink, lanterns light the ghost slabs.'`, `13:'STORM MAUSOLEUM: lightning follows the rods. Keep to the air when the ground sings.'`.
- Cutscenes: `startCut` duration table (L4313), L4320, L4348 (`stage!=13&&stage!=10` — read it: map the old 13 to 16), L4356, L4495, L4524: every `stage==14` → `stage==FIN`.
- Stage select ribbon loop `for(let i=1;i<=14;i++)` (L4111) → `i<=FIN`; `selGo` bound `k>14` (L4075) → `k>FIN`; `stOK` `Math.min(k,13)` (L746) → `Math.min(k,FIN-1)`; `dScene` (L4087-4088) `k==14` → `FIN`, `k%5==0` → `isBoss(k)`; ribbon skull (L4116) `i%5==0||i==14` → `isBoss(i)||i==FIN`; make sure the 17-slot ribbon, arrows and mouse hit-test still work.
- Saves: `rdRun` (L4580) and `sane` (L4596) `st<=14` → `st<=FIN`; `snapRun` (L4582-4586): `stage>=14` → `FIN`, checkpoint list `[1,4,6,7,11]` → `[1,4,6,7,11,14]`.
- Music (L880): `MU[Math.min(stage,13)-1]` → `MU[Math.min(stage,FIN-1)-1]`; **insert** 3 entries into `MU` at indices 10-12 (placeholders below) so old entries shift to 13-15 (old stages 11-14 keep their tracks; stage 16 and 17 share the last one exactly as 13/14 did).
- Colour grade: `gdIdx` (L4889) returns `TH.indexOf(th)` → 6/7/8 would hit `GD[6]` (the frost grade) / `GD[7]` (menu) / undefined. Append 3 rows to `GD` (copy the 12-number shape of an existing dark row, cool/desaturated) and return 8/9/10 for `TH[6..8]`.
After patching run `grep -nE "==14|>=14|<=14|/14|,13\)|==13|%5==0|n>=11|n<11"` and justify **every** remaining hit in `HANDOFF.md`.

### 2. Save migration — per-object stamp `cv:2` (no new localStorage key)
Use `tools/gv_migrate.js` verbatim (pure, unit-tested: `migProg`, `migRun`, `migBag`, `migStore`). Rule: an object **without `cv===2`** has its stage numbers ≥ 11 shifted by +3 and is stamped; an object with `cv:2` is returned unchanged (same reference) ⇒ idempotent, safe if an old build overwrote one key, no global flag to desync.
Wiring (all of it):
(a) **boot**: call `migStore(localStorage)` *before* line 745 (`prog` load) and before `runSv=rdRun()` (L4580);
(b) **new data carries the stamp**: default `prog={fin:[0,0,0],clr:[0,0,0],cv:2}` (L744) and `snapRun`'s object gets `cv:2` — otherwise a fresh player's progress would be shifted at the next boot;
(c) `sane(d)` (L4596) starts with `d=migBag(d)`; this covers `applyData` (import, save-folder restore, sync);
(d) `rdRun`/`sane` bounds use `FIN`; `pack()`/export need no change (the stamps live inside the objects);
(e) never lose progress: any parse error leaves the raw value untouched (the lib already does this).
Note for HANDOFF: an old v31/v32 build reading migrated saves sees `st>14` and discards `aria_run`; don't alternate builds on one profile.

### 3. Themes and music slots (final art/audio come in later parts)
```js
TH[6]={n:'Weeping Cemetery',a:'#9dffcf',g:['#050b0d','#10262a'],pc:'#2c3a36',pt:'#6fae8f',ec:'#c8ff6b'}
TH[7]={n:'Fractal Crypt',   a:'#7ef0ff',g:['#04060f','#0e1a3a'],pc:'#1c2540',pt:'#7ef0ff',ec:'#ffcf6b'}
TH[8]={n:'Storm Mausoleum', a:'#d6e4ff',g:['#02030a','#141c3a'],pc:'#262a40',pt:'#9db8ff',ec:'#ff5a5a'}
MU[10]={r:98,  sc:[0,2,3,5,7,8,10],ch:[0,-4,-2,-7],tk:12,ld:'sine',bs:'triangle',sd:149,bell:1,pd:1}
MU[11]={r:92.5,sc:[0,1,3,6,7,8,11],ch:[0,1,-4,-5],tk:10,ld:'triangle',bs:'sine',sd:157,bell:1,pd:1,ar:1}
MU[12]={r:87.3,sc:[0,1,3,5,6,8,10],ch:[0,-1,-5,-6],tk:7,ld:'sawtooth',bs:'sawtooth',sd:163,bell:1,kk:1,sn:1,pd:1}
```
Keep the neon-cartoon look of the game (glow sprites, rim light, rounded shapes); darkness comes from palette + the lighting pass, not from grimdark realism.

### 4. Level pipeline (`GVL`)
Create `GVL` with the three **seed layouts** below (verbatim; fx options are data only in this part). In `genLayout`: `if(GVL[n]){const G=GVL[n];P=G.p.map(a=>Object.assign(mk(a[0],a[1],a[2],a[3]||0,a[4],a[5],a[6]),a[7]||{}));X=G.x.map(a=>a.slice());lava=0;rs=G.rs;}` and return `Q.gv=G`. Stars/power-ups/enemies must work on these layouts exactly as on any other stage.
```js
const GVL={
11:{n:"THE WEEPING CEMETERY",rs:[60,428],dark:.58,need:9,
  p:[[0,560,1000],[40,470,120],[250,470,100,0,0,0,0,{fx:'q',q0:.15,link:0}],[470,470,110],[690,470,100,0,0,0,0,{fx:'q',q0:.55}],[880,470,100],[150,395,100],[360,395,100],[580,395,90,'h',55,.9,0],[790,395,100],[40,320,100],[260,320,110,0,0,0,0,{fx:'q',q0:.8}],[480,320,100],[690,320,100],[150,245,100],[380,245,120,0,0,0,0,{fx:'q',q0:.35}],[610,245,100],[820,245,110],[300,170,110]],
  x:[[130,40],[640,40],[880,40]],pools:[[300,560]],rods:[],lamps:[]},
12:{n:"THE FRACTAL CRYPT",rs:[60,433],dark:.72,need:10,
  p:[[0,560,1000],[30,475,110],[240,475,100,0,0,0,0,{fx:'s'}],[470,475,90],[690,475,100,0,0,0,0,{fx:'s'}],[880,475,100],[140,400,90],[360,400,100,0,0,0,0,{fx:'q',q0:.3}],[590,400,90],[800,400,90],[160,325,100],[300,325,360,0,0,0,0,{fx:'u',cells:9,cw:40}],[700,325,100],[60,250,100,0,0,0,0,{fx:'l',lamp:0}],[250,250,110],[480,250,110,0,0,0,0,{fx:'l',lamp:1}],[720,250,100],[150,175,100,0,0,0,0,{fx:'q',q0:.7,ins:1}],[400,175,120],[650,175,100,0,0,0,0,{fx:'l',lamp:1}]],
  x:[[240,100],[690,100],[860,60]],pools:[],rods:[],lamps:[{x:205,y:205,link:[13]},{x:600,y:205,link:[15,19]}]},
13:{n:"THE STORM MAUSOLEUM",rs:[60,428],dark:.6,need:11,
  p:[[0,560,1000],[30,470,110],[220,470,100,0,0,0,0,{fx:'q',q0:.2,link:0}],[440,470,100],[640,470,100,0,0,0,0,{fx:'q',q0:.6,link:1}],[860,470,110],[120,395,100,0,0,0,0,{fx:'q',q0:.4}],[330,395,90,0,0,0,0,{fx:'s'}],[530,395,100],[740,395,100,0,0,0,0,{fx:'q',q0:.9,ins:1}],[30,320,90],[220,320,110],[430,320,90,'h',60,.9,0],[640,320,110],[860,320,100],[130,245,100,0,0,0,0,{fx:'q',q0:.1}],[340,245,324,0,0,0,0,{fx:'u',cells:9,cw:36}],[740,245,100,0,0,0,0,{fx:'q',q0:.5}],[60,170,100],[300,170,110],[520,170,110],[760,170,120]],
  x:[[420,60]],pools:[[40,380],[600,940]],rods:[{x:110,p:18,slabs:[2,6],pool:0},{x:575,p:20,slabs:[4,9],pool:1},{x:820,p:21,slabs:[15,17],pool:-1}],lamps:[]}
};
```
`gvLoad(n,Q)` is called from `load(n)` (and creates `gv={n,G:Q.gv,…}` for stages 11-13, `gv=null` otherwise); `GVH.reset` runs on load, retry/death and clearStage. Cantor-cell expansion (`fx:'u'`) is done in Part 11; here the bridge is one plain wide platform.

### 5. Effect-platform plumbing
- `gvOkPlat(p)` filter in: `nextStar` (platform candidates), the `spawn()` platform choice (where `e.p=p`), the power-up placement in `load` (`up=P.filter(p=>!p.t&&p.y<GY)`), and — if Track A is present — `heSpawn` 'platform' placement and the Silk Widow web patches (static, non-fading, **and** `!p.fx`).
- Enemy carry line (`if(e.p&&e.p.t)…`) → `if(e.p&&(e.p.t||e.p.fx))`.
- Wire `GVH` exactly at the anchors in the API block (step after the enemy loop; `drawPlat` inside the `for(const p of P)` loop of `draw0`; `drawBack` after `bg()`/`dLava()`; `drawFront` just before the player draw; `blHit` in the `bl` loop before `rm`; `pjHit` in the `pj` loop; `lights` is read by Part 9's lighting pass).
- Placeholder painters: `bgBuildGV(w)` (follow the `bgBuild` layer schema; route from `bgGet`/`bg()` for `TH[6..8]`; gradient + moon + 2 silhouette layers + fog is enough) and `dGPlat(p)` (early return in `dPlat`/`dPlatO` for `TH[6..8]`: dark stone slab with th.pt top rim). Never let `Math.min(2,TH.indexOf(th))` see index ≥ 6.
- `?gvdebug` only: `window.__gv={go:(n,d)=>{setDif(d??1);beginAt(dif,n)},state:()=>gv}`. `?dev` keeps unlocking the select screen.

### 6. GV core (paste from `tools/gv_lib.js`, then wire — SPEC §2-§3)
- Paste the library body into a `GV part 8: core` block; initialise `GV.slab/pool/sink/lamp/cantor` from the lib defaults (`SLAB,POOL,SINK,LAMP,CANTOR`) and add `GV.zap={cd:12}`, `GV.flash={maxFl:16,minGap:20}`, `GV.maxLights:32`.
- Implement exactly as specified: `gvTry/gvFail`, event bus, `gvJuice` (caps `shake≤24, zm≤.06, hs≤4`; flash limiter; `prefers-reduced-motion`/`FXON==0` → 6-tick dim instead of white), `gvZap`, `gvHint`, `gvReset(reason)` (matrix in SPEC §2.6), sim clock `gv.t`, light registry (32 preallocated `{x,y,r,c,a}`), `gvOkPlat`.
- `gv` skeleton created by `gvLoad`: `{n,G,t:0,retry,zapT:0,zaps:0,slabs:[],pools:[],cabs:[],pulses:null,graves:[],cells:[],spec:[],lamps:[],storm:null}`; `gv.retry` = how many times this stage was (re)loaded in the current run (used to seed directors). Later parts fill their arrays.
- Hook runners: `gvKin()` right after `movP()`; `gvStep()` after the enemy loop (increments `gv.t`, runs `GVH.step` entries each inside `gvTry`, then `gvFlush()`); draw-phase runners at the anchors of the API block. All are no-ops when `!gv`.
- Interpolation (SPEC §1.7): patch the two loops `if(p.t)ipP(p)` and `if(p.t)L(p)` to `p.t||p.fx=='s'`.
- Debug harness behind `?gvdebug` only: `window.__gv={seed,go,step,snap,hash,inv,force,perf}` (SPEC §6 L3). Implement `inv()` with INV-1,2,4,5,6,9,10,11,12,13,15 now; later parts add theirs.

## Tests (run what you can; never claim untested results — say which layers ran)
**L1** `node tools/gv_lib.test.mjs` before and after (must pass). **L2** `node tools/gv_reach.mjs html <your file>` (the seed layouts must pass on the real file; exit code 0).
(a) **Parity:** for stages 1-10 and 14-17 compare `genLayout` output (P, X, rs, lava, th palette, need) with v32's stages 1-10 and 11-14 — identical (hash both JSON dumps). Boss flags only on 5, 10; stage 15 is NOT a boss; stage 17 starts the Void cutscene and ends with the win screen (and writes `prog.clr[dif]=17`); stage 16 → 17 transition and the costume unlock work.
(b) **Migration:** synthetic saves (`clr` 0/10/11/13/14, run at old stage 12 with checkpoint 11, already stamped, corrupt JSON) through boot, `sane()`/`applyData` and an exported file; a fresh profile that plays to stage 14 and reloads is NOT shifted twice.
(c) Stage select shows 17 slots (keyboard + mouse), skulls on 5/10/17, previews of 11-13 render, locks follow `clr`; HUD `/17`; clear texts; TIPS; checkpoints (11 and 14 are respawn points; death on 12 returns to 11).
(d) Music: every stage 1-17 plays without throwing; stages 14-17 use their old tracks. `gdIdx` valid for every theme.
(e) Stages 11-13: spawn, stars reachable, enemies/Wizard spawn, power-up placement never on `fx` slabs, `gv.t` frozen in pause/hit-stop, `kin/step` order verified with a log, no console errors; `GV_ON=0` fallback loads.
(f) Easy/Normal/Hard all start every stage; Track A enemies (if present) still spawn on Hard in 11-17.
(g) If browser automation exists: 20 000-tick fuzz with `inv()` on stages 11-13 × 3 difficulties; otherwise state that it was not run.


# PHASE 2 — scope (G2): darkness engine, ambience, bake/cache helpers, and the full look of STAGE 11 — THE WEEPING CEMETERY
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


# PHASE 3 — scope (G3): the ELECTRIC SYSTEM — Capacitor Slabs, charged enemies, conductive pools, fractal cables — wired into STAGE 11
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


# PHASE 4 — scope (G4): fractal + grave + spectral platforms — STAGE 12, THE FRACTAL CRYPT
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


# PHASE 5 — scope (G5): the STORM — lightning rods, strikes, bell, pulses, fractal lightning — STAGE 13, THE STORM MAUSOLEUM
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


# PHASE 6 — scope (G6): integration, balance, QA, final build — no new features
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

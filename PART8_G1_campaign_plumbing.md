# ARIA → v33 · THE FRACTAL NECROPOLIS (3 new dark stages after stage 10) · PART 8/13 · TRACK B 1/6 — Campaign expansion to 17 stages, save migration, shared plumbing

You are ONE of several Claude Code sessions (possibly on different accounts) that build the same feature **in sequence**. You have NO memory of earlier sessions: everything you need is in this file, `HANDOFF.md`, the reference images and the game file. Stay strictly inside this part's scope.

**Project:** *Aria and the Lost Stars* — heavily customised single-file HTML5 Canvas platformer (~5000 lines, ~835 KB, 1000×600 logical canvas, stages 1-14 today: bosses on 5 / 10 and the Void Singularity final boss on 14; the UI/docs sometimes call it "13 stages + finale"). **Track B** inserts THREE new stages right after the Crimson Reaper (stage 10): **11 THE WEEPING CEMETERY · 12 THE FRACTAL CRYPT · 13 THE STORM MAUSOLEUM** — dark, frightening, *graveyard + fractal*. The old stages 11-14 become **14-17** (campaign = 17 stages). Track A (5 Hard-mode enemies, Parts 1-7) is independent and runs first: Track B's input is `aria_v32.html`. If Track A was skipped the input is `aria_v31.html` and every "HE" note below is N/A.

## Session protocol
**START**
1. Read `HANDOFF.md` completely (Track B sections included), **`GV_ENGINE_SPEC.md` §1-§4** (verified runtime facts + engineering contract) and the **`GV_ANIMATION_BIBLE.md`** entries cited in this part. Open the reference images listed in this part (blueprints = seed layouts + palette). Run `node tools/gv_lib.test.mjs` (must pass: it proves the reference algorithms you will paste) and, once a game file exists, `node tools/gv_reach.mjs html <file>`.
2. Input file: `aria_v32.html`. Track A check (informational): `grep -c "===== HE part" aria_v32.html` should be ≥ 7; if it is 0, Track A was skipped — use `aria_v31.html` as input instead and ignore every HE note. This is the first Track B part: `grep -c "===== GV part" <input>` must be 0, otherwise STOP and tell the user (in Persian).
3. If `HANDOFF.md` marks this part as **WIP**, resume from its remaining checklist instead of starting over (input = the `_WIP` file it names).

**BUDGET (the pack is designed to fit daily limits)**
- Never `cat` the game file. Use `grep -n` and `sed -n 'a,bp'` ranges. All anchors below were verified on v31; **line numbers drift** (Track A shifted them) — re-grep every anchor.
- Work in small verified patches (a patch script with assertions on unique anchors); re-read every modified region; check duplicate functions / unmatched delimiters / template literals.
- If you are about to run out of budget: reach a clean LOADABLE state, save `aria_v33_g1_WIP.html`, write the exact remaining checklist into `HANDOFF.md` (status: WIP). Never leave a half-edited file as "the output".

**END**
1. Save the result as a NEW file `aria_v33_g1.html` (never overwrite earlier files).
2. Append a ≤30-line section `## Part 8` to `HANDOFF.md`: status DONE, output filename, functions/vars/`GV` keys added, hooks used, runtime fields, known issues, tests run.
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

## Scope of THIS part (G1): campaign expansion + shared plumbing
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

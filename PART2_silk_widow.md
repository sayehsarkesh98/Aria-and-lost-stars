# ARIA v31 → v32 · HARD-MODE ENEMIES · PART 2/7 — Root system + Silk Widow (t6)

You are ONE of several Claude Code sessions (possibly on different accounts) that build the same feature **in sequence**. You have NO memory of earlier sessions: everything you need is in this file, `HANDOFF.md` and the game file. Stay strictly inside this part's scope.

**Project:** *Aria and the Lost Stars* — heavily customised single-file HTML5 Canvas platformer (`aria_v31.html`, ~5000 lines, 835 KB, 1000×600 logical canvas, 13 stages + 3 bosses). Feature: 5 new enemies that exist ONLY on Hard (`dif==2`): t6 Silk Widow, t7 Prism Warden, t8 Night-Fang, t9 Void Lantern, t10 Starmaw. Concept sheets (PNG) show each enemy's look, 4 attack phases, palette and specs.

## Session protocol
**START**
1. Read `HANDOFF.md` completely (if it exists).
2. Input file for this part: `aria_v32_p1.html`. Verify earlier parts are really in it: for each K in 1 run `grep -c "===== HE part K:" aria_v32_p1.html` (each must be at least 1). If something is missing → STOP and tell the user (in Persian) which part must run first.
3. If `HANDOFF.md` marks this part as **WIP**, resume from its remaining checklist instead of starting over (input = the `_WIP` file it names).

**BUDGET (the whole pack is designed to fit daily limits)**
- Never `cat` the game file. Use `grep -n` and `sed -n 'a,bp'` ranges; the integration map below is already verified for v31 (line numbers drift — re-grep anchors).
- Work in small verified patches (a patch script with assertions on unique anchors), re-read every modified region.
- If you are about to run out of budget: reach a clean LOADABLE state, save as `aria_v32_p2_WIP.html`, and write the exact remaining checklist into `HANDOFF.md` (status: WIP). Do not leave a half-edited file as the "output".

**END**
1. Save the result as a NEW file `aria_v32_p2.html` (never overwrite earlier files).
2. Append a ≤25-line section `## Part 2` to `HANDOFF.md`: status DONE, output filename, functions/vars/`HE` keys added, hooks used, entity fields, known issues, tests run.
3. Final report **in Persian**: (a) file produced (b) behaviour changed (c) functions/systems touched (d) tests actually run + results (never claim untested results) (e) limitations / notes for the next part.

## Project rules (all parts)
- Single file, no dependencies, keep controls/themes/saves (`aria_*` localStorage + save file) and the 13-stage campaign. No save-schema change.
- Everything new is behind `HE_ON` and only active when `heOn()` (= `HE_ON && dif==2`). Easy/Normal must behave exactly like v31, including the order of `Math.random()` calls. Any exception in new code → `heFail(err)` (turns `HE_ON` off, removes live HE enemies, game continues like v31).
- All tunables live in the single `const HE={…}` block (each part adds its own sub-object, e.g. `HE.widow`). No magic numbers in logic.
- Wrap each part's code in `/* ===== HE part N: name ===== */ … /* ===== /HE part N ===== */` and tag one-line patches inside existing functions with `/*HE<N>*/` so they can be audited/reverted.
- No `Math.random()` inside draw code (render is deterministic: use `tick`, `e.id`). Don't change player physics, existing enemy stats, bosses, level layouts.
- Fairness: every damaging attack = tell → active → recovery → counterplay → failure feedback; no unavoidable damage; never stack two control effects; heavy attacks never spawn on the player (≥220px). Difficulty from layered patterns, not inflated HP/speed. Time unit: 60 ticks = 1 s ("f" = ticks).

## HEX API contract (Part 1 implements it; every other part only USES it)
```js
const HEX={};                                   // registry, key = enemy type t (6..10)
const HEH={step:[],reset:[],drawBack:[],drawFront:[],drawPlayer:[],pjHit:{},blHit:[]};
function heOn(){return HE_ON&&dif==2}
HEX[t]={
  name, w, h, unlock:<stage>, max:<alive>, weight:<rel. spawn weight>,
  place:'ceiling'|'air'|'platform'|function(e){...set e.x,e.y,e.p; return true|false},  // false = abort spawn
  hp:(stage)=>n,                  // FINAL hard hp (shown on the sheets), do not add D.eh
  quiet:false,                    // true = no spawn burst/pop-in scale/theme aura/platform shadow/spawn hint (disguise)
  init(e),                        // after creation: set e.st (state), e.tm (timer) …
  ai(e,px,py),                    // every play tick unless daze; px,py = player centre
  dazed?(e),                      // Neon-Star daze (e.dz); default = freeze with a small bob
  dmg?(e,d)->d2,                  // modify/cancel damage in hitE (0 = immune: spark + chime, no damage)
  contact?(e,px,py,bot)->bool,    // full override of the shared contact test (stomp/hurt); true = handled
  draw(e),                        // painter inside dE2; uses e.x/e.y/e.w/e.h, e.fl>0 = white hit flash; deterministic
  onKill?(e)
};
HEH.step.push(fn(px,py))          // once per play tick after the enemy loop
HEH.reset.push(fn())              // load(n), retry/death, clearStage
HEH.drawBack.push(fn())           // after platforms, before enemies
HEH.drawFront.push(fn())          // after enemies, before HUD
HEH.drawPlayer.push(fn(px,py))    // right after the player sprite
HEH.pjHit[k]=fn(q,i,px,py)->bool  // enemy projectile kind k (pj[i]); true = handled/removed
HEH.blHit.push(fn(b,i)->bool)     // player star b (bl[i]) vs HE objects; true = star consumed (respect tm.p pierce)
function heFail(err); function heHint(t)  // heHint = one-time pop() per run per type
```
HE enemies are normal `E` entries: `{t,x,y,w,h,hp,a:1,fl:0,d,cd,id,born,mn,tp,sp,st,tm,p?}`.

## Verified map of v31 (re-grep before editing)
- `DF[2]` (L93) Hard: hp 3, es 1.25, ps 1.2, bc .8, eh 1, sr .7, cap +3, dr .7, sc 1.6. Existing t0 slime, t1 bat, t2 imp, t3 spiked brute (no stomp), t4 Phantom (hard-only), t5 Wizard (`mkWiz`, `wizAI`).
- `spawn()` L994 (pool, size table `d=[[w,h,hp],…][t]`, placement). `kill(e)` L977 (score array `[85,100,170,255,340,500][e.t]`, `drop`). `hitE` L981. `hurt(dir,fall)` L954 (respects `pl.inv, tm.i, iv, au`; shield `sh` absorbs one hit).
- `update()` L1642: inputs `Lk,Rk,Jk,Dk,Fk`; aim `ax/ay`; jump buffer `jb`; dash `pl.dt` (i-frames); `pl.vx` accel ±.9, clamp ±5 (boss pull precedent: `bs.pu`). Enemy loop ~L1700–1735 (AI chain by `e.t`, then shared contact test: stomp = `pl.vy>0&&pb<=e.y+12` → `hitE(e,2)`). Enemy shots `pj[]` loop ~L1783 `{x,y,vx,vy,r,c,k}`; player stars `bl[]` loop ~L1760 (`rm`, `tm.p` pierce). `sgd(px,py,x1,y1,x2,y2)` L4136 segment distance (boss lasers).
- `P[]` platforms `{x,y,w,h,py,t,dx,dy,al}` (`t` moving, `'f'` fading), floor `GY=560`, pits `X[]`, lava stages. `load(n)` L925 resets arrays. `S[]` pickups/stars (`k=='*'` = stage star, drives `need/nextStar`).
- Helpers: `burst, ring, pop, snd, noise, sx, rnd, clamp, fGl/eGl` (glow), `star()`, `th.ec` (stage enemy glow colour), `act('l'|'r'|'j'|'d'|'f')`.
- Drawing: `dEnemy(e)` L3846 → `dE2(e)` L3860 (live painters when `EN_ON`), `enSh`, death dissolve `dEnTrk` L3831, old painters `dEnemyO/dE2O`. `draw0()` L4022. Real stage-star pickup painter ~L4036 (`fGl` gold r32 + `star(...,13,tick/40)` with bob). Render interpolation (`ipSnap/ipP/L`, ~L4691).

## Scope of THIS part: the Player ROOT system + **t6 SILK WIDOW** (+ web patches)
Reference: `he1_silk_widow.png` (open it first). Mark `/* ===== HE part 2: root + silk widow ===== */`.

### A. Root status (new, shared by later parts)
- State `pl.rt` (root ticks), `pl.rtI` (web immunity ticks); tunables `HE.root={ticks:130,mash:8,imm:150}`. Provide `heRoot(ticks)` — returns false (and does nothing) when `pl.inv>0||tm.i>0||iv>0||au>0||pl.dt>0||pl.rtI>0`; if the shield `sh>0` it absorbs the web instead (`sh--`, shield FX like `hurt`); else sets `pl.rt`.
- While `pl.rt>0` (patch `update()` ~L1652–1700 with `/*HE2*/` tags): **aiming and shooting stay fully active** (compute `ax/ay` from the raw keys as before); but no walking acceleration, no jump (`jb` ignored), no dash; `pl.vx=0`; gravity still applies. Mash: each alternating left/right key edge (or the touch-control equivalent if the game has one) removes `HE.root.mash` ticks; the timer always runs out anyway. On release: `pl.rtI=HE.root.imm`, silk-shatter particles + soft sound. Taking damage never extends the root.
- Visual: silk cocoon over Aria (via `HEH.drawPlayer`) with cracks growing as the timer drains + a small shrinking timer ring above the head. Reset `pl.rt/pl.rtI` in `HEH.reset`.

### B. t6 SILK WIDOW — 40×34, hp 4 (+`stage>>3`), unlock stage 3, max 2, weight 1, `place:'ceiling'`
Tunables in `HE.widow`. Ceiling spider on a silk thread (line from `y≈-10` to the body). States:
1. **DROP** 50f: lowers to `y∈[120,320]` above a platform near the player, then **HANG** 60–90f swaying (`sin(tick)`), then picks SHOOT (65%) or TRAP (35%).
2. **SHOOT**: tell 40f (abdomen glows cyan + dotted aim line, **no lead aiming**) → slow web ball `pj k:'web'`, speed `5*D.ps`, r 9; hit (`HEH.pjHit.web`) → `heRoot(HE.root.ticks)` (web ball removed either way). Cooldown `150*D.bc`. It does NOT fire while `pl.rt>0||pl.rtI>0`.
3. **TRAP**: climbs to the ceiling 25f, scuttles along it 60f, then plants 1–2 web patches `wb[]` `{x,y,w:46,h:30,born,life:1500}` on STATIC platform tops only (not `p.t`, not fading), ≥120px from the player. Each patch = faint ghost outline for 40f, then solid/sticky. Touching a solid patch → `heRoot` (patch consumed). **Any player star destroys a patch** (`HEH.blHit`: sparkle burst; pierce stars (`tm.p>0`) keep flying; normal stars are consumed). Max 5 alive (oldest fades). Patches clear on `HEH.reset` and stage clear. Draw them in `HEH.drawBack` (shimmering net disc).
4. **PUNISH**: if the player is rooted the widow lowers slowly toward them and bites after ≥90f with a 20f tell, so a rooted player who focuses the widow (4 hp) can win the race. Stomp-able from above (default contact). Death: thread snaps and the body falls with particles.
- Painter: see the sheet (8 jointed legs with glow joints, hourglass mark on the abdomen, big magenta eyes, cyan silk).

## Tests
Hard via `?hedebug`, `__heSpawn(6)`: tell timing; web ball root; shield absorbs; invulnerable states don't root; mash shortens the root; aiming/shooting work while rooted; no walk/jump/dash; immunity after release; patches ghost→solid, destroyed by normal and pierce stars, cap 5, cleared on retry/stage clear; widow never webs a rooted/immune player; Easy/Normal unaffected; no console errors.

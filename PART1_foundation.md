# ARIA v31 → v32 · HARD-MODE ENEMIES · PART 1/7 — Foundation: registry, spawn gating, hooks (no visible enemy)

You are ONE of several Claude Code sessions (possibly on different accounts) that build the same feature **in sequence**. You have NO memory of earlier sessions: everything you need is in this file, `HANDOFF.md` and the game file. Stay strictly inside this part's scope.

**Project:** *Aria and the Lost Stars* — heavily customised single-file HTML5 Canvas platformer (`aria_v31.html`, ~5000 lines, 835 KB, 1000×600 logical canvas, 13 stages + 3 bosses). Feature: 5 new enemies that exist ONLY on Hard (`dif==2`): t6 Silk Widow, t7 Prism Warden, t8 Night-Fang, t9 Void Lantern, t10 Starmaw. Concept sheets (PNG) show each enemy's look, 4 attack phases, palette and specs.

## Session protocol
**START**
1. Read `HANDOFF.md` completely (if it exists).
2. Input file for this part: `aria_v31.html`. Verify earlier parts are really in it: this is the first part: the input is the untouched original v31 (`grep -c "HE part" aria_v31.html` must be 0). If something is missing → STOP and tell the user (in Persian) which part must run first.
3. If `HANDOFF.md` marks this part as **WIP**, resume from its remaining checklist instead of starting over (input = the `_WIP` file it names).

**BUDGET (the whole pack is designed to fit daily limits)**
- Never `cat` the game file. Use `grep -n` and `sed -n 'a,bp'` ranges; the integration map below is already verified for v31 (line numbers drift — re-grep anchors).
- Work in small verified patches (a patch script with assertions on unique anchors), re-read every modified region.
- If you are about to run out of budget: reach a clean LOADABLE state, save as `aria_v32_p1_WIP.html`, and write the exact remaining checklist into `HANDOFF.md` (status: WIP). Do not leave a half-edited file as the "output".

**END**
1. Save the result as a NEW file `aria_v32_p1.html` (never overwrite earlier files).
2. Append a ≤25-line section `## Part 1` to `HANDOFF.md`: status DONE, output filename, functions/vars/`HE` keys added, hooks used, entity fields, known issues, tests run.
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

## Scope of THIS part: infrastructure only (no visible new enemy yet)
Implement the HEX/HEH contract above, exactly. Mark the block `/* ===== HE part 1: foundation ===== */`.

1. **Flags/tunables** (near the other feature flags): `HE_ON=1`; `HE_DEBUG=/[?&]hedebug/.test(location.search)?1:0`; `const HE={maxNew:2,maxNewLate:3,lateStage:10,minDist:220,share:.3}`.
2. `heOn()`, `heFail(err)`, `heHint(t)`, registry `HEX`, hooks `HEH`.
3. **`spawn()`**: first line `if(heOn()&&heSpawn())return;`. `heSpawn()` returns true if it created a new enemy. When `!heOn()` NO new code may run → identical `Math.random` order to v31. In `heSpawn()`: candidates = registered types with `unlock<=stage` and alive<`max`; total alive HE enemies < (`stage>=HE.lateStage?HE.maxNewLate:HE.maxNew`); roll `Math.random()<HE.share` (else return false → legacy spawn continues); weighted pick; place by `place`: `'ceiling'` → `x=clamp(pl.x±rnd(200,360))`, `y=-40` (AI lowers it); `'air'` → like the Phantom (`x=clamp(pl.x±rnd(220,380))`, `y=rnd(100,380)`); `'platform'` → a platform with `|centre-pl.x|>HE.minDist`, static unless the type allows moving, `y=p.y-h`, `e.p=p`; a function → call it. Always enforce Euclidean distance ≥ `HE.minDist` from the player (retry a few times, then give up without error). Create the entity `{t,w,h,hp:reg.hp(stage),a:1,fl:0,d:±1,cd:80,id:Math.random()*9,born:tick,mn:100,tp:0,sp:(1+stage*.12)*D.es,st:0,tm:0}`, call `reg.init(e)`, push to `E`; unless `reg.quiet`: spawn burst + `heHint(t)`.
4. **Enemy loop**: in the AI chain insert first `else if(HEX[e.t]){try{HEX[e.t].ai(e,px,py)}catch(x){heFail(x)}}`; dazed (`e.dz`) HE enemies call `reg.dazed?.(e)`. In the shared contact test: if `reg.contact` exists and returns true → skip the legacy test. Keep the moving-platform carry line (`e.p&&e.p.t`).
5. **`hitE(e,d)`**: before applying damage `const r=HEX[e.t];if(r&&r.dmg){d=r.dmg(e,d);if(d<=0)return}`. **`kill(e)`**: extend the score array to 11 entries `[85,100,170,255,340,500, 420,520,380,600,450]` (t6 Widow 420, t7 Prism 520, t8 Hound 380, t9 Lantern 600, t10 Starmaw 450) and call `reg.onKill?.(e)`.
6. **Hook wiring**: `HEH.step` after the enemy loop each play tick; `HEH.reset` in `load(n)`, after death/retry and in `clearStage`; `HEH.pjHit[q.k]` inside the `pj` loop before the generic hit test; `HEH.blHit` inside the `bl` loop before `rm` is applied; `drawBack/drawFront/drawPlayer` in `draw0()` (find the player draw call).
7. **Drawing**: in `dE2(e)` add `if(HEX[e.t]){HEX[e.t].draw(e);return}` after the shared setup of `dEnemy` so pop-in scale, glow, hit flash, daze stars keep working; honour `reg.quiet` (skip pop-in scale, `th.ec` aura and `enSh`). Make `dE2O` and `dEnTrk` tolerate unknown `e.t`.
8. **Interpolation**: HE enemies (normal `E` entries) must interpolate like others; document in HANDOFF that HE-owned arrays are drawn from state (position-static) unless they register with `ipSnap/ipP`.
9. **Debug** (only when `HE_DEBUG`): `window.__heSpawn=(t,x,y)=>…` (ignores gates) and `window.__heHard=()=>setDif(2)`.
10. Write the final "HEX API reference" + any deviation from the contract into `HANDOFF.md`.

## Tests
(a) **Parity**: with a seeded `Math.random` replacement run ≥3000 ticks headless on Easy and Normal for v31 vs your output; the `E` spawn sequence (type/x/y) must be identical. (b) With a temporary dummy registered from the TEST script (never left in the file) on Hard: respects unlock/max/minDist, `ai/draw/dmg/contact/onKill` run, reset on retry and stage clear. (c) Throwing inside `dummy.ai` → `heFail` → `HE_ON=0`, game continues like v31. (d) No console errors; boss stages spawn no HE enemies.

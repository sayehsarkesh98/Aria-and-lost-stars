# (SINGLE-ACCOUNT VERSION) Claude Code prompt — Aria v31 → v32: five new HARD-mode enemies
> After this track, the dark-stage expansion (Track B) is in `ALL_IN_ONE_graveyard_stages.md` / PART8-13.
> Use this only if one account can do everything in one go. Otherwise use the split PART1…PART7 prompts.

You are the careful maintainer of an existing, heavily customised single-file HTML5 Canvas platformer, **Aria and the Lost Stars** (`aria_v31.html`, ~5000 lines, 1000×600 logical canvas, 13 stages + 3 bosses). Do NOT rewrite it. Produce **`aria_v32.html`** (leave v31 untouched) by making narrow, verified patches.

## Goal
Add **5 new enemy types that exist ONLY on Hard (`dif==2`)**. Easy and Normal must behave exactly as in v31 (same spawn pool, same random sequence usage where practical). Each enemy needs a creative special attack, a clear telegraph, real counterplay, and a big-but-fair challenge. Reference concept sheets (one per enemy: hero look + 4 attack-phase cards + palette + specs) are next to this file:

`he1_silk_widow.png` · `he2_prism_warden.png` · `he3_night_fang.png` · `he4_void_lantern.png` · `he5_starmaw.png`

**Open and study all five PNGs first.** Match silhouette, palette and big readable eyes. Draw everything procedurally on canvas (vector shapes, gradients, glow helpers). Do not embed external images.

## Hard rules (maintainer conventions)
- Single file, no new dependencies, keep controls, themes, saves (`aria_*` localStorage / save file) and the 13-stage campaign intact. No save-schema change.
- Wrap everything behind one feature flag `HE_ON=1` (like `EN_ON`, `AUR_V31`). If any new code throws, flip the flag off and fall back to v31 behaviour (try/catch like `aurFail`).
- Put ALL tunables in one `const HE={...}` block at the top of the new code so balance is data-driven.
- No `Math.random()` inside draw functions (v19 rule: render must be deterministic; use `tick`, `e.id`).
- Use patch scripts with assertions on unique anchors; re-read every modified region; check for duplicate functions / unmatched delimiters.
- Don't change player physics, existing enemy stats, bosses, or level layouts.

## Verified integration points in v31 (re-grep, line numbers may drift)
- `DF[2]` (L93): Hard = hp 3, es 1.25, ps 1.2, bc .8, eh 1, sr .7, cap +3, dr .7, sc 1.6. Existing types t=0 slime, 1 bat, 2 imp, 3 spiked brute (stomp-immune), 4 Phantom (hard-only, teleports), 5 Wizard (stage 11+, `wizAI`, `mkWiz`). **New types = t 6…10.**
- `spawn()` (L994): pool + size table `d=[[w,h,hp],…][t]`, hp formula, placement (Phantom: air near player; others: on a platform ≥180px from player). Extend, don't replace.
- Enemy loop in `update()` (~L1700–1735): AI branches by `e.t`, then shared contact test (`tick-e.born>14`, stomp = `pl.vy>0&&pb<=e.y+12` → `hitE(e,2)`, `t!=3` stomp-able, else `hurt`).
- `kill(e)` (L977): score array `[85,100,170,255,340,500][e.t]` — extend to 11 entries (t6 Widow 420, t7 Prism 520, t8 Hound 380, t9 Lantern 600, t10 Starmaw 450); `hitE`, `drop`.
- `hurt(dir,fall)` (L954): respects `pl.inv, tm.i, iv, au`; shield `sh` absorbs one hit.
- Player update (~L1652–1700): inputs `Lk,Rk,Jk,Dk,Fk`, aim from `ax/ay`, jump buffer `jb`, dash `pl.dt` (i-frames), `pl.vx` accel ±.9 clamp ±5. Boss pull precedent: `bs.pu` adds to `pl.vx`.
- Enemy shots `pj[]` loop (~L1783): `{x,y,vx,vy,r,c,k,…}` with generic hit → `hurt`. Boss lasers use `sgd(px,y,x1,y1,x2,y2)` (L4136) for segment hit tests — reuse for the Prism beam.
- Player stars `bl[]` loop (~L1760, `rm` flag, `tm.p` = pierce): hook here for "star hits enemy / web / shard".
- Platforms `P[]`: `{x,y,w,h,py,t,dx,dy,al}`; `t` = moving, `'f'` = fading; floor `GY=560`; pits `X[]`; lava stages.
- Helpers: `burst, ring, pop, snd, noise, sx, rnd, clamp, fGl/eGl` (glow), `star()`, `th.ec` (stage enemy glow colour).
- Drawing: `dEnemy(e)` → `dE2(e)` (v19-E painters, live when `EN_ON`), `enSh`, death-dissolve `dEnTrk`, old `dEnemyO/dE2O` fallback. Add painters for t 6–10 to `dE2`, and make `dE2O`/`dEnTrk` safe for unknown types. Real stage-star pickup is drawn near L4036 (`fGl` gold 32px + `star(...,13,tick/40)` with bob).
- Render interpolation (`ipSnap/ipP/L`, ~L4691): any NEW moving entity stored outside `E/pj/S/P/bl` must be registered or kept position-static; prefer `E`/`pj`.
- `load(n)` (L925) resets arrays on stage start/retry; clear all new state there and on death/clear.

## Shared systems to add
1. **Spawn gating (Hard only).** Unlock stage: Widow 3, Night-Fang 4, Starmaw 5, Prism 6, Lantern 8. Max alive: Widow 2, Hound 2, Starmaw 1, Prism 1, Lantern 1; max 2 new-type enemies alive at once (3 from stage 10). Weight so new types are ~25–35% of spawns once unlocked. Never spawn within 220px of the player. No new types during boss fights.
2. **Root status** `pl.rt` (ticks) + `pl.rtI` (web immunity ticks). While `pl.rt>0`: no walking, no jump, no dash, `pl.vx=0` (gravity still works), **aiming and shooting stay fully active**. Mash left/right (alternating key edges) removes `HE.rootMash` ticks per press. On release: `pl.rtI=HE.rootImm`, silk-shatter particles. Root is ignored (and not consumed) when `pl.inv>0 || tm.i>0 || iv>0 || au>0 || pl.dt>0 || pl.rtI>0`; an active shield `sh>0` absorbs the web (`sh--`, shield FX). Taking damage never extends the root. Draw a silk cocoon over Aria + small shrinking timer ring; find the player draw function and add the overlay after it.
3. **First-sighting hint** once per run per type via `pop(...)`, e.g. "WIDOW! Shoot the webs".
4. Debug hook `window.__heSpawn(type)` guarded by `HE_DEBUG=0` for testing.

## Enemy specs (60 ticks = 1 s; "f" = ticks; all hard-only)

**t=6 SILK WIDOW** — 40×34, hp `4+(stage>>3)+D.eh`, ceiling spider hanging on a silk thread (line from y≈-10 to body).
- DROP 50f from ceiling to y∈[120,320] above a platform near the player; HANG: gentle sway 60–90f; then pick SHOOT (65%) or TRAP (35%).
- SHOOT: tell 40f (abdomen glows cyan + dotted aim line, no lead aiming), then slow web ball `pj k:'web'` speed `5*D.ps`, r 9. On hit → root `HE.rootTicks=130`. Cooldown `150*D.bc`. It will NOT fire while `pl.rt>0||pl.rtI>0`.
- TRAP: climbs up 25f, scuttles along ceiling 60f, then plants 1–2 web patches `wb[]` `{x,y,w:46,h:30,born,life:1500}` on STATIC platform tops only (not `p.t`, not fading), ≥120px from the player. Each patch is a faint ghost outline for 40f, then sticky. Touching a solid patch roots (same rules, patch consumed on use). **Any player star destroys a patch** (sparkle burst; pierce stars keep flying). Max 5 patches alive (oldest fades). Patches vanish on stage clear.
- PUNISH: if the player is rooted, the widow slowly lowers toward them and bites after ≥90f with a 20f tell — a rooted player who shoots it (hp 4) can win the race. Stomp-able from above.

**t=7 PRISM WARDEN** — 38×38 floating crystal with one big eye, hp 5, **invulnerable while eye shut** (stars ping with chime+spark, stomp bounces without damage).
- DRIFT 110f hovering ~260px from the player, y∈[110,260]. LOCK 55f: thin red dotted line tracks the player for 35f, freezes for 20f and turns solid/flashing — the frozen line IS the final beam path including the bounce (pre-compute by ray-stepping 6px until it meets a platform top or `GY`, then reflect once, total ~420px). BEAM 22f: 2-segment beam, hit test with `sgd` (hw≈11). Below 50% hp: twin V-beams (±12°). OPEN 50f: eye opens — the only damage window (flash cue), then back to DRIFT.

**t=8 NIGHT-FANG** — 44×28 shadow hound on platforms, hp 3, fast patrol (existing patrol branch, ×1.5 speed).
- Hunt when player within ~380px horizontally and |dy|<200. CROUCH 28f (dust, flared eyes). Target position is **locked when the crouch ends** (aims where you WERE). LEAP: ballistic arc using the same gravity as the player, speed ≤11, lands on the first platform top / floor it crosses; never leap if the landing point is a pit `X[]`/lava. Hard variant: 30% feint — small hop back, second 18f crouch with white eyes, then leap (still telegraphed). Not stomp-able while airborne; always shoot-able; shadow after-images.
- On landing: two low claw-wave shocks `pj k:'cw'` (height ~14px above the platform surface, speed 4.2, travel 160px each way — must be jumped), then DAZED 45f (orbiting stars, double damage taken).

**t=9 VOID LANTERN** — 34×44 floating lantern with a slit-pupil void core, hp 5.
- IDLE drift 140f (shards folded in). WELL 50f tell: rings shrink toward the core, inward streaks, low hum. ACTIVE 210f: soft gravity pull on the player (`pl.vx += HE.pull*falloff`, zero beyond 420px, weaker than player accel .9 so the player can always resist; small vy pull only when airborne) + ring of 4 orbiting shards at r≈86 (angular speed ±.045 rad/f) with ONE ~70° safe gap. Shards hurt on contact (r≈9); one star destroys a shard (re-forms after 90f). Dash i-frames pass through. COLLAPSE 40f: small implosion burst (telegraph ring, hurts within 40px), then RECOVER 120f: drops lower, dims, stomp-able. Killing it ends the pull instantly.

**t=10 STARMAW (mimic)** — 36×36, hp 3.
- Spawns **disguised as a stage-star pickup** on a platform ≥220px from the player and from every real star. It is an `E` entity, NEVER an `S` star, and never counts toward `need`/`nextStar`. Tells (tiny but learnable): ~8% warmer hue (`#ffb84a` vs `#ffd84d`), pulse period differs from the real star, no sparkle trail. Stars can hit it while disguised (shooting from range is the safe solution).
- Player within 110px → TREMBLE 22f (shake + teeth flicker) → CHOMP: 12f lunge (~70px) with a 56×40 mouth hitbox → stuck open 40f (free hits) → becomes a slow floating hunter firing a 5-shard fan (70° cone, `5.2*D.ps`) every 120f. Guaranteed power-up drop on kill.

## Fairness rules (from design research: telegraphing, no chain-stun, readable counterplay)
Every damaging attack has tell → active → recovery → counterplay → failure feedback. No unavoidable damage; no stacking of two control effects; root always leaves the player able to shoot and has immunity afterwards; heavy attacks never spawn on top of the player; difficulty comes from layering patterns, not from inflated HP/speed. Keep score/combo/xp flow via `kill()`.

## Tests (run what you can; do not claim untested results)
Headless browser smoke test with `localStorage aria_dif=2`: spawn each type via the debug hook; verify tell timing, root/mash/immunity, web destroyed by stars, Prism bounce path matches the frozen line, hound never leaps into pits, lantern pull is resistible, Starmaw never affects star collection. Also: Easy/Normal unchanged (no new types ever spawn), stage start/retry/death/clear/next-stage reset all new state, boss stages spawn no new types, pause/resume, no console errors, FX quality levels, mouse+keyboard (+touch if present).

## Final report (write it in Persian/Farsi)
(a) file produced, (b) behaviour changed, (c) functions/systems touched, (d) tests actually run + results, (e) known limitations and the first tuning knobs in `HE` to adjust after playtesting.

# Hadanion — Companion visual, behavior and performance TODO

**Status:** active canonical roadmap, consolidated 2026-10-09. **Owner:** `llocphann/Hadanion main` (actor/animation/renderer/native Companion). Hadalis `dev` owns the optional host, shared surfaces/theme/power and desktop services; **never modify Hadalis `stable`**. This file is the **only active visual/behavior task list**. For AI, persona, memory, local-model and permissions see [Local AI TODO](WULL_LOCAL_AI.md). Technical decisions: [Mochi × Mak1zu × Hadalis synthesis](../../docs/HADANION_COMPANION_SYNTHESIS_20261009.md), [renderer G0/G1 runbook](../../docs/HADANION_RENDERER_OPTIMIZATION_DECISION_20261008.md), [host API](../../docs/HADALIS_EXTRACTION.md).

**Historical cleanup:** The original 3,059-line imported Hadalis tracker (including pointer investigations, old dev/source SHA checkpoints, obsolete phase 0–5 roadmap and the earlier Mochi proposal) is preserved verbatim in [archive](../archive/ABYSS_WATER_DROPLET_COMPANION_PRE_CLEANUP_20261009.md). It is **retired for planning and status**. Do not execute old commands or treat historical dev SHAs or PASS labels as current Hadanion evidence. Git history also retains every change.

## Current production baseline (preserve)

- One optional Aqua/Octo 3D actor using Qt Quick/ShaderEffect, authored Blender motion curves (**30 each**), Aqua transparency/refraction, Octo four tentacles and 16 suction cups, Abyss theme, four-rim/registered-surface movement, touch/contact/reflection, face, gaze and animations.
- Cast transfer retains the **5.6-second** Octo grip/quicksand policy and only one visible actor. **Portal effects are for distant movement**, not ordinary appearance, cowork start or laptop opening.
- `WullPresence` owns movement/drag/peek/portal, `WullCuriosity` owns feature visits/leases, `WullMotion` owns clip sampling and the native semantic daemon remains deterministic. Do not introduce independent movement owners, GTK sprites, windows, duplicated popup frameworks, hidden renderers or broad pointer regions.
- Existing chat, Mood/Energy, reminder, persona and AI backend belong to [AI TODO](WULL_LOCAL_AI.md). The production shell and optional package remain default-off until enabled by the user. Source snippets/tests do not establish full physical acceptance.

## Current verified engineering status (not GPU acceptance)

- [x] **Repo-only G0 harness exists:** [dual-QSB shader A/A → negative → candidate](../../scripts/wull-shader-ab-sequence.py), [direct oracle](../../scripts/wull-shader-ab.py), offline proof controls and `qsb` build CI; source hashes are recorded.
- [x] **Repo-only G1 instruments exist:** [read-only PID CPU/RSS/PSS sampler](../../scripts/wull-g1-resource-sample.py) and [repeatable cohort comparison](../../scripts/wull-g1-compare.py). GPU times, VRAM, p95/p99 and power remain `NOT_MEASURED` until the correct local profiler captures them.
- [x] **Pure contextual behavior contract exists:** [`WullBehaviorDirector.js`](../../modules/abyss/companion/WullBehaviorDirector.js) with [offline tests](../../scripts/test-wull-behavior-director.cjs): anonymous allow-listed agent events, coarse app categories, deterministic priority, intro/loop/outro ownership tokens, 700 ms focus debounce, permission wait grace, bounded session expiry. **Not connected to the live actor**.
- [x] **Offline CI gate:** [Hadanion Actions #37821769236](https://github.com/llocphann/Hadanion/actions/runs/37821769236) completed both jobs at source `a456991ba56b5c97e5354c782ae8d592a4dc13d0` (Python/Node contracts, QML syntax, independent shader compilation). Docs-only subsequent commits do not retroactively change the tested source.
- [ ] **Physical G0 still OPEN:** prior local same-QSB A/A captured `INCONCLUSIVE_SELF_CONTROL` (exit 2) on `51873887` despite equal shader source and binary hashes; negative/A/B did **not** run. The revised oracle records twice-per-item RGBA, diff bounds and capture variance but **has not yet passed a fresh GPU trial**.
- [ ] **G1 real baseline still OPEN:** no measured GPU frame-time/VRAM/whole-shell p95/p99; no verified performance percent. No production E1 shader is authorized.
- [ ] **Full integration acceptance still OPEN:** `make test HADALIS_ROOT=/path/to/Hadalis`, relevant Hadalis host validator and real Niri/Quickshell four-edge/drag/overlay/suspend/hotplug tests on exact-source releases.

## P0 — Resolve renderer evidence before shader modifications

- [ ] Run [G0 sequence](../../docs/HADANION_RENDERER_OPTIMIZATION_DECISION_20261008.md#one-command-local-chatbot-qualification-preferred) from **clean** Hadanion checkout on actual Wayland GPU. Require **A/A pixel-identical, deliberate negative detectable and independently built candidate A/B**; inspect receipt + images; classify variance, not guess its cause. Never reuse a report from the older schema or turn `INCONCLUSIVE` into `PASS`.
- [ ] Collect [G1 baseline](../../docs/HADANION_RENDERER_OPTIMIZATION_DECISION_20261008.md#g1-tooling-preflight--read-only-resource-sampler-2026-10-09) on pinned Hadanion/Hadalis SHAs and identical hardware, backend, DPR and power policy: disabled, hidden, Aqua idle/move/pitch/fall, Octo idle/grip, cast, four rims, fullscreen and quality 0/1. Distinguish Companion-incremental from full-shell cost. Record actual p50/p95/p99 GPU frames, CPU time/wakeups, RSS/PSS, GPU allocation and power where available. Use AB/BA repetitions and a control/noise floor.
- [ ] Only after qualifying G0/G1: profile `WaterDropletMaterial.frag` (front/back interface and bubbles), `OctoTentacle.frag` geometry/normals/backface, and optionally shader specialization. First candidate is the isolated bubble-ray source; unchanged QSB/visuals do not imply a speedup. Reject regressions or noised-out gains; retain known-good renderer and all 60 authored clips.
- [ ] No 2D replacement or adaptive hybrid without **measured** failure of simpler 3D optimizations plus an explicit, separately approved image-quality/performance tradeoff. Hadalis-owned full-screen `AbyssField.frag` belongs in the [Hadalis optimization audit](https://github.com/llocphann/Hadalis/blob/dev/docs/optimization/STRICT_LOSSLESS_GPU_RAM_CPU_AUDIT.md).

## P0 — Native Hadalis event boundary and arbitration

- [x] Design a pure testable **semantic policy** (Behavior Director; tests above). It accepts only content-blind `none|terminal|editor|other` focus categories and `working|activity|needs_input|prompt_waiting|finished|ended` agent events with a bounded opaque 16-hex session token. No raw prompt, title, path, screenshot, keyboard event, URL or tool body.
- [ ] Design/implement an **explicitly opted-in, versioned, bounded host bridge**. Hadalis `dev` must own real semantic reduction/permissions and authenticated local transport; Hadanion must not add direct privileged polling or a new generic compositor hook. Reject unknown fields, stale/out-of-order events, untrusted senders, bridge restarts and disabled-state emissions. Missing/disabled sources fail silent.
- [ ] Integrate arbitration with **existing** native `inir-companiond`, `WullPresence`, `WullCuriosity` and `WullMotion`; establish exactly one visual-performance owner and epoch token. Priority: hidden/lock/game/fullscreen/security → direct chat/drag/modal → explicit motion/portal → opt-in cowork/context → idle. Context sessions do not own the entire character pose; canceled/late animation callbacks cannot reset new intent.
- [ ] Add owned-host fixtures for rapid focus switching, multi-agent concurrent hooks, 45-second permission grace, no celebration on short interrupted runs, session TTL, disconnect, hover/input pass-through, focus/quiet/reduced-motion, suspend/unload, multi-output routing and no orphan process/timer. Do not install hooks in user config automatically.

## P0 — First *new* observable animation: Aqua/Octo 3D laptop

- [ ] Author an original **single-actor 3D mini-computer** and both Aqua/Octo motions using the existing Blender/procedural pipeline, not copied Mochi sprites/art. It must rotate correctly on all four supporting edges; preserve face/eyes, Aqua liquid volume, Octo cups, Abyss palette, contact/reflection and visibility occlusion.
- [ ] Implement bounded `laptop_open → laptop_typing_loop|laptop_thinking_loop|laptop_agent_loop|laptop_pause → laptop_close` with optional brief success/alert; one action clock and explicit interruption. A transient terminal/editor focus must not restart the prop; drag/chat/portal/modal must yield immediately. **Do not mislabel existing `working` expression as a laptop clip.**
- [ ] Gate prop lifecycle by allowed desktop/agent semantic events and a user-controlled setting. Actor hidden/off means no animation or extra GPU demand. Do not show portal on laptop appearance or spawn another surface. Meet theme, fractional-DPR, four-rim/corner, overlay/hit-region, software quality, cast transitions and resource regression tests.
- [ ] Require full local Niri/Quickshell visual acceptance on **exact-source** Hadanion and Hadalis builds before marking the laptop complete.

## P1 — Add value after P0, not another full feature framework

- [ ] **Focus co-working** using Hadalis's existing timer/session; optional reading/book, coffee/sip and quiet thinking gestures. Do not duplicate timer state.
- [ ] **Ambient reactions** via permitted coarse MPRIS/idle/battery categories (sleep/wake, media, short dance, searching, gentle success/failure) with cooldown, opt-out and no raw content access. Existing expressions/animations come first; author only genuinely missing poses.
- [ ] **User-initiated Pocket** only after Wayland drag/drop and permissions are proven. Reuse Abyss/Vault interfaces; bounded metadata, original-file-safe, no unsolicited AI ingestion or file writes.
- [ ] **Non-punitive bond/dialogue** only after consent: no streak decay, guilt, false intimacy, personal surveillance or dependency. Mood, preference and optional familiarity must remain distinct. No direct import of upstream art, source, catchphrases or copyrighted identity.
- [ ] A small **authoring/regression matrix** for Blender clips, one-shot ownership, four rims, pointer handoff, and lifecycle. Defer catalogue/easter eggs/advanced props until functionality and cost are demonstrated.

## Acceptance and work discipline

1. **GitHub CI pass ≠ hardware proof.** Capture source SHAs, command, test exit, environment and evidence path; untested states remain OPEN. Keep candidate binaries and personal logs private. Run complete product/host tests before enabling a new visual feature.
2. Preserve deterministic behavior with AI unavailable; avoid model-driven motion control, automatic inference on desktop activity or surprise file access. Keep off/quiet/reduced-motion semantics and permission ownership in Hadalis.
3. Avoid task/roadmap duplication: update this file for visual behavior and [AI TODO](WULL_LOCAL_AI.md) for local model, memory, persona and actions. [Synthesis](../../docs/HADANION_COMPANION_SYNTHESIS_20261009.md) is a decision source; [archives](../archive/README.md) are frozen historical evidence, **not** active tickets.

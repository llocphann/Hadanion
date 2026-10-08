# Hadanion Companion — canonical work

| Active owner | Current checklist |
| --- | --- |
| Native Aqua/Octo visuals, event arbitration, Blender clips, G0/G1 | [Visual & Behavior TODO](ABYSS_WATER_DROPLET_COMPANION.md) |
| AI routes, output safety, model benchmarking, user-consented memory and tools | [Local AI TODO](WULL_LOCAL_AI.md) |

**Decision source:** [Hadanion synthesis](../../docs/HADANION_COMPANION_SYNTHESIS_20261009.md). **Technical runbooks:** [docs index](../../docs/README.md). **Old timelines:** [archived/imported work logs](../archive/README.md) (frozen, non-executable).

All new implementation status belongs in the relevant active TODO with exact-source CI/local evidence. Historical source SHAs are provenance, not a release test. Do not recreate the old 3,059-line visual timeline or the pre-extraction P0.5–P10 AI plan. Hadalis's optional host and generic AI remain owned by Hadalis `dev`; stable is never modified.


## Local chatbot execution contract (2026-10-09)

**Start here, then follow exactly one canonical TODO.** The local chatbot is an executor/tester, not the authority to change product requirements or user permission. A roadmap item is not automatically authorization to read private desktop content, alter user settings, register coding-agent hooks, install models, deploy, or run destructive commands.

### Preflight before each independently reviewable change

1. Confirm actual clean or deliberately documented working trees and pin **both** exact commits: Hadanion `main` and compatible Hadalis `dev`; compare installed Hadanion package and Git source if doing runtime tests. Preserve unrelated local changes; do not reset or overwrite them. Hadalis `stable` is immutable. Never make a test pass by removing assertions.
2. Read the selected TODO ticket, relevant `docs/` contract, source and its existing tests. Check source ownership. Hadalis owns the host/provider/compositor; Hadanion owns Companion code and optional package. Never add a second owner for IPC, input region, model supervisor, animation or portal.
3. For an engineering step, make the **smallest reversible diff**, first add/adjust an offline regression and preserve the prior known-good baseline. No hidden file reads, background AI, personal history/memory capture or cloud upload. If approval/desktop evidence is needed, prepare a fail-closed test fixture and mark the ticket `BLOCKED_LOCAL` instead of implementing an unapproved behavior.
4. Run focused affected tests; for local full verification: `make test HADALIS_ROOT=/absolute/path/to/Hadalis` from Hadanion root (this builds Rust 1.95+ workspace and runs the validator in a private host overlay). If Hadalis host code is touched, run its own maintainer tests on exact compatible `dev` source. A skipped check is not a pass; do not install/use a new system package merely to make a test run without user approval.
5. Report: **ticket ID; Hadanion SHA; Hadalis SHA; changed paths; exact commands; exit codes; count PASS/FAIL/SKIP; blocked dependency; local evidence file paths; rollback steps; next proposed ticket.** Keep private logs/desktop screenshots local unless explicitly shared, and pin source identities to every physical/GPU/AI claim. Only mark `[x]` when all acceptance conditions actually pass.

### Safe execution ordering and stop decisions

| Gate | Readiness | What the agent may do |
| --- | --- | --- |
| `PRE-0` — source and runtime test preflight | **READY**, local repo + host required | Inventory current manifests/imports/test entrypoints, verify a clean baseline and run focused/offline checks; report missing Qt/Rust/Wayland dependencies without changing system state |
| `VIS-G0` — real GPU A/A oracle | **READY_TO_ATTEMPT**, not passed | Run the existing one-command shader sequence in a new evidence directory; if `INCONCLUSIVE` or pixel difference, inspect saved images/receipts and prepare a focused oracle fix; **do not** approve E1 or lower pixel strictness |
| `VIS-G1` — CPU/PSS/GPU baseline | **PARTIAL**, user-visible state/PID + profiler needed | Read-only CPU/PSS sampler can run after verified state/UID/PID; GPU frame time/VRAM/p95/p99 cannot be inferred. Do not enable/disable features for samples without an approved, observable state procedure |
| `VIS-BRIDGE` — semantic event contract | **SOURCE-READY**, host permission not yet approved | Add versioned, synthetic JSON fixtures and tests for event ordering/priority and a disabled-by-default adapter proposal; **no live Niri tracking, hook registration or surprise popups** until permissions and integration acceptance are resolved |
| `VIS-LAPTOP` — new original 3D prop/animation | **DESIGN/STAGING**, real source assets and visual QA needed | Audit Blender authoring and build non-running fixtures/preview proposals; do not claim a working animation from a placeholder or start a second actor. Real rollout requires four-rim input/visual and GPU acceptance |
| `AI-OUTPUT` — response boundary regression | **READY**, offline first | Test both shared-QML and helper output paths, malformed JSON and persistent history guard; stage source-only fixes; real-model/host output remains an integration gate |
| `AI-VOICE` — Aqua/Octo quality | **FIXTURES READY**, approved pinned models not verified | Run 14 synthetic matched scenarios only when selected model/provider and local privacy policy are confirmed, then human-review; never use user chat dumps as a fixture |
| `AI-MEMORY` / `AI-PROACTIVE` | **DORMANT / APPROVAL REQUIRED** | Only synthetic contracts and UX/provenance proposals; **do not** connect SQLite memory, background inference, notifications, quiet hours, tool calls or data collection to production without explicit user approval |

**On a failure:** preserve `result.json`/exact exit status and the failed fixture, identify whether the failure belongs to test harness, code, host, permissions or missing environment. Fix only the supported cause, then rerun focused tests. If the cause cannot be established, stop that gate and progress an independent READY ticket instead of weakening it or retrying an indeterminate state-changing command.

**Required progress notation in the canonical TODO:** `READY`, `IN_PROGRESS`, `BLOCKED_LOCAL`, `BLOCKED_APPROVAL`, `FAILED_EVIDENCE`, or `QUALIFIED` with SHA/receipt. A `[x]` for tools means only the source/tool exists, not that the user-visible feature is complete.

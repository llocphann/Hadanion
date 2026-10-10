# Companion source work — Alis central queue

Task intake, triage, priority, status, release gates and archives for
**Alis-Companion** are maintained exclusively in
[the Alis dev task index](https://github.com/llocphann/Alis/blob/dev/to-do/README.md).
No standalone Companion task backlog is active.

This repository owns the actor/animation/renderer, Companion chat/client,
optional package and their tests. Alis owns generic AI/host/compositor
interfaces. Implementation proceeds against an Alis task ID, recording
compatible host SHA and Companion source SHA; avoid duplicate IPC/actor/
model/movement ownership. Report commands, exit status, PASS/FAIL/SKIP,
logs/evidence, blocked permission/hardware prerequisites and next step
to the **Alis task**, not here. Keep feature-disabled state unless the
user explicitly permits enablement.

Safety gates preserved from the earlier source workflow:
- No privileged installer, unexpected data capture, vault access, model
  download, background inference, agent hook or desktop sensor without
  specific user authorization.
- Only use exact-SHA, private/owned native Wayland/Qt/GPU tests; a mock,
  stale CI pass, Blender preview or inconclusive shader A/A is not
  visual/performance/real-model acceptance.
- Never weaken strict RGBA, skip required checks as PASS, rerun an
  indeterminate state-changing action or change quality to fake gains.
- Keep one visual actor/clock/host owner and preserve pointer and model
  lifecycle when Companion is disabled. Alis stable is untouched.

The prior full [local execution contract and priority table](https://github.com/llocphann/Alis-Companion/blob/732136ef65bb3c84d9339207210c955759a85b76/to-do/cloud-bot/README.md)
is archived by the immutable Git revision and can be consulted for
historical evidence only, not as a separate work queue.

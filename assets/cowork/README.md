# Original 3D laptop staging assets

These two editable Blender 4.3 scenes add eight **new** laptop performances per
character to copies of the original 30-action rigs. The shipped Aqua/Octo scenes,
60 motion exports and liquid shaders remain unchanged. The installer excludes
this directory; no desktop context source or live actor imports this bundle.

`AquaLaptopMotion.json` and `OctoLaptopMotion.json` contain the actual stored
LINEAR F-curve keys, not rendered sprites or a substitute `working` expression.
The shared phases are open, typing loop, thinking loop, agent loop, pause, close,
success and alert. Aqua reaches with exactly two hands; Octo reaches with two
of its four opaque tentacles, including their moving suction cups. A real hinge,
rounded shell, keyboard, trackpad and abstract screen form the original prop.
The preview-only 3D iris/catchlights follow the existing eye-closing drivers.

Re-author into a **new** output directory using the existing authoring cache:

```sh
uv run --offline --python 3.11 --with bpy==4.3.0 --with 'numpy<2' python scripts/companion-author-laptop.py --output /new/owned/bundle
node scripts/test-wull-laptop-motion.cjs
uv run --offline --python 3.11 --with bpy==4.3.0 --with 'numpy<2' python scripts/companion-verify-laptop.py --output /new/owned/proof --render
```

The verifier reopens both saved scenes, checks exported interpolation, alternating
keyboard contact, unchanged actor volume, four-rim parent transforms, opaque
Octo tentacles and complete prop removal after close. A fixed five-pose render
schedule supports visual inspection. The reflective studio disc is a preview
surface, not a desktop effect. Four-rim geometry is **not** Niri/input acceptance.

Runtime mesh/material integration, theme binding, interrupted motion ownership,
real four-rim visuals/input and GPU costs remain open in the canonical
[Companion TODO](../../to-do/cloud-bot/ABYSS_WATER_DROPLET_COMPANION.md). These
assets do not qualify original G0, strict lossless rendering, resource savings
or reference parity. No private model, desktop screenshot or vault is a fixture.

`CoworkPerformance.js` stages the presentation policy with the existing Behavior
Director and a caller-owned monotonic clock. Opening, looping, close and optional
bounded success/alert cues use epoch tokens. Drag/chat/modal/travel, cast change,
lock/fullscreen, off/quiet, reduced motion, unsupported placement and clock failure
release the prop immediately. Brief context changes use a one-second exit grace;
an interrupted opening reverses its current authored pose. Late or early finished
signals cannot restart an intro. Loop switches blend poses for 140 ms.

This library is a **synthetic staging contract**, not the live actor or an
authorization API. Only the permitted host owner may supply semantics and cues;
AI text cannot call it. No desktop event subscription, permanent timer, inference
or new window is created. Runtime integration still needs one explicit actor
owner and physical acceptance; the library does not authorize rollout.

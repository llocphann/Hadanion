# Hadanion

Aqua and Octo, expressive 3D desktop companions for [Hadalis](https://github.com/llocphann/Hadalis). Companion is an optional installation, disabled by default in Hadalis.

This repository owns the procedural liquid renderer, Blender models and motion curves, behavior daemon, expressions, movement, curiosity, alternating characters, orbital cloud actions, chat, check-ins and Companion settings. Hadalis supplies the Abyss surfaces, theme, shared AI transport, Obsidian/Todo integration and a small optional host adapter.

## Install

Use a Hadalis revision that provides Hadanion host API 1. Rust 1.95 or newer is required to build the native behavior daemon; rendering uses Hadalis's existing Quickshell/Qt environment. Blender is needed only for authoring.

```sh
git clone https://github.com/llocphann/Hadanion.git
cd Hadanion
make install
inir ipc hadanion refresh
```

Open **Settings → Companion** and enable Aqua or Octo. Existing Companion selections are preserved. **Super + Alt + Comma** retains its existing chat behavior. Installation does not download or load an LLM.

The runtime is installed to `${XDG_DATA_HOME:-$HOME/.local/share}/hadanion/releases/<commit>`. An atomic `current` link selects a release. The payload excludes Blender files, tests, documentation and models. Hadalis discovers this user installation without modifying its source tree or a system package.

## Update and remove

```sh
git pull --ff-only
make install
inir ipc hadanion refresh

make uninstall
inir ipc hadanion refresh
```

Uninstall detaches the runtime. Preferences, chat history, Obsidian notes and previous releases remain intact. No Hadalis updater installs Hadanion automatically. The `abyss.companion` / `abyss.companionMind` preferences, `wull` IPC target, transcript path and `inir-companiond` binary name remain compatible during extraction.

## Development

```sh
make build
make test HADALIS_ROOT=/path/to/Hadalis
```

Validation uses an isolated host checkout and fake inference fixtures; it does not modify the live desktop or call a real LLM. See the [documentation index](docs/README.md) for host API, extraction provenance, renderer runbooks and Mochi × Mak1zu × Hadalis decisions. **Only the [visual/behavior TODO](to-do/cloud-bot/ABYSS_WATER_DROPLET_COMPANION.md) and [AI TODO](to-do/cloud-bot/WULL_LOCAL_AI.md) are active**; [imported historical milestones](to-do/archive/README.md) and [retired research](docs/archive/README.md) are frozen archives, not current implementation instructions. Historical Hadalis evidence remains source-pinned and is not a test result for this repository.

License: GPL-3.0-or-later; imported source attribution is retained.

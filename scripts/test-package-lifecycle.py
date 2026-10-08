#!/usr/bin/env python3
"""Independent atomic install/update/remove on owned directories; preserve user data."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(os.environ.get("HADANION_SOURCE", Path(__file__).resolve().parents[1]))
spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory(prefix="hadanion-install-") as temporary:
    private = Path(temporary)
    source = private / "source"
    source.mkdir()
    for name in module.RUNTIME_DIRS:
        shutil.copytree(ROOT / name, source / name)
    for name in module.RUNTIME_FILES:
        p = source / name
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, p)
    subprocess.run(["git", "init", "-q", str(source)], check=True)
    def commit():
        subprocess.run(["git", "add", "--all"], cwd=source, check=True)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"], cwd=source, check=True)
    commit()
    binary = private / "native"
    binary.write_text("#!/bin/sh\nexit 0\n")
    binary.chmod(0o755)
    data = private / "data/hadanion"
    data.mkdir(parents=True)
    preferences = private / "config.json"
    preferences.write_bytes(b'{"enabled":true,"character":"octo"}\n')
    transcript = private / "chat.sqlite3"
    transcript.write_bytes(b"private fixture history")
    journal = private / "journal.md"
    journal.write_bytes(b"---\nmood: good\nenergy: high\n---\n")
    preserved = {p: p.read_bytes() for p in (preferences, transcript, journal)}
    first = module.install(data, source, binary)
    assert (data / "current").resolve() == first
    assert not (first / "assets").exists() and not (first / "scripts/test-package-lifecycle.py").exists()
    assert module.install(data, source, binary) == first
    untracked = source / "services/uncommitted.qml"
    untracked.write_text("import QtQuick\nItem {}\n")
    try:
        module.install(data, source, binary)
    except ValueError:
        pass
    else:
        raise AssertionError("untracked runtime source was published as an exact release")
    untracked.unlink()
    p = source / "manifest.json"
    payload = json.loads(p.read_text())
    payload["version"] = "0.1.1"
    p.write_text(json.dumps(payload))
    try:
        module.install(data, source, binary)
    except ValueError:
        pass
    else:
        raise AssertionError("dirty source was published as an exact release")
    commit()
    second = module.install(data, source, binary)
    assert second != first and first.exists() and (data / "current").resolve() == second
    module.activate(data, first)
    assert (data / "current").resolve() == first
    module.uninstall(data)
    module.uninstall(data)
    assert not (data / "current").exists() and first.exists() and second.exists()
    (data / "current").mkdir()
    try:
        module.activate(data, first)
    except ValueError:
        pass
    else:
        raise AssertionError("foreign directory was overwritten")
    assert all(path.read_bytes() == raw for path, raw in preserved.items())
print("PASS: exact releases, atomic update/rollback, default-off removal, foreign-path guard and user-data preservation")

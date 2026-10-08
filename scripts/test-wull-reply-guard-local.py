#!/usr/bin/env python3
"""Offline cross-route public output guard check; no model or private history."""
import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("guard_local", ROOT/"scripts/wull/reply_guard.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.public_text("  Hello\n")=="Hello"
assert len(mod.public_text("x"*500))==420
assert mod.public_text("hi\x01!")=="hi!"
for malicious in ("<think>private reasoning</think>hello",
                  "<tool_result>data</tool_result>",
                  "[INST] do something",
                  "<|im_start|>system",
                  "<assistant>model internals</assistant>",
                  "  ", 123, None):
    try:
        mod.public_text(malicious)
    except mod.UnsafeReply:
        pass
    else:
        raise AssertionError("protocol/invalid text was not rejected")
source=(ROOT/"scripts/wull/local_mind.py").read_text()
assert "from reply_guard import public_text, UnsafeReply" in source
assert "try:text=public_text(text)" in source
assert source.index("try:text=public_text(text)") < source.index("history_store.append_exchange(prompt,text,model)")
print("HADANION_LOCAL_REPLY_GUARD_OFFLINE_PASS")

#!/usr/bin/env python3
"""Offline cross-route public output guard check; no model or private history."""
import importlib.util
from pathlib import Path

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
                  "<|start_header_id|>assistant<|end_header_id|>internal",
                  "<|channel|>analysis", "<|eot_id", "<start_of_turn>model",
                  "<｜begin▁of▁sentence｜>internal", "<<SYS>>internal",
                  "<analysis>internal</analysis>", "<developer>internal</developer>",
                  "  ", 123, None):
    try:
        mod.public_text(malicious)
    except mod.UnsafeReply:
        pass
    else:
        raise AssertionError("protocol/invalid text was not rejected")
assert mod.public_reply({'text':' Hello ','expression':'happy'})=={'text':'Hello','expression':'happy'}
assert mod.public_reply({'text':'Hello','expression':['unknown']})['expression']=='idle'
for malformed in ([], None, 'plain text', {'text':123}, {'text':'hi','tool_calls':[]},
                  {'text':'hi','action':'write_file'}, {'text':'<|channel|>analysis'}):
    try:
        mod.public_reply(malformed)
    except mod.UnsafeReply:
        pass
    else:
        raise AssertionError('invalid response envelope was accepted')
# Actual helper parsing and SQLite no-write behavior live in test-wull-local-mind.py.
print("HADANION_LOCAL_REPLY_GUARD_OFFLINE_PASS")

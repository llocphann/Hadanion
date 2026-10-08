#!/usr/bin/env python3
"""Model-free opt-in memory test; temp DB only; no real home or history."""
import importlib.util
import os
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("memory_proto", ROOT/"scripts/wull/memory_store.py")
memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory)

with TemporaryDirectory(prefix="hadanion-memory-sandbox-") as tmp:
    dbfile = Path(tmp)/"private"/"memory.sqlite3"
    with patch.dict(os.environ,{"INIR_WULL_MEMORY_DB":str(dbfile)}):
        assert not dbfile.exists()
        try:
            memory.remember_confirmed("I enjoy tea","shared")
        except memory.MemoryError as e:
            assert "explicit_consent_required" in str(e)
        else:
            raise AssertionError("missing consent must reject before allocating DB")
        assert not dbfile.exists()
        common=memory.remember_confirmed("Tea is nice","shared",consent=True,now_ms=100)
        aqua=memory.remember_confirmed("Aqua joke","aqua",consent=True,now_ms=100)
        octo=memory.remember_confirmed("Octo joke","octo",consent=True,now_ms=100)
        expiry=memory.remember_confirmed("Old preference","shared",consent=True,now_ms=100,expires_ms=200)
        assert octo > aqua > common
        a=memory.list_visible("aqua",now_ms=201)
        o=memory.list_visible("octo",now_ms=201)
        assert {x["text"] for x in a}=={"Tea is nice","Aqua joke"}
        assert {x["text"] for x in o}=={"Tea is nice","Octo joke"}
        assert all(x["source"]=="explicit_user" for x in a+o)
        assert (dbfile.stat().st_mode & 0o777) == 0o600
        assert (dbfile.parent.stat().st_mode & 0o777) == 0o700
        assert memory.forget_one(aqua)
        assert not memory.forget_one(aqua)
        assert not any(x["text"]=="Aqua joke" for x in memory.list_visible("aqua",now_ms=201))
        for bad in ("", "\n", "a"*321, "line\nsecret"):
            try:
                memory.remember_confirmed(bad,"shared",consent=True)
            except memory.MemoryError:
                pass
            else:
                raise AssertionError("memory text invalid")
        for bad_scope in ("invalid", "user", "../octo"):
            try:
                memory.remember_confirmed("test",bad_scope,consent=True)
            except memory.MemoryError:
                pass
            else:
                raise AssertionError("untrusted scope")
        assert memory.forget_all()==3
        assert memory.list_visible("aqua",now_ms=201)==[]
        assert memory.list_visible("octo",now_ms=201)==[]
    # This is a DORMANT schema: code must not auto-wire a model or read a vault.
    src=(ROOT/"scripts/wull/memory_store.py").read_text()
    assert "consent is not True" in src
    assert "sqlite3.connect" in src
    assert "SELECT id,scope,text,source" in src
    helper=(ROOT/"scripts/wull/local_mind.py").read_text()
    assert "import memory_store" not in helper

print("HADANION_MEMORY_CONSENT_OFFLINE_CONTRACT_PASS")

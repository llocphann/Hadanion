"""DORMANT Hadanion opt-in memory-store prototype (not connected to AI/UI).

Stores *explicitly confirmed* short text only, scoped to Aqua/Octo/shared.
There is no automatic extraction, Obsidian access, prompt injection routing
or background inference. A future UI must provide inspect/delete consent.
"""
import os
from pathlib import Path
import sqlite3
import stat
import time

MAX_ITEMS = 128
MAX_TEXT = 320
SCOPES = ("shared", "aqua", "octo")
DB_VERSION = 1


class MemoryError(Exception):
    pass


def path():
    override = os.environ.get("INIR_WULL_MEMORY_DB")
    if override:
        return Path(override).expanduser()
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    return root / "inir/wull/memory.sqlite3"


def connect():
    target = path()
    try:
        parent = target.parent
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        pst = parent.lstat()
        if not stat.S_ISDIR(pst.st_mode) or pst.st_uid != os.getuid():
            raise MemoryError("unsafe_parent")
        os.chmod(parent, 0o700)
        if not target.exists():
            fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            os.close(fd)
        st = target.lstat()
        if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_nlink != 1:
            raise MemoryError("unsafe_database_file")
        os.chmod(target, 0o600)
        db = sqlite3.connect(target, timeout=1.5)
        db.execute("PRAGMA busy_timeout=1500")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA secure_delete=ON")
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, DB_VERSION):
            db.close()
            raise MemoryError("unknown_schema_version")
        db.execute("""CREATE TABLE IF NOT EXISTS memories(
            id INTEGER PRIMARY KEY,
            scope TEXT NOT NULL CHECK(scope IN ('shared','aqua','octo')),
            text TEXT NOT NULL CHECK(length(text) BETWEEN 1 AND 320),
            source TEXT NOT NULL CHECK(source='explicit_user'),
            created_ms INTEGER NOT NULL,
            expires_ms INTEGER NOT NULL DEFAULT 0
        )""")
        if version == 0:
            db.execute("PRAGMA user_version=1")
        db.commit()
        return db
    except MemoryError:
        raise
    except (OSError, sqlite3.Error) as exc:
        raise MemoryError("memory_open_failed") from exc


def remember_confirmed(text, scope, consent=False, expires_ms=0, now_ms=None):
    if consent is not True:
        raise MemoryError("explicit_consent_required")
    if scope not in SCOPES or not isinstance(text, str):
        raise MemoryError("invalid_memory_entry")
    value = text.strip()
    if not value or len(value) > MAX_TEXT or "\x00" in value or "\n" in value:
        raise MemoryError("invalid_memory_text")
    now = int(time.time()*1000) if now_ms is None else int(now_ms)
    if type(expires_ms) is not int or expires_ms < 0 or (expires_ms and expires_ms <= now):
        raise MemoryError("invalid_expiry")
    db = connect()
    try:
        with db:
            count = db.execute("SELECT count(*) FROM memories").fetchone()[0]
            if count >= MAX_ITEMS:
                raise MemoryError("memory_capacity_reached")
            cur = db.execute(
                "INSERT INTO memories(scope,text,source,created_ms,expires_ms) VALUES(?,?,?,?,?)",
                (scope, value, "explicit_user", now, expires_ms))
        return int(cur.lastrowid)
    except sqlite3.Error as exc:
        raise MemoryError("memory_write_failed") from exc
    finally:
        db.close()


def list_visible(character, now_ms=None, limit=12):
    if character not in ("aqua","octo") or type(limit) is not int or not 1<=limit<=32:
        raise MemoryError("invalid_memory_scope")
    now = int(time.time()*1000) if now_ms is None else int(now_ms)
    db = connect()
    try:
        rows = db.execute(
            "SELECT id,scope,text,source,created_ms,expires_ms FROM memories "
            "WHERE scope IN ('shared',?) AND (expires_ms=0 OR expires_ms>?) "
            "ORDER BY id DESC LIMIT ?", (character, now, limit)).fetchall()
        return [dict(id=x[0],scope=x[1],text=x[2],source=x[3],
                     created_ms=x[4],expires_ms=x[5]) for x in rows]
    except sqlite3.Error as exc:
        raise MemoryError("memory_read_failed") from exc
    finally:
        db.close()


def forget_one(memory_id):
    if type(memory_id) is not int or memory_id < 1:
        raise MemoryError("invalid_memory_id")
    db = connect()
    try:
        with db:
            changed = db.execute("DELETE FROM memories WHERE id=?", (memory_id,)).rowcount
        return changed == 1
    except sqlite3.Error as exc:
        raise MemoryError("memory_delete_failed") from exc
    finally:
        db.close()


def forget_all():
    """Delete logical records. OS backups/SSD remnants need separate handling."""
    db = connect()
    try:
        with db:
            changed = db.execute("DELETE FROM memories").rowcount
        db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        return changed
    except sqlite3.Error as exc:
        raise MemoryError("memory_delete_failed") from exc
    finally:
        db.close()

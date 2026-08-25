#!/usr/bin/env python3
"""ledger.py — the append-only task ledger: the write primitive and the projection.

WHAT THIS IS, AT ITS TRUE SIZE
──────────────────────────────
This does NOT make an in-turn prompt suggester better and it does not change what
is felt inside a single turn. What it ships is: the next turn, the next session
and the next worktree start from the COMPLETE set; a loss becomes auditable and
recoverable instead of invisible. Absence of a closing event means OPEN — dropping
an item requires an affirmative append.

THE FOUR PROPERTIES THAT ARE NOT NEGOTIABLE
───────────────────────────────────────────
1. APPEND ATOMICITY IS CONDITIONAL, so the conditions are code, not advice
   (`_append_bytes`): exactly ONE `os.write()` syscall per record, `O_APPEND` on
   every open, never a read-modify-write. MEASURED on macOS/APFS: 8 writers ×
   200 B, and 6 writers at 1 KB / 16 KB / 64 KB — 0 malformed lines in all four
   arms. Buffered IO and `print()` are FORBIDDEN on the append path because a
   flush mid-record breaks the very property that was measured.
   `[unverified — atomicity measured on macOS/APFS ≤64 KB only; Linux/ext4 CI
   runners and network filesystems unmeasured]` — `max_record_bytes` (8 KB) keeps
   the unmeasured region unreachable by construction.
   control: probe-append-atomicity.md, whose FIRST attempt failed in the
   instrument (multiprocessing `spawn` re-imported `<stdin>`; zero bytes were
   ever written concurrently) — recorded so the number is not misread.

2. PROJECTION ORDER IS read → SORT → DEDUPE → fold. NOT dedupe-then-sort.
   A git union merge leaves merged lines in arbitrary order and dedupes only
   BYTE-IDENTICAL ones, so the pairs that reach dedupe are same-id/different-byte
   pairs. Deduping before imposing a total order makes the survivor depend on
   file order: two machines render different Markdown from the same ledger and
   nothing reports it. The total order is (ts, event_id, sha256(canonical bytes));
   the third key is what makes it TOTAL. `--must-fail` plants exactly this bug.

3. NO CHECKPOINT. Measured: 50,000 events fold in ~257 ms. An incremental filter
   keyed on `ts > last_checkpoint` permanently and silently drops events that
   arrive OLDER than the checkpoint — which a union merge produces routinely (a
   sibling branch's work, merged today, timestamped last week). That is a
   dropped-item bug inside the anti-dropped-item mechanism.

4. A RECORD IS NEVER REWRITTEN IN PLACE. A status change is a NEW superseding
   event; a correction is a `redact` event; a late fact is a `provenance` event.

THREE ORTHOGONAL AXES, ONE STORAGE SITE EACH
────────────────────────────────────────────
`state` (4) × `resolution` (7) × `verification`. Verification is stored ONLY on
`verify` events. `awaiting_verification`, `blocked`, `dormant`, `stale` and
`open` are DERIVED — see `derive()`. `blocked` derives over `state != done`,
never over a subset. `confidence` is REFUSED: it is unfalsifiable and a later
reader treats "0.9" as verification.

THE GATE IS THREE-VALUED
────────────────────────
`check-enumeration` returns PASS / FAIL / **UNKNOWN**, and UNKNOWN BLOCKS. An
empty or unreadable ledger is UNKNOWN, never a green pass — a mechanism that
reports clean on an empty ledger is inert exactly when it is most needed.

EXIT CODES (this tool's own convention — tools in this repo differ; read each one)
─────────────────────────────────────────────────────────────────────────────────
    project / check       0 clean · 1 errors[] non-empty · 2 UNKNOWN
    check-enumeration     0 PASS · 1 FAIL · 2 UNKNOWN
    check-committable     0 canary held · 1 the ledger path IS ignored ·
                          2 the POSITIVE CONTROL did not fire (harness failure)
    append commands       0 written · 1 refused
    --self-test           0 pass · 1 fail
    --must-fail           0 when the TEETH BIT · 1 otherwise
⛔ `--must-fail` exits 0 on success here (premise-gate.py's convention).
`scripts/sync-plugin-versions.py` expects 2. There is no repo-wide convention.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import set_conservation as scp  # noqa: E402

EMITTER = "ledger.py@1.0.0"
SCHEMA_VERSION = 1
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
EVENT_SCHEMA_PATH = PLUGIN_ROOT / "templates" / "ledger" / "ledger-event.schema.json"
SCRUB_SH = PLUGIN_ROOT / "hooks" / "_scrub.sh"

CONFIG_REL = ".ravenclaude/ledger-config.json"
DEFAULT_CONFIG: dict[str, Any] = {
    "config_version": 1,
    "ledger_dir": ".ravenclaude/ledger",
    "view_path": "docs/pm/task-list.md",
    "brief_max_items": 12,
    "brief_max_bytes": 4096,
    "dormant_after_days": 90,
    "stale_days": 7,
    "aging_policy": "rollup",
    "max_record_bytes": 8192,
}

STATE_ORDINAL = {"in_progress": 0, "ready": 1, "proposed": 2, "done": 3}
ITEM_BEARING = ("open", "state", "verify", "link", "redact", "provenance")
CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

# Fields that are DERIVED and must never appear as stored asserted keys (G-LED-07).
DERIVED_NEVER_STORED = (
    "blocked",
    "awaiting_verification",
    "dormant",
    "stale",
    "age",
    "confidence",
    "cost",
    "effort_estimate",
)


class LedgerError(Exception):
    """A determinate refusal — maps to a non-zero, non-UNKNOWN exit."""


class LedgerUnknown(Exception):
    """The answer could not be determined. Maps to exit 2. NEVER downgraded."""


# ═════════════════════════════════════════════════════════════════════════════
# Config resolution
# ═════════════════════════════════════════════════════════════════════════════


def resolve_config(repo_root: Path) -> dict[str, Any]:
    """First hit wins: env (harness only) → config file → defaults.

    ⛔ A config file that EXISTS but does not parse is UNKNOWN and a hard stop.
    Falling through to the defaults would write the ledger to a second location
    and split the source of truth, silently.
    """
    config = dict(DEFAULT_CONFIG)
    if not (repo_root / "docs").is_dir():
        config["view_path"] = str(Path(config["ledger_dir"]) / "task-list.md")

    config_path = repo_root / CONFIG_REL
    if config_path.exists():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise LedgerUnknown(
                f"config_unparseable: {config_path} exists but does not parse ({exc}). This is UNKNOWN, "
                "not a fall-through to defaults — a mangled config that silently reverts "
                "splits the source of truth."
            )
        if not isinstance(loaded, dict):
            raise LedgerUnknown(f"config_unparseable: {config_path} is not a JSON object")
        config.update(loaded)
        config["_initialised"] = True
    else:
        config["_initialised"] = False

    env_dir = os.environ.get("RC_LEDGER_DIR")
    if env_dir:
        config["ledger_dir"] = env_dir
    env_view = os.environ.get("RC_LEDGER_VIEW")
    if env_view:
        config["view_path"] = env_view
    return config


def find_repo_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in [here] + list(here.parents):
        if (candidate / ".git").exists():
            return candidate
    return here


# ═════════════════════════════════════════════════════════════════════════════
# Scrub — ONE pattern list, read from the shell SSOT, not a fourth copy
# ═════════════════════════════════════════════════════════════════════════════

_POSIX_CLASSES = (
    ("[:space:]", r"\s"),
    ("[:digit:]", r"\d"),
    ("[:alnum:]", "a-zA-Z0-9"),
    ("[:alpha:]", "a-zA-Z"),
    ("[:upper:]", "A-Z"),
    ("[:lower:]", "a-z"),
)

PII_PATTERNS = (
    ("email", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+"),
    ("phone", r"\+[1-9]\d{7,14}"),
)


def _ere_to_python(pattern: str) -> str:
    for posix, replacement in _POSIX_CLASSES:
        pattern = pattern.replace(posix, replacement)
    return pattern


def load_secret_patterns(scrub_path: Path = SCRUB_SH) -> list[str]:
    """Read `_secret_patterns` out of hooks/_scrub.sh — the SSOT, not a copy.

    POSITIVE CONTROL: the loaded list must be non-trivial AND must actually match
    a known secret-shaped string. A silently-empty pattern list would make every
    scrub a no-op and every G-LED-06 assertion pass by being blind.
    """
    try:
        text = scrub_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LedgerUnknown(f"scrub_unreadable: {scrub_path}: {exc}")
    match = re.search(r"^_secret_patterns=\(\s*$(.*?)^\)\s*$", text, re.M | re.S)
    if not match:
        raise LedgerUnknown(
            f"scrub_unparseable: the _secret_patterns array in {scrub_path} did not parse. An empty "
            "pattern list makes every scrub a silent no-op."
        )
    patterns = [_ere_to_python(p) for p in re.findall(r"^\s*'([^']*)'\s*$", match.group(1), re.M)]
    if len(patterns) < 10:
        raise LedgerUnknown(
            f"scrub_unparseable: only {len(patterns)} pattern(s) parsed from {scrub_path} — expected >=10. "
            "Refusing to scrub with a near-empty list."
        )
    control = "ghp_" + "A" * 32
    if not any(re.search(p, control) for p in patterns):
        raise LedgerUnknown(
            "scrub_control_failed: the loaded patterns do not match a known secret-shaped "
            "control string. The loader is blind, so its clean result means nothing."
        )
    return patterns


_SECRET_CACHE: list[str] | None = None


def scrub(text: str) -> str:
    """Secrets first, then PII. Applied to every asserted string BEFORE append."""
    global _SECRET_CACHE
    if _SECRET_CACHE is None:
        _SECRET_CACHE = load_secret_patterns()
    result = text
    for pattern in _SECRET_CACHE:
        try:
            result = re.sub(pattern, "[REDACTED]", result)
        except re.error:
            # A pattern that will not compile in Python must never be treated as
            # "nothing matched" — that is a scrub failing toward clean.
            raise LedgerUnknown(f"scrub_pattern_uncompilable: {pattern!r}")
    for label, pattern in PII_PATTERNS:
        result = re.sub(pattern, f"[PII:{label}]", result)
    return result


def scrub_asserted(asserted: Any) -> Any:
    if isinstance(asserted, str):
        return scrub(asserted)
    if isinstance(asserted, list):
        return [scrub_asserted(v) for v in asserted]
    if isinstance(asserted, dict):
        return {k: scrub_asserted(v) for k, v in asserted.items()}
    return asserted


# ═════════════════════════════════════════════════════════════════════════════
# Identity
# ═════════════════════════════════════════════════════════════════════════════


def new_ulid(now_ms: int | None = None, rand: bytes | None = None) -> str:
    """26-char Crockford base32 ULID: 48-bit ms timestamp + 80 bits of randomness."""
    if now_ms is None:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    if rand is None:
        rand = secrets.token_bytes(10)
    value = (now_ms << 80) | int.from_bytes(rand, "big")
    out = []
    for _ in range(26):
        out.append(CROCKFORD[value & 0x1F])
        value >>= 5
    return "".join(reversed(out))


def mint_item_id(
    source: str,
    ts: str,
    subject: str,
    existing: Iterable[str],
    max_attempts: int = 8,
    nonce_factory=None,
) -> str:
    """rc- + 12 hex (48 bits) of sha256(source ‖ ts ‖ subject ‖ 64-bit nonce).

    12 hex at 10,000 items is ~1.8e-7 collision probability. But probability is
    not a guarantee, so the mint-time collision check is MANDATORY: re-roll the
    nonce on collision, at most `max_attempts`, then HARD FAIL. It never silently
    reuses an id.
    """
    taken = set(existing)
    factory = nonce_factory or (lambda: secrets.token_bytes(8))
    for _ in range(max_attempts):
        nonce = factory()
        payload = f"{source}\x00{ts}\x00{subject}\x00".encode() + nonce
        candidate = "rc-" + hashlib.sha256(payload).hexdigest()[:12]
        if candidate not in taken:
            return candidate
    raise LedgerError(
        f"item_id collision: {max_attempts} attempts all collided. Refusing to reuse an id — a silently "
        "reused id merges two items into one and the loss is invisible."
    )


# ═════════════════════════════════════════════════════════════════════════════
# The append primitive
# ═════════════════════════════════════════════════════════════════════════════


def canonical_bytes(record: dict[str, Any]) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def shard_for(ts: str) -> str:
    return ts[:7] + ".jsonl"


def _append_bytes(path: Path, data: bytes) -> None:
    """⛔ THE MEASURED CONTRACT, IN CODE.

    * ONE `os.write()` call for the whole record + its newline. A record
      assembled from several writes, or any buffered writer that may flush
      mid-record, breaks the atomicity that was measured.
    * `O_APPEND` on EVERY open. A seek-then-write loses the kernel's atomic
      offset update, and the file then tears under concurrency.
    * No read-modify-write anywhere: that is not an append and inherits none of
      this guarantee.
    """
    if data.count(b"\n") != 1 or not data.endswith(b"\n"):
        raise LedgerError("record must contain exactly one trailing newline")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        written = os.write(fd, data)
    finally:
        os.close(fd)
    if written != len(data):
        raise LedgerError(
            f"short write: {written} of {len(data)} bytes. A partial record is a torn line; the caller "
            "must not treat this as appended."
        )


def append_record(ledger_dir: Path, record: dict[str, Any], max_record_bytes: int) -> Path:
    data = canonical_bytes(record) + b"\n"
    if len(data) > max_record_bytes:
        raise LedgerError(
            f"record is {len(data)} B, over max_record_bytes={max_record_bytes}. The cap keeps every record an order "
            "of magnitude below the largest measured-safe append size."
        )
    path = ledger_dir / shard_for(record["machine"]["ts"])
    _append_bytes(path, data)
    return path


# ═════════════════════════════════════════════════════════════════════════════
# Machine block
# ═════════════════════════════════════════════════════════════════════════════


def _git(repo_root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git"] + list(args),
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", "replace").strip() or None


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"


def machine_block(repo_root: Path, actor: str, ts: str | None = None) -> dict[str, Any]:
    ts = ts or utcnow_iso()
    branch = _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")
    sha = _git(repo_root, "rev-parse", "--short", "HEAD")
    # ⛔ The worktree NAME, never an absolute path. An absolute path embeds an OS
    # username into a permanently retained committed artifact.
    worktree = repo_root.name
    return {
        "ts": ts,
        "source": "{}/{}/{}".format(repo_root.name, branch or "detached", sha or "unknown"),
        "actor": actor,
        "host": os.environ.get("RC_HOST", "claude-code"),
        "emitter": EMITTER,
        "branch": branch,
        "worktree": worktree,
        # null means NOT YET RESOLVED, never "no PR". A `provenance` event
        # supplies it after the merge; a guessed PR is worse than an em dash.
        "pr": None,
    }


# ═════════════════════════════════════════════════════════════════════════════
# Schema validation
# ═════════════════════════════════════════════════════════════════════════════


def load_validator():
    """Return a validator, or raise UNKNOWN. An absent validator is UNKNOWN, not PASS."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise LedgerUnknown(
            f"validator_unavailable: jsonschema is not importable ({exc}). An unvalidated "
            "ledger is UNKNOWN, never a pass."
        )
    try:
        schema = json.loads(EVENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LedgerUnknown(f"schema_unreadable: {EVENT_SCHEMA_PATH}: {exc}")
    validator = Draft202012Validator(schema)
    # POSITIVE CONTROL: a validator that accepts everything would make every
    # schema assertion pass by being dead.
    if validator.is_valid({"nonsense": True}):
        raise LedgerUnknown(
            "validator_control_failed: the validator accepted a known-bad object, so its "
            "clean verdicts mean nothing."
        )
    return validator


def validate_event(validator, record: dict[str, Any]) -> list[str]:
    return [
        "{}: {}".format("/".join(str(p) for p in e.absolute_path) or "<root>", e.message)
        for e in sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
    ]


# ═════════════════════════════════════════════════════════════════════════════
# Reading, sorting, deduping
# ═════════════════════════════════════════════════════════════════════════════


class RawRecord(NamedTuple):
    obj: dict[str, Any]
    raw: bytes
    sha: str
    file: str
    lineno: int


def parse_ts(ts: str) -> datetime:
    text = ts.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        raise LedgerError(f"unparseable timestamp {ts!r}")


def read_ledger(ledger_dir: Path) -> tuple[list[RawRecord], list[dict[str, Any]], int]:
    """READ every shard in sorted filename order. A line that fails to parse is
    recorded as an error and NEVER skipped. Returns (records, errors, lines_seen).
    """
    records: list[RawRecord] = []
    errors: list[dict[str, Any]] = []
    lines_seen = 0
    if not ledger_dir.is_dir():
        raise LedgerUnknown(f"ledger_dir_absent: {ledger_dir} does not exist")
    for shard in sorted(ledger_dir.glob("*.jsonl")):
        try:
            blob = shard.read_bytes()
        except OSError as exc:
            raise LedgerUnknown(f"shard_unreadable: {shard}: {exc}")
        for lineno, raw in enumerate(blob.split(b"\n"), start=1):
            if lineno == len(blob.split(b"\n")) and raw == b"":
                continue  # the trailing newline, not a line
            lines_seen += 1
            if raw.strip() == b"":
                errors.append(
                    {"kind": "malformed_line", "file": shard.name, "lineno": lineno,
                     "detail": "blank line (jsonlines forbids them)"}
                )
                continue
            try:
                obj = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError) as exc:
                errors.append(
                    {"kind": "malformed_line", "file": shard.name, "lineno": lineno,
                     "detail": str(exc)}
                )
                continue
            if not isinstance(obj, dict):
                errors.append(
                    {"kind": "malformed_line", "file": shard.name, "lineno": lineno,
                     "detail": "line is not a JSON object"}
                )
                continue
            records.append(
                RawRecord(obj, raw, hashlib.sha256(raw).hexdigest(), shard.name, lineno)
            )
    return records, errors, lines_seen


def total_order_key(record: RawRecord) -> tuple[str, str, str]:
    """(ts, event_id, sha256(canonical bytes)).

    ⛔ The THIRD key is what makes the order TOTAL. Two records sharing a ts AND
    an event_id is exactly the same-id/different-bytes pair a union merge is
    measured to produce; without the sha the survivor would depend on file order.
    ⛔ FILE ORDER IS NEVER USED — a union merge leaves lines in arbitrary order.
    """
    obj = record.obj
    machine = obj.get("machine") or {}
    return (str(machine.get("ts", "")), str(obj.get("event_id", "")), record.sha)


def sort_then_dedupe(
    records: Sequence[RawRecord], _broken_dedupe_first: bool = False
) -> tuple[list[RawRecord], list[dict[str, Any]]]:
    """⛔ SORT, THEN DEDUPE. `_broken_dedupe_first` exists only for `--must-fail`,
    which plants the inverted order and requires the suite to redden."""
    errors: list[dict[str, Any]] = []

    def dedupe(seq: Sequence[RawRecord]) -> list[RawRecord]:
        kept: dict[str, RawRecord] = {}
        out: list[RawRecord] = []
        for record in seq:
            event_id = str(record.obj.get("event_id", ""))
            if event_id in kept:
                first = kept[event_id]
                if first.sha != record.sha:
                    errors.append(
                        {
                            "kind": "event_id_collision",
                            "event_id": event_id,
                            "kept_sha": first.sha,
                            "dropped_sha": record.sha,
                            "detail": "two records share one event_id and differ in their "
                            "bytes; git union dedupes only byte-identical lines, so this "
                            "pair reached the projector by construction",
                        }
                    )
                continue
            kept[event_id] = record
            out.append(record)
        return out

    if _broken_dedupe_first:
        return sorted(dedupe(records), key=total_order_key), errors
    return dedupe(sorted(records, key=total_order_key)), errors


# ═════════════════════════════════════════════════════════════════════════════
# Fold + derive
# ═════════════════════════════════════════════════════════════════════════════

REDACTED_MARK = "[redacted:{0}]"


def fold(
    records: Sequence[RawRecord], errors: list[dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Fold the ordered, deduped events into per-item state. Returns
    (items, non_item_events, unrecognized)."""
    redacted_targets: dict[str, str] = {}
    for record in records:
        if record.obj.get("type") == "redact":
            asserted = record.obj.get("asserted") or {}
            target = asserted.get("redacts")
            if target:
                redacted_targets[str(target)] = str(asserted.get("reason_class", "wrong_content"))

    items: dict[str, dict[str, Any]] = {}
    non_item: list[dict[str, Any]] = []
    unrecognized: list[dict[str, Any]] = []

    for record in records:
        obj = record.obj
        etype = obj.get("type")
        machine = obj.get("machine") or {}
        ts = str(machine.get("ts", ""))
        asserted = obj.get("asserted") or {}
        event_id = str(obj.get("event_id", ""))

        if event_id in redacted_targets:
            asserted = {
                k: REDACTED_MARK.format(redacted_targets[event_id]) for k in asserted
            }

        if etype in ("bridge_health", "ledger_init"):
            non_item.append(obj)
            continue

        item_id = obj.get("item_id")
        if etype not in ITEM_BEARING:
            unrecognized.append(
                {"reason": "unrecognized event type", "value": etype, "event_id": event_id,
                 "item_id": item_id, "ts": ts}
            )
            continue
        if not isinstance(item_id, str):
            errors.append({"kind": "orphan_event", "event_id": event_id,
                           "detail": "item-bearing event with no item_id"})
            continue

        if etype == "open":
            if item_id in items:
                # A second `open` for one item is not fatal; the first mints
                # identity and the later one is recorded, never silently merged.
                errors.append({"kind": "duplicate_open", "item_id": item_id,
                               "event_id": event_id})
                continue
            items[item_id] = {
                "item_id": item_id,
                "subject": asserted.get("subject", ""),
                "owner": asserted.get("owner"),
                "priority": asserted.get("priority", 3),
                "tags": list(asserted.get("tags") or []),
                "due": asserted.get("due"),
                "state": "proposed",
                "resolution": None,
                "verification": "unverified",
                "verified_by": None,
                "evidence": [],
                "blocked_on": [],
                "cleared_refs": [],
                "provenance": [],
                "pr": None,
                "merge_commit": None,
                "also_shipped_in": [],
                "first_ts": ts,
                "last_event_ts": ts,
                "worktree": machine.get("worktree"),
                "state_events": 0,
            }
            continue

        item = items.get(item_id)
        if item is None:
            errors.append(
                {"kind": "orphan_event", "item_id": item_id, "event_id": event_id,
                 "detail": "no `open` event mints this item_id"}
            )
            continue

        item["last_event_ts"] = ts
        if machine.get("pr") is not None and etype != "provenance":
            item["pr"] = machine["pr"]

        if etype == "state":
            state = asserted.get("state")
            if state not in STATE_ORDINAL:
                unrecognized.append(
                    {"reason": "unrecognized state", "value": state, "event_id": event_id,
                     "item_id": item_id, "ts": ts}
                )
                continue
            prev = asserted.get("prev_state")
            if prev is not None and prev != item["state"]:
                # LAST-WRITE-WINS, but DETECTED. No lock — and no lost update
                # that is also invisible.
                errors.append(
                    {"kind": "divergence", "item_id": item_id, "event_id": event_id,
                     "detail": "asserted prev_state {!r} != folded state {!r}; continuing "
                     "with the later-ts event as the winner".format(prev, item["state"])}
                )
            item["state"] = state
            item["state_events"] += 1
            if state == "done":
                item["resolution"] = asserted.get("resolution")
                for key in ("superseded_by", "split_into", "decided_by", "decided_on",
                            "reverted_by", "attempts"):
                    if key in asserted:
                        item[key] = asserted[key]
            if asserted.get("evidence"):
                item["evidence"] += [e for e in asserted["evidence"] if e]
            if machine.get("worktree"):
                item["worktree"] = machine["worktree"]

        elif etype == "verify":
            verification = asserted.get("verification")
            if verification not in ("self_verified", "independently_verified",
                                    "verification_failed"):
                unrecognized.append(
                    {"reason": "unrecognized verification", "value": verification,
                     "event_id": event_id, "item_id": item_id, "ts": ts}
                )
                continue
            item["verification"] = verification
            item["verified_by"] = asserted.get("verified_by")
            item["evidence"] += [e for e in (asserted.get("evidence") or []) if e]

        elif etype == "link":
            op = asserted.get("op")
            ref = normalise_ref(asserted.get("ref", ""))
            if op == "add":
                if ref not in item["blocked_on"]:
                    item["blocked_on"].append(ref)
            elif op == "clear":
                item["cleared_refs"].append(ref)
                if ref in item["blocked_on"]:
                    item["blocked_on"].remove(ref)
            else:
                unrecognized.append(
                    {"reason": "unrecognized link op", "value": op, "event_id": event_id,
                     "item_id": item_id, "ts": ts}
                )

        elif etype == "provenance":
            item["provenance"].append(
                {"pr": machine.get("pr"), "merge_commit": machine.get("merge_commit"),
                 "merged_at": machine.get("merged_at")}
            )

        elif etype == "redact":
            pass  # already applied above; the event itself carries no item state

    # provenance fold rule: FIRST wins — the merge that shipped it.
    for item in items.values():
        if item["provenance"]:
            item["pr"] = item["provenance"][0]["pr"]
            item["merge_commit"] = item["provenance"][0]["merge_commit"]
            item["also_shipped_in"] = [p["pr"] for p in item["provenance"][1:]]

    return items, non_item, unrecognized


def normalise_ref(ref: str) -> str:
    """`ext:` slugs are normalised AT WRITE AND READ, so `add` and `clear` cannot
    diverge on casing or whitespace."""
    if not ref.startswith("ext:"):
        return ref
    parts = ref.split(":", 2)
    if len(parts) != 3:
        return ref
    slug = re.sub(r"[^a-z0-9]+", "-", parts[2].strip().lower()).strip("-")[:48]
    return f"ext:{parts[1].strip().lower()}:{slug}"


def _levenshtein(a: str, b: str, cap: int = 3) -> int:
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(
                min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb))
            )
        previous = current
    return previous[-1]


def derive(
    items: dict[str, dict[str, Any]], now: datetime, config: dict[str, Any]
) -> list[dict[str, Any]]:
    """⛔ EVERY value here is DERIVED and none of it is ever stored. Storing any
    of it is two hand-maintained copies of one fact."""
    warnings: list[dict[str, Any]] = []
    for item in items.values():
        state = item["state"]
        resolution = item["resolution"]
        verification = item["verification"]

        unresolved = []
        for ref in item["blocked_on"]:
            if ref.startswith("rc-"):
                target = items.get(ref)
                if target is None or target["state"] != "done":
                    unresolved.append(ref)
            else:
                unresolved.append(ref)

        # ⛔ over `state != done`, NEVER over a subset. An item can be blocked in
        # any non-terminal state, and narrowing the domain silently exempts some.
        item["blocked"] = state != "done" and bool(unresolved)
        item["unresolved_blockers"] = unresolved
        item["awaiting_verification"] = (
            state == "done" and resolution == "completed" and verification == "unverified"
        )
        item["open"] = (
            state != "done"
            or verification == "verification_failed"
            or item["awaiting_verification"]
        )
        age_days = (now - parse_ts(item["last_event_ts"])).days
        item["age_days"] = age_days
        item["stale"] = age_days > int(config["stale_days"])
        item["dormant"] = item["open"] and age_days > int(config["dormant_after_days"])
        item["pr_unresolved"] = state == "done" and item["pr"] is None
        item["needs_reopen"] = resolution == "reverted" and not item.get("superseded_by")

        for cleared in item["cleared_refs"]:
            for still in unresolved:
                if cleared != still and _levenshtein(cleared, still) <= 2:
                    warnings.append(
                        {"kind": "probable_typo", "item_id": item["item_id"],
                         "cleared": cleared, "still_blocked_on": still,
                         "detail": "a clear at Levenshtein distance <=2 from a still-unresolved "
                         "blocker — probably a typo, surfaced rather than left silent"}
                    )
    return warnings


# ═════════════════════════════════════════════════════════════════════════════
# Referential integrity + derived-not-stored
# ═════════════════════════════════════════════════════════════════════════════

RESOLUTION_COMPANIONS = {
    "superseded_by": ("superseded_by",),
    "split_into": ("split_into",),
    "descoped": ("decided_by", "decided_on"),
    "obsolete_upstream": ("evidence",),
    "reverted": ("reverted_by",),
    "failed": ("attempts", "evidence"),
    "completed": (),
}


def _asserted_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _asserted_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _asserted_strings(item)


def scan_asserted_for_leaks(record: RawRecord) -> list[dict[str, Any]]:
    """G-LED-06 read-side backstop: a secret or PII shape that survived the write.

    ⛔ The write path scrubs (`scrub_asserted`), so a survivor here means the
    record did NOT come through this writer — a hand-crafted Write, an import,
    or a merge from a branch running an older version. Scrubbing on write and
    NOT re-scanning on read would make the gate trust its own authorship, which
    is exactly the residual-trust gap §4.2 states honestly: `Write` is not a CLI
    flag, and no hook authenticates authorship.

    The finding names the CLASS, never the matched text — this list is rendered
    into the Markdown view and read back into a brief.
    """
    findings: list[dict[str, Any]] = []
    asserted = record.obj.get("asserted") or {}
    try:
        patterns = load_secret_patterns()
    except LedgerUnknown:
        # A scanner that cannot load its patterns must not report "clean".
        return [
            {
                "kind": "scan_unavailable",
                "event_id": record.obj.get("event_id"),
                "detail": "the secret-pattern list could not be loaded; this record is "
                "UNSCANNED, which is not the same as clean",
            }
        ]
    for text in _asserted_strings(asserted):
        for pattern in patterns:
            if re.search(pattern, text):
                findings.append(
                    {
                        "kind": "secret_in_asserted",
                        "event_id": record.obj.get("event_id"),
                        "file": record.file,
                        "lineno": record.lineno,
                        "detail": "an asserted string matches a secret shape and was NOT "
                        "scrubbed — this record did not come through ledger.py's write "
                        "path. Rotate the credential FIRST; a redact event does not erase "
                        "it, because git history keeps the bytes.",
                    }
                )
                break
        else:
            for label, pattern in PII_PATTERNS:
                if re.search(pattern, text):
                    findings.append(
                        {
                            "kind": "pii_in_asserted",
                            "event_id": record.obj.get("event_id"),
                            "file": record.file,
                            "lineno": record.lineno,
                            "pii_class": label,
                            "detail": f"an asserted string carries a {label} shape and was NOT "
                            "scrubbed. The ledger is a permanently retained committed "
                            "artifact; it cannot erase.",
                        }
                    )
                    break
    return findings


def check_integrity(
    records: Sequence[RawRecord], items: dict[str, dict[str, Any]],
    max_record_bytes: int = 8192,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    for record in records:
        errors += scan_asserted_for_leaks(record)
        # G-LED-14 read side. The write path refuses an oversize record, but a
        # record can reach a shard from a merge or an older writer, and the cap
        # is what keeps every record inside the MEASURED-safe append region.
        if len(record.raw) + 1 > max_record_bytes:
            errors.append(
                {
                    "kind": "oversize_record",
                    "event_id": record.obj.get("event_id"),
                    "file": record.file,
                    "lineno": record.lineno,
                    "detail": f"record is {len(record.raw) + 1} B, over max_record_bytes={max_record_bytes} — outside the "
                    "measured-safe append size band",
                }
            )
        asserted = record.obj.get("asserted") or {}
        if not isinstance(asserted, dict):
            continue
        for field in DERIVED_NEVER_STORED:
            if field in asserted:
                errors.append(
                    {"kind": "derived_field_stored", "event_id": record.obj.get("event_id"),
                     "field": field, "detail": _g_led_07_message(record.obj, field)}
                )
        if record.obj.get("type") == "state" and asserted.get("state") in (
            "blocked", "awaiting_verification"
        ):
            errors.append(
                {"kind": "derived_field_stored", "event_id": record.obj.get("event_id"),
                 "field": "state=" + str(asserted.get("state")),
                 "detail": _g_led_07_message(record.obj, str(asserted.get("state")))}
            )

    for item_id, item in sorted(items.items()):
        resolution = item["resolution"]
        if item["state"] == "done" and resolution is None:
            errors.append({"kind": "missing_resolution", "item_id": item_id,
                           "detail": "state=done with no resolution"})
            continue
        for companion in RESOLUTION_COMPANIONS.get(resolution or "", ()):
            value = item.get(companion)
            if not value:
                errors.append(
                    {"kind": "missing_companion", "item_id": item_id, "resolution": resolution,
                     "detail": f"resolution {resolution!r} requires a typed, gate-checked {companion!r}; "
                     "a relationship resolution with no target id is INVALID"}
                )
        target = item.get("superseded_by")
        if target and target not in items:
            errors.append({"kind": "dangling_ref", "item_id": item_id, "ref": target,
                           "detail": "superseded_by names an item that does not exist"})
        children = item.get("split_into") or []
        if resolution == "split_into":
            if len(children) < 2:
                errors.append({"kind": "split_too_small", "item_id": item_id,
                               "detail": "split_into needs >=2 members or the conservation "
                               "arithmetic silently loses scope"})
            for child in children:
                if child not in items:
                    errors.append({"kind": "dangling_ref", "item_id": item_id, "ref": child,
                                   "detail": "split_into names an item that does not exist"})
        for ref in item["blocked_on"]:
            if ref.startswith("rc-") and ref not in items:
                errors.append({"kind": "dangling_ref", "item_id": item_id, "ref": ref,
                               "detail": "blocked_on names an item that does not exist"})
        if (
            item["verification"] == "independently_verified"
            and item.get("verified_by")
            and item.get("verified_by") == item.get("owner")
        ):
            errors.append({"kind": "self_independent_verification", "item_id": item_id,
                           "detail": "independently_verified requires verified_by != the actor"})

    # supersede cycles
    for item_id in sorted(items):
        seen = set()
        cursor = item_id
        while cursor in items:
            target = items[cursor].get("superseded_by")
            if not target:
                break
            if target in seen or target == item_id:
                errors.append({"kind": "supersede_cycle", "item_id": item_id,
                               "detail": "superseded_by forms a cycle through " + str(target)})
                break
            seen.add(target)
            cursor = target
    return errors


def _g_led_07_message(obj: dict[str, Any], field: str) -> str:
    """⛔ The rejection must be a RUNNABLE COMMAND, not a description of one.
    A gate whose message is a description is the shape that produced five
    consecutive blocks to change one regex."""
    item_id = obj.get("item_id") or "rc-<item>"
    return (
        f"G-LED-07: `{field}` is derived and cannot be stored.\n"
        "Run exactly this:\n"
        f"  rc ledger link --item {item_id} --add \"ext:owner-decision:<slug>\"\n"
        "(classes: owner-decision|upstream|vendor|external-run|migration|access)"
    )


# ═════════════════════════════════════════════════════════════════════════════
# Projection
# ═════════════════════════════════════════════════════════════════════════════


class Projection(NamedTuple):
    items: dict[str, dict[str, Any]]
    errors: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    unrecognized: list[dict[str, Any]]
    scp_block: dict[str, Any]
    markdown: str
    verdict: str
    parsed_records: int
    now: datetime


def default_basis(ledger_dir: Path) -> str:
    """`ledger:<last two path components>` — NEVER an absolute path.

    ⛔ This was a real defect, caught by the order-independence test rather than
    by review: the basis used to be the ABSOLUTE ledger dir. Two consequences,
    and the second is the one that bites quietly.

    1. It embeds an OS username into `open-set.json`, which is a COMMITTED,
       permanently-retained artifact — the same leak `machine.worktree` stores a
       NAME to avoid. git history cannot un-say it.
    2. It makes the projection machine-dependent. Two checkouts of the same
       ledger produce different `basis` bytes, so the committed view and a fresh
       regeneration differ for a reason that has nothing to do with the ledger —
       which is exactly the freshness-gate-red-forever failure the semantic
       compare exists to prevent, arriving from the other direction.

    A caller that knows the repo root should pass an explicit repo-relative
    basis (with a git sha) instead of relying on this.
    """
    parts = ledger_dir.parts[-2:] if len(ledger_dir.parts) >= 2 else ledger_dir.parts
    return "ledger:" + "/".join(parts)


def project(
    ledger_dir: Path,
    config: dict[str, Any],
    now: datetime | None = None,
    validator: Any | None = None,
    basis: str = "",
    _broken_dedupe_first: bool = False,
) -> Projection:
    """Pure function of (ledger bytes, now).

    `now` is an EXPLICIT parameter defaulting to the newest event's ts, so the
    projection is a function of the ledger alone. A wall-clock `now` is a hidden
    input, and a determinism test over it passes only because two runs happened
    seconds apart.
    """
    records, errors, _lines = read_ledger(ledger_dir)
    parsed = len(records)

    ordered, dedupe_errors = sort_then_dedupe(records, _broken_dedupe_first)
    errors += dedupe_errors

    if validator is not None:
        for record in ordered:
            for problem in validate_event(validator, record.obj):
                errors.append(
                    {"kind": "schema_violation", "event_id": record.obj.get("event_id"),
                     "file": record.file, "lineno": record.lineno, "detail": problem}
                )

    items, non_item, unrecognized = fold(ordered, errors)

    if now is None:
        stamps = [str((r.obj.get("machine") or {}).get("ts", "")) for r in ordered]
        stamps = [s for s in stamps if s]
        now = parse_ts(max(stamps)) if stamps else datetime.now(timezone.utc)

    warnings = derive(items, now, config)
    errors += check_integrity(ordered, items, int(config["max_record_bytes"]))

    open_ids = sorted(i["item_id"] for i in items.values() if i["open"])
    computed_at = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    non_dormant_open = [i for i in items.values() if i["open"] and not i["dormant"]]
    cap = int(config["brief_max_items"])
    truncated = len(non_dormant_open) > cap

    scp_block = scp.build_block(
        "open_items",
        open_ids,
        basis or default_basis(ledger_dir),
        computed_at,
        coverage={"events_parsed": parsed, "items": len(items), "non_item_events": len(non_item)},
        truncated=truncated,
    )

    if parsed == 0:
        verdict = "UNKNOWN"
    elif errors:
        verdict = "FAIL"
    else:
        verdict = "PASS"

    markdown = render(items, scp_block, errors, warnings, unrecognized, config, now, verdict)
    return Projection(items, errors, warnings, unrecognized, scp_block, markdown, verdict,
                      parsed, now)


# ═════════════════════════════════════════════════════════════════════════════
# Render
# ═════════════════════════════════════════════════════════════════════════════

COLUMNS = ("ID", "Task", "Owner", "Due", "Priority", "State", "Resolution", "Verification",
           "PR", "Worktree", "Evidence", "Last update")


def _cell(value: Any) -> str:
    if value is None or value == "" or value == []:
        return "—"
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value).replace("|", "\\|")


def _display_state(item: dict[str, Any]) -> str:
    """Read vocabulary (blocked / awaiting verification) over WRITE vocabulary
    (the 4 stored states). The view shows the derivation; the gate refuses it."""
    parts = [item["state"]]
    if item["blocked"]:
        parts.append("⛔blocked")
    if item["awaiting_verification"]:
        parts.append("⚠ done, unverified")
    if item["verification"] == "verification_failed":
        parts.append("⚠ verification_failed")
    if item["dormant"]:
        parts.append("dormant")
    elif item["stale"]:
        parts.append("stale")
    return " · ".join(parts)


def _row(item: dict[str, Any]) -> str:
    return "| " + " | ".join(
        [
            item["item_id"],
            _cell(item["subject"]),
            _cell(item["owner"]),
            _cell(item["due"]),
            _cell(item["priority"]),
            _display_state(item),
            _cell(item["resolution"]),
            _cell(item["verification"]),
            _cell(item["pr"]),
            _cell(item["worktree"]),
            _cell(item["evidence"]),
            _cell(item["last_event_ts"]),
        ]
    ) + " |"


def _as_priority(value: Any) -> int:
    """Coerce a priority to a sortable int WITHOUT dropping the row.

    ⛔ A redacted item's `asserted` fields are all blanked to `[redacted:<class>]`,
    so `priority` is legitimately a non-integer after a redact event. An `int()`
    here raised and took the whole render down — and a renderer that dies on a
    valid ledger is a worse dropped-item bug than the one it renders. Unsortable
    priorities sort LAST rather than vanishing; nothing is ever skipped.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return 9


def _sorted_items(values: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        values,
        key=lambda i: (
            _as_priority(i.get("priority")),
            STATE_ORDINAL.get(i["state"], 9),
            i["item_id"],
        ),
    )


def _truncation_block(shown: int, full_ids: list[str], pointer: str, set_kind: str) -> list[str]:
    """⛔ Truncation is NEVER silent. Count + digest + pointer + a machine-readable
    marker, in that order. A truncated list read as a complete one is a measured
    defect, so the marker is mandatory and its absence is a gate failure."""
    digest = scp.compute_digest(set_kind, full_ids)
    return [
        "",
        f"⚠ RENDER TRUNCATED — {len(full_ids) - shown} of {len(full_ids)} not shown. digest {digest}",
        f"Full set: `{pointer}`",
    ]


def render(
    items: dict[str, dict[str, Any]],
    scp_block: dict[str, Any],
    errors: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    unrecognized: list[dict[str, Any]],
    config: dict[str, Any],
    now: datetime,
    verdict: str,
) -> str:
    lines: list[str] = [
        "# Task ledger — generated view",
        "",
        "<!-- GENERATED by ledger.py project. Do NOT hand-edit: regeneration overwrites, and",
        "     the freshness gate compares this file to a fresh projection. -->",
        "",
        f"- as of: `{now.astimezone(timezone.utc).isoformat()}`",
        "- basis: `{}`".format(scp_block["basis"]),
        "- open-set digest: `{}`".format(scp_block["digest"]),
        f"- verdict: **{verdict}**",
        "",
    ]

    open_items = [i for i in items.values() if i["open"]]
    dormant = [i for i in open_items if i["dormant"]]
    active = _sorted_items([i for i in open_items if not i["dormant"]])
    cap = int(config["brief_max_items"])
    shown = active[:cap]

    lines.append(
        "## Open — {} items · digest `{}` · showing {}".format(
            len(open_items), scp_block["digest"], len(shown)
        )
    )
    lines.append("")
    lines.append("| " + " | ".join(COLUMNS) + " |")
    lines.append("|" + "---|" * len(COLUMNS))
    for item in shown:
        lines.append(_row(item))
    if not shown:
        lines.append("| — | _no open items_ | — | — | — | — | — | — | — | — | — | — |")
    if len(active) > len(shown):
        lines += _truncation_block(
            len(shown), sorted(i["item_id"] for i in active), "rc ledger open --all", "open_items"
        )
    if dormant:
        lines += [
            "",
            "dormant: {} of the {} · digest `{}` · `rc ledger open --dormant`".format(
                len(dormant), len(open_items),
                scp.compute_digest("open_items", sorted(i["item_id"] for i in dormant)),
            ),
            "",
            f"_Dormant items are excluded from the {cap}-row budget but INCLUDED in open_count "
            "and in the SCP ids. Ageing must never weaken conservation._",
        ]
    lines.append("")

    closed_not_completed = _sorted_items(
        [i for i in items.values() if not i["open"] and i["resolution"] != "completed"]
    )
    lines.append(f"## Closed — not completed ({len(closed_not_completed)})")
    lines.append("")
    lines.append("| " + " | ".join(COLUMNS) + " |")
    lines.append("|" + "---|" * len(COLUMNS))
    for item in closed_not_completed:
        lines.append(_row(item))
    if not closed_not_completed:
        lines.append("| — | _none_ | — | — | — | — | — | — | — | — | — | — |")
    lines.append("")

    completed = _sorted_items(
        [i for i in items.values() if not i["open"] and i["resolution"] == "completed"]
    )
    lines.append(f"## Completed and verified ({len(completed)})")
    lines.append("")
    lines.append("| " + " | ".join(COLUMNS) + " |")
    lines.append("|" + "---|" * len(COLUMNS))
    for item in completed:
        lines.append(_row(item))
    if not completed:
        lines.append("| — | _none_ | — | — | — | — | — | — | — | — | — | — |")
    lines.append("")

    needs_reopen = _sorted_items([i for i in items.values() if i.get("needs_reopen")])
    if needs_reopen:
        lines.append("## auto: needs re-open (display only — the projector never appends)")
        lines.append("")
        for item in needs_reopen:
            lines.append(
                "- `{}` — reverted with no successor row. {}".format(
                    item["item_id"], _cell(item["subject"])
                )
            )
        lines.append("")

    if unrecognized:
        # ⛔ Rendered, never dropped. There is no `default: skip` in this renderer:
        # a silent skip would make the safety property destroy itself.
        lines.append(f"## Unrecognized (schema drift?) — {len(unrecognized)}")
        lines.append("")
        for entry in sorted(unrecognized, key=lambda e: (str(e.get("ts")), str(e.get("event_id")))):
            lines.append(
                "- {}: `{}` (event `{}`, item `{}`)".format(
                    entry["reason"], entry.get("value"), entry.get("event_id"),
                    entry.get("item_id")
                )
            )
        lines.append("")

    pr_unresolved = [i for i in items.values() if i.get("pr_unresolved")]
    lines += [
        "## Diagnostics",
        "",
        f"- pr_unresolved: {len(pr_unresolved)}",
        f"- errors: {len(errors)}",
        f"- warnings: {len(warnings)}",
        "",
    ]
    for error in errors:
        lines.append("  - ⛔ {}: {}".format(error.get("kind"), error.get("detail", "")))
    for warning in warnings:
        lines.append("  - ⚠ {}: {}".format(warning.get("kind"), warning.get("detail", "")))
    lines.append("")
    return "\n".join(lines) + "\n"


# ═════════════════════════════════════════════════════════════════════════════
# Committability canary — with its positive control
# ═════════════════════════════════════════════════════════════════════════════


def check_committable(repo_root: Path, ledger_path: str) -> tuple[int, list[str]]:
    """⛔ THE POSITIVE CONTROL IS THE POINT.

    Without it, a `git check-ignore` that is broken, absent, or run outside a git
    repo returns "no match" for everything and this canary passes BY BEING BLIND
    — the purest form of the failure the whole ledger exists to stop. Measured
    basis: `.ravenclaude/runs/**` IS gitignored (.gitignore:4), so the control
    has a real subject that will keep firing.
    """
    report: list[str] = []

    def ignored(rel: str) -> bool | None:
        try:
            proc = subprocess.run(
                ["git", "check-ignore", "--quiet", rel],
                cwd=str(repo_root), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                check=False,
            )
        except OSError:
            return None
        if proc.returncode == 0:
            return True
        if proc.returncode == 1:
            return False
        return None

    control_path = ".ravenclaude/runs/_canary.jsonl"
    control = ignored(control_path)
    if control is not True:
        report.append(
            f"HARNESS FAILURE: the positive control `{control_path}` did NOT report ignored "
            f"(got {control!r}). git check-ignore is broken, absent, or this is not a git repo, "
            "so a 'not ignored' answer for the ledger proves nothing."
        )
        return 2, report
    report.append(f"  ok   positive control fired: `{control_path}` IS ignored")

    subject = ignored(ledger_path)
    if subject is None:
        report.append("HARNESS FAILURE: check-ignore returned an indeterminate status")
        return 2, report
    if subject:
        report.append(
            f"⛔ COMMITTABILITY FAILED: `{ledger_path}` IS gitignored. Appends would succeed, exit 0, "
            "and never reach main. Fix the .gitignore rule that captures it; do not move "
            "the ledger under .ravenclaude/runs/."
        )
        return 1, report
    report.append(f"  ok   subject not ignored: `{ledger_path}` commits")
    return 0, report


# ═════════════════════════════════════════════════════════════════════════════
# Commands
# ═════════════════════════════════════════════════════════════════════════════


def _existing_item_ids(ledger_dir: Path) -> list[str]:
    if not ledger_dir.is_dir():
        return []
    ids: list[str] = []
    for shard in sorted(ledger_dir.glob("*.jsonl")):
        for raw in shard.read_bytes().split(b"\n"):
            if not raw.strip():
                continue
            try:
                obj = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                continue
            if isinstance(obj, dict) and isinstance(obj.get("item_id"), str):
                ids.append(obj["item_id"])
    return ids


def build_event(
    repo_root: Path, etype: str, item_id: str | None, asserted: dict[str, Any], actor: str,
    ts: str | None = None, machine_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    machine = machine_block(repo_root, actor, ts)
    if machine_extra:
        machine.update(machine_extra)
    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": new_ulid(),
        "item_id": item_id,
        "type": etype,
        "machine": machine,
        "asserted": scrub_asserted(asserted),
    }


def cmd_init(repo_root: Path, args: argparse.Namespace) -> int:
    config = resolve_config(repo_root)
    ledger_dir = repo_root / config["ledger_dir"]
    ledger_rel = str(Path(config["ledger_dir"]) / "_probe.jsonl")

    code, report = check_committable(repo_root, ledger_rel)
    for line in report:
        print(line)
    if code != 0:
        print("REFUSING to initialise: the resolved ledger path is not committable.",
              file=sys.stderr)
        return code

    ledger_dir.mkdir(parents=True, exist_ok=True)
    config_path = repo_root / CONFIG_REL
    if not config_path.exists():
        payload = {k: v for k, v in config.items() if not k.startswith("_")}
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8")
        print(f"wrote {config_path}")

    # Step 7, load-bearing: a ledger with ZERO events in an INITIALISED repo is
    # UNKNOWN (something is wrong). A repo with no config at all is "not
    # enabled". Those two must never be conflated.
    event = build_event(
        repo_root, "ledger_init", None,
        {"config_version": 1, "ledger_dir": config["ledger_dir"],
         "view_path": config["view_path"]},
        args.actor,
    )
    path = append_record(ledger_dir, event, int(config["max_record_bytes"]))
    print(f"appended ledger_init to {path}")
    print("retention: PERMANENT (a committed git artifact — git history cannot be un-said)")
    print("view_path: {}".format(config["view_path"]))
    return 0


def cmd_open(repo_root: Path, args: argparse.Namespace) -> int:
    config = resolve_config(repo_root)
    ledger_dir = repo_root / config["ledger_dir"]
    ts = args.ts or utcnow_iso()
    machine = machine_block(repo_root, args.actor, ts)
    item_id = mint_item_id(machine["source"], ts, args.subject, _existing_item_ids(ledger_dir))
    asserted: dict[str, Any] = {"subject": args.subject[:140]}
    if args.owner:
        asserted["owner"] = args.owner
    if args.priority:
        asserted["priority"] = args.priority
    if args.tag:
        asserted["tags"] = list(args.tag)
    event = build_event(repo_root, "open", item_id, asserted, args.actor, ts)
    append_record(ledger_dir, event, int(config["max_record_bytes"]))
    print(item_id)
    return 0


def _asserted_from_kv(pairs: Sequence[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for pair in pairs or []:
        key, _, value = pair.partition("=")
        if not _:
            raise LedgerError(f"--set expects key=value, got {pair!r}")
        try:
            out[key] = json.loads(value)
        except ValueError:
            out[key] = value
    return out


def cmd_append(repo_root: Path, args: argparse.Namespace) -> int:
    config = resolve_config(repo_root)
    ledger_dir = repo_root / config["ledger_dir"]
    asserted = _asserted_from_kv(args.set)
    event = build_event(repo_root, args.type, args.item, asserted, args.actor, args.ts)
    path = append_record(ledger_dir, event, int(config["max_record_bytes"]))
    print("{} {} -> {}".format(event["event_id"], args.type, path))
    return 0


def _emit(projection: Projection, config: dict[str, Any], repo_root: Path, write: bool) -> None:
    if not write:
        return
    view = repo_root / config["view_path"]
    view.parent.mkdir(parents=True, exist_ok=True)
    view.write_text(projection.markdown, encoding="utf-8")
    out = repo_root / config["ledger_dir"] / "open-set.json"
    out.write_text(json.dumps(projection.scp_block, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")


def repo_basis(repo_root: Path, config: dict[str, Any]) -> str:
    """`ledger:<repo-relative dir>@<short sha>` — the plan's §8.1 shape.

    REPO-RELATIVE by construction (it is read from the config, never derived
    from an absolute Path), so the block is re-derivable on any checkout and
    carries no OS username. `basis` is in the SCP's volatile-field set, so the
    embedded sha cannot make the freshness gate red on every commit.
    """
    sha = _git(repo_root, "rev-parse", "--short", "HEAD")
    return f"ledger:{config['ledger_dir']}@{sha or 'unknown'}"


def cmd_project(repo_root: Path, args: argparse.Namespace) -> int:
    config = resolve_config(repo_root)
    ledger_dir = repo_root / config["ledger_dir"]
    validator = None if args.no_schema else load_validator()
    now = parse_ts(args.now) if args.now else None
    projection = project(ledger_dir, config, now=now, validator=validator,
                         basis=repo_basis(repo_root, config))
    _emit(projection, config, repo_root, args.write)
    if args.json:
        print(json.dumps({"verdict": projection.verdict, "scp": projection.scp_block,
                          "errors": projection.errors, "warnings": projection.warnings,
                          "unrecognized": projection.unrecognized,
                          "parsed_records": projection.parsed_records},
                         indent=2, sort_keys=True))
    else:
        sys.stdout.write(projection.markdown)
    if projection.verdict == "UNKNOWN":
        print("UNKNOWN: 0 parseable records. This BLOCKS; it is never '0 open'.", file=sys.stderr)
        return 2
    return 1 if projection.errors else 0


def cmd_check_enumeration(repo_root: Path, args: argparse.Namespace) -> int:
    config = resolve_config(repo_root)
    ledger_dir = repo_root / config["ledger_dir"]

    # ⛔ THE INDEPENDENT LOWER BOUND. This is the ONLY path in the design that
    # fires when the ledger is EMPTY: a turn that produced action-shaped output
    # and recorded nothing is UNKNOWN, not "0 open".
    if args.lower_bound is not None and args.lower_bound > 0 and (args.recorded_this_turn or 0) == 0:
        print(f"UNKNOWN (exit 2): unrecorded_lower_bound — {args.lower_bound} action item(s) observed this "
              "turn and 0 events recorded.", file=sys.stderr)
        return 2

    validator = None if args.no_schema else load_validator()
    projection = project(ledger_dir, config, validator=validator)
    if projection.parsed_records == 0:
        print("UNKNOWN (exit 2): ledger_empty — the ledger is initialised and holds 0 "
              "parseable records. UNKNOWN BLOCKS; it is never downgraded to PASS.",
              file=sys.stderr)
        return 2
    if projection.errors:
        print(f"FAIL (exit 1): {len(projection.errors)} projection error(s) — a determinate defect, so the "
              "conservation answer would be built on a broken basis.", file=sys.stderr)
        for error in projection.errors:
            print("  - {}: {}".format(error.get("kind"), error.get("detail", "")),
                  file=sys.stderr)
        return 1

    claimed = scp.load_block(args.claimed)
    verdict = scp.diff_blocks(claimed, projection.scp_block, projection.parsed_records)
    stream = sys.stdout if verdict.verdict == "PASS" else sys.stderr
    print(f"{verdict.verdict} (exit {verdict.exit_code})", file=stream)
    for reason in verdict.reasons:
        print("  - " + reason, file=stream)
    return verdict.exit_code


def cmd_check_committable(repo_root: Path, args: argparse.Namespace) -> int:
    config = resolve_config(repo_root)
    path = args.path or str(Path(config["ledger_dir"]) / "2026-08.jsonl")
    code, report = check_committable(repo_root, path)
    for line in report:
        print(line)
    return code


# ═════════════════════════════════════════════════════════════════════════════
# Self-test
# ═════════════════════════════════════════════════════════════════════════════

_FIXTURES = PLUGIN_ROOT.parent.parent / "tests" / "fixtures" / "ledger"


def _self_test(broken_order: bool = False) -> int:
    import shutil
    import tempfile

    failures: list[str] = []

    def check(label: str, condition: bool) -> None:
        if condition:
            print(f"  ok   {label}")
        else:
            print(f"  FAIL {label}")
            failures.append(label)

    config = dict(DEFAULT_CONFIG)
    workdir = Path(tempfile.mkdtemp(prefix="rc-ledger-selftest-"))
    try:
        # ── the append primitive ─────────────────────────────────────────────
        ledger_dir = workdir / "ledger"
        repo_root = workdir
        event = build_event(repo_root, "open", "rc-000000000001", {"subject": "probe"}, "selftest",
                            "2026-08-19T00:00:00.000Z")
        append_record(ledger_dir, event, 8192)
        shard = ledger_dir / "2026-08.jsonl"
        blob = shard.read_bytes()
        check("append writes exactly one newline-terminated line",
              blob.count(b"\n") == 1 and blob.endswith(b"\n"))
        before = blob
        append_record(ledger_dir, build_event(repo_root, "open", "rc-000000000002",
                                              {"subject": "probe2"}, "selftest",
                                              "2026-08-19T00:00:01.000Z"), 8192)
        after = shard.read_bytes()
        check("append is append-only: the earlier bytes are untouched",
              after.startswith(before))

        try:
            append_record(ledger_dir, build_event(repo_root, "open", "rc-000000000003",
                                                  {"subject": "x" * 200}, "selftest"), 128)
            check("an oversize record is refused", False)
        except LedgerError:
            check("an oversize record is refused", True)

        # ── minting ──────────────────────────────────────────────────────────
        ids = set()
        for n in range(2000):
            ids.add(mint_item_id("src", "2026-08-19T00:00:00.000Z", f"subject-{n}", ids))
        check("2000 mints are collision-free", len(ids) == 2000)
        pinned = mint_item_id("s", "t", "u", [], nonce_factory=lambda: b"\x00" * 8)
        try:
            mint_item_id("s", "t", "u", [pinned], nonce_factory=lambda: b"\x00" * 8)
            check("a forced collision HARD FAILS rather than reusing an id", False)
        except LedgerError:
            check("a forced collision HARD FAILS rather than reusing an id", True)
        rolled = mint_item_id("s", "t", "u", [pinned])
        check("a collision re-rolls to a different id", rolled != pinned)

        # ── scrub ────────────────────────────────────────────────────────────
        secret = "ghp_" + "b" * 36
        scrubbed = scrub(f"token is {secret} for jane.doe@client.com")
        check("a ghp_-shaped token is [REDACTED] on the write path",
              secret not in scrubbed and "[REDACTED]" in scrubbed)
        check("an email address is [PII:email] on the write path",
              "jane.doe@client.com" not in scrubbed and "[PII:email]" in scrubbed)
        check("scrub leaves innocuous prose alone", scrub("fix the sort order") ==
              "fix the sort order")

        # ── fixtures: projection ─────────────────────────────────────────────
        validator = None
        try:
            validator = load_validator()
            check("the JSON-Schema validator loads and its bad-object control fires", True)
        except LedgerUnknown as exc:
            check(f"the JSON-Schema validator loads ({exc})", False)

        canonical = _FIXTURES / "canonical.jsonl"
        shuffled = _FIXTURES / "shuffled-order.jsonl"
        if canonical.exists() and shuffled.exists():
            # ⛔ FIXTURE CONTROL: a missing or empty fixture is a HARNESS FAILURE,
            # not a pass. Assert it parses to >=1 event before trusting a result.
            check("fixture control: canonical.jsonl is non-empty",
                  len(canonical.read_bytes().strip()) > 0)

            def run(src: Path) -> Projection:
                d = workdir / ("proj-" + src.stem)
                d.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(str(src), str(d / "2026-08.jsonl"))
                return project(d, config, validator=validator, basis="ledger:fixture",
                               _broken_dedupe_first=broken_order)

            a = run(canonical)
            b = run(shuffled)
            check("A1.1 order-independence: shuffled input renders byte-identical Markdown",
                  a.markdown == b.markdown)
            check("A1.1 order-independence: identical open-set digest",
                  a.scp_block["digest"] == b.scp_block["digest"])
            check("canonical fixture parses to >=1 event (positive control)",
                  a.parsed_records >= 1)
            check("canonical fixture has no projection errors",
                  not a.errors or all(e["kind"] == "probable_typo" for e in a.errors))
            check("C27 an item with only a `proposed` event is OPEN (no closing event = open)",
                  any(i["open"] and i["state"] == "proposed" for i in a.items.values()))
            check("A1.6 a `completed` item with no verify event stays OPEN (ruling E)",
                  any(i["open"] and i["state"] == "done" and i["resolution"] == "completed"
                      for i in a.items.values()))
            check("`blocked` is derived and appears in the render, never stored",
                  any(i["blocked"] for i in a.items.values()) and "blocked" in a.markdown)
            check("A1.5 regeneration is idempotent", run(canonical).markdown == a.markdown)
            later = project(workdir / "proj-canonical", config, validator=validator,
                            basis="ledger:fixture", now=a.now + timedelta(minutes=5),
                            _broken_dedupe_first=broken_order)
            check("A1.5 `now` is a parameter, so a 5-minute-later run differs ONLY where "
                  "ageing genuinely changed", later.scp_block["ids"] == a.scp_block["ids"])
        else:
            check("fixtures present (canonical.jsonl / shuffled-order.jsonl)", False)

        collision = _FIXTURES / "collision-deterministic.jsonl"
        if collision.exists():
            d = workdir / "proj-collision"
            d.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(str(collision), str(d / "2026-08.jsonl"))
            c1 = project(d, config, validator=validator, basis="b",
                         _broken_dedupe_first=broken_order)
            hits = [e for e in c1.errors if e["kind"] == "event_id_collision"]
            check("A1.2 collision: errors[] carries event_id_collision", len(hits) == 1)
            kept_sha = hits[0]["kept_sha"] if hits else None

            lines = [ln for ln in collision.read_bytes().split(b"\n") if ln.strip()]
            d2 = workdir / "proj-collision-shuffled"
            d2.mkdir(parents=True, exist_ok=True)
            (d2 / "2026-08.jsonl").write_bytes(b"\n".join(reversed(lines)) + b"\n")
            c2 = project(d2, config, validator=validator, basis="b",
                         _broken_dedupe_first=broken_order)
            hits2 = [e for e in c2.errors if e["kind"] == "event_id_collision"]
            check("A1.2 collision: the SURVIVOR is the documented one under shuffle",
                  bool(hits2) and hits2[0]["kept_sha"] == kept_sha)
            check("A1.2 collision: the shuffled projection is byte-identical",
                  c1.markdown == c2.markdown)
        else:
            check("fixture present (collision-deterministic.jsonl)", False)

        torn = _FIXTURES / "bad-truncated-line.jsonl"
        if torn.exists():
            d = workdir / "proj-torn"
            d.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(str(torn), str(d / "2026-08.jsonl"))
            t = project(d, config, validator=validator, basis="b")
            check("C10 a torn line lands in errors[] and the verdict is not PASS",
                  any(e["kind"] == "malformed_line" for e in t.errors) and t.verdict != "PASS")
        else:
            check("fixture present (bad-truncated-line.jsonl)", False)

        # ── the empty ledger: UNKNOWN, never a green pass ────────────────────
        empty_dir = workdir / "empty-ledger"
        empty_dir.mkdir(parents=True, exist_ok=True)
        (empty_dir / "2026-08.jsonl").write_bytes(b"")
        e = project(empty_dir, config, validator=validator, basis="b")
        check("C12 an EMPTY initialised ledger => UNKNOWN, never PASS",
              e.verdict == "UNKNOWN" and e.parsed_records == 0)
        v = scp.diff_blocks(e.scp_block, e.scp_block, e.parsed_records)
        check("C12 the conservation gate on an empty ledger => UNKNOWN, exit 2",
              v.verdict == "UNKNOWN" and v.exit_code == 2)

        try:
            project(workdir / "no-such-dir", config, validator=validator)
            check("an absent ledger_dir => UNKNOWN, never 0 open", False)
        except LedgerUnknown:
            check("an absent ledger_dir => UNKNOWN, never 0 open", True)

        # ── config: unparseable is UNKNOWN, never a default fall-through ─────
        badrepo = workdir / "badconfig"
        (badrepo / ".ravenclaude").mkdir(parents=True, exist_ok=True)
        (badrepo / CONFIG_REL).write_text("{ not json", encoding="utf-8")
        try:
            resolve_config(badrepo)
            check("an unparseable config => UNKNOWN hard stop, never the defaults", False)
        except LedgerUnknown:
            check("an unparseable config => UNKNOWN hard stop, never the defaults", True)

        # ── truncation, BOTH directions ──────────────────────────────────────
        big_dir = workdir / "big"
        big_dir.mkdir(parents=True, exist_ok=True)
        rows = []
        for n in range(40):
            rows.append(build_event(repo_root, "open", f"rc-{n:012x}",
                                    {"subject": f"item {n}"}, "selftest",
                                    f"2026-08-19T00:00:{n % 60:02d}.000Z"))
        (big_dir / "2026-08.jsonl").write_bytes(
            b"\n".join(canonical_bytes(r) for r in rows) + b"\n")
        big = project(big_dir, dict(config, brief_max_items=12), validator=validator, basis="b")
        check("C20 truncation: the banner carries the count, the digest and a pointer",
              "RENDER TRUNCATED" in big.markdown and "digest" in big.markdown
              and "rc ledger open --all" in big.markdown)
        check("C20 truncation: the SCP marks truncated: true", big.scp_block["truncated"] is True)
        check("C20 truncation: the full count is rendered, not the shown count",
              "Open — 40 items" in big.markdown)
        small = project(big_dir, dict(config, brief_max_items=80), validator=validator, basis="b")
        check("C20 negative control: 40 items at cap 80 emits NO truncation banner",
              "RENDER TRUNCATED" not in small.markdown
              and small.scp_block["truncated"] is False)

        # ── committability, against the REAL repo ────────────────────────────
        real_root = find_repo_root(Path(__file__).resolve().parent)
        code, report = check_committable(real_root, ".ravenclaude/ledger/2026-08.jsonl")
        check("C21 committability: the resolved ledger path is NOT gitignored "
              "AND the positive control fired", code == 0)
        code2, _ = check_committable(real_root, ".ravenclaude/runs/x/ledger.jsonl")
        check("C21 negative control: a path under .ravenclaude/runs/ IS caught as ignored",
              code2 == 1)
    finally:
        shutil.rmtree(str(workdir), ignore_errors=True)

    print()
    if failures:
        print(f"ledger self-test FAILED ({len(failures)})")
        return 1
    print("ledger self-test PASS")
    return 0


def _must_fail() -> int:
    """Plant the ruling-C bug — DEDUPE BEFORE SORT — and assert the suite reddens.

    This is the exact defect the projection order exists to prevent: with the
    dedupe first, the collision survivor depends on file order, so the shuffled
    fixture yields a different survivor and different Markdown. If the suite
    still passes with the bug planted, the order-independence assertions are
    decorative.
    """
    print("-- --must-fail: dedupe-before-sort is planted; the suite is MEANT to redden --")
    rc = _self_test(broken_order=True)
    if rc == 0:
        print("TEETH FAILED: dedupe-before-sort still passed the self-test", file=sys.stderr)
        return 1
    print(f"teeth ok: the planted order bug was caught (self-test exited {rc})")
    return 0


# ═════════════════════════════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════════════════════════════


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ledger.py",
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="exit codes — project/check: 0 clean/1 errors/2 UNKNOWN · check-enumeration: "
               "0 PASS/1 FAIL/2 UNKNOWN · check-committable: 0 held/1 ignored/2 harness "
               "failure · --must-fail: 0 when the teeth BIT (premise-gate.py's convention, "
               "NOT sync-plugin-versions.py's)",
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--actor", default=os.environ.get("RC_ACTOR", "unknown"))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--must-fail", action="store_true",
                        help="plant the dedupe-before-sort bug and assert the self-test "
                             "catches it; exits 0 only when the teeth bite")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="initialise the ledger in this repo")
    p_init.set_defaults(func=cmd_init)

    p_open = sub.add_parser("open", help="mint an item")
    p_open.add_argument("--subject", required=True)
    p_open.add_argument("--owner")
    p_open.add_argument("--priority", type=int, choices=[1, 2, 3, 4])
    p_open.add_argument("--tag", action="append")
    p_open.add_argument("--ts")
    p_open.set_defaults(func=cmd_open)

    p_append = sub.add_parser("append", help="append any typed event")
    p_append.add_argument("--type", required=True,
                          choices=["state", "verify", "link", "redact", "provenance",
                                   "bridge_health"])
    p_append.add_argument("--item")
    p_append.add_argument("--set", action="append", default=[], metavar="KEY=JSON")
    p_append.add_argument("--ts")
    p_append.set_defaults(func=cmd_append)

    p_project = sub.add_parser("project", help="fold the ledger and render the view")
    p_project.add_argument("--write", action="store_true", help="write the view + open-set.json")
    p_project.add_argument("--json", action="store_true")
    p_project.add_argument("--now", help="explicit `now`; defaults to the newest event's ts")
    p_project.add_argument("--no-schema", action="store_true",
                           help="skip schema validation (⛔ downgrades the answer; for "
                                "harness use only)")
    p_project.set_defaults(func=cmd_project)

    p_check = sub.add_parser("check", help="alias for project without rendering")
    p_check.add_argument("--json", action="store_true", default=True)
    p_check.add_argument("--write", action="store_true")
    p_check.add_argument("--now")
    p_check.add_argument("--no-schema", action="store_true")
    p_check.set_defaults(func=cmd_project)

    p_enum = sub.add_parser("check-enumeration", help="the three-valued conservation gate")
    p_enum.add_argument("--claimed", required=True)
    p_enum.add_argument("--lower-bound", type=int, default=None,
                        help="independent lower bound on this turn's action items")
    p_enum.add_argument("--recorded-this-turn", type=int, default=None)
    p_enum.add_argument("--no-schema", action="store_true")
    p_enum.set_defaults(func=cmd_check_enumeration)

    p_commit = sub.add_parser("check-committable", help="the committability canary")
    p_commit.add_argument("--path")
    p_commit.set_defaults(func=cmd_check_committable)

    args = parser.parse_args(argv)

    if args.must_fail:
        return _must_fail()
    if args.self_test:
        return _self_test()
    if not getattr(args, "func", None):
        parser.print_help()
        return 1

    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    try:
        return args.func(repo_root, args)
    except LedgerUnknown as exc:
        print(f"UNKNOWN (exit 2): {exc}", file=sys.stderr)
        print("UNKNOWN BLOCKS. It is never downgraded to PASS.", file=sys.stderr)
        return 2
    except LedgerError as exc:
        print(f"REFUSED (exit 1): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

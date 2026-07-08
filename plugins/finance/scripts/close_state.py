#!/usr/bin/env python3
"""close_state.py - the governed review->approve->lock spine for a close package.

Every deliverable the controller-autopilot produces (statements, reconciliations,
flux) is SUBMITTED INTO this state machine. It exists to make the close's controls
*enforced by construction* rather than documented — the failure mode behind the
public "AP agent released $92K past a documented control" incident (2025) is a
control that was written down but not enforced. Here the state machine REFUSES
illegal transitions and REFUSES a same-actor approval above the entity's
materiality threshold, and the audit log is append-only + hash-chained so any
retroactive edit breaks the chain and is detectable.

  submit    draft      -> submitted     (preparer hands the package to review)
  review    submitted  -> in_review     (a reviewer picks it up)
  approve   in_review  -> approved       (approver signs off; SoD-checked)
  reject    submitted|in_review -> draft (send back with a reason)
  lock      approved   -> locked         (period close; needs a non-agent token)
  reopen    locked     -> draft          (authorized, reason required, logged)
  verify    (any)                        (recompute the hash chain; tamper check)

HONEST SCOPE / TIER CAVEAT — READ THIS.
Identity here is *config-asserted, not authenticated*. `--actor NAME` is a string
the caller supplies; this module has no identity provider binding it to a real
person. The hash chain is therefore tamper-EVIDENT (a third party can detect an
edit), NOT tamper-PREVENTING against the operator who holds the file. At this
local tier the SoD check stops the *same declared actor* self-approving above
threshold and blocks the accidental single-process auto-approve — it does NOT, by
itself, make the close auditor-grade. LOCK additionally requires an approval token
that is structurally NOT the driving agent (a human-entered / out-of-band value);
absent it, the package is badged 'self-certified, single-actor'. Real,
auditor-reliable segregation requires an IdP + an immutable store at the
warehouse/ELT tier (deferred). Do not claim this "designs out" the incident at the
local tier — it makes the honor-system honest and testable, which is the point.

Stdlib only (hashlib/json/argparse); runs anywhere Python 3.8+ is present.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

SCHEMA_VERSION = 1

# (action, from_state) -> the single legal destination state.
# Keying by the invoking ACTION (not just destination reachability) enforces the
# documented per-action table: e.g. `reject` is legal only from submitted|in_review,
# and `reopen` only from locked — even though both target "draft". A guard keyed on
# destination membership alone would let reject() run on a locked package and
# reopen() on a submitted/in_review one, since "draft" is reachable from all three.
ACTION_TRANSITIONS = {
    ("submit", "draft"): "submitted",
    ("review", "submitted"): "in_review",
    ("approve", "in_review"): "approved",
    ("reject", "submitted"): "draft",
    ("reject", "in_review"): "draft",
    ("lock", "approved"): "locked",
    ("reopen", "locked"): "draft",
}
TERMINAL = "locked"


def _now(explicit: str | None) -> str:
    """UTC ISO timestamp. Overridable via --now / RAVEN_NOW for deterministic runs."""
    if explicit:
        return explicit
    env = os.environ.get("RAVEN_NOW")
    if env:
        return env
    return datetime.now(timezone.utc).isoformat()


def _event_hash(prev_hash: str, payload: dict) -> str:
    """Hash of (prev_hash + canonical payload). Chains each event to its predecessor."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev_hash + canonical).encode("utf-8")).hexdigest()


class CloseLedger:
    """A single close package's state + append-only hash-chained audit trail."""

    def __init__(self, run_dir: str):
        self.run_dir = run_dir
        self.state_path = os.path.join(run_dir, "state.json")
        self.audit_path = os.path.join(run_dir, "audit.jsonl")

    # ---- persistence -----------------------------------------------------
    def load_state(self) -> dict:
        if not os.path.exists(self.state_path):
            return {
                "schema_version": SCHEMA_VERSION,
                "state": "draft",
                "preparer": None,
                "package_amount": None,
                "self_certified": None,
            }
        with open(self.state_path) as fh:
            st = json.load(fh)
        if st.get("schema_version") != SCHEMA_VERSION:
            raise SystemExit(
                f"state.json schema_version {st.get('schema_version')} != current "
                f"{SCHEMA_VERSION} — re-review this package under the new contract."
            )
        return st

    def _write_state(self, st: dict) -> None:
        os.makedirs(self.run_dir, exist_ok=True)
        tmp = self.state_path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(st, fh, indent=2)
        os.replace(tmp, self.state_path)  # atomic

    def _last_hash(self) -> str:
        if not os.path.exists(self.audit_path):
            return "GENESIS"
        last = "GENESIS"
        with open(self.audit_path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    last = json.loads(line)["hash"]
        return last

    def _append_event(self, action: str, actor: str, detail: dict, now: str | None) -> dict:
        prev = self._last_hash()
        payload = {
            "action": action,
            "actor": actor,
            "ts": _now(now),
            "detail": detail,
            "prev_hash": prev,
        }
        payload["hash"] = _event_hash(
            prev, {k: payload[k] for k in ("action", "actor", "ts", "detail", "prev_hash")}
        )
        os.makedirs(self.run_dir, exist_ok=True)
        with open(self.audit_path, "a") as fh:
            fh.write(json.dumps(payload) + "\n")
        return payload

    # ---- guarded transitions --------------------------------------------
    def _transition(
        self, action: str, to_state: str, actor: str, detail: dict, now: str | None
    ) -> dict:
        st = self.load_state()
        frm = st["state"]
        allowed = ACTION_TRANSITIONS.get((action, frm))
        if allowed is None or allowed != to_state:
            self._append_event(
                f"DENIED:{action}",
                actor,
                {**detail, "reason": f"illegal transition {frm}->{to_state}"},
                now,
            )
            raise SystemExit(f"REFUSED: illegal transition {frm} -> {to_state} ({action}).")
        return st

    def submit(
        self, actor: str, amount: float, now: str | None = None, source_tb_sha256: str | None = None
    ) -> dict:
        # source_tb_sha256 PINS the trial balance this package was built from, so a later
        # NetSuite re-pull whose hash differs can be flagged as "source changed after sign-off"
        # (verify_source). Additive + backward-compatible: when None it is omitted entirely, so
        # existing callers/events/audit hashes are byte-identical (no chain shift).
        detail = {"amount": amount}
        if source_tb_sha256 is not None:
            detail["source_tb_sha256"] = source_tb_sha256
        st = self._transition("submit", "submitted", actor, detail, now)
        st["state"] = "submitted"
        st["preparer"] = actor
        st["package_amount"] = amount
        if source_tb_sha256 is not None:
            st["source_tb_sha256"] = source_tb_sha256
        self._write_state(st)
        self._append_event("submit", actor, detail, now)
        return st

    def verify_source(self, current_hash: str) -> tuple[bool, str]:
        """Cross-system drift control: compare a freshly-pulled TB hash to the one PINNED at
        submit. Returns (unchanged, message). If no hash was pinned, reports that (not a
        pass/fail). Does NOT touch the hash-chain verify() — it is a separate, read-only check."""
        st = self.load_state()
        pinned = st.get("source_tb_sha256")
        if not pinned:
            return (False, "no source TB hash was pinned at submit — cannot check drift")
        if current_hash == pinned:
            return (True, "source TB unchanged since sign-off")
        return (
            False,
            f"SOURCE CHANGED AFTER SIGN-OFF: pinned {pinned[:12]}… != current "
            f"{current_hash[:12]}… — reopen before re-running the cycle",
        )

    def review(self, actor: str, now: str | None = None) -> dict:
        st = self._transition("review", "in_review", actor, {}, now)
        st["state"] = "in_review"
        self._write_state(st)
        self._append_event("review", actor, {}, now)
        return st

    def approve(self, actor: str, threshold: float, now: str | None = None) -> dict:
        st = self._transition("approve", "approved", actor, {}, now)
        preparer = st.get("preparer")
        amount = st.get("package_amount") or 0.0
        # SoD: the same declared actor cannot approve their own package above threshold.
        if actor == preparer and amount >= threshold:
            self._append_event(
                "DENIED:approve",
                actor,
                {
                    "reason": "SoD violation: preparer==approver above threshold",
                    "amount": amount,
                    "threshold": threshold,
                },
                now,
            )
            raise SystemExit(
                f"REFUSED (SoD): actor '{actor}' is the preparer and package amount "
                f"{amount:,.2f} >= threshold {threshold:,.2f}. A different approver is required."
            )
        st["state"] = "approved"
        st["approver"] = actor
        self._write_state(st)
        self._append_event(
            "approve",
            actor,
            {"amount": amount, "threshold": threshold, "sod_ok": actor != preparer},
            now,
        )
        return st

    def reject(self, actor: str, reason: str, now: str | None = None) -> dict:
        st = self._transition("reject", "draft", actor, {"reason": reason}, now)
        st["state"] = "draft"
        self._write_state(st)
        self._append_event("reject", actor, {"reason": reason}, now)
        return st

    def lock(self, actor: str, approval_token: str | None = None, now: str | None = None) -> dict:
        st = self._transition("lock", "locked", actor, {}, now)
        # LOCK needs a structurally-non-agent token; absent it, badge self-certified.
        self_certified = not bool(approval_token)
        st["state"] = "locked"
        st["self_certified"] = self_certified
        self._write_state(st)
        self._append_event(
            "lock",
            actor,
            {"self_certified": self_certified, "approval_token_present": bool(approval_token)},
            now,
        )
        if self_certified:
            sys.stderr.write(
                "WARNING: locked WITHOUT a non-agent approval token — package is "
                "'self-certified, single-actor'. Not audit-grade.\n"
            )
        return st

    def reopen(self, actor: str, reason: str, now: str | None = None) -> dict:
        if not reason:
            raise SystemExit("REFUSED: reopen requires --reason (authorized justification).")
        st = self._transition("reopen", "draft", actor, {"reason": reason}, now)
        st["state"] = "draft"
        self._write_state(st)
        self._append_event("reopen", actor, {"reason": reason}, now)
        return st

    def verify(self) -> tuple[bool, str]:
        """Recompute the hash chain end-to-end. Returns (ok, message)."""
        if not os.path.exists(self.audit_path):
            return True, "no audit log yet (empty chain is trivially valid)"
        prev = "GENESIS"
        n = 0
        with open(self.audit_path) as fh:
            for i, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                ev = json.loads(line)
                if ev.get("prev_hash") != prev:
                    return False, f"line {i}: prev_hash mismatch (chain broken/reordered)"
                expected = _event_hash(
                    prev, {k: ev[k] for k in ("action", "actor", "ts", "detail", "prev_hash")}
                )
                if ev.get("hash") != expected:
                    return False, f"line {i}: hash mismatch (event '{ev.get('action')}' tampered)"
                prev = ev["hash"]
                n += 1
        return True, f"chain valid: {n} event(s), tip {prev[:12]}…"


def _print(st: dict) -> None:
    print(json.dumps(st, indent=2))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Governed close-package state machine + audit ledger.")
    p.add_argument("--run-dir", required=True, help="directory holding state.json + audit.jsonl")
    p.add_argument("--now", help="ISO timestamp override for deterministic runs")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("submit")
    s.add_argument("--actor", required=True)
    s.add_argument("--amount", type=float, required=True)
    s.add_argument(
        "--source-tb-sha256", default=None, help="pin the source TB hash for drift detection"
    )
    s = sub.add_parser("review")
    s.add_argument("--actor", required=True)
    s = sub.add_parser("approve")
    s.add_argument("--actor", required=True)
    s.add_argument("--threshold", type=float, required=True)
    s = sub.add_parser("reject")
    s.add_argument("--actor", required=True)
    s.add_argument("--reason", required=True)
    s = sub.add_parser("lock")
    s.add_argument("--actor", required=True)
    s.add_argument("--approval-token", default=None)
    s = sub.add_parser("reopen")
    s.add_argument("--actor", required=True)
    s.add_argument("--reason", required=True)
    sub.add_parser("verify")
    s = sub.add_parser("verify-source")
    s.add_argument("--current-hash", required=True)
    sub.add_parser("show")

    a = p.parse_args(argv)
    led = CloseLedger(a.run_dir)
    try:
        if a.cmd == "submit":
            _print(led.submit(a.actor, a.amount, a.now, a.source_tb_sha256))
        elif a.cmd == "review":
            _print(led.review(a.actor, a.now))
        elif a.cmd == "approve":
            _print(led.approve(a.actor, a.threshold, a.now))
        elif a.cmd == "reject":
            _print(led.reject(a.actor, a.reason, a.now))
        elif a.cmd == "lock":
            _print(led.lock(a.actor, a.approval_token, a.now))
        elif a.cmd == "reopen":
            _print(led.reopen(a.actor, a.reason, a.now))
        elif a.cmd == "verify":
            ok, msg = led.verify()
            print(("OK: " if ok else "FAIL: ") + msg)
            return 0 if ok else 1
        elif a.cmd == "verify-source":
            ok, msg = led.verify_source(a.current_hash)
            print(("OK: " if ok else "DRIFT: ") + msg)
            return 0 if ok else 1
        elif a.cmd == "show":
            _print(led.load_state())
    except SystemExit as e:
        # guarded refusals print to stderr and exit non-zero
        if isinstance(e.code, str):
            sys.stderr.write(e.code + "\n")
            return 2
        return e.code or 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

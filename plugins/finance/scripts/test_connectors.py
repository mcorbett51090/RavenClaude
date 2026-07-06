#!/usr/bin/env python3
"""test_connectors.py - acceptance/regression suite for the finance OAuth connectors +
drill-through lineage (W2). Stdlib-only, zero-dependency (no pytest).

Run:  python3 test_connectors.py
Exits 0 iff every load-bearing property holds:
  * rotating-token ATOMIC persist-THEN-use ordering (persist precedes the first use);
  * crash-safety: a crash AFTER persist leaves the NEW token durable; a crash DURING the
    write leaves the OLD token fully intact (never a half-written store);
  * the per-entity lock serializes two concurrent refreshes to ONE rotation;
  * invalid_grant -> REAUTH_REQUIRED, NON-retryable, fires the alert hook, no retry;
  * error-cause routing produces THREE distinct actions for 401 / 429 / invalid_grant;
  * Xero 30-min grace: a lost response retries with the EXISTING refresh token;
  * the replay transport refuses a missing fixture LOUDLY and never opens a socket;
  * gl_lineage's first six columns are BYTE-IDENTICAL to statement_engine --gl-detail, it
    lifts the traceability badge, and every adapter's raw export stages clean via tb_stage.

No live credentials, no live sockets, all fixtures synthetic/obviously-fake.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from connectors import gl_lineage, oauth_client  # noqa: E402
from connectors.adapters import ADAPTERS  # noqa: E402
from connectors.oauth_client import (  # noqa: E402
    BACKOFF_RETRY,
    REAUTH_REQUIRED,
    REFRESH_RETRY,
    OAuthClient,
    ReauthRequired,
    SimulatedCrash,
    TransportTimeout,
    classify_error,
    honor_retry_after,
)
from connectors.replay_transport import (  # noqa: E402
    FixtureMissing,
    ReplayTransport,
    TokenResponse,
)

FIX = os.path.join(HERE, "connectors", "fixtures")
GAAP_EX = os.path.join(HERE, "..", "skills", "produce-gaap-statements", "examples")
ENT = os.path.join(GAAP_EX, "meridian-robotics.json")
COA = os.path.join(GAAP_EX, "coa-mapping.csv")
TB = os.path.join(GAAP_EX, "trial-balance-2026-06.csv")
GL_DETAIL = os.path.join(GAAP_EX, "gl-detail-2026-06.csv")
DOCS = os.path.join(FIX, "lineage", "source-docs.csv")

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


class StubTransport:
    """Programmable token endpoint: pops from `responses` (a TokenResponse or an Exception
    to raise). Records payloads + call count; shares an `events` list to prove ordering."""

    def __init__(self, responses, events=None):
        self.responses = list(responses)
        self.payloads = []
        self.token_calls = 0
        self.events = events

    def token_request(self, url, data):
        self.token_calls += 1
        self.payloads.append(data)
        if self.events is not None:
            self.events.append(("token_request", data.get("provider")))
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    def api_request(self):  # models the "use" of the new access token
        if self.events is not None:
            self.events.append(("use", "x"))


class RotatingTransport:
    """Thread-safe: each token_request rotates to a fresh access/refresh pair, so the
    number of actual rotations == token_calls."""

    def __init__(self):
        self._lock = threading.Lock()
        self.token_calls = 0

    def token_request(self, url, data):
        with self._lock:
            self.token_calls += 1
            n = self.token_calls
        return TokenResponse(200, {"access_token": f"A{n}", "refresh_token": f"R{n}",
                                   "expires_in": 3600, "token_type": "Bearer"}, {})


def _write_store(path, tokens):
    with open(path, "w") as fh:
        json.dump(tokens, fh)


def main():
    fixed = {"t": 1_000_000.0}
    clock = lambda: fixed["t"]  # noqa: E731

    print("W2.1 — rotating-token ATOMIC persist-then-use ordering")
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "qbo-MRI.token.json")
        _write_store(store, {"access_token": "A0", "refresh_token": "R0",
                             "expires_at": fixed["t"] - 10})  # expired
        events = []
        tr = StubTransport([TokenResponse(200, {"access_token": "A1", "refresh_token": "R1",
                                               "expires_in": 3600}, {})], events=events)
        client = OAuthClient("qbo", store, tr, clock=clock, events=events)
        client.refresh()
        tr.api_request()  # the "use"
        names = [e[0] for e in events]
        check("token_request precedes persist", names.index("token_request") < names.index("persist"))
        check("persist precedes the first use (persist-THEN-use)",
              names.index("persist") < names.index("use"))
        check("the NEW rotating refresh token is durable on disk after persist",
              json.load(open(store))["refresh_token"] == "R1")

    print("W2.2 — crash-safety (atomic persist)")
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "s.json")
        _write_store(store, {"refresh_token": "OLD", "access_token": "A0"})
        # crash AFTER os.replace: the NEW token is durable.
        oauth_client._atomic_persist(store, {"refresh_token": "NEW", "access_token": "A1"})
        check("crash AFTER persist -> NEW token durable",
              json.load(open(store))["refresh_token"] == "NEW")
        # crash DURING the write (before os.replace): OLD token intact, no half-write.
        _write_store(store, {"refresh_token": "OLD2", "access_token": "A0"})
        raised = False
        try:
            oauth_client._atomic_persist(store, {"refresh_token": "NEW2", "access_token": "A9"},
                                         crash_after_tmp=True)
        except SimulatedCrash:
            raised = True
        check("mid-write crash raises before os.replace", raised)
        check("crash DURING write -> OLD token fully intact (never half-written)",
              json.load(open(store))["refresh_token"] == "OLD2")

    print("W2.3 — per-entity lock serializes two concurrent refreshes to ONE rotation")
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "xero-MRI.token.json")
        _write_store(store, {"access_token": "A0", "refresh_token": "R0",
                             "expires_at": 0.0})  # expired (real-clock client)
        rot = RotatingTransport()
        client = OAuthClient("xero", store, rot)  # real time.time clock
        errs = []

        def worker():
            try:
                client.get_access_token()
            except Exception as e:  # pragma: no cover
                errs.append(e)

        ts = [threading.Thread(target=worker) for _ in range(2)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        check("two concurrent refreshes collapse to ONE rotation (recheck-under-lock)",
              rot.token_calls == 1 and not errs)
        check("store holds exactly the single rotation's token",
              json.load(open(store))["refresh_token"] == "R1")

    print("W2.4 — invalid_grant -> REAUTH_REQUIRED, non-retryable, alert fired")
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "qbo.token.json")
        _write_store(store, {"access_token": "A0", "refresh_token": "R0", "expires_at": fixed["t"] - 10})
        alerts = []
        tr = StubTransport([TokenResponse(400, {"error": "invalid_grant"}, {})])
        client = OAuthClient("qbo", store, tr, clock=clock, alert_hook=alerts.append)
        got_reauth = False
        try:
            client.refresh()
        except ReauthRequired:
            got_reauth = True
        check("invalid_grant raises ReauthRequired", got_reauth)
        check("alert hook fired exactly once", len(alerts) == 1)
        check("alert carries NO token value", all("R0" not in json.dumps(a) for a in alerts))
        check("NON-retryable: the token endpoint was called exactly once (no backoff/retry)",
              tr.token_calls == 1)

    print("W2.5 — error-cause routing: three distinct actions")
    a401 = classify_error(401, {})
    a429 = classify_error(429, {})
    agrant = classify_error(400, {"error": "invalid_grant"})
    check("401 -> REFRESH_RETRY", a401 == REFRESH_RETRY)
    check("429 -> BACKOFF_RETRY", a429 == BACKOFF_RETRY)
    check("invalid_grant -> REAUTH_REQUIRED", agrant == REAUTH_REQUIRED)
    check("the three causes map to THREE distinct actions", len({a401, a429, agrant}) == 3)
    check("429 backoff honors Retry-After header", honor_retry_after({"Retry-After": "12"}, 0) == 12.0)

    print("W2.6 — Xero 30-min grace: lost response retries with the EXISTING refresh token")
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "xero.token.json")
        _write_store(store, {"access_token": "A0", "refresh_token": "RX0", "expires_at": fixed["t"] - 10})
        tr = StubTransport([TransportTimeout("lost response"),
                            TokenResponse(200, {"access_token": "AX1", "refresh_token": "RX1",
                                               "expires_in": 1800}, {})])
        client = OAuthClient("xero", store, tr, clock=clock)
        client.refresh()
        check("grace: the endpoint is retried after a lost response", tr.token_calls == 2)
        check("grace retry reuses the EXISTING refresh token (no assumed rotation)",
              all(p["refresh_token"] == "RX0" for p in tr.payloads))
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "qbo.token.json")
        _write_store(store, {"access_token": "A0", "refresh_token": "R0", "expires_at": fixed["t"] - 10})
        tr = StubTransport([TransportTimeout("lost response")])
        client = OAuthClient("qbo", store, tr, clock=clock)  # grace_seconds == 0
        propagated = False
        try:
            client.refresh()
        except TransportTimeout:
            propagated = True
        check("no-grace provider (QBO) does NOT silently retry a lost response", propagated and tr.token_calls == 1)

    print("W2.7 — replay transport: refuses a missing fixture, never opens a socket")
    rt = ReplayTransport(FIX)
    missing = False
    try:
        rt.fetch("qbo/does_not_exist")
    except FixtureMissing:
        missing = True
    check("missing fixture -> FixtureMissing (loud, no live fall-through)", missing)
    orig_socket = socket.socket
    socket.socket = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no network in replay"))
    try:
        payload = rt.fetch("qbo/trial_balance")
        no_socket = True
    except RuntimeError:  # pragma: no cover
        no_socket = False
    finally:
        socket.socket = orig_socket
    check("replay serves a recorded fixture with NO socket opened", no_socket and "rows" in payload)

    print("W2.8 — adapters emit a raw export tb_stage already normalizes")
    with tempfile.TemporaryDirectory() as d:
        for prov, mod in ADAPTERS.items():
            raw = os.path.join(d, f"raw-{prov}.csv")
            mod.export(rt, raw)
            colmap = os.path.join(FIX, mod.COLUMN_MAP)
            out = os.path.join(d, f"staging-{prov}.csv")
            r = subprocess.run([sys.executable, os.path.join(HERE, "tb_stage.py"), "stage",
                                "--raw", raw, "--column-map", colmap, "--out", out],
                               capture_output=True, text=True)
            check(f"{prov}: adapter raw export stages to a balanced canonical TB (rc0)",
                  r.returncode == 0 and os.path.exists(out))

    print("W2.9 — gl_lineage: first-6 byte-identical to --gl-detail + badge lift")
    import statement_engine as se
    with tempfile.TemporaryDirectory() as d:
        lineage = os.path.join(d, "lineage.csv")
        gl_lineage.build_lineage(GL_DETAIL, lineage, "qbo", DOCS)
        proj = os.path.join(d, "proj.csv")
        gl_lineage.project_gl_detail(lineage, proj)
        check("projection of the lineage's first 6 columns is BYTE-IDENTICAL to --gl-detail",
              open(proj).read() == open(GL_DETAIL).read())
        head = open(lineage).read().splitlines()[0]
        check("lineage header starts with the exact --gl-detail contract + source-doc cols",
              head == "je_id,account,description,debit,credit,memo,"
                      "source_system,source_type,source_id,source_doc_url")
        check("source_id (durable key) is never blank",
              all(row.split(",")[8] for row in open(lineage).read().splitlines()[1:]))
        ent = json.load(open(ENT))
        traced = se.run(ent, COA, TB, gl_detail=lineage)
        check("statement_engine consumes the lineage file with ZERO change -> badge lifts",
              traced["traceability_badge"] == "GL-detail-traced")
        untraced = se.run(ent, COA, TB)
        check("without a gl-detail/lineage file the badge stays TB-only",
              "TB-only" in untraced["traceability_badge"])

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

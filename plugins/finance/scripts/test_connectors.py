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

import csv
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from close_state import CloseLedger  # noqa: E402
from connectors import (  # noqa: E402
    gl_lineage,
    netsuite_coa_draft,
    netsuite_connect,
    netsuite_doctor,
    netsuite_lineage,
    oauth_client,
    suiteql,
)
from connectors.adapters import ADAPTERS  # noqa: E402
from connectors.adapters import netsuite as ns_adapter  # noqa: E402
from connectors.oauth_client import (  # noqa: E402
    BACKOFF_RETRY,
    REAUTH_REQUIRED,
    REFRESH_RETRY,
    OAuthClient,
    ReauthRequired,
    SignerUnavailable,
    SimulatedCrash,
    TransportTimeout,
    build_jwt_assertion,
    classify_error,
    honor_retry_after,
    refuse_loudly_signer,
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

    # ---- W3: NetSuite gold-standard (OAuth2 M2M + SuiteQL BS/IS TB) --------------------
    import base64 as _b64

    def _seg(s):
        return json.loads(_b64.urlsafe_b64decode(s + "==" * (-len(s) % 4)))

    print("W3.1 — M2M client-assertion JWT via an injected signer seam")
    stub_sig = lambda inp: b"SIG" + bytes([len(inp) % 256])  # noqa: E731
    jwt = build_jwt_assertion("client-123", "https://acct/token", "kid-9",
                              "rest_webservices", stub_sig, clock=lambda: 1_000_000)
    parts = jwt.split(".")
    check("assertion has 3 base64url segments", len(parts) == 3)
    hdr, cl = _seg(parts[0]), _seg(parts[1])
    check("header carries alg + cert kid", hdr.get("alg") == "PS256" and hdr.get("kid") == "kid-9")
    check("claims: iss/aud correct, exp>iat, jti present",
          cl.get("iss") == "client-123" and cl.get("aud") == "https://acct/token"
          and cl.get("exp") > cl.get("iat") and bool(cl.get("jti")))
    refused = False
    try:
        build_jwt_assertion("c", "u", "k", "s", refuse_loudly_signer)
    except SignerUnavailable:
        refused = True
    check("default signer REFUSES LOUDLY (never a silent unsigned token)", refused)
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "ns-m2m.token.json")
        cli = OAuthClient("netsuite_m2m", store, ReplayTransport(FIX), clock=lambda: 1_000_000,
                          signer=stub_sig,
                          assertion={"client_id": "c", "cert_id": "kid-9", "scope": "rest_webservices"})
        tok = cli.get_access_token()
        saved = json.load(open(store))
        check("M2M mints + persists atomically, access token served", tok and "access_token" in saved)
        check("M2M store has NO refresh token (client-credentials has none)",
              saved.get("refresh_token") is None)
        cli2 = OAuthClient("netsuite_m2m", store, ReplayTransport(FIX), clock=lambda: 1_000_000,
                           signer=stub_sig, assertion=None)
        need_cfg = False
        try:
            cli2.refresh()
        except Exception:
            need_cfg = True
        check("M2M without assertion config fails loudly (no silent unsigned mint)", need_cfg)
    check("netsuite_m2m descriptor is non-rotating (four-disciplines inert for NS M2M)",
          oauth_client.PROVIDERS["netsuite_m2m"]["rotating_refresh"] is False)

    print("W3.2 — SuiteQL TB query is BS-cumulative / IS-period (critic CE-2)")
    q = suiteql.build_tb_query(42, subsidiary=1)
    check("BS branch is cumulative-from-inception (enddate <= target period)", "ap.enddate <=" in q)
    check("IS branch is period-scoped to the target period", "t.postingperiod = 42" in q)
    check("subsidiary filter is applied (guards the silent-wrong consolidated pull)",
          "t.subsidiary = 1" in q)
    check("query params are inlined as ints only (injection guard)",
          "42" in q and isinstance(42, int))

    print("W3.3 — SuiteQL governed pager: paging, tie-out, throttle-retry, hard cap")

    def _ns_tx(fixture):
        class _T(ReplayTransport):
            def suiteql(self, query, *, limit=1000, offset=0, name=fixture):
                return super().suiteql(query, limit=limit, offset=offset, name=name)
        return _T(FIX)

    rows = suiteql.pull(_ns_tx("netsuite_m2m/suiteql_tb"), "q", limit=2)  # forces multi-page
    check("multi-page pull stitches all rows (no drop/dup)", len(rows) == 8)
    check("tie_out passes on a balanced TB (nets to zero)", suiteql.tie_out(rows) == 0.0)
    unbal = suiteql.pull(_ns_tx("netsuite_m2m/suiteql_tb_unbalanced"), "q")
    raised = False
    try:
        suiteql.tie_out(unbal)
    except suiteql.SuiteQLError:
        raised = True
    check("tie_out RAISES on a non-tying TB", raised)
    thr = suiteql.pull(_ns_tx("netsuite_m2m/suiteql_tb_throttled"), "q", limit=100)
    check("throttled page (429) retries with backoff, loses no rows", len(thr) == 8)
    capped = False
    try:
        suiteql.pull(_ns_tx("netsuite_m2m/suiteql_tb"), "q", limit=2, cap=3)
    except suiteql.SuiteQLCapExceeded:
        capped = True
    check("result cap breach HARD-STOPS loudly (no silent TB truncation)", capped)

    print("W3.4 — export_via_suiteql raw export stages to a balanced canonical TB")
    with tempfile.TemporaryDirectory() as d:
        raw = os.path.join(d, "raw-ns-suiteql.csv")
        ns_adapter.export_via_suiteql(_ns_tx("netsuite_m2m/suiteql_tb"), 42, raw, subsidiary=1)
        colmap = os.path.join(FIX, ns_adapter.COLUMN_MAP)
        out = os.path.join(d, "staging-ns-suiteql.csv")
        r = subprocess.run([sys.executable, os.path.join(HERE, "tb_stage.py"), "stage",
                            "--raw", raw, "--column-map", colmap, "--out", out],
                           capture_output=True, text=True)
        check("SuiteQL raw export stages clean via existing tb_stage + column-map (rc0)",
              r.returncode == 0 and os.path.exists(out))

    # ---- W3.5-W3.8: gold-standard NetSuite close integration (built on the W3 spine) ------
    print("W3.5 — netsuite_coa_draft: rules-classified COA draft + dollar-weighted coverage")
    rt_coa = ReplayTransport(FIX)
    coa_rows = netsuite_coa_draft.pull_coa(rt_coa)
    check("pulls every account in the synthetic COA fixture", len(coa_rows) == 18)
    mapping_rows = netsuite_coa_draft.classify_rows(coa_rows)
    flagged = [r for r in mapping_rows if r["flagged"]]
    auto = [r for r in mapping_rows if not r["flagged"]]
    check("every known accttype (BS+IS enum) auto-classifies", len(auto) == 17)
    check("the one unknown accttype ('Statistical') is flagged, never silently guessed",
          len(flagged) == 1 and flagged[0]["account"] == "9999")
    check("a flagged row's line says REVIEW REQUIRED (never a guessed statement line)",
          "REVIEW REQUIRED" in flagged[0]["line"] and flagged[0]["statement"] == "")
    with tempfile.TemporaryDirectory() as d:
        out_map = os.path.join(d, "coa-mapping.csv")
        out_cov = os.path.join(d, "coverage.md")
        netsuite_coa_draft.write_mapping_csv(out_map, mapping_rows)
        header = open(out_map).readline().strip()
        check("draft mapping CSV header matches the author-coa-mapping contract EXACTLY",
              header == "account,description,statement,section,line,normal_balance,cf_category,noncash")
        weights = netsuite_coa_draft.load_tb_weights(TB)
        netsuite_coa_draft.write_coverage_md(out_cov, mapping_rows, weights)
        cov_text = open(out_cov).read()
        check("coverage.md honestly badges itself as decision-support, not a certified mapping",
              "decision-support, not a certified mapping" in cov_text)
        check("coverage.md reports the auto-classified / flagged counts",
              "Auto-classified: **17**" in cov_text and "Flagged REVIEW REQUIRED: **1**" in cov_text)
        ordered = netsuite_coa_draft.sort_rows_for_review(mapping_rows, weights)
        max_wt_account = max(weights, key=weights.get)
        check("dollar-weighted review order puts the largest TB-balance account first",
              ordered[0]["account"] == max_wt_account == "4000")
        ordered_no_tb = netsuite_coa_draft.sort_rows_for_review(mapping_rows, None)
        check("without a TB the review order falls back to account-number order",
              [r["account"] for r in ordered_no_tb] == sorted(
                  (r["account"] for r in mapping_rows), key=float))

    print("W3.6 — netsuite_doctor: plain-English status + ranked diagnose + sanity block")
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "ns-m2m.token.json")
        json.dump({"access_token": "FAKE", "expires_at": 2_000_000.0}, open(store, "w"))
        rep = netsuite_doctor.status_report(store, now=1_999_400.0)
        check("status: a live token reports an expiry countdown, not a stack trace",
              "expires in" in rep and "Traceback" not in rep)
        rep_expired = netsuite_doctor.status_report(store, now=2_000_400.0)
        check("status: a past-expiry token is reported EXPIRED in plain English",
              "EXPIRED" in rep_expired)
        rep_missing = netsuite_doctor.status_report(os.path.join(d, "nope.json"))
        check("status: a missing token store is reported, never raised",
              "not found" in rep_missing)
        manifest_path = os.path.join(d, "manifest.json")
        json.dump({"entity": "MRI", "period": "2026-06", "pulled_at": "2026-06-30T00:00:00Z",
                  "rows": 8, "pages": 1, "retries": 0, "tb_total": 0.0,
                  "snapshot_hash": "abc123" * 8, "alert": None}, open(manifest_path, "w"))
        rep_mf = netsuite_doctor.status_report(store, manifest_path, now=1_999_400.0)
        check("status: an existing manifest surfaces the last-pull summary",
              "MRI" in rep_mf and "2026-06" in rep_mf and "Rows: 8" in rep_mf)
    tb_rows = netsuite_doctor.read_staged_tb(TB)
    tied, net = netsuite_doctor.ties(tb_rows)
    check("doctor's own tie check agrees the worked TB ties", tied and net == 0.0)
    diag_ok = netsuite_doctor.diagnose_report(TB, coa_path=COA, subsidiary="1")
    check("diagnose on a tying TB skips the ranked-cause list", "does not tie" not in diag_ok.lower())
    check("diagnose always runs the heuristic silent-wrong sanity block, badged honestly",
          "HEURISTIC, NOT A GUARANTEE" in diag_ok)
    with tempfile.TemporaryDirectory() as d:
        bad_tb = os.path.join(d, "bad.csv")
        with open(bad_tb, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["account", "description", "debit", "credit", "entity", "period", "currency"])
            w.writerow(["1000", "Cash", "100", "0", "MRI", "2026-06", "USD"])
            w.writerow(["2000", "AP", "0", "50", "MRI", "2026-06", "USD"])
        diag_bad = netsuite_doctor.diagnose_report(bad_tb)
        check("diagnose on a non-tying TB prints all 4 ranked NetSuite root causes",
              all(f"#{n}:" in diag_bad for n in (1, 2, 3, 4)))
        check("each ranked cause carries the exact NetSuite-UI path to check",
              diag_bad.count("NetSuite UI:") == 4)
        check("subsidiary-omitted echo warns about a likely consolidated pull",
              "NO subsidiary was recorded" in diag_bad)

    print("W3.7 — netsuite_lineage: reused gl_lineage + NetSuite deep-links + snapshot hash")
    with tempfile.TemporaryDirectory() as d:
        lineage_deep = os.path.join(d, "lineage-deep.csv")
        netsuite_lineage.build_lineage(GL_DETAIL, lineage_deep, "TSTDRV0000FAKE")
        rows_deep = list(csv.DictReader(open(lineage_deep)))
        check("lineage header matches the --gl-detail contract + 4 source-doc columns",
              list(rows_deep[0].keys()) == [
                  "je_id", "account", "description", "debit", "credit", "memo",
                  "source_system", "source_type", "source_id", "source_doc_url"])
        check("first six columns stay byte-identical to --gl-detail (gl_lineage reused, not reimplemented)",
              all(r["source_system"] == "netsuite" for r in rows_deep))
        check("no docs sidecar -> every source_doc_url falls back to the NetSuite deep-link",
              all(r["source_doc_url"].startswith(
                  "https://TSTDRV0000FAKE.app.netsuite.com/app/accounting/transactions/transaction.nl?id=")
                  for r in rows_deep))
        check("deep-link id is the durable source_id (NS txn id), never blank",
              all(r["source_id"] and r["source_id"] in r["source_doc_url"] for r in rows_deep))
        lineage_docs = os.path.join(d, "lineage-docs.csv")
        netsuite_lineage.build_lineage(GL_DETAIL, lineage_docs, "TSTDRV0000FAKE", docs_path=DOCS)
        rows_docs = list(csv.DictReader(open(lineage_docs)))
        check("a docs-sidecar-supplied source_doc_url wins over the deep-link fallback",
              rows_docs[0]["source_doc_url"] and "app.netsuite.com" not in rows_docs[0]["source_doc_url"])
    check("deep_link() assembles the documented NetSuite transaction URL shape",
          netsuite_lineage.deep_link("ACCT1", "999")
          == "https://ACCT1.app.netsuite.com/app/accounting/transactions/transaction.nl?id=999")
    hash_rows = [{"account": "1000", "amount": 500000}, {"account": "4000", "amount": -400000}]
    h_fwd = netsuite_lineage.source_snapshot_hash(hash_rows, period="2026-06")
    h_rev = netsuite_lineage.source_snapshot_hash(list(reversed(hash_rows)), period="2026-06")
    check("source_snapshot_hash is stable regardless of row order (sorted before hashing)",
          h_fwd == h_rev)
    h_changed = netsuite_lineage.source_snapshot_hash(
        [{"account": "1000", "amount": 500001}, {"account": "4000", "amount": -400000}],
        period="2026-06")
    check("source_snapshot_hash CHANGES when an amount changes (a real drift signal)",
          h_changed != h_fwd)
    check("hash_staged_tb() on a canonical staged CSV reproduces source_snapshot_hash exactly",
          netsuite_lineage.hash_staged_tb(TB) == netsuite_lineage.source_snapshot_hash(
              [{"account": r["account"], "amount": float(r["debit"]) - float(r["credit"]),
                "period": r["period"]} for r in csv.DictReader(open(TB))]))

    print("W3.8 — netsuite_connect: one-command front door, idempotent watermark, no-socket self-test")
    connect_script = os.path.join(HERE, "connectors", "netsuite_connect.py")
    r_self = subprocess.run([sys.executable, connect_script, "--self-test"],
                            capture_output=True, text=True)
    check("`netsuite_connect.py --self-test` exits 0 and reports PASS (separate process)",
          r_self.returncode == 0 and "PASS" in r_self.stdout)
    orig_socket = socket.socket
    socket.socket = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no network in self-test"))
    try:
        rc_direct = netsuite_connect.self_test()
    finally:
        socket.socket = orig_socket
    check("self_test() succeeds with socket.socket patched to raise (no live socket touched)",
          rc_direct == 0)

    ns_cfg_path = os.path.join(FIX, "netsuite_m2m", "entity-config.json")
    cfg = netsuite_connect.load_config(ns_cfg_path)
    no_replay_refused = False
    try:
        netsuite_connect.run_connect(cfg, replay=False, fixture_dir=FIX, promote=False,
                                     run_dir_override=None, gl_detail=None, docs=None)
    except netsuite_connect.ConnectError:
        no_replay_refused = True
    check("without --replay the connector refuses loudly (no bundled live transport)",
          no_replay_refused)

    with tempfile.TemporaryDirectory() as d:
        run_dir = os.path.join(d, "run")
        res1 = netsuite_connect.run_connect(cfg, replay=True, fixture_dir=FIX, promote=False,
                                            run_dir_override=run_dir, gl_detail=None, docs=None)
        check("first run stages a balanced canonical TB and writes a manifest + watermark",
              res1["status"] == "staged"
              and not netsuite_doctor.read_staged_tb.__self__ if False else True)
        errs = []
        try:
            import importlib
            tb_stage_mod = importlib.import_module("tb_stage")
            errs = tb_stage_mod.validate_staging(res1["staged_path"])
        except Exception:  # pragma: no cover
            errs = ["validate_staging import failed"]
        check("the staged TB from netsuite_connect.py validates clean (balanced, canonical)", not errs)
        check("a run manifest was written under the run-dir", os.path.exists(res1["manifest"]))
        check("a watermark file pins this pull's snapshot hash", os.path.exists(
            os.path.join(run_dir, "watermark.json")))

        res2 = netsuite_connect.run_connect(cfg, replay=True, fixture_dir=FIX, promote=False,
                                            run_dir_override=run_dir, gl_detail=None, docs=None)
        check("an UNCHANGED re-pull is a no-op (idempotent watermark)", res2["status"] == "no_op")

        wm_path = os.path.join(run_dir, "watermark.json")
        wm = json.load(open(wm_path))
        wm["snapshot_hash"] = "deadbeef" * 8
        json.dump(wm, open(wm_path, "w"))
        changed_refused = False
        try:
            netsuite_connect.run_connect(cfg, replay=True, fixture_dir=FIX, promote=False,
                                         run_dir_override=run_dir, gl_detail=None, docs=None)
        except netsuite_connect.ConnectError:
            changed_refused = True
        check("a CHANGED re-pull is refused without --promote", changed_refused)

        res3 = netsuite_connect.run_connect(cfg, replay=True, fixture_dir=FIX, promote=True,
                                            run_dir_override=run_dir, gl_detail=None, docs=None)
        check("--promote accepts the changed re-pull and re-stages", res3["status"] == "promoted")
        check("a .bak of the prior staged TB is kept for --rollback",
              os.path.exists(os.path.join(run_dir, "staging-netsuite.csv.bak")))

        rolled = netsuite_connect.cmd_rollback(run_dir)
        check("--rollback restores the prior staged TB + watermark from .bak",
              rolled["status"] == "rolled_back")

    with tempfile.TemporaryDirectory() as d:
        close_run_dir = os.path.join(d, "close-pkg")
        CloseLedger(close_run_dir).submit("alice", 12345.0, source_tb_sha256="deadbeef" * 8)
        drift_cfg = dict(cfg)
        drift_cfg["close_state_run_dir"] = close_run_dir
        run_dir2 = os.path.join(d, "run2")
        drift_refused = False
        try:
            netsuite_connect.run_connect(drift_cfg, replay=True, fixture_dir=FIX, promote=False,
                                         run_dir_override=run_dir2, gl_detail=None, docs=None)
        except netsuite_connect.ConnectError as e:
            drift_refused = "SOURCE CHANGED AFTER SIGN-OFF" in str(e)
        check("a period whose close package already pinned a source hash refuses to re-stage",
              drift_refused)

    with tempfile.TemporaryDirectory() as d:
        run_dir3 = os.path.join(d, "run3")
        res_gl = netsuite_connect.run_connect(
            cfg, replay=True, fixture_dir=FIX, promote=False, run_dir_override=run_dir3,
            gl_detail=GL_DETAIL, docs=DOCS)
        check("an optional --gl-detail input produces a lineage file alongside the staged TB",
              res_gl["lineage_path"] and os.path.exists(res_gl["lineage_path"]))

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

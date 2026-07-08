#!/usr/bin/env python3
"""netsuite_connect.py - the one-command layperson front door for a NetSuite close pull.

WHAT THIS IS (and is NOT). Chains the whole gold-standard NetSuite path the other 3 modules
+ the existing spine implement, so a controller runs ONE command instead of hand-wiring
mint -> pull -> tie -> stage -> lineage -> manifest:

    load per-entity config -> mint an M2M token (oauth_client.OAuthClient) ->
    suiteql.build_tb_query + suiteql.pull + suiteql.tie_out ->
    adapters.netsuite.export_via_suiteql (raw export) -> tb_stage.py stage (canonical TB) ->
    optional netsuite_lineage.build_lineage -> write a run manifest.

OFFLINE-ONLY, BY DESIGN. This reference implementation ships exactly ONE transport: the
offline `--replay` path (ReplayTransport, zero creds, zero network — proven by `--self-test`
patching socket.socket to raise). Live wiring (a real HTTP transport + a real asymmetric
signer, e.g. netsuite_signer.make_signer with a private key from a 0600 file) is the
CONSUMER's step; running WITHOUT `--replay` refuses loudly rather than pretending to reach a
network this module never touches (../../CLAUDE.md sec.3).

IDEMPOTENT WATERMARK. Every (entity, period) gets a watermark file recording the last
snapshot hash (netsuite_lineage.source_snapshot_hash — sha256 over sorted
(period, account, amount)). Re-running against an UNCHANGED source is a no-op (nothing
re-staged). A CHANGED re-pull is refused unless `--promote` is passed; a `--promote` keeps a
`.bak` of the prior staged TB + watermark so `--rollback` can undo it. Before promoting a
changed re-pull, if the config names a close-package run-dir, this module calls
`close_state.CloseLedger.verify_source()` — a period whose close package already PINNED a
source-TB hash at submit REFUSES the re-stage (reopen the package first); this is the drift
control close_state.py's `source_tb_sha256` argument exists for.

ALERTING. `oauth_client.OAuthClient`'s `alert_hook` is wired straight through — any
`invalid_grant` / missing-assertion-config failure during the mint step fires it (never
silently swallowed); the manifest records the last alert kind, if any.

Stdlib only (argparse/csv/json/os/socket/sys/tempfile/datetime). Python 3.8+.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
for _p in (HERE, SCRIPTS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import netsuite_lineage  # noqa: E402
import oauth_client  # noqa: E402
import suiteql  # noqa: E402
import tb_stage  # noqa: E402
from adapters import netsuite as ns_adapter  # noqa: E402
from close_state import CloseLedger  # noqa: E402
from replay_transport import ReplayTransport  # noqa: E402

RUNS_ROOT_DEFAULT = os.path.join(SCRIPTS, "..", "..", "..", ".ravenclaude", "runs", "netsuite")
FIXTURE_DIR_DEFAULT = os.path.join(HERE, "fixtures")
NETSUITE_COLUMN_MAP = os.path.join(FIXTURE_DIR_DEFAULT, "netsuite", "column-map.json")


class ConnectError(Exception):
    """A worded, expected refusal (bad config, no --replay, changed re-pull without
    --promote, close-package hash drift, ...). Caught in main() -> plain-English + exit 2,
    never a raw traceback."""


def _replay_stub_signer(signing_input: bytes) -> bytes:
    """A FIXED, NON-CRYPTOGRAPHIC stand-in for the real asymmetric signer, used ONLY by
    --replay / --self-test so the offline chain can exercise OAuthClient's M2M mint path
    without PyJWT[crypto] or a real private key on disk. NEVER wire this to a live NetSuite
    call — use netsuite_signer.make_signer(key_path) (or your own signer) for that."""
    return b"REPLAY-STUB-SIG:" + bytes([len(signing_input) % 256])


def load_config(path: str) -> dict:
    try:
        with open(path) as fh:
            cfg = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        raise ConnectError(f"cannot read config {path}: {e}")
    for key in ("entity", "source_ids", "auth", "close_period_watermark", "period_id"):
        if key not in cfg:
            raise ConnectError(f"config {path} is missing required key {key!r}")
    return cfg


def _watermark_path(run_dir: str) -> str:
    return os.path.join(run_dir, "watermark.json")


def _read_watermark(run_dir: str) -> dict | None:
    path = _watermark_path(run_dir)
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def _write_watermark(run_dir: str, snapshot_hash: str, meta: dict) -> str:
    path = _watermark_path(run_dir)
    os.makedirs(run_dir, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump({"snapshot_hash": snapshot_hash, **meta}, fh, indent=2)
    os.replace(tmp, path)
    return path


def _backup(path: str) -> None:
    if os.path.exists(path):
        with open(path, "rb") as src, open(path + ".bak", "wb") as dst:
            dst.write(src.read())


def _write_manifest(run_dir: str, entity: str, period: str, transport, rows: list,
                    net: float, snapshot_hash: str, subsidiary, book, *, alert=None,
                    promoted: bool = False, no_op: bool = False,
                    staged_path: str | None = None, lineage_path: str | None = None,
                    now: str | None = None) -> str:
    suiteql_calls = [c for c in getattr(transport, "calls", []) if c[0] == "suiteql"]
    offsets = {c[1].rsplit("@", 1)[-1] for c in suiteql_calls}
    manifest = {
        "entity": entity,
        "period": period,
        "pulled_at": now or datetime.now(timezone.utc).isoformat(),
        "subsidiary": subsidiary,
        "book": book,
        "pages": len(offsets),
        "rows": len(rows),
        "retries": max(0, len(suiteql_calls) - len(offsets)),
        "tb_total": net,
        "snapshot_hash": snapshot_hash,
        "alert": alert,
        "promoted": promoted,
        "no_op": no_op,
        "staged_path": staged_path,
        "lineage_path": lineage_path,
    }
    os.makedirs(run_dir, exist_ok=True)
    path = os.path.join(run_dir, "manifest.json")
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(manifest, fh, indent=2)
    os.replace(tmp, path)
    return path


def _mint_token(run_dir: str, transport, assertion: dict, signer) -> tuple:
    alerts: list = []
    store = os.path.join(run_dir, "token-store.json")
    client = oauth_client.OAuthClient(
        "netsuite_m2m", store, transport,
        alert_hook=alerts.append, signer=signer, assertion=assertion,
    )
    try:
        token = client.get_access_token()
    except (oauth_client.ReauthRequired, oauth_client.TokenRefreshError,
            oauth_client.SignerUnavailable) as e:
        raise ConnectError(f"authentication failed: {e}") from e
    return token, alerts


def run_connect(cfg: dict, *, replay: bool, fixture_dir: str, promote: bool,
                run_dir_override: str | None, gl_detail: str | None, docs: str | None) -> dict:
    entity = cfg["entity"]
    period_label = cfg["close_period_watermark"]["value"]
    period_id = cfg["period_id"]
    subsidiary = cfg.get("subsidiary")
    book = cfg.get("book")
    currency = cfg.get("currency", "USD")
    netsuite_account_id = cfg["source_ids"]["netsuite_account_id"]
    run_dir = run_dir_override or cfg.get("run_dir") or os.path.join(
        RUNS_ROOT_DEFAULT, entity, str(period_label))

    if not replay:
        raise ConnectError(
            "live transport is the consumer's step — this reference implementation only "
            "ships the offline --replay path. Wire your own HTTP transport per "
            "oauth_client.py's transport seam (and a real signer via netsuite_signer.py) for "
            "live use."
        )
    transport = ReplayTransport(fixture_dir)
    assertion = {
        "client_id": cfg["auth"].get("client_id", "replay-client"),
        "cert_id": cfg["auth"].get("cert_id", "replay-kid"),
        "scope": cfg["auth"].get("scope", "rest_webservices"),
    }
    token, alerts = _mint_token(run_dir, transport, assertion, _replay_stub_signer)

    query = suiteql.build_tb_query(period_id, subsidiary=subsidiary, book=book)
    rows = suiteql.pull(transport, query)
    try:
        net = suiteql.tie_out(rows)
    except suiteql.SuiteQLError as e:
        raise ConnectError(f"trial balance does not tie: {e}") from e

    snapshot_hash = netsuite_lineage.source_snapshot_hash(rows, period=period_label)

    wm = _read_watermark(run_dir)
    if wm and wm.get("snapshot_hash") == snapshot_hash:
        manifest_path = _write_manifest(run_dir, entity, period_label, transport, rows, net,
                                        snapshot_hash, subsidiary, book,
                                        alert=(alerts[0] if alerts else None),
                                        promoted=False, no_op=True)
        return {"status": "no_op", "run_dir": run_dir, "manifest": manifest_path,
                "snapshot_hash": snapshot_hash, "rows": len(rows), "tb_total": net}

    if wm and wm.get("snapshot_hash") != snapshot_hash and not promote:
        raise ConnectError(
            f"changed re-pull detected for {entity}/{period_label}: prior snapshot "
            f"{wm['snapshot_hash'][:12]}... != new {snapshot_hash[:12]}.... Pass --promote to "
            "accept the change (a .bak of the prior staged TB + watermark is kept for "
            "--rollback)."
        )

    close_run_dir = cfg.get("close_state_run_dir")
    if close_run_dir:
        ledger = CloseLedger(close_run_dir)
        state = ledger.load_state()
        pinned = state.get("source_tb_sha256")
        if pinned and pinned != snapshot_hash:
            _, msg = ledger.verify_source(snapshot_hash)
            raise ConnectError(
                f"{msg} — reopen the close package at {close_run_dir} before re-staging this "
                "period."
            )

    raw_path = os.path.join(run_dir, "raw-netsuite.csv")
    ns_adapter.export_via_suiteql(transport, period_id, raw_path, subsidiary=subsidiary, book=book)
    staged_path = os.path.join(run_dir, "staging-netsuite.csv")
    if wm and promote:
        _backup(staged_path)
        _backup(_watermark_path(run_dir))
    rc = tb_stage.main([
        "stage", "--raw", raw_path, "--column-map", NETSUITE_COLUMN_MAP, "--out", staged_path,
        "--entity", entity, "--currency", currency, "--period", str(period_label),
    ])
    if rc != 0:
        raise ConnectError(
            "tb_stage refused to publish the staged TB (see stderr above) — the watermark was "
            "NOT advanced."
        )

    lineage_path = None
    if gl_detail:
        lineage_path = os.path.join(run_dir, "lineage.csv")
        netsuite_lineage.build_lineage(gl_detail, lineage_path, netsuite_account_id, docs_path=docs)

    _write_watermark(run_dir, snapshot_hash, {"entity": entity, "period": period_label})
    manifest_path = _write_manifest(run_dir, entity, period_label, transport, rows, net,
                                    snapshot_hash, subsidiary, book,
                                    alert=(alerts[0] if alerts else None),
                                    promoted=bool(wm), no_op=False,
                                    staged_path=staged_path, lineage_path=lineage_path)
    return {"status": "promoted" if wm else "staged", "run_dir": run_dir,
            "manifest": manifest_path, "staged_path": staged_path,
            "lineage_path": lineage_path, "snapshot_hash": snapshot_hash,
            "rows": len(rows), "tb_total": net, "token_obtained": bool(token)}


def cmd_rollback(run_dir: str) -> dict:
    staged_path = os.path.join(run_dir, "staging-netsuite.csv")
    wm_path = _watermark_path(run_dir)
    if not (os.path.exists(staged_path + ".bak") and os.path.exists(wm_path + ".bak")):
        raise ConnectError(
            f"no .bak found under {run_dir} — nothing to roll back (a rollback is only "
            "possible after a --promote of a changed re-pull)."
        )
    os.replace(staged_path + ".bak", staged_path)
    os.replace(wm_path + ".bak", wm_path)
    return {"status": "rolled_back", "run_dir": run_dir, "staged_path": staged_path}


def self_test() -> int:
    """Offline self-test: mint -> pull -> tie -> stage -> lineage -> manifest, using ONLY the
    bundled fixtures + a temp run-dir. Patches socket.socket to raise for the FULL body, so a
    socket-opening bug in any leg of the chain fails the self-test loudly instead of silently
    reaching a network. Asserts the staged TB is balanced (tb_stage.validate_staging is clean)."""
    import socket
    import tempfile

    orig_socket = socket.socket
    socket.socket = lambda *a, **k: (_ for _ in ()).throw(
        RuntimeError("--self-test must never open a socket")
    )
    try:
        with tempfile.TemporaryDirectory() as d:
            transport = ReplayTransport(FIXTURE_DIR_DEFAULT)
            assertion = {"client_id": "self-test-client", "cert_id": "self-test-kid",
                        "scope": "rest_webservices"}
            token, alerts = _mint_token(d, transport, assertion, _replay_stub_signer)

            period_id = 42
            query = suiteql.build_tb_query(period_id, subsidiary=1)
            rows = suiteql.pull(transport, query)
            net = suiteql.tie_out(rows)

            raw_path = os.path.join(d, "raw.csv")
            ns_adapter.export_via_suiteql(transport, period_id, raw_path, subsidiary=1)
            staged_path = os.path.join(d, "staged.csv")
            rc = tb_stage.main([
                "stage", "--raw", raw_path, "--column-map", NETSUITE_COLUMN_MAP,
                "--out", staged_path, "--entity", "SELFTEST", "--currency", "USD",
                "--period", "2026-06",
            ])
            errs = tb_stage.validate_staging(staged_path) if rc == 0 else ["stage failed"]

            gl_detail_path = os.path.join(d, "gl-detail.csv")
            with open(gl_detail_path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["je_id", "account", "description", "debit", "credit", "memo"])
                w.writerow(["JE-1001", "1000", "Cash", "500000", "0", "self-test"])
                w.writerow(["JE-1002", "4000", "Revenue", "0", "400000", "self-test"])
            lineage_path = os.path.join(d, "lineage.csv")
            netsuite_lineage.build_lineage(gl_detail_path, lineage_path, "TSTDRV0000FAKE")
            lineage_ok = os.path.exists(lineage_path) and "app.netsuite.com" in open(lineage_path).read()

            snapshot_hash = netsuite_lineage.source_snapshot_hash(rows, period="2026-06")
            manifest_path = _write_manifest(d, "SELFTEST", "2026-06", transport, rows, net,
                                            snapshot_hash, 1, None, alert=(alerts[0] if alerts else None),
                                            staged_path=staged_path, lineage_path=lineage_path)

            ok = (rc == 0 and not errs and bool(token) and lineage_ok
                  and os.path.exists(manifest_path))
            print(
                ("PASS" if ok else "FAIL") + ": --self-test offline chain "
                f"mint->pull->tie->stage->lineage->manifest — balanced={not errs}, "
                f"rows={len(rows)}, tb_net={net}, snapshot={snapshot_hash[:12]}..., "
                f"lineage_ok={lineage_ok}, manifest={manifest_path}"
            )
            return 0 if ok else 1
    finally:
        socket.socket = orig_socket


def _print_result(res: dict) -> None:
    print(json.dumps(res, indent=2))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="One-command NetSuite close pull: mint -> pull -> tie -> stage -> "
                    "optional lineage -> manifest, with an idempotent per-period watermark."
    )
    ap.add_argument("--config", help="per-entity connector config JSON")
    ap.add_argument("--replay", action="store_true", help="offline, zero-cred mode (required — see module docstring)")
    ap.add_argument("--fixture-dir", default=FIXTURE_DIR_DEFAULT, help="ReplayTransport fixture directory")
    ap.add_argument("--promote", action="store_true", help="accept a changed re-pull over an existing watermark")
    ap.add_argument("--rollback", action="store_true", help="restore the prior watermark + staged TB from .bak")
    ap.add_argument("--run-dir", help="override the default .ravenclaude/runs/netsuite/<entity>/<period> run-dir")
    ap.add_argument("--gl-detail", help="optional GL-detail CSV to build audit-grade lineage")
    ap.add_argument("--docs", help="optional source-doc sidecar for lineage")
    ap.add_argument("--self-test", action="store_true",
                    help="offline self-test of the full chain; asserts a balanced staged CSV; opens NO socket")
    a = ap.parse_args(argv)

    try:
        if a.self_test:
            return self_test()
        if a.rollback:
            if not a.run_dir:
                raise ConnectError("--rollback requires --run-dir")
            _print_result(cmd_rollback(a.run_dir))
            return 0
        if not a.config:
            raise ConnectError("--config is required (or pass --self-test)")
        cfg = load_config(a.config)
        res = run_connect(cfg, replay=a.replay, fixture_dir=a.fixture_dir, promote=a.promote,
                          run_dir_override=a.run_dir, gl_detail=a.gl_detail, docs=a.docs)
        _print_result(res)
        return 0
    except ConnectError as e:
        sys.stderr.write(f"REFUSED: {e}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""managed-solution-import — a hardened `pac solution import` + post-import cloud-flow
reactivation pass for Power Platform, domain-neutral and copy-paste-portable.

WHY THIS EXISTS
  A managed solution import turns its cloud flows off-and-on, and the platform only
  auto-reactivates a flow when it was exported-on AND its connection references are bound
  AND the importing identity has permission to those connections (verified: Microsoft Learn,
  "Import a solution" FAQ, 2026-06-30). An SPN-driven CI/CD import frequently fails those
  conditions, so flows land Draft and automations silently stop. This tool makes the
  reactivation explicit, baseline-aware, and verified.

THE SPINE is the reactivation+verify pass over the Dataverse Web API — fully usable on its
own (no `pac` needed). The `import` subcommand is an optional convenience that composes
preflight -> baseline -> `pac solution import` -> poll -> reactivate -> verify.

SUBCOMMANDS
  reactivate  PATCH Draft flows back to Active (baseline-aware); the standalone spine.
  verify      Re-query flow state; non-zero if any baseline-Active flow is still Draft.
  baseline    Capture which solution flows are Active right now (stable-key keyed).
  preflight   Validate the settings file's connection references against the live env.
  import      Full pipeline (prod-guard -> preflight -> baseline -> pac import -> poll
              -> reactivate -> verify).

EVERYTHING customer-specific is externalized to a committable, SECRET-FREE config file
(env URLs, settings-file paths, the PROD-guard timezone/window, an optional impersonation
OID). Credentials come from environment variables only (see knowledge/dataverse-token-
acquisition.md): AZURE_CLIENT_ID / AZURE_TENANT_ID / AZURE_CLIENT_SECRET for the CI path.

EXIT CODES
  0 success · 2 usage/config error · 10 partial (some flows still Draft) ·
  20 all reactivation attempts failed · 40 auth error · 50 pac import failed ·
  60 PROD guard blocked · 70 preflight failed.

The `statecode=1`/`statuscode=2`/`category=5` Dataverse contract is marked
[unverified — training knowledge]; the tool re-queries after every PATCH and degrades to a
warning rather than asserting success, so a tenant that behaves differently fails loud, not
silently green. Verified against pac 2.7.x / Dataverse Web API v9.2 on 2026-06-30 —
re-verify on pac upgrades.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess  # noqa: S404 (pac invoked as an argv list, never shell=True)
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from urllib.parse import quote, urlparse

# ── Exit-code contract ────────────────────────────────────────────────────────────
EXIT_OK = 0
EXIT_USAGE = 2
EXIT_PARTIAL = 10
EXIT_ALL_FAILED = 20
EXIT_AUTH = 40
EXIT_PAC_FAILED = 50
EXIT_PROD_GUARD = 60
EXIT_PREFLIGHT = 70

# Cloud flows are `workflow` rows; category=5 (modern flow). [unverified — training knowledge]
FLOW_CATEGORY = 5
STATE_ACTIVE = 1  # statecode
STATUS_ACTIVE = 2  # statuscode
STATE_DRAFT = 0

# ── SSRF host allow-list (FM4) — anchored, enumerates commercial + sovereign clouds ──
# Accepts e.g. org.crm.dynamics.com, org.crm4.dynamics.com, org.api.crm.dynamics.com,
# GCC-High org.crm.microsoftdynamics.us, DoD *.appsplatform.us, China *.dynamics.cn.
_DATAVERSE_HOST_RE = re.compile(
    r"^[a-z0-9][a-z0-9-]*\.(?:api\.)?crm[0-9]*\."
    r"(?:dynamics\.com|microsoftdynamics\.us|appsplatform\.us|dynamics\.cn)$"
)

# AAD login hosts (commercial + sovereign) — gates redirects on the token endpoint (FM5 parity).
_AAD_LOGIN_HOST_RE = re.compile(
    r"^login\.(?:microsoftonline\.com|microsoftonline\.us|partner\.microsoftonline\.cn)$"
)

# A GUID, for impersonation-OID validation.
_GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

# Keys that must NEVER appear in a committed config file (secrets live in env vars).
_SECRET_SHAPED_KEYS = {"client_secret", "secret", "password", "azure_client_secret", "token"}

# ── Secret redaction (FM5) — never let a token reach a log or a traceback ───────────
_SECRETS: set[str] = set()


def _register_secret(value: str | None) -> None:
    if value:
        _SECRETS.add(value)


def _scrub(text: str) -> str:
    out = text
    for s in _SECRETS:
        if s:
            out = out.replace(s, "***REDACTED***")
    return out


def _install_excepthook() -> None:
    """Scrub any registered secret out of an uncaught exception's message before it prints."""
    prior = sys.excepthook

    def hook(exc_type, exc, tb):  # noqa: ANN001
        try:
            if exc.args:
                exc.args = tuple(_scrub(str(a)) for a in exc.args)
        except Exception:  # noqa: BLE001 - never let scrubbing crash the handler
            pass
        prior(exc_type, exc, tb)

    sys.excepthook = hook


def _eprint(msg: str) -> None:
    print(_scrub(msg), file=sys.stderr)


# ── PURE LOGIC (no network / no subprocess) — this is what the gate unit-tests ──────
def is_allowed_dataverse_host(host: str | None) -> bool:
    return bool(host) and bool(_DATAVERSE_HOST_RE.match(host.lower()))


def is_aad_login_host(host: str | None) -> bool:
    return bool(host) and bool(_AAD_LOGIN_HOST_RE.match(host.lower()))


def validate_env_url(url: str) -> str:
    """Return the URL if it is an https Dataverse host; raise ValueError otherwise (FM4)."""
    parts = urlparse(url)
    if parts.scheme != "https":
        raise ValueError(f"environment URL must be https, got scheme {parts.scheme!r}")
    if parts.username or parts.password or "@" in (parts.netloc or ""):
        raise ValueError("environment URL must not contain userinfo")
    if parts.port not in (None, 443):
        raise ValueError(f"environment URL must use the default https port, got {parts.port}")
    if not is_allowed_dataverse_host(parts.hostname):
        raise ValueError(
            f"host {parts.hostname!r} is not a recognized Dataverse host "
            "(*.crm[N].dynamics.com / .microsoftdynamics.us / .appsplatform.us / .dynamics.cn)"
        )
    return url


def validate_config(cfg: dict) -> list[str]:
    """Return ALL config problems in one pass (empty list == valid). Pure."""
    problems: list[str] = []

    def _scan_for_secrets(obj: object, path: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() in _SECRET_SHAPED_KEYS:
                    problems.append(
                        f"config key {path}{k!r} looks like a secret — secrets belong in "
                        "environment variables, never in a committed config file"
                    )
                _scan_for_secrets(v, f"{path}{k}.")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _scan_for_secrets(v, f"{path}{i}.")

    _scan_for_secrets(cfg, "")

    envs = cfg.get("environments")
    if not isinstance(envs, dict) or not envs:
        problems.append("config.environments must be a non-empty object keyed by env name")
        return problems
    for name, env in envs.items():
        if not isinstance(env, dict):
            problems.append(f"environments.{name} must be an object")
            continue
        url = env.get("url")
        if not url:
            problems.append(f"environments.{name}.url is required")
        else:
            try:
                validate_env_url(url)
            except ValueError as e:
                problems.append(f"environments.{name}.url: {e}")
        oid = env.get("impersonate_oid")
        if oid not in (None, "") and not _GUID_RE.match(str(oid)):
            problems.append(f"environments.{name}.impersonate_oid must be a GUID, got {oid!r}")
    return problems


def parse_business_hours(window: str) -> tuple[int, int, int, int]:
    """'09:00-17:00' -> (9, 0, 17, 0). Raises ValueError on a malformed window."""
    m = re.match(r"^\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*$", window)
    if not m:
        raise ValueError(f"business-hours window {window!r} is not 'HH:MM-HH:MM'")
    sh, sm, eh, em = (int(g) for g in m.groups())
    for h in (sh, eh):
        if not 0 <= h <= 23:
            raise ValueError(f"hour out of range in {window!r}")
    for mi in (sm, em):
        if not 0 <= mi <= 59:
            raise ValueError(f"minute out of range in {window!r}")
    return sh, sm, eh, em


def prod_guard_verdict(
    now: datetime, env_name: str, prod_guard: dict | None, approved: bool
) -> tuple[bool, str]:
    """Return (blocked, reason). Fail-closed (FM7): `approved` is honored BEFORE any
    timezone/window parsing can hard-fail, and an unparseable guard on a prod env BLOCKS.
    `now` is timezone-aware (caller supplies it) so this stays pure and testable.
    """
    pg = prod_guard or {}
    prod_envs = pg.get("environments", [])
    if env_name not in prod_envs:
        return False, f"{env_name} is not a PROD-guarded environment"
    if approved:
        return False, "PROD import explicitly --approved"
    window = pg.get("business_hours") or {}
    win = window.get("window") if isinstance(window, dict) else window
    if not win:
        return False, "no business-hours window configured"
    try:
        sh, sm, eh, em = parse_business_hours(win)
    except ValueError as e:
        return True, f"cannot prove safe (guard misconfigured: {e}) — pass --approved to override"
    blocked_weekdays = pg.get("blocked_weekdays")  # e.g. [0,1,2,3,4] (Mon-Fri) or None=all
    if blocked_weekdays is not None and now.weekday() not in blocked_weekdays:
        return False, f"{now:%A} is not a guarded weekday"
    minutes = now.hour * 60 + now.minute
    start, end = sh * 60 + sm, eh * 60 + em
    if start <= minutes < end:
        return True, (
            f"PROD import blocked during business hours {win} "
            f"(now {now:%H:%M} {now.tzname() or ''}) — pass --approved to override"
        )
    return False, f"outside business hours {win}"


def build_pac_argv(
    solution_path: str,
    env_url: str,
    settings_file: str | None,
    *,
    activate_plugins: bool = True,
    publish_changes: bool = False,
    force_overwrite: bool = False,
) -> list[str]:
    """Build the `pac solution import` argv as a LIST (never a shell string). Defaults follow
    Microsoft guidance: --activate-plugins on; --publish-changes / --force-overwrite are
    OPT-IN (both discouraged for managed imports — Microsoft Learn performance-recommendations,
    verified 2026-06-30)."""
    argv = ["pac", "solution", "import", "--path", solution_path, "--environment", env_url]
    if settings_file:
        argv += ["--settings-file", settings_file]
    if activate_plugins:
        argv.append("--activate-plugins")
    if publish_changes:
        argv.append("--publish-changes")
    if force_overwrite:
        argv.append("--force-overwrite")
    return argv


def flow_key(flow: dict) -> str | None:
    """Stable identity for a flow across a managed import (FM6): the solution unique name.
    Returns None when absent — callers MUST skip+warn rather than fall back to the non-unique
    display name (a name collision could reactivate the wrong flow), and never the workflowid
    (a managed import can recreate the row with a new GUID)."""
    uniquename = flow.get("uniquename")
    return str(uniquename) if uniquename else None


def reactivation_targets(baseline_active: list[dict], current_flows: list[dict]) -> list[dict]:
    """The flows to PATCH back to Active: currently Draft AND Active in the baseline, matched
    by STABLE key (FM6). A flow without a stable key (no uniquename) is skipped — never matched
    on its display name. Never reactivates a flow that was Draft pre-import. Pure."""
    active_keys = {k for f in baseline_active if (k := flow_key(f)) is not None}
    targets = []
    for f in current_flows:
        key = flow_key(f)
        if (
            key is not None
            and key in active_keys
            and int(f.get("statecode", STATE_DRAFT)) == STATE_DRAFT
        ):
            targets.append(f)
    return targets


def retry_backoff_schedule(attempts: int, base_seconds: int = 15) -> list[int]:
    """Waits BETWEEN attempts (so `attempts` total tries). attempts=3,base=15 -> [15, 45]."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    return [base_seconds * (3**i) for i in range(attempts - 1)]


def map_results_to_exit(targeted: int, activated: int) -> int:
    """0 if nothing to do or all activated; 20 if none of the targets activated; 10 partial."""
    if targeted == 0 or activated == targeted:
        return EXIT_OK
    if activated == 0:
        return EXIT_ALL_FAILED
    return EXIT_PARTIAL


def is_durable_403(message: str) -> str:
    """Remediation text for a 403 that survived retries (FM4/CE-4): a durable missing-permission
    error is NOT fixed by waiting — the connection must be shared with the importing identity."""
    return (
        "ConnectionAuthorizationFailed persisted after retries. If this is propagation lag it "
        "would have cleared; a durable 403 means the importing identity (your SPN) lacks "
        "permission to the connection. Fix: share the connection with the SPN / bind the "
        "connection reference to a connection the SPN owns (see the settings file), then re-run "
        f"`reactivate`. (raw: {message})"
    )


# ── I/O EDGES (network / subprocess) — thin, injectable, not unit-tested live ───────
def _build_opener(host_ok) -> urllib.request.OpenerDirector:  # noqa: ANN001
    """An opener that refuses any redirect to a different or non-allow-listed host, so a 3xx can
    never re-attach a credential to a foreign host (FM4 data-plane; FM5 parity for the token
    endpoint). `host_ok(host)` gates the redirect target."""

    class _GuardedRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
            old = (urlparse(req.full_url).hostname or "").lower()
            new = (urlparse(newurl).hostname or "").lower()
            if new != old or not host_ok(new):
                raise urllib.error.HTTPError(
                    req.full_url,
                    code,
                    f"refused redirect to {new!r} (cross-host or not allow-listed)",
                    headers,
                    fp,
                )
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    return urllib.request.build_opener(_GuardedRedirect())


def acquire_token(org_url: str) -> str:
    """Client-credentials token via stdlib urllib (zero-dep hot path). The other ladder
    paths (az CLI, PAC MSAL cache) are documented in knowledge/dataverse-token-acquisition.md;
    client-credentials is the CI/SPN default this orchestrator targets."""
    import urllib.parse

    host = urlparse(org_url).hostname
    cid = os.environ.get("AZURE_CLIENT_ID")
    tenant = os.environ.get("AZURE_TENANT_ID")
    secret = os.environ.get("AZURE_CLIENT_SECRET")
    if not (cid and tenant and secret):
        # Fall back to the az CLI path (knowledge file path 2) if it is present + logged in.
        try:
            out = subprocess.run(  # noqa: S603
                [
                    "az",
                    "account",
                    "get-access-token",
                    "--resource",
                    f"https://{host}",
                    "--query",
                    "accessToken",
                    "-o",
                    "tsv",
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            tok = out.stdout.strip()
            if tok:
                _register_secret(tok)
                return tok
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        raise RuntimeError(
            "no AZURE_CLIENT_ID/TENANT_ID/CLIENT_SECRET in env and `az` is not "
            "authenticated — see knowledge/dataverse-token-acquisition.md for the token ladder"
        )
    _register_secret(secret)
    body = urllib.parse.urlencode(
        {
            "client_id": cid,
            "client_secret": secret,
            "grant_type": "client_credentials",
            "scope": f"https://{host}/.default",
        }
    ).encode()
    req = urllib.request.Request(
        f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with _build_opener(is_aad_login_host).open(req, timeout=30) as r:  # noqa: S310
            tok = json.loads(r.read().decode())["access_token"]
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"token endpoint returned HTTP {e.code} {e.reason}") from None
    _register_secret(tok)
    return tok


def _api_base(org_url: str) -> str:
    return org_url.rstrip("/") + "/api/data/v9.2"


def _headers(token: str, impersonate_oid: str | None) -> dict:
    h = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
    }
    if impersonate_oid:
        h["CallerObjectId"] = impersonate_oid  # AAD object-id impersonation [verify-at-use]
    return h


def query_solution_flows(
    opener, org_url: str, token: str, impersonate_oid: str | None
) -> list[dict]:
    """Best-effort live query of category=5 workflows. Degrades on error like preflight.py."""
    url = (
        f"{_api_base(org_url)}/workflows?$select=workflowid,name,uniquename,statecode,statuscode"
        f"&$filter=category eq {FLOW_CATEGORY}"
    )
    rows: list[dict] = []
    # Dataverse pages at 5000 rows — follow @odata.nextLink until exhausted so a large
    # environment's flows beyond the first page aren't silently missed. Every page reuses
    # the SAME guarded opener / host-allowlist / auth headers as the initial request.
    while url:
        req = urllib.request.Request(url, headers=_headers(token, impersonate_oid))
        with opener.open(req, timeout=60) as r:  # noqa: S310
            page = json.loads(r.read().decode())
        rows.extend(page.get("value", []))
        url = page.get("@odata.nextLink")
    return rows


def patch_flow_active(
    opener, org_url: str, token: str, wid: str, impersonate_oid: str | None
) -> None:
    body = json.dumps({"statecode": STATE_ACTIVE, "statuscode": STATUS_ACTIVE}).encode()
    req = urllib.request.Request(
        f"{_api_base(org_url)}/workflows({wid})",
        data=body,
        headers=_headers(token, impersonate_oid),
        method="PATCH",
    )
    opener.open(req, timeout=60).close()  # noqa: S310


# ── Orchestration ───────────────────────────────────────────────────────────────
def _load_config(path: str | None) -> dict:
    if not path:
        return {}
    cfg = json.load(open(path, encoding="utf-8"))
    problems = validate_config(cfg)
    if problems:
        _eprint("[managed-import] config validation failed:")
        for p in problems:
            _eprint(f"  - {p}")
        raise SystemExit(EXIT_USAGE)
    return cfg


def _resolve_env(args, cfg: dict) -> tuple[str, str | None, str | None]:
    """Resolve (env_url, settings_file, impersonate_oid) from --env (config) or explicit flags."""
    env_url, settings_file, oid = args.env_url, args.settings_file, args.impersonate_oid
    if args.env:
        env = (cfg.get("environments") or {}).get(args.env)
        if not env:
            _eprint(f"[managed-import] --env {args.env!r} not found in config")
            raise SystemExit(EXIT_USAGE)
        env_url = env_url or env.get("url")
        settings_file = settings_file or env.get("settings_file")
        oid = oid or env.get("impersonate_oid")
    if not env_url:
        _eprint("[managed-import] need --env-url or --env <name> (with a config)")
        raise SystemExit(EXIT_USAGE)
    validate_env_url(env_url)  # SSRF guard before any token is ever attached
    if oid and not _GUID_RE.match(str(oid)):
        _eprint(f"[managed-import] --impersonate-oid must be a GUID, got {oid!r}")
        raise SystemExit(EXIT_USAGE)
    return env_url, settings_file, oid


def _classified_prod(env_name: str | None, cfg: dict) -> bool:
    return bool(env_name) and env_name in ((cfg.get("prod_guard") or {}).get("environments", []))


def cmd_baseline(args, cfg) -> int:
    env_url, _, oid = _resolve_env(args, cfg)
    token = acquire_token(env_url)
    opener = _build_opener(is_allowed_dataverse_host)
    flows = query_solution_flows(opener, env_url, token, oid)
    active = [f for f in flows if int(f.get("statecode", 0)) == STATE_ACTIVE]
    out = {"env_url": env_url, "active_flows": active, "total_flows_queried": len(flows)}
    path = args.baseline_file or "./pp-import-baseline.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps({"baseline_file": path, "active": len(active), "total": len(flows)}, indent=2))
    return EXIT_OK


def _read_baseline(args) -> list[dict]:
    path = args.baseline_file or "./pp-import-baseline.json"
    try:
        return json.load(open(path, encoding="utf-8")).get("active_flows", [])
    except FileNotFoundError:
        _eprint(
            f"[managed-import] baseline file {path} not found — run `baseline` first; "
            "refusing to report success without a baseline (reactivation must be baseline-aware)"
        )
        raise SystemExit(EXIT_USAGE) from None


def cmd_reactivate(args, cfg) -> int:
    env_url, _, oid = _resolve_env(args, cfg)
    baseline_active = _read_baseline(args)
    token = acquire_token(env_url)
    opener = _build_opener(is_allowed_dataverse_host)
    current = query_solution_flows(opener, env_url, token, oid)
    keyless = [
        f for f in current if flow_key(f) is None and int(f.get("statecode", 0)) == STATE_DRAFT
    ]
    if keyless:
        _eprint(
            f"[managed-import] {len(keyless)} Draft flow(s) lack a solution unique name and "
            "were skipped (cannot stably identify; refusing to match on display name)"
        )
    targets = reactivation_targets(baseline_active, current)
    if not targets:
        print(json.dumps({"targeted": 0, "activated": 0, "note": "no Draft baseline-Active flows"}))
        return EXIT_OK
    waits = retry_backoff_schedule(args.max_retries, args.retry_wait)
    activated = 0
    for f in targets:
        wid = f["workflowid"]
        name = f.get("name", wid)
        ok = False
        for attempt in range(args.max_retries):
            if args.dry_run:
                _eprint(f"[dry-run] would PATCH {name} ({wid}) -> Active")
                ok = True
                break
            try:
                patch_flow_active(opener, env_url, token, wid, oid)
                # FM6: a 204 is not proof — re-query and assert BOTH codes.
                again = query_solution_flows(opener, env_url, token, oid)
                now = next((x for x in again if x["workflowid"] == wid), None)
                if (
                    now
                    and int(now.get("statecode", 0)) == STATE_ACTIVE
                    and int(now.get("statuscode", 0)) == STATUS_ACTIVE
                ):
                    ok = True
                    break
                _eprint(
                    f"[managed-import] {name}: PATCH returned but flow is not Active — retrying"
                )
            except urllib.error.HTTPError as e:
                if e.code == 403 and attempt < args.max_retries - 1:
                    w = waits[attempt] if attempt < len(waits) else waits[-1]
                    _eprint(f"[managed-import] {name}: 403 (attempt {attempt + 1}); waiting {w}s")
                    time.sleep(w)
                    continue
                if e.code == 403:
                    _eprint(f"[managed-import] {name}: {is_durable_403(f'{e.code} {e.reason}')}")
                else:
                    _eprint(f"[managed-import] {name}: HTTP {e.code} {e.reason}")
                break
        activated += 1 if ok else 0
    rc = map_results_to_exit(len(targets), activated)
    print(json.dumps({"targeted": len(targets), "activated": activated, "exit": rc}, indent=2))
    return rc


def cmd_verify(args, cfg) -> int:
    env_url, _, oid = _resolve_env(args, cfg)
    baseline_active = _read_baseline(args)
    token = acquire_token(env_url)
    opener = _build_opener(is_allowed_dataverse_host)
    current = query_solution_flows(opener, env_url, token, oid)
    still_draft = reactivation_targets(baseline_active, current)
    print(
        json.dumps(
            {
                "expected_active": len(baseline_active),
                "still_draft": [f.get("name") for f in still_draft],
            },
            indent=2,
        )
    )
    return EXIT_OK if not still_draft else EXIT_PARTIAL


def cmd_preflight(args, cfg) -> int:
    env_url, settings_file, oid = _resolve_env(args, cfg)
    if not settings_file:
        _eprint("[managed-import] preflight needs --settings-file (or env.settings_file in config)")
        return EXIT_USAGE
    try:
        settings = json.load(open(settings_file, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        _eprint(f"[managed-import] settings file unreadable: {e}")
        return EXIT_PREFLIGHT
    crefs = settings.get("ConnectionReferences", []) or []
    token = acquire_token(env_url)
    opener = _build_opener(is_allowed_dataverse_host)
    base = _api_base(env_url)
    missing = []
    for cr in crefs:
        logical = cr.get("LogicalName")
        if not logical:
            continue
        safe = quote(
            str(logical).replace("'", "''"), safe=""
        )  # OData-escape + URL-encode the value
        url = (
            f"{base}/connectionreferences?$select=connectionreferenceid,connectionid"
            f"&$filter=connectionreferencelogicalname eq '{safe}'"
        )
        try:
            req = urllib.request.Request(url, headers=_headers(token, oid))
            rows = json.loads(opener.open(req, timeout=60).read().decode()).get("value", [])
        except urllib.error.HTTPError as e:
            _eprint(f"[managed-import] preflight query failed for {logical}: HTTP {e.code}")
            rows = []
        if not rows:
            missing.append(logical)
    if missing:
        _eprint(
            f"[managed-import] preflight: {len(missing)} connection reference(s) absent in "
            f"target env: {missing}"
        )
        return EXIT_OK if args.force_preflight else EXIT_PREFLIGHT
    print(json.dumps({"preflight": "ok", "connection_references_checked": len(crefs)}, indent=2))
    return EXIT_OK


def cmd_import(args, cfg) -> int:
    env_url, settings_file, oid = _resolve_env(args, cfg)
    # Step 0 — PROD guard (FM7: aware datetime; approved honored before tz can hard-fail).
    if _classified_prod(args.env, cfg):
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

        tzname = ((cfg.get("prod_guard") or {}).get("timezone")) or "UTC"
        try:
            now = datetime.now(ZoneInfo(tzname))
        except ZoneInfoNotFoundError:
            if not args.approved:
                _eprint(
                    f"[managed-import] PROD guard: timezone {tzname!r} unavailable "
                    "(install tzdata) — cannot prove safe; pass --approved to override"
                )
                return EXIT_PROD_GUARD
            now = datetime.now().astimezone()
        blocked, reason = prod_guard_verdict(now, args.env, cfg.get("prod_guard"), args.approved)
        _eprint(f"[managed-import] PROD guard: {reason}")
        if blocked:
            return EXIT_PROD_GUARD
    if not args.solution_path:
        _eprint("[managed-import] import needs --solution-path")
        return EXIT_USAGE
    # Step 1 — preflight (unless skipped).
    if not args.skip_preflight:
        rc = cmd_preflight(args, cfg)
        if rc not in (EXIT_OK,):
            return rc
    # Step 2 — baseline.
    cmd_baseline(args, cfg)
    # Step 3 — pac import.
    argv = build_pac_argv(
        args.solution_path,
        env_url,
        settings_file,
        activate_plugins=True,
        publish_changes=args.publish_changes,
        force_overwrite=args.force_overwrite,
    )
    if args.dry_run:
        _eprint(f"[dry-run] would run: {' '.join(argv)}")
    else:
        if not _pac_on_path():
            _eprint("[managed-import] `pac` not found on PATH — install the Power Platform CLI")
            return EXIT_USAGE
        proc = subprocess.run(argv, check=False)  # noqa: S603 (argv list, no shell)
        if proc.returncode != 0:
            _eprint(f"[managed-import] pac solution import failed (exit {proc.returncode})")
            return EXIT_PAC_FAILED
    # Step 4 — reactivate + verify.
    return cmd_reactivate(args, cfg)


def _pac_on_path() -> bool:
    from shutil import which

    return which("pac") is not None


# ── CLI ─────────────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="managed_import.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--env-url", help="Dataverse org URL (https://org.crm.dynamics.com)")
        p.add_argument("--env", help="named env from --config (resolves url/settings/oid)")
        p.add_argument("--config", help="path to a secret-free JSON config file")
        p.add_argument(
            "--impersonate-oid",
            help="AAD object-id to impersonate (GUID; OFF by "
            "default — needs prvActOnBehalfOfAnotherUser; flows run under that user's "
            "connections)",
        )
        p.add_argument(
            "--baseline-file", help="baseline JSON path (default ./pp-import-baseline.json)"
        )
        p.add_argument("--dry-run", action="store_true", help="print the plan; change nothing")

    for name, fn, helptext in [
        ("reactivate", cmd_reactivate, "PATCH Draft baseline-Active flows back to Active"),
        ("verify", cmd_verify, "report flows still Draft vs baseline (exit 10 if any)"),
        ("baseline", cmd_baseline, "capture currently-Active solution flows"),
        ("preflight", cmd_preflight, "validate the settings file's connection refs vs the env"),
        (
            "import",
            cmd_import,
            "full pipeline (guard->preflight->baseline->pac->reactivate->verify)",
        ),
    ]:
        p = sub.add_parser(name, help=helptext)
        common(p)
        p.set_defaults(_fn=fn)
        if name in ("reactivate", "verify", "import"):
            p.add_argument(
                "--max-retries", type=int, default=3, help="403 retry attempts (default 3)"
            )
            p.add_argument(
                "--retry-wait", type=int, default=15, help="base backoff seconds (default 15)"
            )
        if name in ("preflight", "import"):
            p.add_argument(
                "--settings-file", help="deploymentSettings.json (connection refs/env vars)"
            )
            p.add_argument(
                "--force-preflight", action="store_true", help="continue past preflight gaps"
            )
        if name == "import":
            p.add_argument("--solution-path", help="path to the managed solution .zip")
            p.add_argument(
                "--approved", action="store_true", help="override the PROD business-hours guard"
            )
            p.add_argument("--skip-preflight", action="store_true")
            p.add_argument(
                "--publish-changes",
                action="store_true",
                help="OPT-IN: pass --publish-changes (discouraged for managed imports)",
            )
            p.add_argument(
                "--force-overwrite",
                action="store_true",
                help="OPT-IN: pass --force-overwrite (discouraged; slows the import)",
            )
    # ensure the non-import commands still expose settings/preflight attrs the resolver reads
    for p in sub.choices.values():
        for attr, default in (
            ("settings_file", None),
            ("force_preflight", False),
            ("max_retries", 3),
            ("retry_wait", 15),
            ("solution_path", None),
            ("approved", False),
            ("skip_preflight", False),
            ("publish_changes", False),
            ("force_overwrite", False),
        ):
            if not any(a.dest == attr for a in p._actions):  # noqa: SLF001
                p.set_defaults(**{attr: default})
    return ap


def main(argv: list[str] | None = None) -> int:
    _install_excepthook()
    args = build_parser().parse_args(argv)
    cfg = _load_config(args.config)
    try:
        return args._fn(args, cfg)  # noqa: SLF001
    except ValueError as e:  # config/URL validation
        _eprint(f"[managed-import] {e}")
        return EXIT_USAGE
    except RuntimeError as e:  # auth
        _eprint(f"[managed-import] auth error: {e}")
        return EXIT_AUTH


if __name__ == "__main__":
    raise SystemExit(main())

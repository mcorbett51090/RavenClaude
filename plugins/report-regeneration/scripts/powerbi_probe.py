#!/usr/bin/env python3
"""
report-regeneration — Power BI ingestion PROBE (Phase 0, gate G0-b).

Phase-0 spike: prove, on THIS host (macOS), that we can (a) read data from a
client's Power BI model and (b) capture a screenshot of a published report —
with graceful, fail-CLOSED degradation when either route is unavailable. This
script is authored NOW so it is ready to run the moment the maintainer supplies
tenant details (workspace/dataset IDs + an auth token); it is NOT run as part
of authoring this file, and it makes NO network call at import time.

Fail-closed contract (binding, mirrors docs/accuracy-near-guarantee-design.md
+ the report-regeneration plan §3/§4 "Fail-closed data-read degrade" /
"screenshot = regenerate asset" rulings):
  - A probe error is NEVER a pass. `data` reports {"route": null,
    "verdict": "not_captured"} on any failure — missing env var, missing
    library, network error, non-200 response, malformed payload.
  - `shot` reports {"captured": false, "verdict": "not_captured"} on any
    failure — missing Playwright, missing auth, navigation error, timeout.
    It NEVER fabricates a screenshot path that doesn't exist on disk.
  - Neither subcommand ever prints a secret. Tokens are read from env vars
    ONLY (never a CLI flag, never a config file, never hardcoded) and are
    referenced in receipts only as `"present": true/false` — the value
    itself never appears in any printed or returned structure.
  - No network call happens on `import powerbi_probe` — every network-capable
    branch is inside a subcommand function, invoked only from `main()`.

Routes (per the report-regeneration plan §2/§4, rev. 2):
  DATA:
    1. XMLA (confirmed tenant route, requires Premium/PPU/Fabric capacity +
       the "Allow XMLA endpoints..." tenant setting) via a native client
       (ADOMD.NET / pyadomd). NOT attempted by this script — see
       "Why XMLA has no code path here" below. Always reports `route: null`
       unless a future revision adds a working macOS ADOMD.NET binding.
    2. Power BI REST `executeQueries` (DAX, JSON) — the macOS-runnable
       fallback this script actually calls. Works on Pro/PPU/Premium/Fabric
       (no XMLA-tier capacity requirement), stdlib-only (urllib + json).
       [verified this session, 2026-07-16, against
       https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group]
  SCREENSHOT (maintainer-confirmed, 2026-07-16: the tenant is Premium, and
  the required behavior is "the tool logs in and grabs it" — auto-capture,
  not user-provided-by-default):
    1. **PRIMARY — Power BI REST `ExportToFile` (Export Report To File In
       Group)**, format=PNG, authenticated by the SAME service-principal
       bearer token as the `data` path. This is a server-side render: POST
       to trigger the export job, poll `GetExportToFileStatus` until
       Succeeded/Failed, then GET the file bytes. No browser, no
       interactive/MFA login — the clean "log in and grab it" for a Premium
       tenant. Requires the workspace's semantic model(s) to be on a
       Premium/Embedded/Fabric capacity (documented as **NOT supported for
       Premium Per User (PPU)** — a materially different requirement from
       XMLA/data-read, which DOES support PPU). Requires the tenant admin
       setting "Export reports as image files" (disabled by default — the
       maintainer's tenant admin needs to turn this on for PNG specifically;
       PDF/PPTX export is enabled by default but PNG is not).
       [verified this session, 2026-07-16, against
       https://learn.microsoft.com/en-us/rest/api/power-bi/reports/export-to-file-in-group
       and https://learn.microsoft.com/en-us/power-bi/developer/embedded/export-to]
    2. **FALLBACK — Playwright** against the published-report UI with
       injected auth, attempted only if `ExportToFile` failed or its
       prerequisites are absent, AND Playwright + the fallback env vars are
       present. Kept for graceful degradation (e.g. a report not owned by
       the service principal, or a tenant setting not yet enabled) — it is
       NOT the primary route per the maintainer's stated requirement.
    3. **User-provided image** — the always-available fallback of last
       resort; this script cannot do that step (it's a human action), so it
       just names it in the `shot` receipt's `fallback` field when both
       auto-capture routes report `not_captured`.

Why XMLA has no code path here (native client, Windows-only in practice):
  A native XMLA client on Python is `pyadomd`, which wraps the CLASSIC
  .NET-Framework `Microsoft.AnalysisServices.AdomdClient` via pythonnet —
  that classic package is Windows/.NET-Framework-only. A `.NetCore` variant
  of the ADOMD.NET client DOES exist on NuGet
  (`Microsoft.AnalysisServices.AdomdClient.NetCore.retail.amd64`), but (a) it
  ships amd64-only builds with no documented macOS/ARM64 support, and (b) no
  Python wrapper (pyadomd or otherwise) targets it — using it from Python on
  macOS would mean hand-rolling a pythonnet/.NET-8 bridge, which is out of
  scope for a Phase-0 probe. `doctor.py` already probes for `pyadomd` and
  labels it "EXPECTED-ABSENT on macOS -> use Power BI REST executeQueries
  (DAX) instead" — this script is that fallback, made runnable.
  [this-session verification, 2026-07-16: see
  plugins/report-regeneration/knowledge/powerbi-ingest-contract.md]

Env vars read (NEVER hardcode; NEVER pass via argv):
  POWERBI_ACCESS_TOKEN     - a service-principal bearer token for
                             api.powerbi.com (required, `data`; required,
                             `shot`'s primary ExportToFile route — the SAME
                             token covers both, per the maintainer's stated
                             single-service-principal design)
  POWERBI_WORKSPACE_ID     - the workspace (group) GUID (required, `data`
                             and `shot`'s ExportToFile route)
  POWERBI_DATASET_ID       - the semantic model (dataset) GUID (required, `data`)
  POWERBI_DAX_QUERY        - the DAX query string (optional, `data`; a safe
                             default `EVALUATE ROW("probe", 1)` is used if unset
                             so the probe never needs a real table name to run)
  POWERBI_REPORT_ID        - the report GUID to export/screenshot (required,
                             `shot`'s ExportToFile route)
  POWERBI_EXPORT_PAGE_NAME - a specific report page name to export (optional,
                             `shot`; unset exports the whole report, which
                             Power BI compresses to a .zip of per-page PNGs
                             when the report has more than one page)
  POWERBI_EXPORT_BOOKMARK_NAME - a bookmark name to apply to the exported
                             page (optional, `shot`; only used if
                             POWERBI_EXPORT_PAGE_NAME is also set)
  POWERBI_EXPORT_TIMEOUT_SECONDS - poll timeout in seconds for the async
                             export job (optional, `shot`; default 120)
  POWERBI_REPORT_URL       - the published-report URL to screenshot via the
                             Playwright FALLBACK route (required only if
                             ExportToFile is unavailable/failed and the
                             fallback is to be attempted)
  POWERBI_SHOT_AUTH_TOKEN  - a bearer/cookie token Playwright can inject for
                             the Playwright FALLBACK route (required for
                             that fallback, unless the report is already
                             publicly embeddable)
  POWERBI_SHOT_OUT_PATH    - where to write the exported/captured file
                             (optional, `shot`; defaults to a path under the
                             OS temp dir; the ExportToFile route uses the
                             extension the service reports, e.g. `.png` or
                             `.zip` for a multi-page PNG export)

Run:
  python3 plugins/report-regeneration/scripts/powerbi_probe.py data [--json]
  python3 plugins/report-regeneration/scripts/powerbi_probe.py shot [--json]

Exit: always 0 (this is a probe, not a gate) — the `verdict` field inside the
      emitted receipt carries the PASS / not_captured signal for a caller to
      branch on. This mirrors doctor.py's own "Exit: 0 always" contract.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request
from typing import Any

SCHEMA_DATA = "report-regeneration/powerbi-probe-data@1"
SCHEMA_SHOT = "report-regeneration/powerbi-probe-shot@1"

# Power BI REST — Execute Queries In Group (JSON, DAX-only).
# [verified this session, 2026-07-16, against
#  https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group]
POWERBI_API_BASE = "https://api.powerbi.com/v1.0/myorg"
EXECUTE_QUERIES_RATE_LIMIT_PER_MIN = 120  # per-user, regardless of dataset
DEFAULT_DAX_QUERY = 'EVALUATE ROW("probe", 1)'
REQUEST_TIMEOUT_SECONDS = 20

# Power BI REST — Export To File In Group / Get Export To File Status In Group /
# Get File Of Export To File In Group. PNG format only (this probe's use case).
# [verified this session, 2026-07-16, against
#  https://learn.microsoft.com/en-us/rest/api/power-bi/reports/export-to-file-in-group
#  https://learn.microsoft.com/en-us/rest/api/power-bi/reports/get-export-to-file-status-in-group
#  https://learn.microsoft.com/en-us/rest/api/power-bi/reports/get-file-of-export-to-file-in-group
#  https://learn.microsoft.com/en-us/power-bi/developer/embedded/export-to]
EXPORT_FORMAT = "PNG"
EXPORT_POLL_INTERVAL_SECONDS = 3
EXPORT_DEFAULT_TIMEOUT_SECONDS = 120
EXPORT_TERMINAL_STATES = {"Succeeded", "Failed"}


def _env_present(name: str) -> bool:
    """True if the env var is set and non-empty. Never returns the value."""
    val = os.environ.get(name)
    return bool(val and val.strip())


def _env(name: str) -> str | None:
    """Read an env var. Callers must never print/log the return value."""
    return os.environ.get(name)


def _redact_url(url: str) -> str:
    """Best-effort strip of any query-string that might carry a token/key."""
    return url.split("?", 1)[0]


# --------------------------------------------------------------------------
# Shared mechanics — Power BI REST executeQueries (DAX, JSON), ONE query.
# Used by probe_data() below (fixed default query, CLI probe) AND by
# skills/powerbi-ingest/powerbi_ingest.py's `data` pipeline mode (one call
# per manifest dax-kind binding, real query text per binding). Extracting
# this keeps the HTTP/error-handling mechanics in exactly one place rather
# than duplicated across the probe and the pipeline adapter.
# --------------------------------------------------------------------------

def execute_dax_query(
    dax_query: str,
    *,
    workspace_id: str | None = None,
    dataset_id: str | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    """
    Execute a single DAX query via Power BI REST `executeQueries` (JSON).
    Falls back to POWERBI_WORKSPACE_ID / POWERBI_DATASET_ID / POWERBI_ACCESS_TOKEN
    from the environment for any argument left as None. NEVER raises; NEVER
    logs the token (it is used only inside a request header, never returned or
    printed). Fail-CLOSED: any missing prerequisite or runtime error yields
    `ok: False` with a `reason` — never a fabricated row.

    Returns:
        {"ok": bool, "reason": str | None, "http_status": int | None,
         "elapsed_ms": float | None, "row_count": int | None,
         "first_row": dict | None}
    `first_row` is the first row of the first result table (column name ->
    typed value), or None on any failure or an empty result set.
    """
    ws = workspace_id if workspace_id is not None else _env("POWERBI_WORKSPACE_ID")
    ds = dataset_id if dataset_id is not None else _env("POWERBI_DATASET_ID")
    tok = token if token is not None else _env("POWERBI_ACCESS_TOKEN")

    empty: dict[str, Any] = {
        "ok": False, "reason": None, "http_status": None,
        "elapsed_ms": None, "row_count": None, "first_row": None,
    }

    missing = [name for name, val in (("workspace_id", ws), ("dataset_id", ds), ("token", tok)) if not (val and str(val).strip())]
    if missing:
        empty["reason"] = f"missing required value(s): {', '.join(missing)}"
        return empty

    url = f"{POWERBI_API_BASE}/groups/{ws}/datasets/{ds}/executeQueries"
    body = json.dumps({
        "queries": [{"query": dax_query}],
        "serializerSettings": {"includeNulls": True},
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            # NEVER log this header's value.
            "Authorization": f"Bearer {tok}",
        },
    )

    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            status = resp.status
            payload_raw = resp.read()
        elapsed_ms = round((time.monotonic() - started) * 1000, 1)
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            err_body = "(unreadable error body)"
        reason = f"HTTP {e.code} from {_redact_url(url)}: {err_body}"
        if e.code == 429:
            reason += " (rate limit: 120 queries/min/user)"
        empty["reason"] = reason
        empty["http_status"] = e.code
        return empty
    except urllib.error.URLError as e:
        empty["reason"] = f"network error reaching {_redact_url(url)}: {e.reason}"
        return empty
    except TimeoutError:
        empty["reason"] = f"request timed out after {REQUEST_TIMEOUT_SECONDS}s"
        return empty
    except Exception as e:  # fail-closed: any unexpected error -> not ok
        empty["reason"] = f"unexpected error: {type(e).__name__}: {e}"
        return empty

    try:
        payload = json.loads(payload_raw.decode("utf-8"))
    except Exception as e:
        empty["reason"] = f"response was not valid JSON: {e}"
        empty["http_status"] = status
        empty["elapsed_ms"] = elapsed_ms
        return empty

    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list) or not results:
        err = payload.get("error") if isinstance(payload, dict) else None
        empty["reason"] = f"unexpected response shape (error={err!r})" if err else "empty 'results'"
        empty["http_status"] = status
        empty["elapsed_ms"] = elapsed_ms
        return empty

    first = results[0]
    if isinstance(first, dict) and first.get("error"):
        empty["reason"] = f"DAX query error: {first['error']}"
        empty["http_status"] = status
        empty["elapsed_ms"] = elapsed_ms
        return empty

    tables = first.get("tables") if isinstance(first, dict) else None
    rows = tables[0].get("rows") if isinstance(tables, list) and tables and isinstance(tables[0], dict) else None
    if not isinstance(rows, list):
        empty["reason"] = "response had no 'rows' array"
        empty["http_status"] = status
        empty["elapsed_ms"] = elapsed_ms
        return empty

    first_row = rows[0] if rows and isinstance(rows[0], dict) else None
    return {
        "ok": True,
        "reason": None,
        "http_status": status,
        "elapsed_ms": elapsed_ms,
        "row_count": len(rows),
        "first_row": first_row,
    }


# --------------------------------------------------------------------------
# `data` subcommand — Power BI REST executeQueries (DAX, JSON) probe
# --------------------------------------------------------------------------

def probe_data() -> dict[str, Any]:
    """
    Attempt a Power BI REST `executeQueries` (DAX) call. Fail-CLOSED: any
    missing prerequisite or runtime error yields `route: null,
    verdict: "not_captured"` — never a fabricated PASS.

    Deliberately does NOT attempt XMLA (see module docstring "Why XMLA has
    no code path here"). A future revision may add a native-client branch
    guarded by `importlib.util.find_spec("pyadomd")`; until then this
    reports the REST fallback only, and `route` is always either
    `"rest-execute-queries"` or `null`.
    """
    receipt: dict[str, Any] = {
        "schema": SCHEMA_DATA,
        "route": None,
        "verdict": "not_captured",
        "reason": None,
        "recompute_path_independent": None,  # V1 leg: is this a real 2nd execution path?
        "rate_limit_per_min": EXECUTE_QUERIES_RATE_LIMIT_PER_MIN,
        "note": "XMLA not attempted (no macOS-runnable native client available; "
                "see knowledge/powerbi-ingest-contract.md). This probe exercises "
                "only the REST executeQueries fallback.",
    }

    token_present = _env_present("POWERBI_ACCESS_TOKEN")
    workspace_id = _env("POWERBI_WORKSPACE_ID")
    dataset_id = _env("POWERBI_DATASET_ID")
    dax_query = _env("POWERBI_DAX_QUERY") or DEFAULT_DAX_QUERY

    receipt["env"] = {
        "POWERBI_ACCESS_TOKEN": {"present": token_present},
        "POWERBI_WORKSPACE_ID": {"present": bool(workspace_id)},
        "POWERBI_DATASET_ID": {"present": bool(dataset_id)},
        "POWERBI_DAX_QUERY": {"present": bool(_env("POWERBI_DAX_QUERY")), "used_default": _env("POWERBI_DAX_QUERY") is None},
    }

    missing = [
        name for name, present in (
            ("POWERBI_ACCESS_TOKEN", token_present),
            ("POWERBI_WORKSPACE_ID", bool(workspace_id)),
            ("POWERBI_DATASET_ID", bool(dataset_id)),
        )
        if not present
    ]
    if missing:
        receipt["reason"] = f"missing required env var(s): {', '.join(missing)}"
        return receipt

    # The actual HTTP call + response parsing lives in execute_dax_query() — the
    # shared mechanics also used by skills/powerbi-ingest/powerbi_ingest.py's
    # `data` pipeline mode (one call per manifest dax-kind binding). Keeping it
    # in one place means a fix to error handling here fixes it there too.
    outcome = execute_dax_query(dax_query, workspace_id=workspace_id, dataset_id=dataset_id, token=_env("POWERBI_ACCESS_TOKEN"))
    if not outcome["ok"]:
        receipt["reason"] = outcome["reason"]
        if outcome["http_status"] is not None:
            receipt["http_status"] = outcome["http_status"]
        return receipt

    receipt.update({
        "route": "rest-execute-queries",
        "verdict": "PASS",
        "reason": None,
        "recompute_path_independent": True,  # a real re-query, per plan §3 V1
        "http_status": outcome["http_status"],
        "elapsed_ms": outcome["elapsed_ms"],
        "row_count": outcome["row_count"],
    })
    return receipt


# --------------------------------------------------------------------------
# `shot` subcommand — PRIMARY: Power BI REST ExportToFile (server-side PNG
# render, service-principal auth, no browser, no interactive/MFA login).
# FALLBACK: Playwright against the published-report UI.
# --------------------------------------------------------------------------

def _playwright_available() -> bool:
    try:
        return importlib.util.find_spec("playwright") is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def _export_to_file_attempt(out_path_hint: str) -> dict[str, Any]:
    """
    Attempt the primary ExportToFile route: POST to trigger the export job,
    poll GetExportToFileStatus until terminal, GET the file bytes on success.
    Returns a dict describing the outcome; never raises. Fail-CLOSED: any
    missing prerequisite or runtime error yields `ok: False` with `reason`
    set — the caller falls through to the Playwright fallback.
    """
    outcome: dict[str, Any] = {"ok": False, "path": None, "reason": None, "attempted": False}

    token_present = _env_present("POWERBI_ACCESS_TOKEN")
    workspace_id = _env("POWERBI_WORKSPACE_ID")
    report_id = _env("POWERBI_REPORT_ID")

    missing = [
        name for name, present in (
            ("POWERBI_ACCESS_TOKEN", token_present),
            ("POWERBI_WORKSPACE_ID", bool(workspace_id)),
            ("POWERBI_REPORT_ID", bool(report_id)),
        )
        if not present
    ]
    if missing:
        outcome["reason"] = f"missing required env var(s): {', '.join(missing)}"
        return outcome

    outcome["attempted"] = True
    base = f"{POWERBI_API_BASE}/groups/{workspace_id}/reports/{report_id}"
    export_url = f"{base}/ExportTo"

    page_name = _env("POWERBI_EXPORT_PAGE_NAME")
    bookmark_name = _env("POWERBI_EXPORT_BOOKMARK_NAME")
    try:
        timeout_seconds = int(_env("POWERBI_EXPORT_TIMEOUT_SECONDS") or EXPORT_DEFAULT_TIMEOUT_SECONDS)
    except ValueError:
        timeout_seconds = EXPORT_DEFAULT_TIMEOUT_SECONDS

    body: dict[str, Any] = {"format": EXPORT_FORMAT}
    if page_name:
        page: dict[str, Any] = {"pageName": page_name}
        if bookmark_name:
            page["bookmark"] = {"name": bookmark_name}
        body["powerBIReportConfiguration"] = {"pages": [page]}

    headers = {
        "Content-Type": "application/json",
        # NEVER log this header's value.
        "Authorization": f"Bearer {_env('POWERBI_ACCESS_TOKEN')}",
    }

    # --- Step 1: trigger the export job (expects 202 Accepted + an Export object) ---
    req = urllib.request.Request(export_url, data=json.dumps(body).encode("utf-8"), method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            trigger_payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            err_body = "(unreadable error body)"
        reason = f"HTTP {e.code} triggering export at {_redact_url(export_url)}: {err_body}"
        if e.code == 429:
            reason += " (concurrency limit: 500 concurrent ExportToFile requests/capacity)"
        outcome["reason"] = reason
        return outcome
    except urllib.error.URLError as e:
        outcome["reason"] = f"network error triggering export: {e.reason}"
        return outcome
    except TimeoutError:
        outcome["reason"] = f"export trigger timed out after {REQUEST_TIMEOUT_SECONDS}s"
        return outcome
    except Exception as e:  # fail-closed
        outcome["reason"] = f"unexpected error triggering export: {type(e).__name__}: {e}"
        return outcome

    export_id = trigger_payload.get("id") if isinstance(trigger_payload, dict) else None
    if not export_id:
        outcome["reason"] = "export trigger response had no 'id' (job could not be tracked)"
        return outcome

    # --- Step 2: poll GetExportToFileStatus until Succeeded/Failed or timeout ---
    status_url = f"{base}/exports/{export_id}"
    deadline = time.monotonic() + max(timeout_seconds, 1)
    status = trigger_payload.get("status")
    resource_extension = trigger_payload.get("resourceFileExtension") or ".png"

    while status not in EXPORT_TERMINAL_STATES:
        if time.monotonic() >= deadline:
            outcome["reason"] = f"export job did not reach a terminal state within {timeout_seconds}s (last status: {status})"
            return outcome
        time.sleep(EXPORT_POLL_INTERVAL_SECONDS)
        poll_req = urllib.request.Request(status_url, method="GET", headers=headers)
        try:
            with urllib.request.urlopen(poll_req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
                poll_payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            outcome["reason"] = f"HTTP {e.code} polling export status"
            return outcome
        except urllib.error.URLError as e:
            outcome["reason"] = f"network error polling export status: {e.reason}"
            return outcome
        except Exception as e:  # fail-closed
            outcome["reason"] = f"unexpected error polling export status: {type(e).__name__}: {e}"
            return outcome
        status = poll_payload.get("status")
        resource_extension = poll_payload.get("resourceFileExtension") or resource_extension

    if status != "Succeeded":
        outcome["reason"] = f"export job finished with status={status!r} (not Succeeded)"
        return outcome

    # --- Step 3: download the file ---
    file_url = f"{status_url}/file"
    file_req = urllib.request.Request(file_url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(file_req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            file_bytes = resp.read()
    except urllib.error.HTTPError as e:
        outcome["reason"] = f"HTTP {e.code} retrieving exported file"
        return outcome
    except urllib.error.URLError as e:
        outcome["reason"] = f"network error retrieving exported file: {e.reason}"
        return outcome
    except Exception as e:  # fail-closed
        outcome["reason"] = f"unexpected error retrieving exported file: {type(e).__name__}: {e}"
        return outcome

    if not file_bytes:
        outcome["reason"] = "export succeeded but the downloaded file was empty"
        return outcome

    # Use the extension the SERVICE reports (a multi-page PNG export is a
    # .zip of per-page PNGs, per the docs) rather than assuming .png.
    ext = resource_extension if resource_extension.startswith(".") else f".{resource_extension}"
    out_path = os.path.splitext(out_path_hint)[0] + ext
    try:
        with open(out_path, "wb") as f:
            f.write(file_bytes)
    except OSError as e:
        outcome["reason"] = f"could not write exported file to disk: {e}"
        return outcome

    if not os.path.isfile(out_path) or os.path.getsize(out_path) == 0:
        outcome["reason"] = "export reported success but no non-empty file was written"
        return outcome

    outcome.update({"ok": True, "path": out_path, "reason": None})
    return outcome


def _playwright_fallback_attempt(out_path: str) -> dict[str, Any]:
    """
    Attempt the FALLBACK route: a Playwright screenshot of the published-
    report UI. Only meaningful when the primary ExportToFile route failed
    or its prerequisites were absent. Fail-CLOSED: any missing prerequisite
    or runtime error yields `ok: False` with `reason` set.
    """
    outcome: dict[str, Any] = {"ok": False, "path": None, "reason": None, "attempted": False}

    if not _playwright_available():
        outcome["reason"] = "playwright not installed (optional dependency; doctor.py Tier-B)"
        return outcome

    report_url = _env("POWERBI_REPORT_URL")
    if not report_url:
        outcome["reason"] = "missing env var: POWERBI_REPORT_URL"
        return outcome

    if not _env_present("POWERBI_SHOT_AUTH_TOKEN"):
        # Power BI Service reports are not publicly viewable by default — an
        # unauthenticated capture attempt will almost always land on a
        # sign-in redirect. Refuse rather than "successfully" screenshot a
        # login page, which would be a worse failure than not_captured.
        outcome["reason"] = (
            "missing POWERBI_SHOT_AUTH_TOKEN — refusing to attempt an "
            "unauthenticated capture (would likely screenshot a sign-in page, "
            "not the report; that is a worse failure than not_captured)"
        )
        return outcome

    outcome["attempted"] = True
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:
        outcome["reason"] = f"playwright present but failed to import sync_api: {e}"
        return outcome

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    extra_http_headers={
                        # NEVER log this header's value.
                        "Authorization": f"Bearer {_env('POWERBI_SHOT_AUTH_TOKEN')}",
                    }
                )
                page = context.new_page()
                page.goto(report_url, wait_until="networkidle", timeout=REQUEST_TIMEOUT_SECONDS * 1000)
                page.screenshot(path=out_path, full_page=True)
            finally:
                browser.close()
    except Exception as e:  # fail-closed: any Playwright/navigation error -> not ok
        outcome["reason"] = f"capture failed: {type(e).__name__}: {e}"
        return outcome

    if not os.path.isfile(out_path) or os.path.getsize(out_path) == 0:
        outcome["reason"] = "capture reported success but no non-empty file was written"
        return outcome

    outcome.update({"ok": True, "path": out_path, "reason": None})
    return outcome


def probe_shot() -> dict[str, Any]:
    """
    Attempt PRIMARY (ExportToFile, server-side, service-principal auth) then
    FALLBACK (Playwright against the Service UI) to obtain a Power BI report
    image. Fail-CLOSED at every step: any missing prerequisite or runtime
    error yields `captured: false, verdict: "not_captured"` and names the
    user-provided-image fallback of last resort — never a fabricated path.
    """
    receipt: dict[str, Any] = {
        "schema": SCHEMA_SHOT,
        "captured": False,
        "verdict": "not_captured",
        "route": None,
        "path": None,
        "reason": None,
        "attempts": {},
        "fallback": "user-provided image (always-available fallback per plan §2/§4 — "
                    "the plugin accepts a human-supplied screenshot, classed `regenerate`, "
                    "guarded by the period-coherence check same as an auto-captured one)",
    }

    out_path_hint = _env("POWERBI_SHOT_OUT_PATH") or os.path.join(
        tempfile.gettempdir(), "report-regeneration-powerbi-shot.png"
    )

    receipt["env"] = {
        "POWERBI_ACCESS_TOKEN": {"present": _env_present("POWERBI_ACCESS_TOKEN")},
        "POWERBI_WORKSPACE_ID": {"present": bool(_env("POWERBI_WORKSPACE_ID"))},
        "POWERBI_REPORT_ID": {"present": bool(_env("POWERBI_REPORT_ID"))},
        "POWERBI_EXPORT_PAGE_NAME": {"present": bool(_env("POWERBI_EXPORT_PAGE_NAME"))},
        "POWERBI_REPORT_URL": {"present": bool(_env("POWERBI_REPORT_URL"))},
        "POWERBI_SHOT_AUTH_TOKEN": {"present": _env_present("POWERBI_SHOT_AUTH_TOKEN")},
        "POWERBI_SHOT_OUT_PATH": {"present": bool(_env("POWERBI_SHOT_OUT_PATH")), "resolved_hint": out_path_hint},
    }

    # --- PRIMARY: ExportToFile ---
    export_outcome = _export_to_file_attempt(out_path_hint)
    receipt["attempts"]["export-to-file"] = {k: v for k, v in export_outcome.items() if k != "path" or export_outcome["ok"]}
    if export_outcome["ok"]:
        receipt.update({
            "captured": True,
            "verdict": "PASS",
            "route": "export-to-file",
            "path": export_outcome["path"],
            "reason": None,
            "auth": "service-principal bearer token (no browser, no interactive/MFA login)",
            # This is a `regenerate`-class asset (plan §2/§3): fresh-from-source,
            # never transplanted. The caller MUST still run the period-coherence
            # check (see knowledge/powerbi-ingest-contract.md) before it ships —
            # a successful export is NOT proof the reporting period is current.
            "node_class": "regenerate",
            "period_coherence_checked": False,
        })
        return receipt

    # --- FALLBACK: Playwright vs Service UI ---
    playwright_outcome = _playwright_fallback_attempt(out_path_hint)
    receipt["attempts"]["playwright-fallback"] = {k: v for k, v in playwright_outcome.items() if k != "path" or playwright_outcome["ok"]}
    if playwright_outcome["ok"]:
        receipt.update({
            "captured": True,
            "verdict": "PASS",
            "route": "playwright-fallback",
            "path": playwright_outcome["path"],
            "reason": None,
            "auth": "injected bearer/cookie header (fallback route — primary ExportToFile failed or was unavailable)",
            "node_class": "regenerate",
            "period_coherence_checked": False,
        })
        return receipt

    # --- Neither route succeeded: not_captured, name the human fallback ---
    receipt["reason"] = (
        f"export-to-file: {export_outcome['reason']}; "
        f"playwright-fallback: {playwright_outcome['reason']}"
    )
    return receipt


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _print_human(kind: str, receipt: dict[str, Any]) -> None:
    print(f"report-regeneration powerbi_probe [{kind}] — verdict: {receipt['verdict']}")
    if kind == "data":
        print(f"  route: {receipt['route']}")
    else:
        print(f"  route: {receipt['route']}  captured: {receipt['captured']}  path: {receipt['path']}")
    if receipt.get("reason"):
        print(f"  reason: {receipt['reason']}")
    if kind == "shot" and receipt["verdict"] != "PASS":
        print(f"  fallback: {receipt['fallback']}")
    print("  NOTE: a probe error is never a PASS (accuracy-near-guarantee W5).")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase-0 Power BI ingestion probe: data (REST executeQueries) + "
                    "shot (ExportToFile primary, Playwright fallback)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_data = sub.add_parser("data", help="Attempt a Power BI REST executeQueries (DAX) call.")
    p_data.add_argument("--json", action="store_true", help="Emit the receipt as JSON.")

    p_shot = sub.add_parser(
        "shot",
        help="Attempt a Power BI report image: ExportToFile (primary, service-principal, "
             "no browser) then Playwright-vs-Service-UI (fallback).",
    )
    p_shot.add_argument("--json", action="store_true", help="Emit the receipt as JSON.")

    args = parser.parse_args(argv)

    if args.command == "data":
        receipt = probe_data()
    else:
        receipt = probe_shot()

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        _print_human(args.command, receipt)

    return 0  # always 0 — this is a probe, not a gate; `verdict` carries the signal


if __name__ == "__main__":
    sys.exit(main())

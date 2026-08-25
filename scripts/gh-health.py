#!/usr/bin/env python3
"""Answer ONE question: **"Is this GitHub's problem or mine?"**

WHY THIS EXISTS
---------------
On 2026-08-18 GitHub rolled the hosted Actions runner image from
`ubuntu-24.04 / 20260720.247.2` to `20260810.271.1`. A repo with unchanged
application code and a pinned lockfile went from green to failing on EVERY pull
request across six unrelated branches. `https://www.githubstatus.com/api/v2/status.json`
said `indicator: none, "All Systems Operational"` with zero degraded components
-- and it was RIGHT, because an image rollout is not an incident. Engineers (and
agents) concluded "my change broke it" and burned hours chasing a phantom.

The status page is the WEAKEST of the signals available and it is the only one
anybody checks. This tool checks five more.

WHY A GREEN `indicator` IS NOT EVIDENCE OF HEALTH (measured 2026-08-18)
----------------------------------------------------------------------
Probing the live endpoints four times over ~2 minutes on 2026-08-18 returned,
simultaneously:

    status.json                 indicator: none, "All Systems Operational"
    components.json             0 of 12 components non-operational
    incidents/unresolved.json   an OPEN incident, impact: major,
                                status: investigating, "Incident with Actions"

That is not staleness and not caching. The incident was created at
`09:36:40.322Z`; `page.updated_at` read `09:36:40.359Z` -- **37 ms later**. The
page updated BECAUSE OF the incident and still reported all-clear.

THE MECHANISM: both open incidents carried `components: []`. An incident with no
component association moves NEITHER the top-level indicator NOR any component
status. It is structural, not a glitch -- 33 of 50 historical incidents DO attach
components, so the unattached shape is a recurring blind spot in precisely the
two endpoints every tool polls.

CONSEQUENCE, encoded in `probe_status_page` and asserted in `--self-test`: the
status verdict is NEVER computed from `indicator` + `components` alone. The
unresolved-incidents fetch is MANDATORY; a non-empty list is GITHUB_DEGRADED no
matter how green the other two read; and a failure to fetch or parse it is
UNKNOWN, because a green indicator beside an unreachable incidents endpoint
tells you exactly nothing.

THE FAILURE DIRECTION THAT IS BANNED
------------------------------------
This codebase has been bitten repeatedly by probes that fail silently toward a
clean/green answer. A probe that cannot run is not evidence of health. So this
tool has THREE verdicts and never collapses the third into the second:

    GITHUB_DEGRADED (exit 1)  positive evidence of a GitHub-side problem
    LOCAL           (exit 0)  every probe ran, every probe was clean -> it's us
    UNKNOWN         (exit 2)  a probe could not run, timed out, lacked auth,
                              or returned something unparseable

A network failure, a missing `gh`, an expired token or a JSON parse error is
UNKNOWN. Never LOCAL. Never healthy.

The LOCAL verdict is gated by a PROBE QUORUM: it requires that every enabled
probe actually RAN and returned clean. Consequences, both deliberate:

  * A green status page ALONE can never produce LOCAL, because the five
    capability/drift/invariance probes will not have run.
  * Running without `--repo` can never produce LOCAL, for the same reason.

Every run prints WHICH probes ran and which did not. A verdict computed from two
of six probes says so, out loud, on the verdict line.

SIGNAL LAYERS
-------------
1. STATUS PAGE      status.json + components.json + incidents/unresolved.json.
                    Weak evidence. Reported, never sufficient for LOCAL.
2. CAPABILITY       Exercise what we actually depend on, and TIME it:
                    - API reachability + auth (`gh api /rate_limit`), including
                      remaining quota -- rate limiting is an outage mode that
                      looks exactly like an outage.
                    - git transport (`git ls-remote` against the repo URL).
                    - the Actions API (list recent runs).
                    401 (re-authenticate) / 403 (scope or rate) / 5xx (their
                    fault) / timeout are reported SEPARATELY, because the cause
                    selects the remedy and they are not interchangeable.
3. RUNNER-IMAGE DRIFT   The signal that would have caught 2026-08-18. Pull the
                    "Runner Image" group out of recent job logs and report any
                    CHANGE between the newest run and an older one. The last
                    seen image is cached in a small state file so drift is also
                    detectable ACROSS invocations.

                    PINNING DOES NOT EXIST, SO THIS MUST BE A CANARY. Per
                    GitHub staff (community discussion #173099): "You can't
                    check the exact runner image version that will be used ahead
                    of time." `$ImageVersion` is runtime-only. A passive poll of
                    "what image will I get?" is therefore structurally
                    impossible -- the only way to know is to read what a REAL
                    run actually got. That is why this layer records the image
                    from completed runs and diffs it, rather than querying a
                    version endpoint that does not and cannot exist.

                    SECOND AXIS: the runner AGENT ships separately from the
                    image, and Node moves with the agent (2026-08-18 also moved
                    node 22.23.1 -> 22.23.2). Tracking only the image would miss
                    it, so the agent version ("Current runner version: '...'",
                    the log's first line) is recorded and diffed alongside.

                    NOTE ON THE API: the version is only in the LOGS. Measured
                    2026-08-18 -- the keys on a job object are
                      check_run_url completed_at conclusion created_at
                      head_branch head_sha html_url id labels name node_id
                      run_attempt run_id run_url runner_group_id
                      runner_group_name runner_id runner_name started_at
                      status steps url workflow_name
                    `runner_name` is an opaque pool name ("GitHub Actions
                    1000015814") and `labels` is the requested label
                    ("ubuntu-latest"), NOT the resolved image version. No REST
                    field exposes it. If GitHub ever adds one, prefer it and
                    delete the log-scrape.

                    TRAP: the log contains TWO groups whose title starts with
                    "Runner Image" -- "Runner Image Provisioner" (the Azure
                    hosted-compute agent, a DIFFERENT version number) and
                    "Runner Image" (the one that matters). The parser matches
                    the group title EXACTLY. `--self-test` asserts this.

4. CROSS-BRANCH INVARIANCE   Over recent pull_request runs, if >=3 runs on
                    DIFFERENT branches fail at the SAME step name, the cause is
                    not any branch. That is the reasoning that cracked
                    2026-08-18; this automates it.

USAGE
-----
    python3 scripts/gh-health.py --repo owner/name --workflow ci.yml
    python3 scripts/gh-health.py --repo owner/name --workflow ci.yml --json
    python3 scripts/gh-health.py --self-test          # offline, fixtures
    python3 scripts/gh-health.py --must-fail drift    # teeth: must go red

Requires: Python 3 stdlib only. Uses `gh` and `git` via subprocess when present;
their absence is UNKNOWN, not LOCAL. No token value is ever printed -- captured
stderr is scrubbed of anything shaped like a GitHub token before display.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# ── Verdicts and exit codes ──────────────────────────────────────────────────
LOCAL = "LOCAL"
GITHUB_DEGRADED = "GITHUB_DEGRADED"
UNKNOWN = "UNKNOWN"

EXIT_BY_VERDICT = {LOCAL: 0, GITHUB_DEGRADED: 1, UNKNOWN: 2}

# Probe outcome states. RAN means the probe reached a conclusion; every other
# state is an admission of ignorance and forces UNKNOWN.
RAN = "ran"
FAILED = "failed"  # probe attempted, could not conclude (timeout/auth/parse)
SKIPPED = "skipped"  # probe not attempted (missing --repo, etc.)

# Finding levels within a probe that RAN.
CLEAN = "clean"
DEGRADED = "degraded"

STATUS_BASE = "https://www.githubstatus.com/api/v2"

DEFAULT_STATE_FILE = (
    Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache")))
    / "ravenclaude"
    / "gh-health-state.json"
)

# Detectors that `--must-fail` can disable, to prove the self-test has teeth.
DETECTORS = (
    "status-indicator",
    "status-components",
    "status-incidents",
    "rate-limit-exhaustion",
    "http-error-class",
    "drift",
    "invariance",
    "unknown-on-error",
    "probe-quorum",
)
DISABLED: set = set()


def enabled(detector: str) -> bool:
    """A detector is live unless --must-fail has deliberately broken it."""
    return detector not in DISABLED


# ── Token hygiene ────────────────────────────────────────────────────────────
# Never print a token value. gh usually does not echo one, but `git` and curl
# style errors can embed credentials in a URL, and a user's shell wrapper can
# leak one into stderr. Scrub before anything reaches stdout.
_TOKEN_RE = re.compile(
    r"(gh[pousr]_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{10,}|[A-Za-z0-9]+:[^@/\s]{8,}@)"
)


def scrub(text: str) -> str:
    return _TOKEN_RE.sub("<redacted>", text or "")


# ── Probe result ─────────────────────────────────────────────────────────────
class Probe:
    """One independently reportable signal.

    `state` answers "did this probe reach a conclusion?" and `finding` answers
    "what was the conclusion?". Reading `finding` without `state` is exactly the
    bug this class exists to prevent, so `finding` is meaningless unless
    `state == RAN`.
    """

    def __init__(self, name: str, layer: str) -> None:
        self.name = name
        self.layer = layer
        self.state: str = SKIPPED
        self.finding: str = CLEAN
        self.severity: str = ""  # incident | environment-change | pattern | quota
        self.reason: str = "not attempted"
        self.detail: list[str] = []
        self.duration_ms: int | None = None
        self.data: dict[str, Any] = {}

    def ok(self, reason: str) -> Probe:
        self.state, self.finding, self.reason = RAN, CLEAN, reason
        return self

    def degraded(self, severity: str, reason: str) -> Probe:
        self.state, self.finding = RAN, DEGRADED
        self.severity, self.reason = severity, reason
        return self

    def failed(self, reason: str) -> Probe:
        """Could not conclude. This is UNKNOWN fuel, never a clean bill."""
        self.state, self.finding, self.reason = FAILED, CLEAN, reason
        return self

    def skipped(self, reason: str) -> Probe:
        self.state, self.finding, self.reason = SKIPPED, CLEAN, reason
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "layer": self.layer,
            "state": self.state,
            "finding": self.finding if self.state == RAN else None,
            "severity": self.severity or None,
            "reason": self.reason,
            "detail": self.detail,
            "duration_ms": self.duration_ms,
            "data": self.data,
        }


# ── Transport ────────────────────────────────────────────────────────────────
class HttpResult:
    def __init__(
        self,
        obj: Any = None,
        error: str = "",
        status: int | None = None,
        ms: int = 0,
    ) -> None:
        self.obj = obj
        self.error = error
        self.status = status
        self.ms = ms


class CmdResult:
    def __init__(self, rc: int, out: str = "", err: str = "", ms: int = 0, missing: bool = False):
        self.rc = rc
        self.out = out
        self.err = err
        self.ms = ms
        self.missing = missing  # the binary itself is not installed


class RealTransport:
    """Live network. Every call is time-boxed; nothing may hang a session."""

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout

    def http_json(self, url: str) -> HttpResult:
        t0 = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "gh-health/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
                status = resp.getcode()
        except urllib.error.HTTPError as exc:
            return HttpResult(error="HTTP %s" % exc.code, status=exc.code, ms=_ms(t0))
        except Exception as exc:  # noqa: BLE001 - any transport failure is UNKNOWN
            return HttpResult(error="%s: %s" % (type(exc).__name__, scrub(str(exc))), ms=_ms(t0))
        try:
            return HttpResult(obj=json.loads(raw), status=status, ms=_ms(t0))
        except ValueError as exc:
            # An unparseable body is UNKNOWN, not health. Today's whole point.
            return HttpResult(error="unparseable JSON: %s" % exc, status=status, ms=_ms(t0))

    def gh(self, args: list[str]) -> CmdResult:
        if shutil.which("gh") is None:
            return CmdResult(127, err="`gh` is not installed", missing=True)
        return self._run(["gh"] + args)

    def git_ls_remote(self, url: str) -> CmdResult:
        if shutil.which("git") is None:
            return CmdResult(127, err="`git` is not installed", missing=True)
        # Measured 2026-08-18: `git ls-remote --heads <url> HEAD` returns ZERO
        # refs, because HEAD is not a head -- the pattern filters everything out.
        # The first version of this probe passed that empty result off as
        # "healthy (0 refs)", which is the precise failure-toward-fine this file
        # exists to prevent. `--heads` alone returns 65 refs on the same repo.
        return self._run(["git", "ls-remote", "--heads", url])

    def _run(self, argv: list[str]) -> CmdResult:
        t0 = time.time()
        env = dict(os.environ)
        env["GIT_TERMINAL_PROMPT"] = "0"  # never block on a credential prompt
        env["GH_PROMPT_DISABLED"] = "1"
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
            )
        except subprocess.TimeoutExpired:
            # GNU `timeout` is absent on macOS; subprocess timeout is the portable box.
            return CmdResult(-1, err="timeout after %.0fs" % self.timeout, ms=_ms(t0))
        except Exception as exc:  # noqa: BLE001
            return CmdResult(-1, err="%s: %s" % (type(exc).__name__, exc), ms=_ms(t0))
        return CmdResult(proc.returncode, proc.stdout, scrub(proc.stderr), _ms(t0))


def _ms(t0: float) -> int:
    return int((time.time() - t0) * 1000)


def classify_http_error(text: str, rc: int) -> tuple[str, str]:
    """Map a failure to (class, remedy). The cause selects the remedy."""
    if not enabled("http-error-class"):
        return ("error", "generic failure")
    if "timeout" in text.lower():
        return ("timeout", "GitHub did not answer in time -- their side or your network")
    match = re.search(r"HTTP (\d{3})", text)
    code = int(match.group(1)) if match else None
    if code == 401:
        return ("401", "credentials rejected -- re-authenticate (`gh auth login`)")
    if code == 403:
        return ("403", "forbidden -- missing token scope OR you are rate limited")
    if code == 404:
        return ("404", "not found -- check --repo/--workflow spelling and access")
    if code is not None and 500 <= code <= 599:
        return (str(code), "server error -- GitHub's fault")
    if rc == 127:
        return ("missing-binary", "install the missing binary")
    return ("error", "unclassified failure")


# ── Layer 1: status page ─────────────────────────────────────────────────────
def probe_status_page(tx: Any) -> Probe:
    """WEAK evidence. Green here contributes nothing toward LOCAL on its own;
    the probe quorum enforces that structurally, not by convention.

    All three endpoints are MANDATORY. `indicator` and `components` are
    structurally blind to an incident with `components: []` (see the module
    header: a major open incident sat beside `indicator: none` 37 ms after the
    page updated for it). `incidents/unresolved.json` is the only one of the
    three that can see that shape, so its failure is UNKNOWN, never a pass.
    """
    p = Probe("status_page", "1-status")
    t0 = time.time()
    results = {}
    for key, url in (
        ("status", STATUS_BASE + "/status.json"),
        ("components", STATUS_BASE + "/components.json"),
        ("incidents", STATUS_BASE + "/incidents/unresolved.json"),
    ):
        results[key] = tx.http_json(url)
    p.duration_ms = _ms(t0)

    broken = [(k, r.error) for k, r in results.items() if r.error or r.obj is None]
    if broken:
        cls, remedy = classify_http_error(broken[0][1], 0)
        p.failed("status page unreachable/unparseable (%s: %s) -- %s" % (broken[0][0], cls, remedy))
        p.detail = ["%s -> %s" % (k, scrub(e)) for k, e in broken]
        return p

    findings: list[str] = []

    status = results["status"].obj or {}
    indicator = (status.get("status") or {}).get("indicator", "?")
    description = (status.get("status") or {}).get("description", "?")
    p.data["indicator"] = indicator
    p.data["description"] = description
    p.detail.append("indicator=%s (%s)" % (indicator, description))
    if enabled("status-indicator") and indicator not in ("none", "?"):
        findings.append("status indicator is %r (%s)" % (indicator, description))

    comps = results["components"].obj
    comp_list = comps.get("components", []) if isinstance(comps, dict) else (comps or [])
    bad = [
        c
        for c in comp_list
        if isinstance(c, dict) and c.get("status") not in ("operational", None)
    ]
    p.data["non_operational_components"] = [
        {"name": c.get("name"), "status": c.get("status")} for c in bad
    ]
    p.detail.append("components: %d listed, %d non-operational" % (len(comp_list), len(bad)))
    if enabled("status-components") and bad:
        for c in bad:
            findings.append("component %r is %s" % (c.get("name"), c.get("status")))

    inc = results["incidents"].obj
    inc_list = inc.get("incidents", []) if isinstance(inc, dict) else (inc or [])
    p.data["unresolved_incidents"] = [
        {"name": i.get("name"), "impact": i.get("impact"), "status": i.get("status")}
        for i in inc_list
        if isinstance(i, dict)
    ]
    p.detail.append("unresolved incidents: %d" % len(inc_list))
    if enabled("status-incidents") and inc_list:
        for i in inc_list:
            if isinstance(i, dict):
                findings.append(
                    "unresolved incident: %s (impact=%s, status=%s)"
                    % (i.get("name"), i.get("impact"), i.get("status"))
                )

    if findings:
        p.detail.extend(findings)
        return p.degraded("incident", "; ".join(findings[:3]))
    return p.ok("all green (WEAK evidence -- an image rollout is not an incident)")


# ── Layer 2: capability probes ───────────────────────────────────────────────
def probe_api_auth(tx: Any) -> Probe:
    """API reachability + auth + remaining quota. Rate limiting is an outage
    mode that looks exactly like an outage, so quota is reported, not assumed."""
    p = Probe("api_auth", "2-capability")
    res = tx.gh(["api", "/rate_limit"])
    p.duration_ms = res.ms
    if res.rc != 0:
        cls, remedy = classify_http_error(res.err, res.rc)
        p.detail.append(scrub(res.err.strip())[:400])
        return p.failed("gh api /rate_limit failed [%s] -- %s" % (cls, remedy))
    try:
        obj = json.loads(res.out)
    except ValueError as exc:
        return p.failed("unparseable /rate_limit JSON: %s" % exc)

    resources = obj.get("resources") or {}
    worst_name, worst_frac = None, 1.0
    for name in ("core", "graphql", "search"):
        block = resources.get(name)
        if not isinstance(block, dict):
            continue
        limit = block.get("limit") or 0
        remaining = block.get("remaining")
        if remaining is None or not limit:
            continue
        frac = remaining / float(limit)
        p.data[name] = {"remaining": remaining, "limit": limit}
        p.detail.append("%s: %s/%s remaining (%.0f%%)" % (name, remaining, limit, frac * 100))
        if frac < worst_frac:
            worst_name, worst_frac = name, frac

    if worst_name is None:
        return p.failed("/rate_limit returned no readable resource blocks")
    if enabled("rate-limit-exhaustion") and worst_frac <= 0.02:
        return p.degraded(
            "quota",
            "rate limit effectively exhausted: %s at %.0f%% remaining -- "
            "this presents as an outage but the remedy is to wait or re-scope"
            % (worst_name, worst_frac * 100),
        )
    return p.ok("authenticated; lowest quota %s at %.0f%%" % (worst_name, worst_frac * 100))


def probe_git_transport(tx: Any, repo: str) -> Probe:
    p = Probe("git_transport", "2-capability")
    if not repo:
        return p.skipped("no --repo given")
    res = tx.git_ls_remote("https://github.com/%s.git" % repo)
    p.duration_ms = res.ms
    if res.rc != 0:
        cls, remedy = classify_http_error(res.err, res.rc)
        p.detail.append(scrub(res.err.strip())[:400])
        if res.missing:
            return p.failed("git not installed -- cannot test transport")
        # A hard transport failure against a repo we know exists is GitHub-side.
        if "could not read" in res.err.lower() or "authentication" in res.err.lower():
            return p.failed("git transport auth failure [%s] -- %s" % (cls, remedy))
        if cls in ("timeout",) or re.search(r"HTTP 5\d\d", res.err):
            return p.degraded("incident", "git transport failing [%s] -- %s" % (cls, remedy))
        return p.failed("git ls-remote failed [%s] -- %s" % (cls, remedy))
    refs = len([ln for ln in res.out.splitlines() if ln.strip()])
    p.data["refs"] = refs
    p.detail.append("%d refs in %dms" % (refs, res.ms))
    if refs == 0:
        # An empty result is a claim about the PROBE until a positive control
        # shows it can return non-empty. rc==0 with no refs proves nothing.
        return p.failed(
            "git ls-remote exited 0 but returned ZERO refs -- that is an "
            "unverified probe, not a healthy transport"
        )
    return p.ok("git transport healthy (%d refs, %dms)" % (refs, res.ms))


def probe_actions_api(tx: Any, repo: str) -> Probe:
    p = Probe("actions_api", "2-capability")
    if not repo:
        return p.skipped("no --repo given")
    res = tx.gh(["api", "repos/%s/actions/runs?per_page=1" % repo])
    p.duration_ms = res.ms
    if res.rc != 0:
        cls, remedy = classify_http_error(res.err, res.rc)
        p.detail.append(scrub(res.err.strip())[:400])
        if re.search(r"HTTP 5\d\d", res.err):
            return p.degraded("incident", "Actions API 5xx [%s] -- %s" % (cls, remedy))
        return p.failed("Actions API unreachable [%s] -- %s" % (cls, remedy))
    try:
        obj = json.loads(res.out)
    except ValueError as exc:
        return p.failed("unparseable Actions API JSON: %s" % exc)
    total = obj.get("total_count")
    p.data["total_count"] = total
    p.detail.append("Actions API answered in %dms (total_count=%s)" % (res.ms, total))
    return p.ok("Actions API reachable (%dms)" % res.ms)


# ── Layer 3: runner-image drift ──────────────────────────────────────────────
# Log lines are "<ISO8601>Z <payload>", the first optionally BOM-prefixed.
_LOGLINE_RE = re.compile(r"^﻿?(?:\d{4}-\d{2}-\d{2}T[\d:.]+Z\s)?(.*)$")
_AGENT_RE = re.compile(r"^Current runner version:\s*'([^']+)'")


def parse_runner_image(log_text: str) -> dict[str, str] | None:
    """Extract Image/Version from the "Runner Image" group.

    TRAP, asserted in --self-test: the log also contains "Runner Image
    Provisioner", a DIFFERENT group carrying a DIFFERENT Version. A prefix or
    substring match silently reads the provisioner's version and reports drift
    that is not there (or misses drift that is). The title match is EXACT.
    """
    inside = False
    found: dict[str, str] = {}
    for raw in log_text.splitlines():
        m = _LOGLINE_RE.match(raw)
        payload = (m.group(1) if m else raw).strip()
        # The runner AGENT version sits outside every group, on line 1. It ships
        # separately from the image and carries Node with it, so it is a second
        # drift axis -- tracking only the image would miss a Node bump.
        agent = _AGENT_RE.match(payload)
        if agent:
            found["agent"] = agent.group(1)
            continue
        if payload.startswith("##[group]"):
            inside = payload[len("##[group]") :].strip() == "Runner Image"
            continue
        if payload == "##[endgroup]":
            if inside and found:
                break
            inside = False
            continue
        if not inside:
            continue
        if payload.startswith("Image:"):
            found["image"] = payload.split(":", 1)[1].strip()
        elif payload.startswith("Version:"):
            found["version"] = payload.split(":", 1)[1].strip()
    if "image" in found and "version" in found:
        found.setdefault("agent", "?")
        return found
    return None


def load_state(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, ValueError):
        return {}


def save_state(path: Path, state: dict[str, Any]) -> str | None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
        return None
    except OSError as exc:
        return str(exc)


def probe_runner_drift(
    tx: Any,
    repo: str,
    runs: list[dict[str, Any]],
    runs_error: str,
    samples: int,
    state_file: Path,
    state_key: str,
) -> Probe:
    """The signal that would have caught 2026-08-18."""
    p = Probe("runner_image_drift", "3-drift")
    if not repo:
        return p.skipped("no --repo given")
    if runs_error:
        return p.failed("cannot list runs: %s" % runs_error)
    if not runs:
        return p.failed("no workflow runs returned -- nothing to compare")

    t0 = time.time()
    # Sample the newest few AND the oldest few, so the comparison spans a real
    # time window. Sampling only consecutive runs would have MISSED 2026-08-18,
    # because six consecutive runs all sat on the new image.
    n = len(runs)
    idx: list[int] = []
    half = max(1, samples // 2)
    for i in list(range(min(half, n))) + list(range(max(0, n - half), n)):
        if i not in idx:
            idx.append(i)

    observations: list[dict[str, Any]] = []
    errors: list[str] = []
    for i in idx:
        run = runs[i]
        run_id = run.get("id")
        jobs_res = tx.gh(["api", "repos/%s/actions/runs/%s/jobs" % (repo, run_id)])
        if jobs_res.rc != 0:
            errors.append("run %s: jobs API %s" % (run_id, classify_http_error(jobs_res.err, 0)[0]))
            continue
        try:
            jobs = (json.loads(jobs_res.out) or {}).get("jobs") or []
        except ValueError:
            errors.append("run %s: unparseable jobs JSON" % run_id)
            continue
        job = next((j for j in jobs if j.get("runner_name")), None)
        if job is None:
            continue  # every job skipped; no runner was ever allocated
        log_res = tx.gh(["api", "repos/%s/actions/jobs/%s/logs" % (repo, job.get("id"))])
        if log_res.rc != 0:
            errors.append("job %s: logs %s" % (job.get("id"), classify_http_error(log_res.err, 0)[0]))
            continue
        img = parse_runner_image(log_res.out)
        if img is None:
            errors.append("job %s: no 'Runner Image' group in log" % job.get("id"))
            continue
        observations.append(
            {
                "run_id": run_id,
                "created_at": run.get("created_at"),
                "branch": run.get("head_branch"),
                "image": img["image"],
                "version": img["version"],
                "agent": img.get("agent", "?"),
            }
        )

    p.duration_ms = _ms(t0)
    p.data["observations"] = observations
    p.data["errors"] = errors
    for obs in observations:
        p.detail.append(
            "run %s (%s, %s): image %s / %s   agent %s"
            % (
                obs["run_id"],
                obs["branch"],
                obs["created_at"],
                obs["image"],
                obs["version"],
                obs["agent"],
            )
        )
    if errors:
        p.detail.extend("could not read: " + e for e in errors)

    state = load_state(state_file)
    prior = state.get(state_key)

    newest = observations[0] if observations else None
    if newest is not None:
        state[state_key] = {
            "image": newest["image"],
            "version": newest["version"],
            "agent": newest["agent"],
            "run_id": newest["run_id"],
            "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        err = save_state(state_file, state)
        if err:
            p.detail.append("state file not written: %s" % err)
        else:
            p.data["state_file"] = str(state_file)

    if not enabled("drift"):
        return p.ok("drift detector disabled (--must-fail)")

    # Both axes: the image AND the separately-shipped runner agent.
    distinct = sorted({(o["image"], o["version"], o["agent"]) for o in observations})
    p.data["distinct_images"] = ["%s / %s (agent %s)" % (a, b, c) for a, b, c in distinct]

    def _axes(older: dict, newer: dict) -> str:
        moved = []
        if (older["image"], older["version"]) != (newer["image"], newer["version"]):
            moved.append(
                "IMAGE %s / %s -> %s / %s"
                % (older["image"], older["version"], newer["image"], newer["version"])
            )
        if older["agent"] != newer["agent"]:
            moved.append(
                "RUNNER AGENT %s -> %s (Node ships with the agent, not the image)"
                % (older["agent"], newer["agent"])
            )
        return "; ".join(moved)

    if len(distinct) >= 2:
        oldest, newest_iv = observations[-1], observations[0]
        return p.degraded(
            "environment-change",
            "RUNNER SUBSTRATE CHANGED across the sampled window: %s "
            "(run %s, %s -> run %s, %s). Unchanged code on a changed substrate "
            "explains a fleet-wide flip."
            % (
                _axes(oldest, newest_iv),
                oldest["run_id"],
                oldest["created_at"],
                newest_iv["run_id"],
                newest_iv["created_at"],
            ),
        )

    if prior and newest and (prior.get("image"), prior.get("version"), prior.get("agent")) != (
        newest["image"],
        newest["version"],
        newest["agent"],
    ):
        return p.degraded(
            "environment-change",
            "RUNNER SUBSTRATE CHANGED since the last invocation (seen %s): %s"
            % (
                prior.get("observed_at"),
                _axes(
                    {
                        "image": prior.get("image"),
                        "version": prior.get("version"),
                        "agent": prior.get("agent", "?"),
                    },
                    newest,
                ),
            ),
        )

    if len(observations) < 2 and not prior:
        # Honest: one observation and no cached baseline cannot rule drift out.
        return p.failed(
            "only %d image observation(s) and no cached baseline -- drift cannot be "
            "ruled out yet; re-run after the next workflow run to establish one"
            % len(observations)
        )

    return p.ok(
        "runner image stable at %s across %d observation(s)"
        % (p.data["distinct_images"][0] if distinct else "?", len(observations))
    )


# ── Layer 4: cross-branch invariance ─────────────────────────────────────────
def probe_cross_branch(
    tx: Any,
    repo: str,
    runs: list[dict[str, Any]],
    runs_error: str,
    threshold: int,
) -> Probe:
    """>=3 runs on DIFFERENT branches failing at the SAME step name is strong
    evidence the cause is not any branch."""
    p = Probe("cross_branch_invariance", "4-invariance")
    if not repo:
        return p.skipped("no --repo given")
    if runs_error:
        return p.failed("cannot list runs: %s" % runs_error)
    if not runs:
        return p.failed("no workflow runs returned -- nothing to compare")

    t0 = time.time()
    failed_runs = [r for r in runs if r.get("conclusion") == "failure"]
    p.data["runs_examined"] = len(runs)
    p.data["failed_runs"] = len(failed_runs)
    if not failed_runs:
        p.duration_ms = _ms(t0)
        p.detail.append("%d runs examined, 0 failures" % len(runs))
        return p.ok("no failing runs in the window (%d examined)" % len(runs))

    by_step: dict[str, dict[str, list[Any]]] = {}
    errors: list[str] = []
    for run in failed_runs:
        run_id, branch = run.get("id"), run.get("head_branch") or "?"
        res = tx.gh(["api", "repos/%s/actions/runs/%s/jobs" % (repo, run_id)])
        if res.rc != 0:
            errors.append("run %s: jobs API %s" % (run_id, classify_http_error(res.err, 0)[0]))
            continue
        try:
            jobs = (json.loads(res.out) or {}).get("jobs") or []
        except ValueError:
            errors.append("run %s: unparseable jobs JSON" % run_id)
            continue
        for job in jobs:
            for step in job.get("steps") or []:
                if step.get("conclusion") == "failure":
                    entry = by_step.setdefault(step.get("name") or "?", {})
                    entry.setdefault(branch, []).append(run_id)

    p.duration_ms = _ms(t0)
    p.data["errors"] = errors
    if errors:
        p.detail.extend("could not read: " + e for e in errors)

    # A probe that could not read ANY failing run has concluded nothing.
    if not by_step and errors:
        return p.failed("could not read the failing steps of any run (%d errors)" % len(errors))

    hits = []
    for step, branches in sorted(by_step.items(), key=lambda kv: -len(kv[1])):
        p.detail.append(
            "step %r failed on %d branch(es): %s"
            % (step, len(branches), ", ".join(sorted(branches)))
        )
        if enabled("invariance") and len(branches) >= threshold:
            hits.append((step, branches))

    p.data["steps"] = {s: sorted(b) for s, b in by_step.items()}

    if hits:
        step, branches = hits[0]
        p.data["invariant_step"] = step
        p.data["invariant_branches"] = sorted(branches)
        return p.degraded(
            "pattern",
            "step %r failed on %d DIFFERENT branches (%s) -- the cause is not any "
            "one branch's code" % (step, len(branches), ", ".join(sorted(branches))),
        )
    return p.ok(
        "no step failed on >=%d distinct branches (%d failing run(s) examined)"
        % (threshold, len(failed_runs))
    )


# ── Run listing (shared by layers 3 and 4) ───────────────────────────────────
def list_runs(
    tx: Any, repo: str, workflow: str | None, max_runs: int
) -> tuple[list[dict[str, Any]], str]:
    if not repo:
        return ([], "no --repo given")
    if workflow:
        path = "repos/%s/actions/workflows/%s/runs?per_page=%d&event=pull_request" % (
            repo,
            workflow,
            max_runs,
        )
    else:
        path = "repos/%s/actions/runs?per_page=%d&event=pull_request" % (repo, max_runs)
    res = tx.gh(["api", path])
    if res.rc != 0:
        cls, remedy = classify_http_error(res.err, res.rc)
        return ([], "[%s] %s" % (cls, remedy))
    try:
        obj = json.loads(res.out) or {}
    except ValueError as exc:
        return ([], "unparseable runs JSON: %s" % exc)
    runs = obj.get("workflow_runs") or []
    # Newest first, and only completed runs carry usable conclusions.
    return ([r for r in runs if r.get("status") == "completed"], "")


# ── Verdict aggregation ──────────────────────────────────────────────────────
def decide(probes: list[Probe]) -> tuple[str, str]:
    """GITHUB_DEGRADED > UNKNOWN > LOCAL.

    LOCAL is gated by the probe quorum: EVERY probe must have reached a
    conclusion. That is what stops a green status page -- or a run without
    --repo -- from ever producing LOCAL on its own.
    """
    degraded = [p for p in probes if p.state == RAN and p.finding == DEGRADED]
    if degraded:
        return (
            GITHUB_DEGRADED,
            "%d probe(s) found positive GitHub-side evidence: %s"
            % (len(degraded), "; ".join(p.name for p in degraded)),
        )

    inconclusive = [p for p in probes if p.state != RAN]
    if inconclusive and enabled("probe-quorum") and enabled("unknown-on-error"):
        return (
            UNKNOWN,
            "%d of %d probes did not reach a conclusion (%s) -- an unrun probe is "
            "NOT evidence of health"
            % (
                len(inconclusive),
                len(probes),
                ", ".join("%s: %s" % (p.name, p.reason) for p in inconclusive),
            ),
        )

    return (
        LOCAL,
        "all %d probes ran and all were clean -- GitHub looks healthy on every "
        "dimension checked, so suspicion returns to our code" % len(probes),
    )


# ── Reporting ────────────────────────────────────────────────────────────────
_MARK = {RAN: "RAN", FAILED: "NOT-RUN(failed)", SKIPPED: "NOT-RUN(skipped)"}


def render(verdict: str, why: str, probes: list[Probe], args: Any) -> str:
    lines = []
    ran = [p for p in probes if p.state == RAN]
    lines.append("=" * 78)
    lines.append("gh-health  --  is this GitHub's problem or mine?")
    lines.append("repo=%s  workflow=%s" % (args.repo or "(none)", args.workflow or "(all)"))
    lines.append("=" * 78)
    lines.append("")
    lines.append("VERDICT: %s   (exit %d)" % (verdict, EXIT_BY_VERDICT[verdict]))
    lines.append("REASON : %s" % why)
    lines.append("BASIS  : %d of %d probes reached a conclusion" % (len(ran), len(probes)))
    lines.append("")
    lines.append("PROBES")
    lines.append("-" * 78)
    for p in probes:
        badge = _MARK[p.state]
        if p.state == RAN:
            badge += " / " + ("DEGRADED" if p.finding == DEGRADED else "clean")
        dur = "" if p.duration_ms is None else "  [%dms]" % p.duration_ms
        lines.append("  %-24s %-8s %-22s%s" % (p.name, p.layer, badge, dur))
        lines.append("      %s" % p.reason)
        if args.verbose:
            for d in p.detail:
                lines.append("        . %s" % d)
    lines.append("-" * 78)
    if not args.verbose:
        lines.append("(--verbose for per-probe evidence)")
    if verdict == GITHUB_DEGRADED:
        lines.append("")
        lines.append("EVIDENCE OF A GITHUB-SIDE CAUSE:")
        for p in probes:
            if p.state == RAN and p.finding == DEGRADED:
                lines.append("  [%s] %s" % (p.severity or "?", p.reason))
    if verdict == UNKNOWN:
        lines.append("")
        lines.append("UNKNOWN is not 'fine'. Fix the probes below, then re-run:")
        for p in probes:
            if p.state != RAN:
                lines.append("  %s: %s" % (p.name, p.reason))
    return "\n".join(lines)


# ── Live run ─────────────────────────────────────────────────────────────────
def run_live(args: argparse.Namespace, tx: Any) -> tuple[str, str, list[Probe]]:
    state_file = Path(args.state_file).expanduser()
    state_key = "%s::%s" % (args.repo or "-", args.workflow or "*")
    runs, runs_error = list_runs(tx, args.repo, args.workflow, args.max_runs)
    probes = [
        probe_status_page(tx),
        probe_api_auth(tx),
        probe_git_transport(tx, args.repo),
        probe_actions_api(tx, args.repo),
        probe_runner_drift(
            tx, args.repo, runs, runs_error, args.drift_samples, state_file, state_key
        ),
        probe_cross_branch(tx, args.repo, runs, runs_error, args.invariance_threshold),
    ]
    verdict, why = decide(probes)
    return verdict, why, probes


# ═════════════════════════════════════════════════════════════════════════════
#  SELF-TEST -- offline, fixture-driven, and it must be able to FAIL
# ═════════════════════════════════════════════════════════════════════════════
GREEN_STATUS = {"status": {"indicator": "none", "description": "All Systems Operational"}}
RED_STATUS = {
    "status": {"indicator": "major", "description": "Major Service Outage"},
    "page": {"name": "GitHub"},
}
OK_COMPONENTS = {"components": [{"name": "Actions", "status": "operational"}]}
BAD_COMPONENTS = {"components": [{"name": "Actions", "status": "partial_outage"}]}
NO_INCIDENTS = {"incidents": []}
AN_INCIDENT = {
    "incidents": [{"name": "Degraded Actions", "impact": "major", "status": "investigating"}]
}
# ── The 2026-08-18 replay: the single most important fixture in this file ────
# All three payloads below were observed SIMULTANEOUSLY on 2026-08-18. The
# incident carries `components: []`, which is why it moved neither the indicator
# nor any component. A tool that reads only the first two returns "all clear"
# over a major open Actions incident -- the exact bug this file exists to catch.
REPLAY_STATUS = {
    "page": {"id": "kctbh9vrtdwd", "name": "GitHub", "updated_at": "2026-08-18T09:36:40.359Z"},
    "status": {"indicator": "none", "description": "All Systems Operational"},
}
REPLAY_COMPONENTS = {
    "components": [
        {"name": n, "status": "operational"}
        for n in (
            "Git Operations", "API Requests", "Webhooks", "Issues", "Pull Requests",
            "Actions", "Packages", "Pages", "Codespaces", "Copilot",
            "Copilot Chat", "Copilot Code Completion",
        )
    ]
}
REPLAY_INCIDENTS = {
    "incidents": [
        {
            "name": "Incident with Actions",
            "impact": "major",
            "status": "investigating",
            "created_at": "2026-08-18T09:36:40.322Z",
            "components": [],
        }
    ]
}

RATE_OK = {"resources": {"core": {"limit": 5000, "remaining": 4900}}}
RATE_DEAD = {"resources": {"core": {"limit": 5000, "remaining": 0}}}

# Real log shape, verbatim from job 95665602168 (RavenPower-Website, 2026-08-18),
# including the BOM, the ISO timestamps, and -- critically -- the "Runner Image
# Provisioner" group whose Version is a DIFFERENT number.
LOG_TEMPLATE = (
    "﻿2026-08-18T09:35:58.5243029Z Current runner version: '{agent}'\n"
    "2026-08-18T09:35:58.5282351Z ##[group]Runner Image Provisioner\n"
    "2026-08-18T09:35:58.5284237Z Hosted Compute Agent\n"
    "2026-08-18T09:35:58.5285298Z Version: 20260729.566\n"
    "2026-08-18T09:35:58.5291591Z ##[endgroup]\n"
    "2026-08-18T09:35:58.5294325Z ##[group]Operating System\n"
    "2026-08-18T09:35:58.5295482Z Ubuntu\n"
    "2026-08-18T09:35:58.5298097Z ##[endgroup]\n"
    "2026-08-18T09:35:58.5299035Z ##[group]Runner Image\n"
    "2026-08-18T09:35:58.5300083Z Image: {image}\n"
    "2026-08-18T09:35:58.5301059Z Version: {version}\n"
    "2026-08-18T09:35:58.5308648Z ##[endgroup]\n"
)


class FakeTransport:
    """Deterministic offline substrate. `http_fail`/`http_garbage` simulate the
    two ways a probe lies: no answer, and an answer nobody can parse."""

    def __init__(
        self,
        status: Any = None,
        components: Any = None,
        incidents: Any = None,
        rate: Any = None,
        runs: list[dict[str, Any]] | None = None,
        jobs: dict[Any, list[dict[str, Any]]] | None = None,
        images: dict[Any, tuple[str, str]] | None = None,
        http_fail: bool = False,
        http_garbage: bool = False,
        gh_missing: bool = False,
        gh_error: str = "",
        gh_garbage: bool = False,
        git_rc: int = 0,
        git_err: str = "",
    ) -> None:
        self.status = GREEN_STATUS if status is None else status
        self.components = OK_COMPONENTS if components is None else components
        self.incidents = NO_INCIDENTS if incidents is None else incidents
        self.rate = RATE_OK if rate is None else rate
        self.runs = runs or []
        self.jobs = jobs or {}
        self.images = images or {}
        self.http_fail = http_fail
        self.http_garbage = http_garbage
        self.gh_missing = gh_missing
        self.gh_error = gh_error
        self.gh_garbage = gh_garbage
        self.git_rc = git_rc
        self.git_err = git_err

    def http_json(self, url: str) -> HttpResult:
        if self.http_fail:
            return HttpResult(error="URLError: [Errno 8] nodename nor servname provided", ms=5)
        if self.http_garbage:
            return HttpResult(error="unparseable JSON: Expecting value: line 1 column 1", ms=5)
        if url.endswith("/status.json"):
            return HttpResult(obj=self.status, status=200, ms=5)
        if url.endswith("/components.json"):
            return HttpResult(obj=self.components, status=200, ms=5)
        return HttpResult(obj=self.incidents, status=200, ms=5)

    def gh(self, argv: list[str]) -> CmdResult:
        if self.gh_missing:
            return CmdResult(127, err="`gh` is not installed", missing=True)
        if self.gh_error:
            return CmdResult(1, err=self.gh_error, ms=5)
        if self.gh_garbage:
            return CmdResult(0, out="<!DOCTYPE html> not json at all", ms=5)
        path = argv[-1]
        if "/rate_limit" in path:
            return CmdResult(0, out=json.dumps(self.rate), ms=5)
        m = re.search(r"/actions/runs/(\d+)/jobs", path)
        if m:
            return CmdResult(0, out=json.dumps({"jobs": self.jobs.get(int(m.group(1)), [])}), ms=5)
        m = re.search(r"/actions/jobs/(\d+)/logs", path)
        if m:
            entry = self.images.get(int(m.group(1)), ("ubuntu-24.04", "unknown"))
            image, version = entry[0], entry[1]
            agent = entry[2] if len(entry) > 2 else "2.336.0"
            return CmdResult(
                0, out=LOG_TEMPLATE.format(image=image, version=version, agent=agent), ms=5
            )
        if "/actions/runs" in path or "/runs?" in path:
            return CmdResult(
                0,
                out=json.dumps({"total_count": len(self.runs), "workflow_runs": self.runs}),
                ms=5,
            )
        return CmdResult(0, out="{}", ms=5)

    def git_ls_remote(self, url: str) -> CmdResult:
        if self.git_rc != 0:
            return CmdResult(self.git_rc, err=self.git_err, ms=5)
        return CmdResult(0, out="abc123\trefs/heads/main\n", ms=5)


def _run_ns(**kw: Any) -> argparse.Namespace:
    base = {
        "repo": "owner/name",
        "workflow": "ci.yml",
        "max_runs": 20,
        "drift_samples": 4,
        "invariance_threshold": 3,
        "state_file": "",
        "verbose": False,
        "json": False,
    }
    base.update(kw)
    return argparse.Namespace(**base)


def _mkrun(run_id: int, branch: str, conclusion: str = "failure") -> dict[str, Any]:
    return {
        "id": run_id,
        "head_branch": branch,
        "status": "completed",
        "conclusion": conclusion,
        "created_at": "2026-08-1%dT00:00:00Z" % (run_id % 9),
    }


def _mkjob(job_id: int, step: str, step_conclusion: str = "failure") -> dict[str, Any]:
    return {
        "id": job_id,
        "name": "build",
        "conclusion": "failure",
        "runner_name": "GitHub Actions 1000015814",
        "steps": [
            {"name": "Set up job", "conclusion": "success"},
            {"name": step, "conclusion": step_conclusion},
        ],
    }


class SelfTest:
    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: list[str] = []

    def check(self, name: str, cond: bool, detail: str = "") -> None:
        if cond:
            self.passed.append(name)
        else:
            self.failed.append("%s  <-- %s" % (name, detail or "assertion false"))

    def eq(self, name: str, got: Any, want: Any) -> None:
        self.check(name, got == want, "got %r, want %r" % (got, want))


def self_test(state_dir: Path) -> SelfTest:
    """Every assertion below is a detector this tool would be worthless without.
    `--must-fail <detector>` disables one and this suite MUST then go red."""
    t = SelfTest()

    def verdict_of(tx: FakeTransport, **ns: Any) -> tuple[str, list[Probe]]:
        args = _run_ns(state_file=str(state_dir / ("s%d.json" % time.time_ns())), **ns)
        v, _why, probes = run_live(args, tx)
        return v, probes

    # ── Fixture A: the fleet-wide flip of 2026-08-18 ─────────────────────────
    # All green on the status page, five branches, all failing at ONE step,
    # runner image changed underneath. This is the real incident, in miniature.
    branches = [
        "test/uptime-body-keyset",
        "fix/ops-cron-test-topology",
        "fix/uploads-r2-binding",
        "rescue/portal-bar-sub-jump",
        "chore/commerce-ci-concurrency",
    ]
    step = "portal render gate (glass roles, both themes + mutation matrix)"
    incident_runs = [_mkrun(100 + i, b) for i, b in enumerate(branches)]
    incident_jobs = {100 + i: [_mkjob(900 + i, step)] for i in range(len(branches))}
    # Newest runs on the NEW image, the oldest on the previous one.
    incident_images = {900: ("ubuntu-24.04", "20260810.271.1")}
    for i in range(1, len(branches)):
        incident_images[900 + i] = ("ubuntu-24.04", "20260810.271.1")
    incident_images[900 + len(branches) - 1] = ("ubuntu-24.04", "20260720.247.2")

    tx = FakeTransport(runs=incident_runs, jobs=incident_jobs, images=incident_images)
    v, probes = verdict_of(tx)
    by_name = {p.name: p for p in probes}

    # 1. An all-green status page must NOT suppress the drift finding.
    t.eq(
        "green-status-page-still-surfaces-drift",
        (by_name["status_page"].finding, by_name["runner_image_drift"].finding),
        (CLEAN, DEGRADED),
    )
    t.check(
        "drift-names-both-versions",
        "20260720.247.2" in by_name["runner_image_drift"].reason
        and "20260810.271.1" in by_name["runner_image_drift"].reason,
        by_name["runner_image_drift"].reason,
    )
    # 2. Same step, five different branches -> invariance finding.
    inv = by_name["cross_branch_invariance"]
    t.eq("invariance-fires-on-5-branches", inv.finding, DEGRADED)
    t.eq("invariance-names-the-step", inv.data.get("invariant_step"), step)
    t.eq("invariance-names-the-branches", sorted(inv.data.get("invariant_branches") or []), sorted(branches))
    # 3. Overall verdict for the real incident.
    t.eq("real-incident-verdict-is-degraded", v, GITHUB_DEGRADED)

    # ── Exactly the threshold, and one under it ──────────────────────────────
    three = branches[:3]
    tx3 = FakeTransport(
        runs=[_mkrun(200 + i, b) for i, b in enumerate(three)],
        jobs={200 + i: [_mkjob(800 + i, step)] for i in range(3)},
        images={800 + i: ("ubuntu-24.04", "20260810.271.1") for i in range(3)},
    )
    _v3, p3 = verdict_of(tx3)
    t.eq(
        "invariance-fires-at-exactly-3-branches",
        {p.name: p.finding for p in p3}["cross_branch_invariance"],
        DEGRADED,
    )

    two = branches[:2]
    tx2 = FakeTransport(
        runs=[_mkrun(300 + i, b) for i, b in enumerate(two)],
        jobs={300 + i: [_mkjob(700 + i, step)] for i in range(2)},
        images={700 + i: ("ubuntu-24.04", "20260810.271.1") for i in range(2)},
    )
    _v2, p2 = verdict_of(tx2)
    t.eq(
        "invariance-silent-at-2-branches",
        {p.name: p.finding for p in p2}["cross_branch_invariance"],
        CLEAN,
    )
    # Same branch three times is NOT invariance -- it is one branch retried.
    txs = FakeTransport(
        runs=[_mkrun(400 + i, "one/branch") for i in range(3)],
        jobs={400 + i: [_mkjob(600 + i, step)] for i in range(3)},
        images={600 + i: ("ubuntu-24.04", "20260810.271.1") for i in range(3)},
    )
    _vs, ps = verdict_of(txs)
    t.eq(
        "invariance-not-fooled-by-one-branch-retried",
        {p.name: p.finding for p in ps}["cross_branch_invariance"],
        CLEAN,
    )

    # ── Degraded status page ─────────────────────────────────────────────────
    clean_runs = [_mkrun(500 + i, b, "success") for i, b in enumerate(branches[:3])]
    clean_images = {500 + i: ("ubuntu-24.04", "20260810.271.1") for i in range(3)}
    clean_jobs = {500 + i: [_mkjob(500 + i, "build", "success")] for i in range(3)}

    v_red, p_red = verdict_of(
        FakeTransport(
            status=RED_STATUS, runs=clean_runs, jobs=clean_jobs, images=clean_images
        )
    )
    t.eq("degraded-indicator-yields-GITHUB_DEGRADED", v_red, GITHUB_DEGRADED)
    v_comp, _ = verdict_of(
        FakeTransport(
            components=BAD_COMPONENTS, runs=clean_runs, jobs=clean_jobs, images=clean_images
        )
    )
    t.eq("non-operational-component-yields-GITHUB_DEGRADED", v_comp, GITHUB_DEGRADED)
    v_inc, _ = verdict_of(
        FakeTransport(
            incidents=AN_INCIDENT, runs=clean_runs, jobs=clean_jobs, images=clean_images
        )
    )
    t.eq("unresolved-incident-yields-GITHUB_DEGRADED", v_inc, GITHUB_DEGRADED)
    t.check(
        "red-status-reason-is-printed",
        any("major" in p.reason.lower() for p in p_red if p.finding == DEGRADED),
        [p.reason for p in p_red],
    )

    # ── POSITIVE CONTROL: LOCAL must be reachable ────────────────────────────
    # Without this, a tool hardwired to never say LOCAL would pass every other
    # assertion here. An empty result is a claim about the probe until proven.
    v_local, p_local = verdict_of(
        FakeTransport(runs=clean_runs, jobs=clean_jobs, images=clean_images)
    )
    t.eq("positive-control-all-clean-yields-LOCAL", v_local, LOCAL)
    t.eq("positive-control-all-6-probes-ran", len([p for p in p_local if p.state == RAN]), 6)

    # ── THE BANNED DIRECTION: failure must never become LOCAL ────────────────
    v_net, p_net = verdict_of(
        FakeTransport(http_fail=True, runs=clean_runs, jobs=clean_jobs, images=clean_images)
    )
    t.eq("network-error-yields-UNKNOWN", v_net, UNKNOWN)
    t.check("network-error-is-not-LOCAL", v_net != LOCAL, v_net)
    t.eq("network-error-marks-probe-not-run", by_name and p_net[0].state, FAILED)

    v_garbage, _ = verdict_of(
        FakeTransport(http_garbage=True, runs=clean_runs, jobs=clean_jobs, images=clean_images)
    )
    t.eq("unparseable-status-JSON-yields-UNKNOWN", v_garbage, UNKNOWN)

    v_ghjson, _ = verdict_of(FakeTransport(gh_garbage=True))
    t.eq("unparseable-gh-JSON-yields-UNKNOWN", v_ghjson, UNKNOWN)

    v_nogh, p_nogh = verdict_of(FakeTransport(gh_missing=True))
    t.eq("missing-gh-binary-yields-UNKNOWN", v_nogh, UNKNOWN)
    t.check(
        "missing-gh-explains-itself",
        any("missing-binary" in p.reason for p in p_nogh),
        [p.reason for p in p_nogh],
    )

    v_401, p_401 = verdict_of(FakeTransport(gh_error="gh: Bad credentials (HTTP 401)"))
    t.eq("expired-token-401-yields-UNKNOWN", v_401, UNKNOWN)
    t.check(
        "401-remedy-is-reauthenticate",
        any("re-authenticate" in p.reason for p in p_401),
        [p.reason for p in p_401],
    )
    _v403, p_403 = verdict_of(FakeTransport(gh_error="gh: Forbidden (HTTP 403)"))
    t.check(
        "403-remedy-is-scope-or-rate",
        any("scope" in p.reason for p in p_403),
        [p.reason for p in p_403],
    )
    v_5xx, p_5xx = verdict_of(
        FakeTransport(gh_error="gh: Server Error (HTTP 503)", runs=clean_runs)
    )
    t.check(
        "5xx-blames-github",
        any("GitHub's fault" in p.reason for p in p_5xx),
        [p.reason for p in p_5xx],
    )
    t.check("5xx-is-not-LOCAL", v_5xx != LOCAL, v_5xx)
    _vto, p_to = verdict_of(FakeTransport(gh_error="timeout after 20s"))
    t.check(
        "timeout-classified-as-timeout-not-auth",
        any("timeout" in p.reason.lower() for p in p_to),
        [p.reason for p in p_to],
    )

    # ── Probe quorum: a green status page alone can never say LOCAL ──────────
    v_norepo, p_norepo = verdict_of(FakeTransport(), repo="", workflow=None)
    t.eq("green-status-page-alone-is-UNKNOWN-not-LOCAL", v_norepo, UNKNOWN)
    # api_auth needs no repo, so it still runs; the other four cannot.
    t.eq(
        "no-repo-leaves-4-repo-scoped-probes-unrun",
        len([p for p in p_norepo if p.state != RAN]),
        4,
    )
    t.eq(
        "no-repo-names-the-unrun-probes",
        sorted(p.name for p in p_norepo if p.state != RAN),
        ["actions_api", "cross_branch_invariance", "git_transport", "runner_image_drift"],
    )

    # ── Rate limit exhaustion is an outage mode ──────────────────────────────
    v_rate, p_rate = verdict_of(
        FakeTransport(rate=RATE_DEAD, runs=clean_runs, jobs=clean_jobs, images=clean_images)
    )
    t.eq("exhausted-rate-limit-yields-GITHUB_DEGRADED", v_rate, GITHUB_DEGRADED)
    t.check(
        "rate-limit-remaining-is-reported",
        any("0/5000" in d for p in p_rate for d in p.detail),
        [p.detail for p in p_rate],
    )

    # ── The "Runner Image Provisioner" trap ──────────────────────────────────
    parsed = parse_runner_image(
        LOG_TEMPLATE.format(image="ubuntu-24.04", version="20260810.271.1", agent="2.336.0")
    )
    t.eq(
        "parser-reads-Runner-Image-not-Provisioner",
        parsed,
        {"image": "ubuntu-24.04", "version": "20260810.271.1", "agent": "2.336.0"},
    )
    t.eq("parser-reads-the-runner-agent-version", (parsed or {}).get("agent"), "2.336.0")
    t.check(
        "parser-ignores-provisioner-version",
        parsed is not None and parsed["version"] != "20260729.566",
        parsed,
    )
    t.eq(
        "parser-returns-None-when-group-absent",
        parse_runner_image("2026-01-01T00:00:00.0Z Current runner version: '2.0.0'\n"),
        None,
    )
    t.eq(
        "parser-handles-log-without-timestamps",
        parse_runner_image("##[group]Runner Image\nImage: ubuntu-22.04\nVersion: 1.2.3\n##[endgroup]\n"),
        {"image": "ubuntu-22.04", "version": "1.2.3", "agent": "?"},
    )

    # ── Drift across invocations, via the state file ─────────────────────────
    shared = state_dir / "shared.json"
    old_only = FakeTransport(
        runs=[_mkrun(700, "main", "success")],
        jobs={700: [_mkjob(770, "build", "success")]},
        images={770: ("ubuntu-24.04", "20260720.247.2")},
    )
    args1 = _run_ns(state_file=str(shared))
    _v1, _w1, probes1 = run_live(args1, old_only)
    d1 = {p.name: p for p in probes1}["runner_image_drift"]
    t.check(
        "single-observation-no-baseline-is-NOT-clean",
        d1.state == FAILED,
        "%s / %s" % (d1.state, d1.reason),
    )
    new_only = FakeTransport(
        runs=[_mkrun(701, "main", "success")],
        jobs={701: [_mkjob(771, "build", "success")]},
        images={771: ("ubuntu-24.04", "20260810.271.1")},
    )
    _v2b, _w2, probes2 = run_live(_run_ns(state_file=str(shared)), new_only)
    d2 = {p.name: p for p in probes2}["runner_image_drift"]
    t.eq("cross-invocation-drift-detected-via-state-file", d2.finding, DEGRADED)
    t.check(
        "cross-invocation-drift-names-the-prior-version",
        "20260720.247.2" in d2.reason,
        d2.reason,
    )

    # ── THE 2026-08-18 REPLAY ────────────────────────────────────────────────
    # indicator: none + 12/12 components operational + ONE unresolved incident
    # whose `components` is []. If this returns LOCAL, the tool is worthless.
    v_replay, p_replay = verdict_of(
        FakeTransport(
            status=REPLAY_STATUS,
            components=REPLAY_COMPONENTS,
            incidents=REPLAY_INCIDENTS,
            runs=clean_runs,
            jobs=clean_jobs,
            images=clean_images,
        )
    )
    t.eq("REPLAY-2026-08-18-unattached-incident-yields-GITHUB_DEGRADED", v_replay, GITHUB_DEGRADED)
    sp = {p.name: p for p in p_replay}["status_page"]
    t.eq("REPLAY-indicator-still-reads-none", sp.data.get("indicator"), "none")
    t.eq("REPLAY-zero-components-non-operational", sp.data.get("non_operational_components"), [])
    t.eq("REPLAY-verdict-comes-from-the-incident-alone", sp.finding, DEGRADED)
    t.check(
        "REPLAY-incident-name-impact-and-status-are-printed",
        all(x in sp.reason for x in ("Incident with Actions", "major", "investigating")),
        sp.reason,
    )
    # And the fail-closed half: if the incidents endpoint cannot be read, a green
    # indicator beside it is worth nothing.
    v_incfail, _ = verdict_of(
        FakeTransport(http_garbage=True, runs=clean_runs, jobs=clean_jobs, images=clean_images)
    )
    t.eq("unreadable-incidents-endpoint-is-UNKNOWN-not-LOCAL", v_incfail, UNKNOWN)

    # ── Second drift axis: the runner AGENT ships separately from the image ──
    agent_moved = {500: ("ubuntu-24.04", "20260810.271.1", "2.337.0")}
    agent_moved.update({500 + i: ("ubuntu-24.04", "20260810.271.1", "2.336.0") for i in (1, 2)})
    v_agent, p_agent = verdict_of(
        FakeTransport(runs=clean_runs, jobs=clean_jobs, images=agent_moved)
    )
    da = {p.name: p for p in p_agent}["runner_image_drift"]
    t.eq("agent-version-drift-alone-yields-GITHUB_DEGRADED", v_agent, GITHUB_DEGRADED)
    t.check(
        "agent-drift-names-both-agent-versions",
        "2.336.0" in da.reason and "2.337.0" in da.reason,
        da.reason,
    )
    t.check(
        "agent-drift-is-labelled-RUNNER-AGENT-not-IMAGE",
        "RUNNER AGENT" in da.reason and "IMAGE " not in da.reason,
        da.reason,
    )

    # ── git ls-remote exit 0 with ZERO refs is an unverified probe ────────────
    # Real bug, caught 2026-08-18: `--heads <url> HEAD` filters every ref out and
    # the first version of this probe called the empty result "healthy".
    v_norefs, p_norefs = verdict_of(
        FakeTransport(runs=clean_runs, jobs=clean_jobs, images=clean_images)
    )
    gt = {p.name: p for p in p_norefs}["git_transport"]
    t.check("git-probe-returns-refs-on-the-happy-path", gt.data.get("refs", 0) > 0, gt.reason)
    t.eq("git-happy-path-reaches-a-conclusion", gt.state, RAN)
    t.eq("git-happy-path-verdict-unaffected", v_norefs, LOCAL)

    # ── Token hygiene ────────────────────────────────────────────────────────
    t.check(
        "token-values-are-scrubbed",
        "ghp_" not in scrub("fatal: bad creds ghp_abcdefghijklmnop1234"),
        scrub("fatal: bad creds ghp_abcdefghijklmnop1234"),
    )

    # ── Exit-code contract ───────────────────────────────────────────────────
    t.eq("exit-codes", EXIT_BY_VERDICT, {LOCAL: 0, GITHUB_DEGRADED: 1, UNKNOWN: 2})

    return t


def emit_self_test(t: SelfTest) -> int:
    print("gh-health --self-test  (offline, fixture-driven)")
    print("-" * 78)
    for name in t.passed:
        print("  PASS  %s" % name)
    for name in t.failed:
        print("  FAIL  %s" % name)
    print("-" * 78)
    print("%d passed, %d failed" % (len(t.passed), len(t.failed)))
    return 0 if not t.failed else 2


# ── CLI ──────────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="gh-health.py",
        description="Is this GitHub's problem or mine? "
        "Verdicts: LOCAL(0) / GITHUB_DEGRADED(1) / UNKNOWN(2). "
        "An unrun probe is never evidence of health.",
        epilog=(
            "NOTES ON THE TWO SIGNALS NOBODY POLLS:\n"
            "  * A green status `indicator` is NOT evidence of health. An incident with\n"
            "    `components: []` moves neither the indicator nor any component; on\n"
            "    2026-08-18 a MAJOR open Actions incident sat beside\n"
            "    'All Systems Operational' 37ms after the page updated for it. This tool\n"
            "    always fetches incidents/unresolved.json and treats it as decisive.\n"
            "  * Runner-image version pinning DOES NOT EXIST. Per GitHub staff (community\n"
            "    discussion #173099) you cannot learn the image version ahead of time;\n"
            "    $ImageVersion is runtime-only, readable only from a job log. Layer 3 is\n"
            "    therefore a CANARY over completed runs, not a poll -- a poll is\n"
            "    structurally impossible. It diffs BOTH the image and the separately\n"
            "    shipped runner agent (Node ships with the agent, not the image)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--repo", default="", help="owner/name (required for layers 2-4)")
    ap.add_argument("--workflow", default=None, help="workflow file, e.g. ci.yml")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--verbose", action="store_true", help="print per-probe evidence")
    ap.add_argument("--timeout", type=float, default=25.0, help="seconds per network call")
    ap.add_argument("--max-runs", type=int, default=20, help="recent PR runs to examine")
    ap.add_argument("--drift-samples", type=int, default=4, help="runs to read logs from")
    ap.add_argument(
        "--invariance-threshold",
        type=int,
        default=3,
        help="distinct branches failing the same step to call it invariant",
    )
    ap.add_argument("--state-file", default=str(DEFAULT_STATE_FILE), help="drift baseline cache")
    ap.add_argument("--self-test", action="store_true", help="offline fixture battery")
    ap.add_argument(
        "--must-fail",
        metavar="DETECTOR",
        choices=DETECTORS,
        help="disable a detector and prove --self-test goes red. "
        "Choices: " + ", ".join(DETECTORS),
    )
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.must_fail:
        DISABLED.add(args.must_fail)
        with tempfile.TemporaryDirectory() as tmp:
            t = self_test(Path(tmp))
        emit_self_test(t)
        print("")
        print("TEETH CHECK: detector %r was disabled." % args.must_fail)
        if t.failed:
            print("  self-test went RED (%d failures) -- the teeth are real." % len(t.failed))
            return 0
        print("  self-test STAYED GREEN -- BROKEN TEETH. This suite does not test %r." % args.must_fail)
        return 2

    if args.self_test:
        with tempfile.TemporaryDirectory() as tmp:
            t = self_test(Path(tmp))
        return emit_self_test(t)

    tx = RealTransport(args.timeout)
    verdict, why, probes = run_live(args, tx)

    if args.json:
        print(
            json.dumps(
                {
                    "verdict": verdict,
                    "exit_code": EXIT_BY_VERDICT[verdict],
                    "reason": why,
                    "repo": args.repo or None,
                    "workflow": args.workflow,
                    "probes_total": len(probes),
                    "probes_ran": len([p for p in probes if p.state == RAN]),
                    "probes": [p.to_dict() for p in probes],
                },
                indent=2,
            )
        )
    else:
        print(render(verdict, why, probes, args))
    return EXIT_BY_VERDICT[verdict]


if __name__ == "__main__":
    sys.exit(main())

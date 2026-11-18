#!/usr/bin/env python3
"""Classify a GitHub Actions run as running, queued, stalled, or finished.

The procedure this implements is plugins/devops-cicd/knowledge/ci-run-status.md.
A queued or in-progress job is alive. A completed conclusion is the only
stopped state. This tool prints one JSON verdict and does not re-run anything.

  python3 classify_ci_run_state.py --snapshot snapshot.json
  python3 classify_ci_run_state.py --repo OWNER/REPO --run-id 123
  python3 classify_ci_run_state.py --self-test

Exit 0 means a verdict was printed. Exit 2 means the input or the transport
failed. A failed CI run is still exit 0: the verdict's phase says failed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

LOST_RX = re.compile(
    r"lost communication with the server|was not acquired by Runner",
    re.I,
)
SHUTDOWN_RX = re.compile(
    r"runner has received a shutdown signal|exit code 143",
    re.I,
)
GUARD_RX = re.compile(r"runner guard: refusing", re.I)
TEST_RX = re.compile(
    r"AssertionError|FAIL\s+\S|failed tests|Test Files\s+\d+\s+failed|not ok \d+",
    re.I,
)
AUTH_RX = re.compile(r"Authentication error|code 10000|Invalid API token", re.I)
SHARD_RX = re.compile(r"\([^()]+\)\s*$")

ALIVE_STATUSES = {"queued", "in_progress", "waiting", "pending", "requested"}
OK = {"success", "skipped", "neutral"}
RERUN_ATTEMPT = {
    "runner_lost": 2,
    "runner_shutdown": 2,
    "timeout": 2,
    "flake_shard": 1,
    "startup_failure": 1,
}

DEFAULTS = {
    "ghost_minutes": 10,
    "queue_alarm_minutes": 15,
    "stall_factor": 2.0,
    "sleep_grace_minutes": 10,
    "default_job_minutes": 30,
    "gate_jobs": ["ci-gate", "test"],
}


def parse_time(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def minutes_between(start: datetime | None, end: datetime | None) -> float | None:
    if start is None or end is None:
        return None
    return (end - start).total_seconds() / 60.0


def as_messages(raw: Any) -> list[str] | None:
    """None means the annotations could not be read. [] means none were present."""
    if raw is None:
        return None
    out: list[str] = []
    if isinstance(raw, str):
        return [raw]
    if not isinstance(raw, list):
        return None
    for item in raw:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            out.append(str(item.get("message") or ""))
    return out


def blob(job: dict[str, Any]) -> str:
    parts = as_messages(job.get("annotations")) or []
    tail = job.get("log_tail")
    if isinstance(tail, str):
        parts.append(tail)
    return "\n".join(parts)


def job_labels(job: dict[str, Any]) -> list[str]:
    labels = job.get("labels") or []
    return [str(item) for item in labels]


def runner_matches(runner: dict[str, Any], labels: list[str]) -> bool:
    have = {str(item) for item in (runner.get("labels") or [])}
    return all(label in have for label in labels)


def matching_runners(
    job: dict[str, Any], runners: list[dict[str, Any]] | None
) -> list[dict[str, Any]] | None:
    if runners is None:
        return None
    labels = job_labels(job)
    return [runner for runner in runners if runner_matches(runner, labels)]


def expected_minutes(name: str, snapshot: dict[str, Any]) -> float:
    table = snapshot.get("expected_minutes") or {}
    if name in table:
        return float(table[name])
    base = name.split(" (", 1)[0]
    if base in table:
        return float(table[base])
    return float(snapshot.get("default_job_minutes") or DEFAULTS["default_job_minutes"])


def limit(snapshot: dict[str, Any], key: str) -> Any:
    if key in snapshot and snapshot[key] is not None:
        return snapshot[key]
    return DEFAULTS[key]


def current_step(job: dict[str, Any]) -> dict[str, Any] | None:
    steps = job.get("steps") or []
    for step in steps:
        if step.get("status") == "in_progress":
            return step
    return None


def is_shard(name: str) -> bool:
    return bool(SHARD_RX.search(name or ""))


def verdict(
    *,
    phase: str,
    alive: bool | None,
    failure_class: str | None,
    action: str,
    why: str,
    rerun_allowed: bool = False,
    guardrails: list[str] | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "phase": phase,
        "alive": alive,
        "failure_class": failure_class,
        "action": action,
        "rerun_allowed": rerun_allowed,
        "why": why,
        "guardrails": guardrails
        or [
            "A re-run uses the original commit and ref, not the branch tip.",
            "Do not re-run a ghost, a superseded cancel, a guard rejection, or a mixed failure.",
            "Do not re-run after the runner guard changed; push a new commit so the new guard is what runs.",
            "Stop after the attempt cap. A re-run is not a reset of a failure counter.",
        ],
        "evidence": evidence or {},
    }


def classify_job(job: dict[str, Any]) -> str:
    conclusion = str(job.get("conclusion") or "")
    steps = job.get("steps")
    text = blob(job)
    annotations = as_messages(job.get("annotations"))
    if GUARD_RX.search(text):
        return "guard_rejection"
    if isinstance(steps, list) and len(steps) == 0 and conclusion in {"cancelled", "failure"}:
        return "runner_lost"
    if LOST_RX.search(text):
        return "runner_lost"
    if SHUTDOWN_RX.search(text):
        return "runner_shutdown"
    if AUTH_RX.search(text):
        return "auth"
    if conclusion == "timed_out":
        return "timeout"
    if conclusion in {"cancelled", "timed_out"} and is_shard(str(job.get("name") or "")):
        return "flake_shard"
    if TEST_RX.search(text):
        return "test"
    if conclusion == "failure":
        if annotations is None and not isinstance(job.get("log_tail"), str):
            return "unproven"
        return "test" if text else "unproven"
    if conclusion == "cancelled":
        return "cancelled"
    return "unknown_failure"


def failed_jobs(jobs: list[dict[str, Any]], gate_jobs: list[str]) -> list[dict[str, Any]]:
    return [
        job
        for job in jobs
        if job.get("conclusion") not in OK
        and job.get("conclusion") not in (None, "")
        and job.get("name") not in gate_jobs
    ]


def rerun_ok(failure_class: str, attempt: int, guard_changed: bool) -> bool:
    if guard_changed:
        return False
    cap = RERUN_ATTEMPT.get(failure_class)
    if cap is None:
        return False
    return attempt <= cap


def action_for(failure_class: str, attempt: int, guard_changed: bool) -> tuple[str, bool]:
    if failure_class == "guard_rejection":
        return "do_not_rerun", False
    if failure_class == "test":
        return "fix_test", False
    if failure_class in {"unproven", "unknown_failure", "mixed", "cancelled", "auth"}:
        return "escalate", False
    if guard_changed and failure_class in RERUN_ATTEMPT:
        return "update_branch", False
    if rerun_ok(failure_class, attempt, guard_changed):
        return "rerun_failed", True
    if failure_class in RERUN_ATTEMPT:
        return "escalate", False
    return "escalate", False


def classify(snapshot: dict[str, Any]) -> dict[str, Any]:
    if snapshot.get("transport_error"):
        return verdict(
            phase="unknown",
            alive=None,
            failure_class="transport",
            action="retry_later",
            why=str(snapshot["transport_error"]),
            evidence={"transport_error": snapshot["transport_error"]},
        )
    if snapshot.get("jobs_truncated"):
        return verdict(
            phase="unknown",
            alive=None,
            failure_class="transport",
            action="retry_later",
            why=(
                "The jobs list was a single page and total_count was higher. "
                "Read the rest before deciding."
            ),
            evidence={"jobs_truncated": True},
        )

    run = snapshot.get("run") or {}
    jobs = list(snapshot.get("jobs") or [])
    status = str(run.get("status") or "")
    conclusion = run.get("conclusion")
    now = parse_time(snapshot.get("now")) or datetime.now(timezone.utc)
    created = parse_time(run.get("created_at"))
    updated = parse_time(run.get("updated_at"))
    age = minutes_between(created, now)
    attempt = int(run.get("run_attempt") or 1)
    guard_changed = bool(snapshot.get("guard_changed"))
    expected_head = snapshot.get("expected_head_sha")
    head = run.get("head_sha")
    head_mismatch = bool(expected_head and head and expected_head != head)
    runners = snapshot.get("runners", None)
    if runners is not None and not isinstance(runners, list):
        runners = None
    gate_jobs = list(snapshot.get("gate_jobs") or DEFAULTS["gate_jobs"])
    evidence: dict[str, Any] = {
        "status": status,
        "conclusion": conclusion,
        "run_attempt": attempt,
        "job_count": len(jobs),
        "age_minutes": None if age is None else round(age, 1),
    }

    if head_mismatch and status in ALIVE_STATUSES:
        evidence["head_sha"] = head
        evidence["expected_head_sha"] = expected_head
        return verdict(
            phase="stale",
            alive=True,
            failure_class=None,
            action="watch_head",
            why=(
                "This run is still going, but it is not the current head. "
                "Watch the run for the current SHA."
            ),
            evidence=evidence,
        )

    if status in ALIVE_STATUSES and not jobs:
        return _empty_jobs(snapshot, status, created, updated, age, evidence)

    if status in {"pending", "waiting", "requested"} or (
        status == "queued" and jobs and all(job.get("status") != "in_progress" for job in jobs)
    ):
        return _queued_or_waiting(snapshot, jobs, runners, now, status, age, evidence)

    if status == "in_progress" or any(job.get("status") == "in_progress" for job in jobs):
        return _in_progress(snapshot, jobs, runners, now, evidence)

    if status == "completed" or conclusion:
        return _completed(
            snapshot,
            jobs,
            conclusion,
            attempt,
            guard_changed,
            head_mismatch,
            head,
            expected_head,
            evidence,
            gate_jobs,
        )

    return verdict(
        phase="unknown",
        alive=None,
        failure_class=None,
        action="retry_later",
        why=f"Unrecognized run status {status!r}.",
        evidence=evidence,
    )


def _empty_jobs(snapshot, status, created, updated, age, evidence):
    ghost_after = float(limit(snapshot, "ghost_minutes"))
    unchanged = updated is None or created is None or updated == created
    evidence["updated_equals_created"] = unchanged
    if age is not None and age >= ghost_after and unchanged and status in {"queued", "requested"}:
        return verdict(
            phase="ghost",
            alive=False,
            failure_class="infra_ghost",
            action="wait_for_github",
            why=(
                "The run says queued and has no jobs, and its updated time has not moved. "
                "Cancel often returns 409 because the run was never queued. That is a "
                "GitHub-side orphan, not a stopped test and not a dead runner."
            ),
            evidence=evidence,
        )
    return verdict(
        phase="queued",
        alive=True,
        failure_class=None,
        action="wait",
        why=(
            "No jobs are listed yet and the run is younger than the ghost threshold. "
            "It may still be provisioning."
        ),
        evidence=evidence,
    )


def _queued_or_waiting(snapshot, jobs, runners, now, status, age, evidence):
    alarm = float(limit(snapshot, "queue_alarm_minutes"))
    waited = age
    queued = [
        job
        for job in jobs
        if job.get("status") in {"queued", "pending", "waiting", "requested"}
    ]
    if queued:
        ages = []
        for job in queued:
            job_age = minutes_between(
                parse_time(job.get("created_at") or job.get("started_at")), now
            )
            if job_age is not None:
                ages.append(job_age)
        if ages:
            waited = max(ages)
    evidence["queue_minutes"] = None if waited is None else round(waited, 1)
    if status == "pending":
        return verdict(
            phase="waiting",
            alive=True,
            failure_class="concurrency_pending",
            action="wait",
            why="pending means the concurrency group is full. The run is waiting, not stopped.",
            evidence=evidence,
        )
    if status == "waiting":
        return verdict(
            phase="waiting",
            alive=True,
            failure_class="deployment_protection",
            action="wait",
            why=(
                "waiting means a deployment protection rule has not been satisfied. "
                "The run is not stopped."
            ),
            evidence=evidence,
        )
    if status == "requested":
        return verdict(
            phase="queued",
            alive=True,
            failure_class=None,
            action="wait",
            why="requested means the run exists and has not been queued yet. It is not a failure.",
            evidence=evidence,
        )

    offline = None
    unmatched = False
    if runners is not None and queued:
        matched_any = False
        any_online = False
        for job in queued:
            matched = matching_runners(job, runners)
            if not matched:
                unmatched = True
                continue
            matched_any = True
            if any(item.get("status") == "online" for item in matched):
                any_online = True
        if not matched_any:
            unmatched = True
        offline = matched_any and not any_online
    evidence["no_matching_runner"] = unmatched
    evidence["matching_runners_offline"] = offline
    old = waited is not None and waited >= alarm
    if unmatched and old:
        return verdict(
            phase="queued",
            alive=True,
            failure_class="queue_no_match",
            action="relabel",
            why=(
                "Jobs are queued and no runner carries every requested label. "
                "The run has not stopped."
            ),
            evidence=evidence,
        )
    if offline and old:
        return verdict(
            phase="queued",
            alive=True,
            failure_class="box_offline",
            action="restart_runner",
            why=(
                "Jobs are queued and every matching runner is offline past the queue alarm. "
                "The run is still alive."
            ),
            evidence=evidence,
        )
    return verdict(
        phase="queued",
        alive=True,
        failure_class=None,
        action="wait",
        why="Jobs are queued. A queue is not a stopped or failed run.",
        evidence=evidence,
    )


def _in_progress(snapshot, jobs, runners, now, evidence):
    grace = float(limit(snapshot, "sleep_grace_minutes"))
    factor = float(limit(snapshot, "stall_factor"))
    active = [job for job in jobs if job.get("status") == "in_progress"]
    for job in jobs:
        outputs = job.get("outputs") or {}
        state = outputs.get("state")
        if state and state not in {"success", "failure"} and job.get("conclusion") == "success":
            evidence["gate_output_state"] = state
            evidence["gate_job"] = job.get("name")
    stalled = None
    for job in active:
        step = current_step(job)
        started = parse_time((step or {}).get("started_at") or job.get("started_at"))
        elapsed = minutes_between(started, now)
        budget = expected_minutes(str(job.get("name") or ""), snapshot)
        if elapsed is not None and elapsed > budget * factor:
            stalled = (job, elapsed, budget)
            break
    if stalled:
        job, elapsed, budget = stalled
        evidence["stalled_job"] = job.get("name")
        evidence["elapsed_minutes"] = round(elapsed, 1)
        evidence["budget_minutes"] = budget
        return verdict(
            phase="stalled",
            alive=False,
            failure_class="hang",
            action="escalate",
            why=(
                f"{job.get('name')} has been on one step for {elapsed:.0f} minutes, "
                f"past {factor:g} times its {budget:g} minute baseline. "
                "That is a hang, not a queue."
            ),
            evidence=evidence,
        )
    if runners is not None and active:
        online = False
        saw_match = False
        for job in active:
            matched = matching_runners(job, runners)
            if not matched:
                continue
            saw_match = True
            if any(item.get("status") == "online" for item in matched):
                online = True
        if saw_match and not online:
            ages = [
                minutes_between(parse_time(job.get("started_at")), now) or 0 for job in active
            ]
            elapsed = max(ages) if ages else 0
            evidence["matching_runners_offline"] = True
            evidence["elapsed_minutes"] = round(elapsed, 1)
            if elapsed <= grace:
                return verdict(
                    phase="running",
                    alive=True,
                    failure_class="box_offline",
                    action="wait",
                    why=(
                        "Matching runners are offline but the job is inside the sleep grace. "
                        "A box that sleeps and reconnects looks like this before GitHub marks "
                        "the job failed."
                    ),
                    evidence=evidence,
                )
            return verdict(
                phase="stalled",
                alive=False,
                failure_class="box_offline",
                action="restart_runner",
                why=(
                    "Matching runners are offline past the sleep grace while a job "
                    "is still in progress."
                ),
                evidence=evidence,
            )
    why = (
        "A job is in progress. Read step status for liveness; "
        "log text for the whole run is not available yet."
    )
    if evidence.get("gate_output_state"):
        why = (
            f"{evidence.get('gate_job')} concluded success with output state "
            f"{evidence['gate_output_state']}. The job exiting 0 is not a pass of the suite."
        )
    return verdict(
        phase="running",
        alive=True,
        failure_class=None,
        action="wait",
        why=why,
        evidence=evidence,
    )


def _completed(
    snapshot,
    jobs,
    conclusion,
    attempt,
    guard_changed,
    head_mismatch,
    head,
    expected_head,
    evidence,
    gate_jobs,
):
    conclusion = str(conclusion or "")
    evidence["guard_changed"] = guard_changed
    if head_mismatch:
        evidence["head_sha"] = head
        evidence["expected_head_sha"] = expected_head
        return verdict(
            phase="stale",
            alive=False,
            failure_class=None,
            action="watch_head",
            why=(
                "This completed run is for a different SHA than the current head. "
                "It is not the verdict for the head."
            ),
            evidence=evidence,
        )
    required = list(snapshot.get("required_jobs") or [])
    if conclusion == "success":
        skipped = [
            job.get("name")
            for job in jobs
            if job.get("name") in required and job.get("conclusion") == "skipped"
        ]
        if skipped:
            evidence["skipped_required"] = skipped
            return verdict(
                phase="false_green",
                alive=False,
                failure_class="skipped_required",
                action="do_not_rerun",
                why=(
                    "The run succeeded and a required job was skipped. GitHub treats a "
                    "skipped job as success for merge, so this can look green without "
                    "the suite having run."
                ),
                evidence=evidence,
            )
        return verdict(
            phase="succeeded",
            alive=False,
            failure_class=None,
            action="none",
            why="The run completed with success and no required job was skipped.",
            evidence=evidence,
        )
    if conclusion == "cancelled" and snapshot.get("successor_run_id"):
        evidence["successor_run_id"] = snapshot["successor_run_id"]
        return verdict(
            phase="failed",
            alive=False,
            failure_class="cancelled_superseded",
            action="watch_successor",
            why=(
                "This run was cancelled because a newer run replaced it. "
                "Do not re-run it. Watch the successor."
            ),
            evidence=evidence,
        )
    if conclusion == "startup_failure":
        action, allowed = action_for("startup_failure", attempt, guard_changed)
        return verdict(
            phase="failed",
            alive=False,
            failure_class="startup_failure",
            action=action,
            rerun_allowed=allowed,
            why=(
                "startup_failure means the check suite failed before jobs ran. "
                "One re-run is the corrective action."
            ),
            evidence=evidence,
        )
    if conclusion == "skipped":
        return verdict(
            phase="false_green",
            alive=False,
            failure_class="skipped_required",
            action="do_not_rerun",
            why=(
                "The run itself was skipped. A path filter that skips a required "
                "workflow leaves the check pending instead. A skipped run is not "
                "a pass of the suite."
            ),
            evidence=evidence,
        )

    judged = failed_jobs(jobs, gate_jobs)
    if not judged and conclusion in {"failure", "timed_out", "cancelled"}:
        judged = [
            job
            for job in jobs
            if job.get("conclusion") not in OK and job.get("conclusion") not in (None, "")
        ]
    classes = {classify_job(job) for job in judged}
    shard_only = bool(judged) and all(
        job.get("conclusion") in {"cancelled", "timed_out"} and is_shard(str(job.get("name") or ""))
        for job in judged
    )
    if shard_only:
        failure_class = "flake_shard"
    elif len(classes) == 1:
        failure_class = classes.pop()
    elif not classes:
        failure_class = {
            "timed_out": "timeout",
            "cancelled": "cancelled",
            "failure": "unproven",
        }.get(conclusion, "unknown_failure")
    else:
        failure_class = "mixed"
    action, allowed = action_for(failure_class, attempt, guard_changed)
    if conclusion == "timed_out" and failure_class in {"test", "unproven", "unknown_failure"}:
        failure_class = "timeout"
        action, allowed = action_for(failure_class, attempt, guard_changed)
    evidence["job_classes"] = sorted({classify_job(job) for job in judged}) if judged else []
    why = f"Run conclusion {conclusion or 'completed'} classified as {failure_class}."
    if failure_class == "mixed":
        why = "Failed jobs are not all the same kind. Re-running would hide a real failure."
    if guard_changed and action == "update_branch":
        why = (
            "The runner guard changed after this SHA. A re-run would execute the old "
            "guard. Push a new commit."
        )
    return verdict(
        phase="failed",
        alive=False,
        failure_class=failure_class,
        action=action,
        rerun_allowed=allowed,
        why=why,
        evidence=evidence,
    )


def _gh_json(args: list[str]) -> tuple[Any | None, str | None]:
    try:
        proc = subprocess.run(
            ["gh", "api", *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None, "gh is not on PATH"
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return None, detail[0] if detail else f"gh api exited {proc.returncode}"
    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError:
        return None, "gh api did not return JSON"


def fetch_snapshot(repo: str, run_id: str, with_runners: bool) -> dict[str, Any]:
    run, err = _gh_json([f"repos/{repo}/actions/runs/{run_id}"])
    if err or not isinstance(run, dict):
        return {"transport_error": err or "empty run"}
    jobs_doc, err = _gh_json([f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"])
    if err or not isinstance(jobs_doc, dict):
        return {"transport_error": err or "empty jobs"}
    jobs = list(jobs_doc.get("jobs") or [])
    total = int(jobs_doc.get("total_count") or len(jobs))
    snapshot: dict[str, Any] = {
        "run": {
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "created_at": run.get("created_at"),
            "updated_at": run.get("updated_at"),
            "run_started_at": run.get("run_started_at"),
            "run_attempt": run.get("run_attempt"),
            "head_sha": run.get("head_sha"),
            "name": run.get("name"),
            "html_url": run.get("html_url"),
        },
        "jobs": jobs,
        "now": datetime.now(timezone.utc).isoformat(),
    }
    if total > len(jobs):
        snapshot["jobs_truncated"] = True
        return snapshot
    for job in jobs:
        if job.get("conclusion") in OK or job.get("conclusion") in (None, ""):
            job["annotations"] = []
            continue
        ann, ann_err = _gh_json(
            [f"repos/{repo}/check-runs/{job.get('id')}/annotations?per_page=100"]
        )
        job["annotations"] = ann if ann_err is None and isinstance(ann, list) else None
    if with_runners:
        runners, runners_err = _gh_json([f"repos/{repo}/actions/runners?per_page=100"])
        if runners_err or not isinstance(runners, dict):
            snapshot["runners_error"] = runners_err or "empty runners"
        else:
            listed = list(runners.get("runners") or [])
            if int(runners.get("total_count") or len(listed)) > len(listed):
                snapshot["runners_error"] = "runner list was truncated"
            else:
                snapshot["runners"] = listed
    return snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", help="Path to a JSON snapshot. '-' reads stdin.")
    parser.add_argument("--repo", help="OWNER/REPO, with --run-id, to read a live run via gh.")
    parser.add_argument("--run-id", help="Workflow run id to read via gh.")
    parser.add_argument(
        "--with-runners",
        action="store_true",
        help="Also list self-hosted runners. Needs a token that can read them.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the unit tests and exit.")
    args = parser.parse_args(argv)
    if args.self_test:
        import unittest
        from pathlib import Path

        tests = Path(__file__).with_name("test_classify_ci_run_state.py")
        suite = unittest.defaultTestLoader.discover(str(tests.parent), pattern=tests.name)
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        return 0 if result.wasSuccessful() else 1
    if args.repo or args.run_id:
        if not (args.repo and args.run_id):
            print("Both --repo and --run-id are required.", file=sys.stderr)
            return 2
        snapshot = fetch_snapshot(args.repo, args.run_id, args.with_runners)
    elif args.snapshot:
        if args.snapshot == "-":
            raw = sys.stdin.read()
        else:
            with open(args.snapshot, encoding="utf-8") as handle:
                raw = handle.read()
        try:
            snapshot = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"snapshot is not JSON: {exc}", file=sys.stderr)
            return 2
    else:
        parser.error("pass --snapshot or --repo and --run-id")
    if not isinstance(snapshot, dict):
        print("snapshot must be a JSON object", file=sys.stderr)
        return 2
    print(json.dumps(classify(snapshot), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

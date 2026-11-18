"""Fixture tests for classify_ci_run_state. No network."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_PATH = Path(__file__).with_name("classify_ci_run_state.py")
_SPEC = importlib.util.spec_from_file_location("classify_ci_run_state", _PATH)
assert _SPEC and _SPEC.loader
clf = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(clf)

NOW = "2026-11-16T02:00:00Z"
CREATED = "2026-11-16T01:00:00Z"


def snap(**kwargs):
    base = {"now": NOW, "run": {"status": "queued", "created_at": CREATED, "updated_at": CREATED}}
    base.update(kwargs)
    return base


class ClassifyTests(unittest.TestCase):
    def test_in_progress_step_is_alive(self):
        out = clf.classify(
            snap(
                run={
                    "status": "in_progress",
                    "created_at": CREATED,
                    "updated_at": NOW,
                    "run_attempt": 1,
                },
                jobs=[
                    {
                        "name": "build",
                        "status": "in_progress",
                        "started_at": "2026-11-16T01:40:00Z",
                        "steps": [
                            {
                                "name": "test",
                                "status": "in_progress",
                                "started_at": "2026-11-16T01:50:00Z",
                            }
                        ],
                    }
                ],
                expected_minutes={"build": 20},
            )
        )
        self.assertEqual(out["phase"], "running")
        self.assertTrue(out["alive"])
        self.assertEqual(out["action"], "wait")
        self.assertFalse(out["rerun_allowed"])

    def test_queued_with_idle_runner_is_not_stopped(self):
        out = clf.classify(
            snap(
                jobs=[
                    {
                        "name": "static",
                        "status": "queued",
                        "created_at": "2026-11-16T01:50:00Z",
                        "labels": ["self-hosted", "box", "raven-web"],
                    }
                ],
                runners=[
                    {
                        "name": "box-raven-web-9",
                        "status": "online",
                        "busy": False,
                        "labels": ["self-hosted", "box", "raven-web", "Linux"],
                    }
                ],
            )
        )
        self.assertEqual(out["phase"], "queued")
        self.assertTrue(out["alive"])
        self.assertEqual(out["action"], "wait")
        self.assertIsNone(out["failure_class"])

    def test_queue_with_no_matching_label_stays_alive(self):
        out = clf.classify(
            snap(
                jobs=[
                    {
                        "name": "static",
                        "status": "queued",
                        "created_at": "2026-11-16T01:00:00Z",
                        "labels": ["self-hosted", "box", "raven-web"],
                    }
                ],
                runners=[
                    {
                        "name": "laptop",
                        "status": "online",
                        "busy": False,
                        "labels": ["self-hosted", "laptop"],
                    }
                ],
            )
        )
        self.assertEqual(out["phase"], "queued")
        self.assertTrue(out["alive"])
        self.assertEqual(out["failure_class"], "queue_no_match")
        self.assertEqual(out["action"], "relabel")

    def test_ghost_when_queued_with_zero_jobs(self):
        out = clf.classify(
            snap(
                run={
                    "status": "queued",
                    "created_at": "2026-11-11T20:25:31Z",
                    "updated_at": "2026-11-11T20:25:31Z",
                    "run_attempt": 1,
                },
                jobs=[],
                now="2026-11-16T01:30:00Z",
            )
        )
        self.assertEqual(out["phase"], "ghost")
        self.assertFalse(out["alive"])
        self.assertEqual(out["failure_class"], "infra_ghost")
        self.assertEqual(out["action"], "wait_for_github")
        self.assertFalse(out["rerun_allowed"])

    def test_young_empty_job_list_is_still_provisioning(self):
        out = clf.classify(
            snap(
                run={
                    "status": "queued",
                    "created_at": "2026-11-16T01:58:00Z",
                    "updated_at": "2026-11-16T01:58:00Z",
                },
                jobs=[],
            )
        )
        self.assertEqual(out["phase"], "queued")
        self.assertTrue(out["alive"])
        self.assertEqual(out["action"], "wait")

    def test_pending_is_concurrency_not_failure(self):
        out = clf.classify(
            snap(
                run={"status": "pending", "created_at": CREATED, "updated_at": NOW},
                jobs=[{"name": "build", "status": "pending", "created_at": CREATED}],
            )
        )
        self.assertEqual(out["phase"], "waiting")
        self.assertTrue(out["alive"])
        self.assertEqual(out["failure_class"], "concurrency_pending")

    def test_lost_communication_rerun_once(self):
        out = clf.classify(
            snap(
                run={
                    "status": "completed",
                    "conclusion": "failure",
                    "run_attempt": 1,
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[
                    {
                        "name": "build",
                        "status": "completed",
                        "conclusion": "failure",
                        "annotations": [
                            "The self-hosted runner lost communication with the server."
                        ],
                    }
                ],
            )
        )
        self.assertEqual(out["failure_class"], "runner_lost")
        self.assertEqual(out["action"], "rerun_failed")
        self.assertTrue(out["rerun_allowed"])

    def test_lost_communication_stops_after_attempt_cap(self):
        out = clf.classify(
            snap(
                run={
                    "status": "completed",
                    "conclusion": "failure",
                    "run_attempt": 3,
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[
                    {
                        "name": "build",
                        "conclusion": "failure",
                        "status": "completed",
                        "annotations": ["lost communication with the server"],
                    }
                ],
            )
        )
        self.assertEqual(out["action"], "escalate")
        self.assertFalse(out["rerun_allowed"])

    def test_guard_change_blocks_rerun(self):
        out = clf.classify(
            snap(
                guard_changed=True,
                run={
                    "status": "completed",
                    "conclusion": "failure",
                    "run_attempt": 1,
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[
                    {
                        "name": "build",
                        "conclusion": "failure",
                        "status": "completed",
                        "annotations": ["lost communication with the server"],
                    }
                ],
            )
        )
        self.assertEqual(out["action"], "update_branch")
        self.assertFalse(out["rerun_allowed"])

    def test_guard_rejection_is_not_rerun(self):
        out = clf.classify(
            snap(
                run={
                    "status": "completed",
                    "conclusion": "failure",
                    "run_attempt": 1,
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[
                    {
                        "name": "build",
                        "conclusion": "failure",
                        "status": "completed",
                        "log_tail": "runner guard: refusing to run on 'mac-mini'",
                    }
                ],
            )
        )
        self.assertEqual(out["failure_class"], "guard_rejection")
        self.assertEqual(out["action"], "do_not_rerun")

    def test_test_failure_is_a_fix_not_a_rerun(self):
        out = clf.classify(
            snap(
                run={
                    "status": "completed",
                    "conclusion": "failure",
                    "run_attempt": 1,
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[
                    {
                        "name": "static",
                        "conclusion": "failure",
                        "status": "completed",
                        "annotations": ["AssertionError: expected 1"],
                    }
                ],
            )
        )
        self.assertEqual(out["failure_class"], "test")
        self.assertEqual(out["action"], "fix_test")
        self.assertFalse(out["rerun_allowed"])

    def test_superseded_cancel_watches_successor(self):
        out = clf.classify(
            snap(
                successor_run_id=99,
                run={
                    "status": "completed",
                    "conclusion": "cancelled",
                    "run_attempt": 1,
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[{"name": "build", "conclusion": "cancelled", "status": "completed"}],
            )
        )
        self.assertEqual(out["failure_class"], "cancelled_superseded")
        self.assertEqual(out["action"], "watch_successor")
        self.assertFalse(out["rerun_allowed"])

    def test_skipped_required_job_is_false_green(self):
        out = clf.classify(
            snap(
                required_jobs=["build"],
                run={
                    "status": "completed",
                    "conclusion": "success",
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[
                    {"name": "changes", "conclusion": "success", "status": "completed"},
                    {"name": "build", "conclusion": "skipped", "status": "completed"},
                ],
            )
        )
        self.assertEqual(out["phase"], "false_green")
        self.assertEqual(out["failure_class"], "skipped_required")

    def test_completed_success_for_other_sha_is_stale(self):
        out = clf.classify(
            snap(
                expected_head_sha="bbbb",
                run={
                    "status": "completed",
                    "conclusion": "success",
                    "head_sha": "aaaa",
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[{"name": "build", "conclusion": "success", "status": "completed"}],
            )
        )
        self.assertEqual(out["phase"], "stale")
        self.assertEqual(out["action"], "watch_head")

    def test_hang_when_step_exceeds_baseline(self):
        out = clf.classify(
            snap(
                run={"status": "in_progress", "created_at": CREATED, "updated_at": NOW},
                jobs=[
                    {
                        "name": "build",
                        "status": "in_progress",
                        "started_at": "2026-11-16T01:00:00Z",
                        "steps": [
                            {
                                "name": "suite",
                                "status": "in_progress",
                                "started_at": "2026-11-16T01:00:00Z",
                            }
                        ],
                    }
                ],
                expected_minutes={"build": 20},
            )
        )
        self.assertEqual(out["phase"], "stalled")
        self.assertEqual(out["failure_class"], "hang")
        self.assertEqual(out["action"], "escalate")

    def test_offline_runners_inside_grace_still_running(self):
        out = clf.classify(
            snap(
                run={"status": "in_progress", "created_at": CREATED, "updated_at": NOW},
                jobs=[
                    {
                        "name": "build",
                        "status": "in_progress",
                        "started_at": "2026-11-16T01:55:00Z",
                        "labels": ["self-hosted", "box"],
                        "steps": [
                            {
                                "name": "suite",
                                "status": "in_progress",
                                "started_at": "2026-11-16T01:55:00Z",
                            }
                        ],
                    }
                ],
                runners=[{"name": "box-1", "status": "offline", "busy": False, "labels": ["self-hosted", "box"]}],
                expected_minutes={"build": 60},
            )
        )
        self.assertEqual(out["phase"], "running")
        self.assertTrue(out["alive"])
        self.assertEqual(out["failure_class"], "box_offline")
        self.assertEqual(out["action"], "wait")

    def test_mixed_failures_are_not_rerun(self):
        out = clf.classify(
            snap(
                run={
                    "status": "completed",
                    "conclusion": "failure",
                    "run_attempt": 1,
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[
                    {
                        "name": "build",
                        "conclusion": "failure",
                        "status": "completed",
                        "annotations": ["lost communication with the server"],
                    },
                    {
                        "name": "static",
                        "conclusion": "failure",
                        "status": "completed",
                        "annotations": ["AssertionError: nope"],
                    },
                ],
            )
        )
        self.assertEqual(out["failure_class"], "mixed")
        self.assertEqual(out["action"], "escalate")
        self.assertFalse(out["rerun_allowed"])

    def test_shard_timeout_reruns_on_attempt_one_only(self):
        out = clf.classify(
            snap(
                run={
                    "status": "completed",
                    "conclusion": "failure",
                    "run_attempt": 1,
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[
                    {
                        "name": "test-shard (2)",
                        "conclusion": "timed_out",
                        "status": "completed",
                        "annotations": [],
                    },
                    {"name": "ci-gate", "conclusion": "failure", "status": "completed", "annotations": []},
                ],
            )
        )
        self.assertEqual(out["failure_class"], "flake_shard")
        self.assertTrue(out["rerun_allowed"])
        again = clf.classify(
            snap(
                run={
                    "status": "completed",
                    "conclusion": "failure",
                    "run_attempt": 2,
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[
                    {
                        "name": "test-shard (2)",
                        "conclusion": "cancelled",
                        "status": "completed",
                        "annotations": [],
                    }
                ],
            )
        )
        self.assertFalse(again["rerun_allowed"])

    def test_unreadable_annotations_do_not_authorize_rerun(self):
        out = clf.classify(
            snap(
                run={
                    "status": "completed",
                    "conclusion": "failure",
                    "run_attempt": 1,
                    "created_at": CREATED,
                    "updated_at": NOW,
                },
                jobs=[
                    {
                        "name": "build",
                        "conclusion": "failure",
                        "status": "completed",
                        "steps": [{"name": "suite", "status": "completed", "conclusion": "failure"}],
                        "annotations": None,
                    }
                ],
            )
        )
        self.assertEqual(out["failure_class"], "unproven")
        self.assertFalse(out["rerun_allowed"])

    def test_gate_output_success_is_not_a_suite_pass(self):
        out = clf.classify(
            snap(
                run={"status": "in_progress", "created_at": CREATED, "updated_at": NOW},
                jobs=[
                    {
                        "name": "cursor-gate",
                        "status": "completed",
                        "conclusion": "success",
                        "outputs": {"state": "missing"},
                    },
                    {
                        "name": "build",
                        "status": "in_progress",
                        "started_at": "2026-11-16T01:40:00Z",
                        "steps": [
                            {
                                "name": "suite",
                                "status": "in_progress",
                                "started_at": "2026-11-16T01:50:00Z",
                            }
                        ],
                    },
                ],
                expected_minutes={"build": 20},
            )
        )
        self.assertEqual(out["phase"], "running")
        self.assertIn("missing", out["why"])

    def test_transport_error_is_not_a_failed_run(self):
        out = clf.classify({"transport_error": "HTTP 403 rate limit"})
        self.assertEqual(out["phase"], "unknown")
        self.assertEqual(out["failure_class"], "transport")
        self.assertEqual(out["action"], "retry_later")
        self.assertIsNone(out["alive"])

    def test_truncated_jobs_page_is_not_classified(self):
        out = clf.classify(snap(jobs_truncated=True, jobs=[]))
        self.assertEqual(out["phase"], "unknown")
        self.assertEqual(out["action"], "retry_later")


if __name__ == "__main__":
    unittest.main()

"""Background job scheduler.

Runs periodic jobs (reminder emails, report generation) from a worker thread
pool / asyncio event loop, so multiple jobs' start_job/finish_job calls can
land concurrently from different threads or tasks at the same time.
"""
import time

_job_status = {}


def start_job(job_name: str) -> None:
    """Mark a job as running. Called from worker threads."""
    _job_status[job_name] = {"running": True, "started_at": time.time()}


def finish_job(job_name: str, ok: bool) -> None:
    """Mark a job as finished. Called from worker threads, concurrently with
    other threads calling start_job/finish_job for *different* jobs.
    """
    # Shared dict is read and written here with no lock, so two worker
    # threads finishing different jobs at the same moment can interleave
    # this read-modify-write and clobber each other's status update.
    status = _job_status.get(job_name, {})
    status["running"] = False
    status["ok"] = ok
    _job_status[job_name] = status


def is_running(job_name: str) -> bool:
    """Check whether a job is currently marked running."""
    return _job_status.get(job_name, {}).get("running", False)

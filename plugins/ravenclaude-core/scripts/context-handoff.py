#!/usr/bin/env python3
"""context-handoff.py — derive-fill a run-dir handoff skeleton.

write --task-id <id>  creates/refreshes `.ravenclaude/runs/<id>/handoff.md`
and `handoff-seed.txt` in the SAME run dir (continue-in-place).

Does not spawn a session. Does not invent a second task-id.
Does not add handoff.md to rc-artifacts STANDARD_FILES.

Python 3.9, stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

FORBIDDEN_SEED = (
    "grok -p",
    "--single",
    "--prompt-file",
    "--prompt-json",
    "/fork",
    "SessionStart",
)

_TEMPLATE_NAME = "handoff.md"


def find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / ".ravenclaude").is_dir() or (candidate / ".git").exists():
            return candidate
    return start


def plugin_root() -> Path:
    return Path(__file__).resolve().parents[1]


def template_path() -> Path:
    return plugin_root() / "skills" / "session-handoff" / "templates" / _TEMPLATE_NAME


def _normalize_handoff_host(raw: str) -> str:
    val = (raw or "").strip().lower()
    if val in ("grok", "grok-tui"):
        return "grok"
    if val in ("cli", "copilot-cli", "copilot"):
        return "cli"
    if val in ("chat", "copilot-chat"):
        return "chat"
    return val


def detect_host() -> str:
    explicit = os.environ.get("THING_HOST") or os.environ.get("RC_HOST")
    if explicit:
        return _normalize_handoff_host(explicit)
    if os.environ.get("GROK_AGENT") or os.environ.get("GROK_HOOK_EVENT"):
        return "grok"
    if os.environ.get("COPILOT_CLI") or os.environ.get("GITHUB_COPILOT_CLI"):
        return "cli"
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return "claude-code"
    return "unknown"


def _run_git(root: Path, args: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def git_facts(root: Path) -> dict:
    branch = _run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"]) or "(not a git repo)"
    status = _run_git(root, ["status", "--porcelain"])
    dirty = "yes" if status else "no"
    log = _run_git(root, ["log", "-5", "--oneline"]) or "(none)"
    commits = "\n".join(f"- `{line}`" for line in log.splitlines() if line) or "- (none)"
    return {"branch": branch, "dirty": dirty, "recent_commits": commits}


def _ensure_run_dir(root: Path, task_id: str) -> Path:
    dest = root / ".ravenclaude" / "runs" / task_id
    dest.mkdir(parents=True, exist_ok=True)
    meta = dest / "meta.json"
    if not meta.is_file():
        payload = {
            "task": task_id,
            "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "host": detect_host(),
        }
        meta.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return dest


def _run_files(dest: Path) -> str:
    names = [
        "meta.json",
        "summary.md",
        "decisions.md",
        "structured-output.json",
        "events.jsonl",
        "handoff.md",
        "handoff-seed.txt",
    ]
    lines = []
    for name in names:
        p = dest / name
        if p.is_file() and p.stat().st_size > 0:
            lines.append(f"- `{name}` ({p.stat().st_size} bytes)")
    return "\n".join(lines) or "- (none yet besides what this write creates)"


def _recent_events(dest: Path, n: int = 8) -> str:
    ev = dest / "events.jsonl"
    if not ev.is_file():
        return "- (no events.jsonl)"
    try:
        lines = ev.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "- (unreadable events.jsonl)"
    tail = lines[-n:]
    out = []
    for line in tail:
        snippet = line.strip()
        if len(snippet) > 200:
            snippet = snippet[:197] + "..."
        out.append(f"- `{snippet}`")
    return "\n".join(out) or "- (empty events.jsonl)"


def _session_id_if_hook() -> str:
    if not os.environ.get("GROK_HOOK_EVENT"):
        return "(unknown — agent process; do not read GROK_SESSION_ID from env)"
    sid = os.environ.get("GROK_SESSION_ID") or ""
    return sid.strip() or "(hook payload missing session id)"


def render_skeleton(values: dict) -> str:
    text = template_path().read_text(encoding="utf-8")

    def repl(match: re.Match) -> str:
        key = match.group(1)
        return str(values.get(key, ""))

    return re.sub(r"\{\{([a-z_]+)\}\}", repl, text)


def seed_text(
    root: Path, task_id: str, host: str | None = None, named: bool = False
) -> str:
    """Pick the successor's launch command.

    `named` says a host was ASKED FOR (a --host flag), as opposed to merely
    detected. It is the only thing separating two situations that both end up
    labelled "unknown", and conflating them is what shipped:

      (a) nothing named, nothing detected -> the grok-first fallback, because
          this tooling exists for Grok->Grok handoff and the session-handoff
          skill records that Grok's markers are unreliable in the agent process
          ("Detection is hook-only"). handoff-spawn.sh's Gate 215 pins the same
          default, and the two scripts write the seed for the SAME handoff, so
          they must not disagree about it.
      (b) a host was named and we do not know the name -> host-neutral text.
          Answering a named successor with a different agent's launch command
          is never right.
    """
    rel = f".ravenclaude/runs/{task_id}/handoff.md"
    abs_path = root / rel
    resolved = _normalize_handoff_host(host or detect_host())
    if resolved == "chat":
        return (
            f"Read {rel} and .ravenclaude/runs/{task_id}/chat-resume.md in a NEW "
            f"Copilot Chat session (Cmd+N). Do not /fork. Do not launch grok."
        )
    if resolved == "cli":
        return (
            f"copilot  # then: Continue task {task_id}. Read {rel}. "
            f"Do not /fork. Do not launch grok."
        )
    if resolved == "claude-code":
        text = (
            f"claude  # then: Continue task {task_id}. Read {rel} first. "
            f"Fresh window. Do not /fork. Do not /compact. Do not launch grok."
        )
    elif resolved == "grok" or (resolved in ("", "unknown") and not named):
        # host=grok, or case (a) above. Unchanged from the original behaviour.
        text = (
            f'grok "Continue task {task_id} in this repo. '
            f"Read {rel} first (then meta.json, decisions.md, summary.md if present). "
            f'Fresh window. Do not /fork. Do not /compact. Do not re-derive the brief from history you do not have. Execute the next steps in the brief."'
        )
    else:
        # ⛔ CASE (b): A NAMED HOST WE HAVE NO RECIPE FOR.
        #
        # This branch previously WAS the `grok "…"` seed — the fall-through
        # default — so `claude-code`, `codex` and every future NAMED host got a
        # command that launches a DIFFERENT AGENT. The session-handoff skill
        # forbids exactly that ("A Chat or CLI successor must not launch grok"),
        # and the failure is silent: the wrong command lands in
        # `handoff-seed.txt`, where the next person pastes it without a second
        # thought.
        #
        # Observed 2026-08-18: `context-handoff.py write --host claude-code`
        # wrote a `grok "…"` seed. `detect_host()` returned "claude-code"
        # correctly — it has a branch for it; only this function lacked one, and
        # its default was the most host-SPECIFIC option rather than the most
        # neutral.
        #
        # Host-neutral text is correct on every host, including ones that do not
        # exist yet. It is deliberately NOT applied to case (a), which would
        # regress the Grok->Grok flow this tooling was built for.
        text = (
            f"Read the handoff at {abs_path} and continue. "
            f"Fresh window. Do not /fork. Do not /compact. Do not launch grok."
        )
    if any(tok in text and f"Do not {tok}" not in text and f"do not {tok}" not in text.lower()
           for tok in ("grok -p", "--single", "--prompt-file", "--prompt-json", "SessionStart")):
        text = f"Read the handoff at {abs_path} and continue."
    if len(text) > 1800:
        text = f"Read the handoff at {abs_path} and continue."
    return text


def stamp_meta(dest: Path) -> None:
    meta_path = dest / "meta.json"
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}
    data["last_handoff_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["last_handoff_host"] = detect_host()
    if os.environ.get("GROK_HOOK_EVENT") and os.environ.get("GROK_SESSION_ID"):
        data["last_handoff_session_id"] = os.environ["GROK_SESSION_ID"]
    meta_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def cmd_write(
    task_id: str,
    project_root: Path | None,
    percent: str,
    threshold: str,
    named_host: bool = False,
) -> int:
    if not task_id or "/" in task_id or task_id in (".", ".."):
        print("context-handoff: invalid task-id", file=sys.stderr)
        return 2
    root = find_project_root(project_root or Path.cwd())
    dest = _ensure_run_dir(root, task_id)
    git = git_facts(root)
    values = {
        "task_id": task_id,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": detect_host(),
        "branch": git["branch"],
        "dirty": git["dirty"],
        "recent_commits": git["recent_commits"],
        "session_id": _session_id_if_hook(),
        "threshold": threshold or "(unset)",
        "percent": percent or "(unknown)",
        "run_files": _run_files(dest),
        "recent_events": _recent_events(dest),
    }
    dest.joinpath("handoff.md").write_text(render_skeleton(values), encoding="utf-8")
    host = values.get("host") or detect_host()
    dest.joinpath("handoff-seed.txt").write_text(
        seed_text(root, task_id, host, named=named_host) + "\n", encoding="utf-8"
    )
    if _normalize_handoff_host(str(host)) == "chat":
        dest.joinpath("chat-resume.md").write_text(
            f"# Copilot Chat resume — task {task_id}\n\n"
            f"Read `.ravenclaude/runs/{task_id}/handoff.md` first. "
            f"New Chat session. Do not `/fork`. Do not launch `grok`.\n",
            encoding="utf-8",
        )
    stamp_meta(dest)
    print(str(dest / "handoff.md"))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Derive-fill a session handoff skeleton")
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("--task-id", required=True)
    w.add_argument("--project-root")
    w.add_argument("--percent", default="")
    w.add_argument("--threshold", default="70")
    w.add_argument("--host", default="")
    args = ap.parse_args(argv)
    if args.cmd == "write":
        root = Path(args.project_root) if args.project_root else None
        if args.host:
            os.environ["RC_HOST"] = args.host
        # `--host` given == the caller NAMED a successor. Once RC_HOST is set,
        # detect_host() can no longer tell a named host from a detected one, so
        # the distinction has to be captured here, at the only place that sees
        # the flag.
        return cmd_write(
            args.task_id, root, args.percent, args.threshold, named_host=bool(args.host)
        )
    return 2


if __name__ == "__main__":
    sys.exit(main())

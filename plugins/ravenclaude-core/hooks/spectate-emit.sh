#!/usr/bin/env bash
# spectate-emit.sh — observe-only Spectate emitter (v0.2)
#
# Appends ONE scrubbed rc.spectate.v1 line to
#   ${CLAUDE_PROJECT_DIR}/.ravenclaude/runs/<session>/spectate-events.jsonl
# for SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop /
# SubagentStart / PreCompact. Never blocks; never writes stdout; never carries
# raw prompts, tool arguments, tool output, or secrets.
#
# Input:  hook event JSON on stdin (plus optional CLAUDE_HOOK_EVENT / $1).
# Output: exit 0 always; empty stdout.

set -uo pipefail
trap 'exit 0' EXIT

here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)" || here="."
HOOKNAME="spectate-emit.sh"
payload="$(cat 2>/dev/null || true)"
event_hint="${1:-}"

if [ -f "$here/_portable.sh" ]; then
  # shellcheck source=/dev/null
  . "$here/_portable.sh" 2>/dev/null || true
fi
if [ -f "$here/_emit-event.sh" ]; then
  # shellcheck source=/dev/null
  . "$here/_emit-event.sh" 2>/dev/null || true
fi

# Prefer python3 for closed-schema JSON construction; silent no-op without it.
if ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi

project_dir="${CLAUDE_PROJECT_DIR:-}"
[ -n "$project_dir" ] && [ -d "$project_dir" ] || exit 0

export CLAUDE_PROJECT_DIR="$project_dir"
export CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-}"
export CLAUDE_HOOK_EVENT="${CLAUDE_HOOK_EVENT:-${HOOK_EVENT:-}}"
export SPECTATE_EVENT_HINT="$event_hint"
export SPECTATE_PAYLOAD="$payload"
export THING_HOST="${THING_HOST:-}"
export CLAUDECODE="${CLAUDECODE:-}"
export CLAUDE_CODE_ENTRYPOINT="${CLAUDE_CODE_ENTRYPOINT:-}"
export CODEX_SESSION_ID="${CODEX_SESSION_ID:-}"
export CODEX_PROJECT_ROOT="${CODEX_PROJECT_ROOT:-}"
export CURSOR_AGENT="${CURSOR_AGENT:-}"
export CURSOR_TRACE_ID="${CURSOR_TRACE_ID:-}"
export GITHUB_COPILOT_CLI="${GITHUB_COPILOT_CLI:-}"
export GEMINI_CLI="${GEMINI_CLI:-}"
export GROK_BUILD="${GROK_BUILD:-}"
export XAI_GROK_BUILD="${XAI_GROK_BUILD:-}"

python3 - <<'PY' 2>/dev/null || exit 0
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlsplit

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
SESSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHELL_TARGET_RE = re.compile(r"^[A-Za-z0-9._+@/-]{1,128}$")
PATH_TARGET_RE = re.compile(r"^[A-Za-z0-9._@+-][A-Za-z0-9._@+/-]{0,255}$")
DOTDOT = re.compile(r"(^|/)\.\.(/|$)")

KIND_BY_EVENT = {
    "sessionstart": "session.start",
    "userpromptsubmit": "prompt.submit",
    "pretooluse": "tool.pre",
    "posttooluse": "tool.post",
    "stop": "turn.end",
    "subagentstart": "subagent.start",
    "precompact": "compact.pre",
    "permissionrequest": "permission.request",
}


def now_ts() -> str:
    # Millisecond UTC RFC3339 (schema pattern).
    t = time.time()
    base = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t))
    ms = int((t % 1) * 1000)
    return f"{base}.{ms:03d}Z"


def sanitize_id(raw: object, default: str = "") -> str:
    s = re.sub(r"[^A-Za-z0-9._:-]", "", str(raw or ""))[:64]
    if not ID_RE.fullmatch(s):
        return default
    return s


def sanitize_session(raw: object) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]", "", str(raw or ""))[:128]
    if s in (".", "..", "") or not SESSION_RE.fullmatch(s):
        return "unknown"
    return s


def detect_harness() -> str:
    # Honesty: THING_HOST is adapter-asserted; ambient COPILOT_* is not enough.
    th = (os.environ.get("THING_HOST") or "").strip().lower()
    if th in {"claude-code", "codex-cli", "copilot-cli", "copilot-vscode", "cursor", "gemini-cli", "grok-build", "grok-bot"}:
        return th
    if th == "codex":
        return "codex-cli"
    if th == "copilot":
        return "copilot-cli"
    if th == "gemini":
        return "gemini-cli"
    # Grok Build — env detection override (v0.2). Prefer explicit build markers,
    # then session/home markers shared with handoff-spawn.sh. GROK_AGENT alone
    # is not enough to distinguish grok-bot from grok-build.
    if (
        os.environ.get("GROK_BUILD")
        or os.environ.get("XAI_GROK_BUILD")
        or os.environ.get("GROK_SESSION_ID")
        or os.environ.get("GROK_HOME")
        or os.environ.get("GROK_HOOK_EVENT")
    ):
        return "grok-build"
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return "claude-code"
    if os.environ.get("CODEX_SESSION_ID") or os.environ.get("CODEX_PROJECT_ROOT"):
        return "codex-cli"
    if os.environ.get("CURSOR_AGENT") or os.environ.get("CURSOR_TRACE_ID"):
        return "cursor"
    if os.environ.get("GITHUB_COPILOT_CLI"):
        return "copilot-cli"
    if os.environ.get("GEMINI_CLI"):
        return "gemini-cli"
    return "unknown"


def detect_event(payload: dict) -> str:
    for key in (
        os.environ.get("CLAUDE_HOOK_EVENT"),
        os.environ.get("SPECTATE_EVENT_HINT"),
        payload.get("hook_event_name"),
        payload.get("hookEventName"),
        payload.get("event"),
        payload.get("event_name"),
    ):
        if isinstance(key, str) and key.strip():
            return re.sub(r"[^A-Za-z]", "", key).lower()
    # Heuristics from payload shape when the host omits the event name.
    if "tool_name" in payload or "toolName" in payload:
        if "tool_response" in payload or "toolResponse" in payload:
            return "posttooluse"
        return "pretooluse"
    if "prompt" in payload and "tool_name" not in payload:
        return "userpromptsubmit"
    if "transcript_path" in payload or "transcriptPath" in payload:
        return "sessionstart"
    return ""


def tool_family(name: str) -> str:
    # Cursor preToolUse/postToolUse use "Shell"; Claude Code uses "Bash".
    if name in {"Bash", "Shell"}:
        return "shell"
    if name == "WebFetch":
        return "url"
    if name in {"Read", "Write", "Edit", "MultiEdit", "Delete"}:
        return "path"
    return "other"


def shell_target(command: object) -> str | None:
    if not isinstance(command, str) or not command.strip():
        return None
    # First argv token only — never the rest of the command line.
    tok = command.strip().split()[0]
    tok = tok.rsplit("/", 1)[-1][:128]
    if SHELL_TARGET_RE.fullmatch(tok):
        return tok
    return None


def path_target(path: object) -> str | None:
    if not isinstance(path, str) or not path.strip():
        return None
    base = path.strip().replace("\\", "/").rstrip("/").rsplit("/", 1)[-1][:256]
    if not base or DOTDOT.search(base) or not PATH_TARGET_RE.fullmatch(base):
        return None
    return base


def url_target(url: object) -> str | None:
    if not isinstance(url, str) or not url.strip():
        return None
    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return None
    if not parts.scheme or not parts.netloc:
        return None
    host = parts.netloc.split("@")[-1]
    out = f"{parts.scheme.lower()}://{host}"
    if len(out) > 256:
        return None
    if not re.fullmatch(
        r"^[a-z][a-z0-9+.-]{0,15}://[A-Za-z0-9.-]{1,253}(:[0-9]{1,5})?$", out
    ):
        return None
    return out


def main() -> None:
    project = Path(os.environ["CLAUDE_PROJECT_DIR"])
    raw = os.environ.get("SPECTATE_PAYLOAD") or ""
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, ValueError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    event = detect_event(payload)
    kind = KIND_BY_EVENT.get(event)
    if not kind:
        return

    session = sanitize_session(
        os.environ.get("CLAUDE_SESSION_ID")
        or payload.get("session_id")
        or payload.get("sessionId")
        or "unknown"
    )
    harness = detect_harness()
    agent = sanitize_id(
        payload.get("agent_id")
        or payload.get("agentId")
        or payload.get("subagent_id")
        or payload.get("subagentId")
        or "main",
        "main",
    )

    corr = sanitize_id(
        payload.get("tool_use_id")
        or payload.get("toolUseId")
        or payload.get("tool_useId")
    )

    tool_name = sanitize_id(
        payload.get("tool_name") or payload.get("toolName") or payload.get("tool")
    )
    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}

    node_id = ""
    tool_obj = None
    metrics = None
    asserted = None

    if kind == "session.start":
        node_id = "session"
    elif kind == "prompt.submit":
        node_id = "prompt"
        prompt = payload.get("prompt")
        if isinstance(prompt, str):
            metrics = {"prompt_chars": min(len(prompt), 1_000_000_000_000)}
    elif kind in {"tool.pre", "tool.post", "permission.request"}:
        if not tool_name:
            return
        node_id = corr or sanitize_id(f"tool-{tool_name}", f"tool-{tool_name[:40]}")
        if not node_id:
            return
        family = tool_family(tool_name)
        tool_obj = {"name": tool_name, "family": family}
        if family == "shell":
            t = shell_target(tool_input.get("command"))
            if t:
                tool_obj["target"] = t
        elif family == "path":
            t = path_target(
                tool_input.get("file_path")
                or tool_input.get("filePath")
                or tool_input.get("path")
            )
            if t:
                tool_obj["target"] = t
        elif family == "url":
            t = url_target(tool_input.get("url"))
            if t:
                tool_obj["target"] = t
        if kind == "tool.pre":
            asserted = "running"
        elif kind == "tool.post":
            asserted = "succeeded"
        else:
            asserted = "waiting-approval"
    elif kind == "subagent.start":
        node_id = sanitize_id(
            payload.get("agent_id")
            or payload.get("subagent_type")
            or payload.get("subagentType")
            or "subagent",
            "subagent",
        )
    elif kind == "compact.pre":
        node_id = "compact"
    elif kind == "turn.end":
        node_id = "turn"
    else:
        return

    if kind not in {"session.start", "session.end", "stream.truncated", "emitter.truncated"}:
        if not ID_RE.fullmatch(node_id):
            return

    event_out: dict = {
        "schema": "rc.spectate.v1",
        "ts": now_ts(),
        "session_id": session,
        "harness": harness,
        "source": "hook",
        "kind": kind,
        "agent_id": agent,
        "detail": "minimal",
    }
    if kind not in {"session.start", "session.end", "stream.truncated", "emitter.truncated"}:
        event_out["node_id"] = node_id
    if kind in {"tool.pre", "tool.post", "tool.fail", "permission.request"}:
        event_out["step"] = "execute-tools"
    if kind == "prompt.submit":
        event_out["step"] = "assemble"
    if corr:
        event_out["corr_id"] = corr
    if tool_obj:
        event_out["tool"] = tool_obj
    if asserted:
        event_out["asserted_status"] = asserted
    if metrics:
        event_out["metrics"] = metrics

    run_dir = project / ".ravenclaude" / "runs" / session
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return
    log = run_dir / "spectate-events.jsonl"
    # Refuse symlink escapes: resolved path must stay under runs/.
    try:
        runs_root = (project / ".ravenclaude" / "runs").resolve()
        resolved = log.resolve()
        if runs_root not in resolved.parents and resolved != runs_root:
            return
    except OSError:
        return

    line = json.dumps(event_out, separators=(",", ":"), ensure_ascii=True)
    try:
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        return


if __name__ == "__main__":
    main()
PY
exit 0

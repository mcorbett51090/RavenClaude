---
description: "Write a run-dir handoff and print a fresh-window resume prompt. Optional argument: task-id. Use when context is hot or the user says /handoff."
argument-hint: "[task-id]"
allowed-tools: Bash, Read, Write, Edit
---

Load and follow `plugins/ravenclaude-core/skills/session-handoff/SKILL.md`.

Optional `$ARGUMENTS` is the `task-id`. If empty, resolve per the skill (most-recent run dir, else propose a slug). Resolve the originating host — `claude-code` / `grok` / `cli` / `chat`, or its `host-support.json` name, or `other` — and pass it. Then write the handoff and call `rc handoff --task-id <id> --host <host>`. ⛔ Always quote the value (`--host "$HOST"`) and never pass `--host` with nothing after it. Do not hard-code grok. Do not substitute a host you are not.

⛔ **This is a NEW interactive session (unbounded TUI), not cheap-lane.** One bounded job with `cheap_lane: advise|agent` is `cheap-lane-delegation` — do not spawn. If `cheap_lane` is on and you still hand off, state in one clause why (quota, leftover multi-item list, different CLI must own the rest). The spawn script prints a `PRODUCT` line; do not launch until that line has been shown.

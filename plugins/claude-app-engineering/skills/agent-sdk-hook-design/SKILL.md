---
name: agent-sdk-hook-design
description: "Playbook for designing Claude Agent SDK hooks (PreToolUse, PostToolUse, SessionStart, Stop) — selecting the right event, writing the handler contract, deciding advisory vs blocking behaviour, and avoiding the four common hook anti-patterns. Owned by agent-sdk-engineer."
---

# Agent SDK Hook Design

## When to invoke

- Adding a new PreToolUse or PostToolUse hook to a Claude Agent SDK session.
- A hook is firing on the wrong events or causing unintended blocks.
- Designing the hook's advisory-vs-blocking posture.
- Reviewing a hook handler for safety and idempotency.

## Hook event map

| Event | Fires | Typical use |
|---|---|---|
| `PreToolUse` | Before a tool call is executed | Validate args, block dangerous calls, log intent |
| `PostToolUse` | After a tool returns | Redact PII from results, log outcome, rate-limit |
| `SessionStart` | When a new agent session opens | Inject context, warm up state, validate auth |
| `Stop` | When the agent concludes (any reason) | Audit log, cleanup ephemeral resources |

## Step 1 — Choose advisory vs blocking

```
Decision: should the hook STOP execution on a violation?
├── YES (blocking) — exit with a non-zero code / raise + return deny verdict
│     Use for: security controls, destructive-action gates, required-field validation
│     Rule: blocking hooks must fail FAST (< 200 ms); never block on network I/O
└── NO (advisory) — log to stderr and exit 0
      Use for: cost warnings, style guidance, telemetry
      Rule: advisory hooks must NEVER cause data loss if ignored
```

## Step 2 — Write the handler contract

Every hook handler must state:

1. **Scope** — which tool names (or `*`) it fires on.
2. **Input** — what fields from the tool-call payload it reads.
3. **Output** — allow (exit 0) / deny (exit non-zero + message) / annotate (exit 0 + JSON to stderr).
4. **Latency budget** — for blocking hooks: target < 100 ms; hard ceiling 500 ms.
5. **Failure mode** — if the handler itself errors, does it allow or deny? Default: allow (fail-open) unless the hook is a security gate (then fail-closed).

```python
# Example: PreToolUse blocking hook — deny file writes outside /tmp
import json, sys

payload = json.load(sys.stdin)
tool_name = payload.get("tool", {}).get("name", "")
tool_input = payload.get("tool", {}).get("input", {})

if tool_name == "write_file":
    path = tool_input.get("path", "")
    if not path.startswith("/tmp/"):
        print(json.dumps({"decision": "deny",
                          "reason": f"write_file outside /tmp is not allowed: {path}"}))
        sys.exit(1)

sys.exit(0)
```

## Step 3 — Scope narrowly

| Anti-pattern | Fix |
|---|---|
| Hook fires on `*` (all tools) for a write-specific check | Scope to `write_file`, `edit_file`, etc. |
| Hook reads the full message history on every call | Read only `tool.input`; access history only in `SessionStart` |
| PostToolUse hook mutates the tool result | Return annotated metadata to stderr; never mutate — the model already processed the result |
| Hook makes a synchronous HTTP call in the hot path | Cache, pre-fetch in `SessionStart`, or make the hook advisory |

## Step 4 — Idempotency and re-entry

Hooks may fire multiple times on retried tool calls. Design for idempotency:

- Log with a deduplication key (session ID + tool call ID).
- If the hook writes to an external system, use upsert semantics.
- For rate-limit hooks: track counts in a shared store keyed by session, not per-invocation.

## Hook testing checklist

- [ ] Unit-test the handler with a synthetic `payload.json` — both allow and deny branches.
- [ ] Confirm the hook exits within its latency budget under synthetic load.
- [ ] Test the error path: handler crashes → what does the session do?
- [ ] Verify `PreToolUse` deny message surfaces to the agent (not swallowed by the SDK runtime).
- [ ] For security-gate hooks: confirm fail-closed behaviour (an unexpected exception should deny, not allow).

## Pitfalls

- A blocking hook with a database lookup in the hot path — one slow query serialises every tool call.
- Using `PostToolUse` to decide whether to allow a tool call — the tool already executed; `PostToolUse` cannot undo writes.
- Registering the same hook twice (in both the plugin's `hooks.json` and the session-level config) — both fire; effects double.
- Forgetting that `PreToolUse` for computer-use tools fires *before* the screen action — keep blocking logic tight or you'll desynchronise the computer-use state machine.

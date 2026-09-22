---
description: Check or drive the source-control coordinator's ledger-backed handoff queue.
allowed-tools: Bash, Read
---

# /coordinate

Check or drive the **source-control coordinator**'s ledger-backed handoff queue — the
`source-control-coordinator` agent's own command surface. See
[`../agents/source-control-coordinator.md`](../agents/source-control-coordinator.md) for what the
coordinator itself does; this command is the human-facing front door over its ledger/`gh` state.

## Verb table

| Verb | Underlying command | Output shape | Empty state |
|---|---|---|---|
| `/coordinate status` | Reads `.ravenclaude/runs/coordinator/status.json` + the lock record's `heartbeat_at` (`$RC_WORKTREE_GUARD_HOME/coordinator-lock/lease.json`, default `~/.ravenclaude/coordinator-lock/lease.json`) | One-line liveness summary + subscribed-PR count | "No coordinator status recorded — has it ever run?" |
| `/coordinate queue` | A raw-JSONL read over `.ravenclaude/ledger/*.jsonl`, filtered to `coordinator-handoff`-tagged items and folded through their `state`/`link` events (see [`../knowledge/coordinator-ledger-convention.md`](../knowledge/coordinator-ledger-convention.md)) | A table of open items: PR #, state, age | "No open coordinator-handoff items." |
| `/coordinate handoff <pr>` | `rc ledger --repo-root <primary> open --subject "pr:<pr> <summary>" --tag coordinator-handoff` (per the ledger convention's PR-correlation prefix) | The new item's id, echoed back | n/a (always creates) |

`allowed-tools: Bash, Read` is sufficient for all three verbs — `status`/`queue` are read-only, and
`handoff` writes via `rc ledger` (which does the writing itself), not via a direct file write.

## Usage

Run the matching command with the Bash tool from the **project root** (the primary checkout, not a
worktree) so `--repo-root` resolves correctly:

```
# status
rc ledger --repo-root "$(pwd)" project --json | ...   # or read .ravenclaude/runs/coordinator/status.json directly

# queue
cat .ravenclaude/ledger/*.jsonl | jq -c 'select(.type=="open") | select(.asserted.tags | index("coordinator-handoff"))'
# then fold subsequent state/link events sharing item_id, per the ledger convention doc

# handoff <pr>
rc ledger --repo-root "$(pwd)" open --subject "pr:<pr> <one-line summary>" --owner coordinator --priority 2 --tag coordinator-handoff
```

## Notes

- `/coordinate` is Claude-Code-only as a slash command; the underlying `rc ledger`/`gh` invocations
  work from any host.
- This command never merges, resolves, or escalates on your behalf — it reads and it opens a handoff
  item. The coordinator agent itself performs the actions in its own file.

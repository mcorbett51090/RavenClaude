---
id: mcp-quarantine-matcher-is-a-prefix
title: "The MCP quarantine hook matches a prefix, not WebFetch's exact string"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 914
summary: "sanitize-mcp-output.py extends F1's WebFetch quarantine to mcp__* tool results — but the tool-name match has to be a prefix check, and a substring match had to be deliberately excluded."
last_verified: 2026-08-30
covers:
  - plugins/ravenclaude-core/hooks/sanitize-mcp-output.sh
  - plugins/ravenclaude-core/hooks/sanitize-mcp-output.py
covers_digest: "sha256:3b6351ebcadda447559e44fb8339c4aaf39d8eb45c143a20414a4c329c9602e7"
nuance: "F1's WebFetch hook matches one exact tool name. This one must be a PREFIX check (mcp__ names are dynamic) — and a tool name merely CONTAINING 'mcp__' without starting with it must NOT match."
nuance_evidence:
  measured: 2026-08-30
  control: "handle() on {tool_name: 'not_mcp__lookalike', ...} returns None (no-op) in the self-test, proving the prefix check rejects a substring match"
  falsifier: "the same fixture producing a sanitize envelope instead of None"
  probe: "plugins/ravenclaude-core/hooks/sanitize-mcp-output.py"
nuance_source: "plugins/ravenclaude-core/hooks/sanitize-mcp-output.py:1-140 (_is_mcp_tool + handle)"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/hooks/sanitize-mcp-output.py"
  teeth_exit: 1
sources:
  - label: Q1/L4 of the analog-repos-gap-fill leftovers, unparked on owner request
    url: https://github.com/mcorbett51090/RavenClaude/pull/928
---

## What a reader would have assumed instead

Copy F1's WebFetch matcher verbatim (`tool_name == "WebFetch"`) and swap the string — an
exact-match check would silently never fire, because MCP tool names are dynamic
(`mcp__<server>__<verb>`), not a fixed string.

## The discriminator

control: `handle()` on a payload naming `not_mcp__lookalike` returns `None` (no-op) in the
self-test — proving the prefix check correctly rejects a substring match, not just an
exact-match miss.
Measured 2026-08-30: the matcher is `tool_name.startswith("mcp__")`, a prefix check — and the
self-test asserts both the negative direction (a real MCP name is quarantined) and the false-prefix
direction (a name merely containing `mcp__` is not).

## Why it matters

Falsifier: the same fixture producing a sanitize envelope instead of `None`.

Probe: `plugins/ravenclaude-core/hooks/sanitize-mcp-output.py` (`--self-test`)

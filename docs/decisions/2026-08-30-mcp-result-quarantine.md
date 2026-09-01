# Decision record — MCP result quarantine (Q1 / L4)

**Date:** 2026-08-30 · **Owner:** Matt · **Method:** `/forge` (unparked via the trigger stated in the
pickup sheet — "owner asks for MCP quarantine" — Matt selected this leftover for the build queue)

**Source:** [`docs/follow-ups/2026-08-14-analog-repos-leftovers.md`](../follow-ups/2026-08-14-analog-repos-leftovers.md)
§1 (Q1 / L4), queue row [`pr-queue.md`](../plans/2026-08-14-analog-repos-gap-fill/pr-queue.md) Q1.
**Depends on:** F1 (`sanitize-webfetch-output.sh`/`.py`, [#928](https://github.com/mcorbett51090/RavenClaude/pull/928), shipped `0.267.0`) — already merged.

## 0. What this closes

F1's own hooks.json comment named the limit explicitly: *"Matcher is WebFetch ONLY (`mcp__.*` is an
accepted-limit this increment)."* An MCP server's tool result can carry the same injection-shaped
blocks (`<system-reminder>`, `<system-instruction>`, etc.) a WebFetch body can, and until this PR they
reached the model unsanitized. This is the fast-follow the pickup sheet reserved as Q1, unparked now
because the owner asked for it (the file's own stated trigger).

## 1. What shipped

- **`plugins/ravenclaude-core/hooks/sanitize-mcp-output.py`** + **`.sh`** — same fail-open contract and
  same underlying `sanitize()` (from `scripts/sanitize-webfetch-body.py`, unchanged — reused, not
  forked) as F1. The MCP-specific work is the envelope shape: MCP tool results carry
  `content: [{"type": "text", "text": "..."}]` (a content-array), not F1's plain-string body, and the
  matcher is a prefix check (`tool_name.startswith("mcp__")`) rather than an exact-match — a name that
  merely *contains* `mcp__` must not match, which the hook's own `--self-test` asserts as a named
  boundary case.
- **`hooks.json`** — new `PostToolUse` block, matcher `mcp__.*` (the same regex form already used
  elsewhere in this file for the Thing's own PreToolUse matcher — not new syntax), pointing at
  `sanitize-mcp-output.sh`.
- **`scripts/audit-gates.sh`** — two `gate` assertions appended to the existing Gate 48 section (no new
  gate number minted; this is additional coverage of the same "WebFetch return-envelope sanitizer"
  concern, now covering the sibling MCP path): the hook's own `--self-test` must pass, and must contain
  zero `FAIL` lines.
- **This decision doc** — the House Rule 3 walkthrough the pickup sheet required (§2 below).

## 2. House Rule 3 walkthrough

*"What happens when a consumer runs `/plugin marketplace update`?"*

Every consumer who has this plugin installed and issues **any** MCP tool call (`mcp__*`) will, from
this version forward, have that tool's result **rewritten** before the model sees it — the same
consumer-visible behavior change F1 already made for WebFetch, now extended to MCP. Concretely:

- **What changes:** an MCP tool result containing an injection-shaped block (e.g. a poisoned document
  a third-party MCP server returns) has that block stripped; `hookSpecificOutput.additionalContext`
  names the tool and the strip count. A clean result is byte-identical (verified: the self-test's
  "clean is identity" case).
- **What does NOT change:** any consumer who does not call an `mcp__*` tool sees nothing — the hook
  no-ops on every other tool name (self-test: WebFetch, Bash, and a non-`mcp__`-prefixed name
  containing the substring `mcp__` all confirmed no-op). No new plugin, skill, or agent. No semver
  requirement beyond the plugin's normal patch bump (this PR: `0.307.0` → `0.308.0`).
- **Fail-open is the default-break mitigator**, matching F1's own precedent exactly: any parse / IO /
  sanitizer error in the new hook prints nothing and exits 0, so a bug in this code degrades to "MCP
  results pass through unsanitized" (the pre-PR behavior), never to "the MCP tool call fails." A
  consumer's existing MCP integrations cannot be broken by this hook erroring.
- **Copilot projection:** `scripts/generate-copilot-hooks.py --check` confirms the new hook is picked
  up by the existing coverage check (not added to `_SKIP`) — no separate committed artifact to
  regenerate; that script computes coverage live from `hooks.json`.

## 3. What this is not

- Not a rewrite or extension of F1's WebFetch matcher — F1's matcher stays `WebFetch` only, unchanged.
- Not `mcp__.*` added to `sanitize-webfetch-output.sh`'s own matcher — the pickup sheet explicitly
  banned that shortcut ("that is explicitly banned until this forge lands"); this is a **separate**
  hook + matcher, sharing only the underlying body sanitizer.
- Not a change to which MCP servers are trusted or how their results are otherwise handled — this is a
  content-quarantine floor, not an allowlist or an identity check (the deferred `mcp.allowed_servers`
  work named in `plugins/ravenclaude-core/CLAUDE.md`'s Track B engine-foundation notes is a distinct,
  still-not-live concern).

## 4. Acceptance (from the pickup sheet, verified this session)

- Same fail-open fixtures on an MCP-shaped payload — ✅ `sanitize-mcp-output.py --self-test`, 13/13
  checks pass, including the poisoned/clean pair and the malformed-stdin no-op.
- House Rule 3 walkthrough — ✅ §2 above.
- Version `0.270.0+` — this PR ships `0.308.0` (current HEAD was already `0.307.0`; not reusing any
  version the pickup sheet's do-not-redo list names).

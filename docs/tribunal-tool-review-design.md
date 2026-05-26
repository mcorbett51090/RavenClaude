# Tribunal tool-review extension — design & phasing

> **Status:** design (architect-reviewed 2026-05-26). Implementation is phased and
> multi-PR; each phase is independently shippable + gated. This extends the
> command-review tribunal ("the Thing") from **Bash-only** review to the
> **file (Edit/Write/MultiEdit), network (WebFetch/WebSearch), and MCP** tool
> shapes, retiring the "Early access / Preview" flags on the comfort-posture
> categories as each goes live. Companion to
> [`tribunal-review-feature-design.md`](tribunal-review-feature-design.md) and the
> [`thing` skill](../plugins/ravenclaude-core/skills/thing/SKILL.md).

## The core structural finding

Every layer of the engine is hardwired to a Bash **command string**:

- `hooks/thing-orchestrator.sh` gates on `tool_name == "Bash"`, pulls
  `tool_input.command`, and bails if empty; `tool_name:"Bash"` is hardcoded into
  the Sága log and the cache key.
- `scripts/thing-decision.py` `classify()` parses only `Bash(...)` EMISSIONS
  patterns (`_command_prefixes()` explicitly skips non-Bash patterns).
- `scripts/thing-concerns.py` regexes match a command string; the EDIT-safety
  invariant re-runs those regexes on a rewritten command.
- `scripts/thing-seat.sh` wraps "the command" as untrusted data.

**The extension is therefore: introduce a `payload` abstraction (the reviewed
text + a shape tag) and make each layer shape-aware, leaving the Bash path
byte-for-byte unchanged.**

## #1 security finding — a live hole this build closes

`xc.tribunal-self-disable` (critical, `pre_llm_deny`, `always_screen`) blocks a
**Bash command** that mutates the Thing's own substrate. But a **`Write`/`Edit`
to `thing-orchestrator.sh`, `hooks/hooks.json`, `thing-concerns.py`, …** is the
identical threat and is **completely unreviewed today**, because file-edits never
reach the orchestrator. Shipping file-edit review (Phase 1) closes this hole — it
is the strongest reason to do file review early.

## Per-tool-shape design

Orchestrator hooking: **extend the existing `PreToolUse` Bash matcher** to
`Bash|Write|Edit|MultiEdit|WebFetch|WebSearch|mcp__.*` (the matcher supports `|`).
One orchestrator keeps the self-disable screen, audit/cache/fail-closed machinery
uniform. Replace the `tool_input.command` extraction with a **payload-extraction
dispatch** keyed on `tool_name`:

| Tool | Payload reviewed | Category | EDIT (rewrite)? | Read? |
|---|---|---|---|---|
| Bash | `command` | EMISSIONS classify (unchanged) | yes (unchanged) | shell_readonly |
| Edit/MultiEdit | path + diff | `file_edit_project`/`_global` by **realpath** (symlink-resolved) vs cwd | **defer** — ALLOW/DENY-only v1 | no |
| Write | path + content | same | defer — ALLOW/DENY-only | no |
| Read | path | `file_read_project`/`_global` | n/a | **yes** |
| WebFetch/WebSearch | url / query | `network_read` | **no** | **yes** |
| MCP (`mcp__*`) | tool name + args | `mcp_tools` (read/write by method verb) | defer to v2 | verb-based |

Notes: `network_write` stays Bash-only (no first-class non-Bash network-write
tool; its EMISSIONS are all `Bash(curl -X …)`/`Bash(gh api …)`). The `is_read`
set already lists `file_read_*` + `network_read`, so **reads-never-surfaced**
works for free once they classify. The `updatedInput` emitter must become
shape-aware (`{new_string}`/`{edits}`/`{content}`, not `{command}`).

**Path classification is a new security boundary** — project vs global must use
`os.path.realpath` (symlink + `..` resolved) in Python, never a regex, and be
CI-fuzzed.

## Security must-haves

1. **Extend `xc.tribunal-self-disable` to edit-target paths** (the substrate
   dirs, `thing.yaml`, and `comfort-posture.yaml` writes of `thing:`/`gate_floor:`/
   `command_review:`) via `screen_always` — a path-shaped trigger family.
2. **Fail-closed per shape** — a toggled category whose payload can't be parsed
   must DENY, not fall through like an empty Bash command does today.
3. **Injection screen over file CONTENT and URLs** — `xc.injection-attempt` +
   Heimdall must run on a Write's content (injected-data-into-context is the
   canonical attack) and on URLs/MCP args; reuse the nonce-tagged untrusted
   envelope (already correct for arbitrary payloads).
4. **Secret backstop over content/URL/args** — `thing-seat.sh`'s pre-egress
   secret scan must cover the new payloads (a Write introducing an inline key →
   local deny, never transmitted).
5. **No regression to the Bash path** — identical `classify` behavior, Sága
   `tool_name`, cache key; Gate 14/15 must pass unchanged.

## Phasing (smallest blast radius first)

- **Pre-phase (near-free):** flip `shell_local_mutate` + `shell_package_install`
  live — already Bash, already classified + tier-mapped. Mostly a
  `THING_LIVE_CATEGORIES` flip + ensuring every `slm.*`/`spi.*` concern has
  `triggers` OR `judgment_only` (Gate 21 #17) + Gate 14 cases. No engine change.
- **Phase 1:** file Edit/Write/MultiEdit (project). Introduces the payload
  abstraction; closes the self-disable file-edit gap. ALLOW/DENY-only.
- **Phase 2:** `file_edit_global` + `file_read_project`/`_global` (reads, cheap).
- **Phase 3:** WebFetch/WebSearch → `network_read` (ALLOW/DENY-only, read tier).
- **Phase 4:** MCP tools (most heterogeneous; verb-based read/write; ALLOW/DENY
  first, arg-narrowing EDIT later).

Each phase: gated on its own `THING_LIVE_CATEGORIES` entry; new Gate-23-style
fixtures (mirroring Gate 14/15, CI-safe via `THING_SEAT_MOCK_VERDICT`).

## Open decisions for the owner

1. **EDIT-rewrite for file content** — the invariant `concerns(revised) ⊆
   concerns(original) − {cited}` re-runs the same regexes on a command; for a
   file it would need a reconstructed post-edit file (read dependency + TOCTOU).
   **Recommendation: ALLOW/DENY-only for file shapes in v1; defer content-EDIT.**
2. **URL/MCP have no verifiable rewrite** → EDIT disabled for those shapes
   (reduces the "fix it for you" value). Confirm acceptable.
3. **MCP read/write verb heuristic is soft** (`get_*` vs `create_*`); default
   policy for unconventional method names — deny-write vs ask — is an owner call.
4. **WebFetch carries a `prompt`** as well as a `url` — review the prompt for
   injection (risks false-positives on legit prompts) or the URL only?

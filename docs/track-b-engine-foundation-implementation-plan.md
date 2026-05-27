# Track B — Engine Foundation (Phase 0) — Implementation Plan

> **Status:** plan, pending owner approval + gap-analysis refinement. This is the
> FIRST Track B PR. It builds the shared, payload-shaped machinery every non-Bash
> tool shape needs — fixture-gated, with **zero Bash regression**. **Nothing goes
> live** (`THING_LIVE_CATEGORIES` untouched). Phase 1 (`file_edit_project`,
> ALLOW/DENY-only) ships as the next PR, rebased on this.
>
> Companion: [`tribunal-tool-review-design.md`](tribunal-tool-review-design.md)
> (the v3.1 design — this plan implements its **Engine Foundation (Phase 0)**
> section). Track A merged as PR #104 (v0.36.0).

## Owner decisions (locked — building to them)

1. Two parallel tracks; Track A merged first, Track B rebases on it.
2. **ALLOW/DENY-only v1** for file/URL/MCP shapes — no EDIT rewrite (no
   machine-checked `concerns(revised) ⊆ concerns(original)` invariant for content).
3. **WebFetch → review the URL only**, not the `prompt`.
4. **MCP unknown/unconventional verb → classify as WRITE at an escalated tier.**

## Current seams (verified against the live code)

- `hooks/thing-orchestrator.sh`: `Bash`-only PreToolUse matcher; the gate
  `[ "$tool_name" != "Bash" ] && exit 0` sits at the top (above the self-disable
  screen — the design doc's P0-2 silent bypass). Calls
  `thing-decision.py classify "$cmd"` (command-shaped). Then: fast `grep`
  short-circuit (no toggle → exit 0), self-disable deny, hard-rule deny,
  `enabled != true` gate, panel, `emit`/`emit_edit`, Sága write (early-write +
  main write), verdict cache.
- `scripts/thing-decision.py`: `classify()` parses only `Bash(...)` EMISSIONS
  prefixes (longest-prefix, `_normalize_lead`); `_screen_always`;
  `_decision_detail`; `main` (`classify`/`preview`); `config_hash`.
- `scripts/thing-concerns.py`: `evaluate(catalog, command, category)` (string);
  `screen_always` (raw ∪ normalized); `_decoded_payload_concerns` (base64,
  depth-1); `_normalize_for_match`; `revalidate` (EDIT-safety invariant).
- `scripts/thing-seat.sh`: `THING_CMD`/`THING_CATEGORY` (command-shaped); egress
  secret backstop scans the command string only.
- `scripts/apply-comfort-posture.py` EMISSIONS already declares the non-Bash
  categories (`Read(**)`, `Edit(**)`, `Write(**)`, `MultiEdit(**)`, `WebFetch`,
  `WebSearch` is ABSENT, `mcp_tools: []`). `classify()` ignores non-`Bash(...)`
  patterns, so `classify_payload` is **name-keyed**, not EMISSIONS-prefix-keyed.

## Commit-by-commit

### Commit 1 — `classify_payload` (§1) · `thing-decision.py`

- `CLASSIFY_PAYLOAD_VERSION = "1"`.
- `classify_payload(tool_name, tool_input) -> category | None`: Bash →
  `classify(tool_input["command"])`; Edit/Write/MultiEdit → `file_edit_project`/
  `_global` by canonicalized path (from `file_path` / `edits[].file_path`);
  Read → `file_read_*`; WebFetch/WebSearch → `network_read`; `mcp__*` →
  `mcp_tools`.
- `main`: add a `classify-payload` subcommand that reads a tool-call JSON
  (`{tool_name, tool_input}`) from argv/stdin; keep `classify <cmd>` for Bash.
- **Gate 24**: every supported tool name yields a non-None category; an unknown
  tool name yields None.

### Commit 2 — self-disable above the tool gate + `screen_substrate_path` + canonicalization (§2/§2a/§4) · `thing-concerns.py`, `thing-decision.py`, `thing-orchestrator.sh`

- `thing-concerns.py`: single-source `THING_SUBSTRATE` (the §2a glob list);
  `screen_substrate_path(target, inode_set)` — stdlib `os.path` + `os.stat().st_ino`
  membership, catalog-INDEPENDENT (never loads the catalog, so no catalog-load
  except-branch); `canonicalize_path()` per §4 (reject lexical `..`/leading `~`;
  realpath; NFC-normalize; casefold on case-insensitive platforms; lexical +
  realpath + inode-set membership; ambiguous → stricter tier).
- `thing-decision.py`: `config_hash` folds `sha256(JSON sorted THING_SUBSTRATE)`
  + `CLASSIFY_PAYLOAD_VERSION`.
- orchestrator: **remove the `tool_name!=Bash` first-gate**; run the self-disable
  screen FIRST for every shape (text → `screen_always`; file → `screen_substrate_path`)
  ABOVE the per-category enabled gate. A `comfort-posture.yaml` write is screened
  by parsing the RESULTING YAML (not regex); unparseable → DENY.
- **Gates**: Write to each substrate path → deny even with file categories OFF;
  **hardlink** and **`..`/symlink** variants; posture `thing:off` /
  `command_review:` / `gate_floor:` write → deny; unparseable posture → DENY.

### Commit 3 — full-payload local screen + caps (§3/§Payload caps) · `thing-concerns.py`

- Route the entire reviewed payload (file content, URL, MCP args) through
  `evaluate` / `screen_always` / the secret+injection screen (all already
  string-based).
- `SCREEN_MAX_BYTES = 1 MiB`: a larger payload DENIES for a toggled category
  (cannot fully screen → fail closed); never truncate-then-screen.
- `DECODE_MAX_BYTES = 256 KiB`: total decoded-output budget across
  `_decoded_payload_concerns` (incl. the depth-1 recursion), plus the existing
  200-run cap — kills the quadratic base64 path inside the 1 MiB budget.
- **Gates**: a secret / injection / `curl|sh` inside `Write.content` is screened;
  a >1 MiB payload → deny; a 1 MiB single base64 blob stops at `DECODE_MAX_BYTES`.

### Commit 4 — payload-shaped seat + egress backstop (§3a) · `thing-seat.sh`, orchestrator

- `thing-seat.sh` accepts `THING_PAYLOAD` (a shape tag + the reviewed text)
  alongside `THING_CMD` (Bash back-compat); the egress secret ERE runs over the
  **full reviewed text**, not just a command. **No file/network/MCP category may
  convene a seat until this lands** (deterministic full-payload screen +
  ALLOW/DENY-only is the only permitted path before it).
- **Gate**: a secret embedded in `Write.content` is denied by the backstop (mock
  seat, asserts no egress).

### Commit 5 — orchestrator widening + fail-closed table + EDIT coercion (§Fail-open/§EDIT) · `hooks/hooks.json` (+ `.claude/settings.json` dev-mirror), orchestrator

- Matcher → `Bash|Write|Edit|MultiEdit|WebFetch|WebSearch|mcp__.*` (plugin
  canonical AND the dev-mirror).
- orchestrator: read `tool_name` + `tool_input` generically; call
  `classify-payload`; per-shape extraction-failure → DENY for a toggled category;
  keep the no-toggle `grep` short-circuit FIRST (opted-out consumers pay nothing);
  the aggregator coerces a non-Bash seat `verdict:"edit"` → `deny` BEFORE the
  `emit_edit` path is reached.
- **Gates**: a `Write` with no posture file → exit 0 with no python call
  (opted-out pays nothing); extraction-fail under a toggled category → deny; a
  payload-shape seat returning `edit` → `deny`, never `updatedInput`.

### Commit 6 — serialization (§Serialization) · orchestrator, `thing-decision.py`

- Per-shape Sága `tool_input` at BOTH write sites: Bash `{command}`; file
  `{file_path, content_sha256, bytes}`; network `{url}`; MCP `{name, args_sha256}`.
- Cache `identity` via ONE shared helper used at the read AND write sites; key =
  `shape|identity|category|config_hash`. file = `realpath` + `sha256(content|edits)`;
  network = full URL; MCP = `server__verb` + `sha256(canonical-json(args))`.
- **Gate**: cache non-collision — two distinct payloads in the same category
  differing only by `identity` produce two distinct keys; the second is not
  served the first's verdict.

### Commit 7 — Gates 24+ + Bash-regression proof + migration (§Gate matrix/§Bash-regression/§Migration/§schema_version) · `scripts/audit-gates.sh`, `CLAUDE.md`

- New **Gate 24+** per-phase matrix, CI-safe via `THING_SEAT_MOCK_VERDICT`:
  (a) clean→allow, (b) concerning→deny, (c) unparseable/empty→deny,
  (d) self-disable-via-shape incl. hardlink + `..`/symlink, (e) cache
  non-collision, (f) MultiEdit edit#2 → substrate → whole call deny + malformed
  `edits[]`, (g) EDIT coercion, (h) seat egress backstop.
- **Assert Gate 14 + Gate 15 pass with ZERO fixture edits** — the Bash-regression
  guarantee (the shared `screen_always` + seat-wrapper became payload-shaped).
- `CLAUDE.md` migration note: the widened matcher is a consumer-visible behavior
  change (the hook now spawns on Write/Edit/WebFetch/MCP); the no-toggle `grep`
  short-circuit keeps opted-out consumers at zero cost. `schema_version` bump not
  required (categories reuse the existing shape). Version bump `plugin.json` +
  `marketplace.json`.

## Risks & guarantees

- **Bash regression** (shared `screen_always` + seat become payload-shaped) →
  proof obligation: Gate 14/15 unchanged.
- **Matcher-widening cost** → grep short-circuit first; a fixture proves an
  opted-out consumer pays nothing.
- **Path canonicalization** → TOCTOU accepted (a PreToolUse hook cannot lock the
  FS); inode set best-effort; mis-classification only bumps tier.
- New top-level dirs: none → `.repo-layout.json` unchanged (verify before push).

## Sequencing

This PR = **Phase 0 only**. Then: Phase 1 `file_edit_project` (live, ALLOW/DENY)
→ Phase 2 reads + `file_edit_global` → Phase 3 WebFetch/WebSearch (`network_read`;
adds `WebSearch` to EMISSIONS `network_read`) → Phase 4 MCP (verb-based + server
allowlist; author the 5 `mcp_tools` concern triggers first). Each later phase
that widens behavior carries its own migration note.

## Open questions (to resolve before/with implementation)

_(populated by the gap analysis + owner refinement)_

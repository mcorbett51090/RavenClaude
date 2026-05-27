# Track B — Engine Foundation (Phase 0) — Implementation Plan

> **Status:** plan, **v2 (gap-analysis-refined, 7.5/10 → addressing P0/P1)**, pending
> owner confirmation of the open decisions below. This is the FIRST Track B PR. It
> builds the shared, payload-shaped machinery every non-Bash tool shape needs —
> fixture-gated, with **zero Bash regression**. **Nothing goes live**
> (`THING_LIVE_CATEGORIES` untouched). Phase 1 (`file_edit_project`,
> ALLOW/DENY-only) ships as the next PR, rebased on this.
>
> Companion: [`tribunal-tool-review-design.md`](tribunal-tool-review-design.md)
> (v3.1 — this plan implements its **Engine Foundation (Phase 0)** section). Track A
> merged as PR #104 (v0.36.0).

## Owner decisions (locked — building to them)

1. Two parallel tracks; Track A merged first, Track B rebases on it.
2. **ALLOW/DENY-only v1** for file/URL/MCP shapes — no EDIT rewrite.
3. **WebFetch → review the URL only**, not the `prompt`.
4. **MCP unknown/unconventional verb → classify as WRITE at an escalated tier.**

## Current seams (verified against the live code)

- `hooks/thing-orchestrator.sh`: `Bash`-only matcher; `[ "$tool_name" != "Bash" ] && exit 0`
  (`:68`) above the self-disable screen (design P0-2). Fast `grep` short-circuit
  (`:79`, no toggle → exit 0). `classify "$cmd"` (`:90`, command-shaped). Then
  self-disable deny (`:102-118`), hard-rule deny (`:126-142`), `enabled != true`
  gate (`:144`), panel, `emit`/`emit_edit` (`:497`). **THREE** Sága write sites that
  hardcode `tool_name:"Bash", {command}`: self-disable early-write (`:107-115`),
  hard-rule early-write (`:131-139`), main write (`:455-467`). Verdict cache read
  (`:201`) + write (`:466`).
- `scripts/thing-decision.py`: `classify()` parses only `Bash(...)` EMISSIONS
  prefixes; `_screen_always`; `_decision_detail`; `main` (`classify`/`preview`);
  `config_hash` at `:586-595` = `sha256(json.dumps(cfg_blob, sort_keys=True) + cat_text)[:16]`
  where `cat_text` is `concerns-catalog.md`.
- `scripts/thing-concerns.py`: `evaluate(catalog, command, category)` (string);
  `screen_always` (raw ∪ normalized, scans cross_cutting + all categories for
  `always_screen`); `_decoded_payload_concerns` (`:147`, base64, depth-1, **uses an
  UNBOUNDED `_B64_RUN.finditer` — no run cap today**); `_normalize_for_match`;
  `revalidate`.
- `scripts/thing-seat.sh`: `THING_CMD`/`THING_CATEGORY` (command-shaped); egress
  secret backstop scans the command string only.
- `scripts/apply-comfort-posture.py` EMISSIONS declares the non-Bash categories
  (`Read(**)`, `Edit(**)`, `Write(**)`, `MultiEdit(**)`, `WebFetch`); **`WebSearch`
  is ABSENT**; `mcp_tools: []`. `classify()` ignores non-`Bash(...)` patterns, so
  `classify_payload` is **name-keyed**.

## Commit ordering principle (fixes gap P0-2)

Commits **1–4 are pure additions** — they add Python/seat machinery and **do not
change the orchestrator's behavior** (it stays Bash-only, gate + matcher intact),
so no non-Bash call can reach a half-built path. **Commit 5 is the atomic
multi-shape switch**: it removes the Bash gate, reads `tool_input` generically,
calls `classify-payload`, runs self-disable-for-all-shapes, AND widens the matcher
— all together, so there is never an intermediate where the gate is removed but
the read/matcher are unaligned. Commits 6–7 finalize serialization + gates.

## Commit-by-commit

### Commit 1 — `classify_payload` (§1) · `thing-decision.py` (Python only; orchestrator unchanged)

- `CLASSIFY_PAYLOAD_VERSION = "1"`.
- `classify_payload(tool_name, tool_input) -> category | None`: Bash →
  `classify(tool_input["command"])`; Edit/Write/MultiEdit → `file_edit_project`/
  `_global` by canonicalized path; Read → `file_read_*`; WebFetch/WebSearch →
  `network_read`; `mcp__server__verb` → `mcp_tools`, **read vs write by the fixed
  read-verb prefix set `get_ list_ read_ search_ describe_ fetch_`** (everything
  else → write/escalated, per locked decision 4). _[Open #4 — recommended A: ship
  the verb set now so `CLASSIFY_PAYLOAD_VERSION` stays stable across phases; the
  `mcp.allowed_servers` allowlist + the 5 `mcp_tools` concern triggers remain
  Phase 4.]_
- `main`: add a `classify-payload` subcommand that reads the tool-call JSON
  **from stdin** (`{tool_name, tool_input}`) — _[Open #3 — recommended stdin: a
  1 MiB `Write.content` on argv risks `ARG_MAX`]_. Keep `classify <cmd>` (argv) for
  the Bash path / back-compat.
- **Gate 24**: every supported tool name → non-None category; an unknown tool → None.

### Commit 2 — `THING_SUBSTRATE` + `screen_substrate_path` + canonicalization + `config_hash` fold (§2a/§4) · `thing-concerns.py`, `thing-decision.py` (Python only)

- `thing-concerns.py`: single-source `THING_SUBSTRATE` (the §2a glob list);
  `screen_substrate_path(target, inode_set)` — stdlib `os.path` + `os.stat().st_ino`,
  catalog-INDEPENDENT. The inode-set is precomputed from `THING_SUBSTRATE` paths
  with `os.stat` only — **it never loads the concern catalog** (the whole point of
  the v3.1 split, so no catalog-load except-branch). `canonicalize_path()` per §4
  (reject lexical `..`/leading `~`; realpath; NFC; casefold on case-insensitive
  platforms; lexical + realpath + inode membership; ambiguous → stricter tier).
- `thing-decision.py`: fold the two new terms **into the existing hashed blob** —
  extend `cfg_blob` with `"substrate": sorted(THING_SUBSTRATE)` and
  `"classify_payload_version": CLASSIFY_PAYLOAD_VERSION` **before** the
  `json.dumps(..., sort_keys=True)` at `:586` (not a separate `sha256` concat), so
  the existing 16-char digest covers them.
- **Gate**: `screen_substrate_path` membership unit tests (path, realpath, inode,
  hardlink) — exercised end-to-end in Commit 5's orchestrator gates.

### Commit 3 — full-payload local screen + caps (§3/§Payload caps) · `thing-concerns.py` (Python only)

- Route the entire reviewed payload (file content, URL, MCP args) through
  `evaluate` / `screen_always` / the secret+injection screen (all string-based).
- `SCREEN_MAX_BYTES = 1 MiB`: a larger payload DENIES for a toggled category (fail
  closed); never truncate-then-screen.
- **Introduce BOTH caps in `_decoded_payload_concerns`** (gap P0-1 — neither exists
  today): a **200-candidate-run cap** AND a **`DECODE_MAX_BYTES = 256 KiB`**
  total-decoded-output budget across the pass incl. the depth-1 recursion — kills
  the quadratic base64 path inside the 1 MiB budget. _[Open #2 — recommended:
  accept the design's `SCREEN_MAX_BYTES`=1 MiB / `SEAT_MAX_BYTES`=64 KiB /
  `DECODE_MAX_BYTES`=256 KiB defaults; they're flagged tunable and revisitable.]_
- **Gates**: secret/injection/`curl|sh` inside `Write.content` screened; >1 MiB
  payload → deny; a 1 MiB single base64 blob stops at `DECODE_MAX_BYTES`.

### Commit 4 — payload-shaped seat + egress backstop (§3a) · `thing-seat.sh` (seat only; Bash back-compat)

- Seat accepts `THING_PAYLOAD` (shape tag + reviewed text) alongside `THING_CMD`;
  the egress secret ERE runs over the **full reviewed text**. `SEAT_MAX_BYTES`
  truncation (64 KiB) applies to the seat prompt **only**, after the local screen
  ran on the full ≤1 MiB text.
- **Gate**: a secret in `Write.content` denied by the backstop (mock seat, no egress).
- _Note: "no non-Bash seat may convene until this lands" is a **Phase-1 gate
  precondition** (nothing goes live in Phase 0), not a Phase-0 deliverable._

### Commit 5 — orchestrator multi-shape switch (ATOMIC) (§2/§Fail-open/§EDIT/§Migration) · `hooks/thing-orchestrator.sh`, `hooks/hooks.json` (+ `.claude/settings.json` dev-mirror)

All of the following land together so there is no intermediate fail-open:
- Keep the no-toggle `grep` short-circuit FIRST (opted-out consumers pay nothing).
- Read `tool_name` + `tool_input` generically; pipe the tool-call JSON to
  `thing-decision.py classify-payload` **via stdin**.
- **Remove the `tool_name!=Bash` first-gate**; run the self-disable screen FIRST
  for every shape (text → `screen_always`; file → `screen_substrate_path`) above
  the per-category enabled gate. A `comfort-posture.yaml` write is screened by
  parsing the RESULTING YAML; unparseable → DENY.
- Per-shape extraction-failure → DENY for a toggled category (the §Fail-open table,
  row by row: empty hook stdin → allow; new-shape extraction-fail → DENY;
  `classify_payload`→None but a matcher matched → DENY).
- Coerce a non-Bash seat `verdict:"edit"` → `deny` BEFORE `emit_edit` (`:497`) is
  reachable (the aggregator at `:354`/`:368`).
- **Widen the matcher** → `Bash|Write|Edit|MultiEdit|WebFetch|WebSearch|mcp__.*`
  (plugin canonical `hooks.json` AND the `.claude/settings.json` dev-mirror).
- **Gates** (in Commit 7): opt-out (`Write`, no posture → exit 0, **no python
  call**); extraction-fail (toggled) → deny; EDIT coercion → deny not updatedInput;
  the self-disable-via-shape matrix.

### Commit 6 — serialization (§Serialization) · `thing-orchestrator.sh`, `thing-decision.py`

- Per-shape Sága `tool_input` at **ALL THREE** write sites (gap P1-7): the
  self-disable early-write (`:107`), the **hard-rule early-write (`:131`)**, and the
  main write (`:455`) — each must emit the shape-appropriate `tool_input` (Bash
  `{command}`; file `{file_path, content_sha256, bytes}`; network `{url}`; MCP
  `{name, args_sha256}`), never a hardcoded `{command}` for a non-Bash hit.
- Cache `identity` via ONE shared helper at the read (`:201`) AND write (`:466`)
  sites; key = `shape|identity|category|config_hash`. file = `realpath` +
  `sha256(content|edits)`; network = full URL; MCP = `server__verb` +
  `sha256(canonical-json(args))`.
- **Gate**: cache non-collision (two payloads, same category, differ only by
  `identity` → two keys; second not served the first's verdict).

### Commit 7 — Gates 24+ + Bash-regression proof + migration (§Gate matrix/§Bash-regression/§Migration/§schema_version) · `scripts/audit-gates.sh`, `CLAUDE.md`

- New **Gate 24+** (Gate 23 is the current last) per-phase matrix, CI-safe via
  `THING_SEAT_MOCK_VERDICT`, **bidirectional** (each fails-on-bad AND passes-on-good
  — gap P1-5): (a) clean→allow, (b) concerning→deny, (c) unparseable/empty→deny,
  (d) self-disable-via-shape incl. **hardlink** + **`..`/symlink**, (e) cache
  non-collision, (f) MultiEdit edit#2→substrate → whole call deny **AND malformed
  `edits[]` under an UNtoggled-unmatched tool → exit 0** (the opt-out half),
  (g) EDIT coercion, (h) seat egress backstop, **(i) opt-out: `Write` with no
  posture file → exit 0 with no python call** (the §Migration fixture).
- **Assert Gate 14 + Gate 15 pass with ZERO fixture edits** — the Bash-regression
  guarantee.
- Run the AGENTS.md `.repo-layout.json` verification snippet (no new dirs expected).
- `CLAUDE.md` migration note (widened matcher is consumer-visible; grep
  short-circuit keeps opted-out at zero cost). `schema_version` bump not required.
  Version bump `plugin.json` + `marketplace.json`.

## Risks & guarantees

- **Bash regression** (shared `screen_always` + seat become payload-shaped) → proof:
  Gate 14/15 unchanged.
- **Matcher-widening cost** → grep short-circuit first; a fixture proves opted-out
  zero-cost.
- **Path canonicalization** → TOCTOU accepted; inode set best-effort; mis-class only
  bumps tier.

## Sequencing

This PR = **Phase 0 only**. Then Phase 1 `file_edit_project` (live, ALLOW/DENY) →
Phase 2 reads + `file_edit_global` → Phase 3 WebFetch/WebSearch (adds `WebSearch`
to EMISSIONS `network_read`) → Phase 4 MCP (verb-based + `mcp.allowed_servers`
allowlist; author the 5 `mcp_tools` concern triggers first). Each later phase that
widens behavior carries its own migration note.

## Open decisions (recommendations marked; pending owner confirmation)

1. **Phase 0 as one PR vs split at C4/C5.** _Recommend ONE PR_ — the Bash-regression
   proof (Gate 14/15 parity) lands in a single `audit-gates.sh` run, and a split
   risks an intermediate where the matcher is widened (C5) before gates land (C7).
2. **Cap values.** _Recommend the design defaults_ (`SCREEN_MAX_BYTES`=1 MiB,
   `SEAT_MAX_BYTES`=64 KiB, `DECODE_MAX_BYTES`=256 KiB) — documented + tunable later;
   no live traffic in Phase 0 to tune against.
3. **`classify-payload` input transport.** _Recommend stdin_ — argv breaks on a
   1 MiB `Write.content` (`ARG_MAX`); stdin is the only safe path for large content.
4. **MCP verb classification in Phase 0 vs Phase 4.** _Recommend A (verb set now)_ —
   ship the read-verb prefix set in Commit 1 so `CLASSIFY_PAYLOAD_VERSION` is stable
   across phases (no cache-invalidating re-bump when verbs land); allowlist +
   triggers stay Phase 4.
5. **Collapse the triplicated live-list now?** _Recommend DEFER_ — no new shape in
   Phase 0 needs it; collapsing is scope-creep. Track as a follow-up.
6. **EDIT-coercion in Phase 0?** _Recommend KEEP_ — the seam is Bash-only-reachable
   today (dead until a non-Bash seat exists), but it's cheap and the design wants it
   gated as a prerequisite; future-proofs Phase 1.

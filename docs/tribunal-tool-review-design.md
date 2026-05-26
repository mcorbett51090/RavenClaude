# Tribunal tool-review extension — design & phasing

> **Status:** design, v2 (architect + security reviewed 2026-05-26).
> **Score: 5/10 as first drafted → this revision fills the gaps below.** Two
> independent expert reviews (security rigor + completeness/shippability) both
> scored the v1 draft 5/10 and returned the same verdict: the architecture is
> right, but the "near-free pre-phase," "phases are independent," and "Bash path
> byte-for-byte unchanged" claims were false, and three **P0 silent-bypass** gaps
> made Phase 1 unsafe as written. This v2 incorporates every finding.
>
> This extends the command-review tribunal ("the Thing") from **Bash-only**
> review to the **file (Edit/Write/MultiEdit), network (WebFetch/WebSearch), and
> MCP** tool shapes. Companion to
> [`tribunal-review-feature-design.md`](tribunal-review-feature-design.md) and the
> [`thing` skill](../plugins/ravenclaude-core/skills/thing/SKILL.md).

## Review findings — what changed from v1

| # | Severity | Finding | Resolution in this doc |
|---|---|---|---|
| P0-1 | silent bypass | `classify()` is built on a Bash-only matcher (`thing-decision.py:110,124`) that drops `Edit/Write/MCP/WebSearch` emissions → returns `None` → orchestrator treats as "not enabled" → **exit 0 (allow)**. A category shows "reviewed" but never convenes a panel. | New **Engine Foundation §** — a `classify_payload(tool_name, tool_input)` that does NOT reuse `_command_prefixes()`; fixture proves every new tool name → non-None category. |
| P0-2 | silent bypass | Orchestrator's `[ "$tool_name" != "Bash" ] && exit 0` (`thing-orchestrator.sh:68`) sits **above** the self-disable screen, and that screen matches shell verbs against a command string (`concerns-catalog.md:165`). A `Write` to `thing-orchestrator.sh` matches no trigger → Phase 1 would **open** a new self-disable vector. | Engine Foundation §: self-disable screen runs **above any tool-name gate**, on a normalized edit-target path; new path-trigger family. |
| P0-3 | silent bypass | Secret backstop (`thing-seat.sh:67`) + injection screen are command-string-shaped; a `Write` whose `content` carries a key + "ignore previous instructions" can reach `claude -p` unscreened. | Engine Foundation §: deterministic screen runs on the **full reviewed payload before any seat**, with a size cap + "truncation never reduces what is screened." |
| P0-4 | won't ship | **Pre-phase is NOT free** — all 14 `slm.*`/`spi.*` concerns lack triggers AND `judgment_only` (`concerns-catalog.md:424-468,589-619`); Gate 21 #17 would fail. | Pre-phase rewritten below to own the 14-concern authoring with a per-concern disposition table. |
| P0-5 | won't ship | **"Gate 23" is already taken** (Learn-tab concept pipeline, `audit-gates.sh:785`). | New fixtures are **Gate 24+**. |
| P1-1 | fail-open | Empty/unparseable payload hits `[ -z "$cmd" ] && exit 0` (`:71`) = **allow**. A refactor bug degrades Bash to silent allow. | Per-shape extraction-failure branch **emits DENY** for a toggled category; `exit 0` kept only for genuinely-unmatched tools. Fuzz fixture per tool name. |
| P1-2 | tier bypass | project↔global via realpath is classify-time only → symlink/`..`/TOCTOU/case-fold downgrades `file_edit_global`→`project`. | Deny on lexical `..`/`~`; treat symlink targets as global/escalated; **mis-classification may only bump tier, never skip the screen.** |
| P1-3 | spoofing | MCP routing trusts the `mcp__server__verb` name string; `mcp__github__delete_repo` from a typosquatted server is classified by string. | Phase 4 needs a server allowlist/identity check; unconventional verbs default to write/surfaced. |
| P1-4 | shared refactor | Self-disable extension touches `screen_always` (`thing-concerns.py:236`), shared with the Bash path — so Phase 1 is **not** independent of Bash code. | "Byte-for-byte unchanged" claim corrected; self-disable refactor is an explicit Engine-Foundation prerequisite, regression-gated by Gate 14/15 parity. |
| P2 | hardening | MultiEdit `edits[]` per-edit screen; Sága log hardcodes `tool_name:"Bash"`/`{command}` (`:111,438`); cache key `cmd\|category\|config_hash` has no path (`:201`); EDIT-deferral residual risk; WebFetch `prompt` vs `xc.injection-attempt` being `pre_llm_deny`. | Addressed in Payload §, Security §, and Open Decisions below. |

## Core structural finding

Every layer is hardwired to a Bash **command string**: `thing-orchestrator.sh`
gates on `tool_name=="Bash"` + `tool_input.command`; `thing-decision.py
classify()` parses only `Bash(...)` EMISSIONS; `thing-concerns.py` regexes match a
command string and the EDIT-safety invariant re-runs them on a rewritten command;
`thing-seat.sh` wraps "the command." The extension introduces a **`payload`
abstraction** (reviewed text/fields + a shape tag) threaded through every layer.
**Correction to v1:** the Bash path is unchanged *in behavior*, but the
self-disable screen (`screen_always`) is genuinely **shared** and must be
refactored to be payload-shaped — so Bash-path regression is a real risk and is
gated by Gate 14/15 parity, not assumed away.

## Engine Foundation (Phase 0) — prerequisites before ANY category goes live

These three mechanisms are shared by all shapes and **must land + be fixture-gated
before** the pre-phase or Phase 1, because each is a silent-bypass otherwise:

1. **`classify_payload(tool_name, tool_input) → category`** (P0-1). A new
   classifier that maps tool shape → comfort-posture category, NOT built on
   `_command_prefixes()`. Bash delegates to the existing path; `Edit/Write/
   MultiEdit/Read` → file_* by path (see §realpath); `WebFetch/WebSearch` →
   `network_read`; `mcp__*` → `mcp_tools`. Note `mcp_tools` EMISSIONS is empty
   `[]` and `network_read` lists only `WebFetch` (not `WebSearch`) — classification
   for these is **name-keyed, not EMISSIONS-keyed.** Fixture: every supported tool
   name yields a non-`None` category.
2. **Self-disable screen above any tool gate, path-aware** (P0-2, P1-4). Remove
   the `tool_name != "Bash"` early-return as the first gate; run
   `xc.tribunal-self-disable` (`always_screen`) on a **normalized edit-target
   path** for file shapes, against a new path-trigger family covering: the
   substrate dirs (`plugins/ravenclaude-core/hooks/`, `/scripts/`), `thing.yaml`,
   `comfort-posture.yaml` (any write flipping `thing:`/`command_review:`/
   `gate_floor:`), `generate-dashboards.py`, the concern catalog itself, **and the
   `realpath` of the target** (catch a project symlink pointing into the
   substrate). Category-independent (fires even when file categories are off).
3. **Screen the full payload locally before any seat** (P0-3). `evaluate` +
   `screen_always` + the secret backstop run on the **entire** reviewed payload
   (file content, URL, MCP args) before `claude -p` is ever invoked. Explicit
   size cap; rule: **truncation may only shrink the seat prompt, never what the
   local screen inspects.** base64-decode pass runs over content too.

**Fail-closed contract (P1-1):** for a *toggled* category, an extraction or
classify failure **emits DENY**. The legacy `[ -z "$cmd" ] && exit 0` fall-through
is fail-OPEN and must not be inherited by new shapes.

## Per-tool-shape design

Orchestrator hooking: extend the existing `PreToolUse` matcher to
`Bash|Write|Edit|MultiEdit|WebFetch|WebSearch|mcp__.*`.

| Tool | Payload reviewed | Category | EDIT (rewrite)? | Read? |
|---|---|---|---|---|
| Bash | `command` | EMISSIONS (unchanged) | yes (unchanged) | shell_readonly |
| Edit/MultiEdit | path + diff (`old/new_string`, or `edits[]` serialized) | `file_edit_project`/`_global` by realpath | **defer** — ALLOW/DENY-only v1 | no |
| Write | path + `content` | same | defer | no |
| Read | path | `file_read_project`/`_global` | n/a | **yes** |
| WebFetch / WebSearch | `url`+`prompt` / `query` | `network_read` | **no** | **yes** |
| MCP (`mcp__*`) | tool name + args | `mcp_tools` (read/write by verb) | defer to v2 | verb-based |

**Payload serialization (P1, P2)** — the doc must pin a canonical serialization
because the cache key and Sága log assume a single string:
- **Cache key** becomes `shape|identity|category|config_hash`, where `identity` =
  the command (Bash), the realpath + a content hash (file), the URL (network), or
  `server__verb` + an args hash (MCP). (Today: `cmd|category|config_hash`,
  `:201,466` — no path, so two files would collide.)
- **Sága log** (`:111,438`) must record the real `tool_name` + a shape-appropriate
  `tool_input`, never a fabricated `{command}` — else forensics + the
  `#10 no-unrecorded-allow` downgrade key off a lie.
- **`emit_edit`** (`:54`) becomes shape-aware (`{new_string}`/`{edits}`/`{content}`).
- **MultiEdit** `edits[]`: screen **per-edit**; deny the whole call if **any**
  edit hits the substrate or a secret/injection trigger.

`is_read` already lists `file_read_*` + `network_read`, so reads-never-surfaced
works once `classify_payload` returns those categories.

## Security must-haves

1. **Self-disable** — see Engine Foundation #2 (the #1 finding; naïve extension
   *opens* a vector, so it is a hard prerequisite, not a Phase-1 nicety).
2. **Fail-closed per shape** — Engine Foundation fail-closed contract.
3. **Injection + secret over content/URL/args** — Engine Foundation #3.
4. **realpath hardening (P1-2)** — classify on realpath; **deny** lexical `..`/`~`;
   symlink targets → treat as global/escalated; mis-classification may only bump
   tier, never skip the screen (so `file_edit_project` still runs the full
   concern screen — a wrong project call costs a tier, not a bypass).
5. **MCP identity (P1-3)** — server allowlist; unconventional verbs default to
   write/surfaced (see Open Decision 3).
6. **No Bash regression** — Gate 14/15 fixtures pass unchanged + a fuzz fixture
   feeds malformed `tool_input` per tool name asserting DENY (toggled) / allow
   (untoggled-unmatched).

## Phasing

> **Two parallel tracks (owner decision 2026-05-26).** Track A and Track B share
> no code and can proceed concurrently (at the cost of two concurrent
> security-review PRs):
>
> - **Track A — Pre-phase only.** Author the 14 `slm.*`/`spi.*` concerns + flip
>   the 2 Bash categories live. Self-contained: needs **no** Engine Foundation
>   (it's pure Bash, already classified). Ships independently.
> - **Track B — Engine Foundation (Phase 0) → Phase 1 → 2 → 3 → 4.** Engine
>   Foundation lands first and gates everything in this track.

- **Pre-phase (Track A) — flip `shell_local_mutate` + `shell_package_install`
  live. NOT free (P0-4):** requires authoring all 14 concerns to satisfy Gate 21 #17
  (triggers OR `judgment_only`), a security-reviewed constitution change with new
  regexes that must pass Gate 16 (compile) + new Gate 21 FP/FN corpus cases.
  Per-concern disposition (final call is part of the PR's security review):

  | Disposition | Concerns |
  |---|---|
  | **Regex triggers** | `slm.rm-without-trash`, `slm.git-reset-hard-uncommitted`, `slm.chmod-broad`, `slm.delete-protected-branch-locally`, `spi.global-install`, `spi.no-pinned-version`, `spi.local-tarball-from-tmp`, `spi.private-registry-leak` |
  | **`judgment_only`** (needs worktree/package state, not regex-able) | `slm.checkout-orphans-staged`, `slm.commit-without-staging-review`, `slm.mv-across-fs-boundary`, `slm.merge-or-rebase-with-uncommitted`, `spi.typosquat-risk` (Levenshtein corpus), `spi.post-install-script-risk` (package DB) |

- **Phase 1** — file Edit/Write/MultiEdit (**project**). ALLOW/DENY-only. Depends
  on all of Engine Foundation. Highest security value (closes self-disable hole).
- **Phase 2** — `file_edit_global` + `file_read_project`/`_global` (reads, cheap).
- **Phase 3** — WebFetch/WebSearch → `network_read` (ALLOW/DENY-only, read tier).
- **Phase 4** — MCP tools (verb-based read/write + server identity; ALLOW/DENY
  first, arg-narrowing EDIT later — note the `revalidate` invariant has no
  non-command mode, so "arg-narrowing EDIT" needs a verifier that doesn't exist
  yet).

**Per-phase Gate matrix (Gate 24+, CI-safe via `THING_SEAT_MOCK_VERDICT`)** — each
category ships with **all four**: (a) clean → allow, (b) concerning → deny, (c)
**unparseable/empty payload → deny** (fail-closed), (d) **self-disable via the
shape** (e.g. `Write` to `thing-orchestrator.sh` → deny *even with the category
off*). Existing Gate 14/15 Bash fixtures must pass unchanged.

## Go-live surface area (per category) — the full checklist

Beyond the engine, flipping a category live touches:
`generate-dashboards.py` `THING_LIVE_CATEGORIES` (`:973`) **and** the prose in
`_render_thing_preview` ("Live for three categories", `:497`) **and**
`_render_thing_toggle` copy; regenerate `dashboard.html` (Gate 13 freshness);
`SKILL.md` (description, Categories row, the "No file-edit review" caveat);
`plugins/ravenclaude-core/CLAUDE.md` ("T3 is live for…" paragraph); version bump
in `plugin.json` **and** `marketplace.json` (Gate 8 cross-check); regenerate
repo-guide + copilot (Gate 11, Gate 20 freshness). `thing.yaml` already lists all
12 categories in `category_tier_map` — no change.

## Resolved decisions (owner, 2026-05-26)

1. **EDIT-rewrite for file content → ALLOW/DENY-only v1.** Defer the rewrite.
   Accepted residual risk: the machine-checked `concerns(revised) ⊆
   concerns(original)` invariant does **not** exist for file content — a seat's
   reasoning + the DENY path are the only screen on edit content.
2. **URL/MCP EDIT disabled** (no verifiable rewrite) — consistent with #1.
3. **MCP unknown/unconventional verb → classify as WRITE at an escalated tier**
   (surfaces for review), never a silent read. (The v1 "deny-write vs ask"
   framing was moot — reads are never surfaced and `mcp_tools` base tier is
   `medium`, `thing-decision.py:361`; the real lever is `is_read` + tier, set
   here to write/escalated.) Phase 4 also adds the server allowlist (P1-3).
4. **WebFetch → review the URL only, not the `prompt`.** Rationale: the actual
   prompt-injection-via-fetch threat is the *fetched content* reaching the model
   **after** the fetch, which a PreToolUse screen cannot observe; the `prompt`
   field is our own instruction to the summarizer, so screening it yields false
   `pre_llm_deny` hard-denies (no appeal) without catching the real threat. The
   URL screen covers SSRF, cloud-metadata endpoints, `localhost`, and
   credential-in-URL.

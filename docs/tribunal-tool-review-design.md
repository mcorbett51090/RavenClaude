# Tribunal tool-review extension — design & phasing

> **Status:** design, **v3** (4 independent expert reviews total). v1 scored 5/10;
> v2 filled those gaps; two further independent reviews (security-rigor, shippability)
> scored v2 **6.5/10** and **7/10**. This v3 closes every finding from that second
> round and is the intended **9/10** pre-execution baseline.
>
> This extends the command-review tribunal ("the Thing") from **Bash-only** review
> to the **file (Edit/Write/MultiEdit), network (WebFetch/WebSearch), and MCP**
> tool shapes. Companion to
> [`tribunal-review-feature-design.md`](tribunal-review-feature-design.md) and the
> [`thing` skill](../plugins/ravenclaude-core/skills/thing/SKILL.md).

## What changed in v3 (the second-round gap closure)

| # | Sev | Finding (reviewer) | Resolution in v3 |
|---|---|---|---|
| V3-1 | P0 | **Stale premise:** v2's P0-4 claimed the 14 `slm.*`/`spi.*` concerns were unauthored. They are now **authored + verified** ([PR #104](https://github.com/mcorbett51090/RavenClaude/pull/104) on this branch). | P0-4 marked RESOLVED; **Track A re-scoped to flip-only** (§Phasing). |
| V3-2 | P0 | Path normalization was hand-waved ("normalized edit-target path") — no realpath/`..`/casefold/Unicode/Windows/hardlink/TOCTOU spec. | New **Engine Foundation §4 — Path canonicalization spec** (concrete algorithm). |
| V3-3 | P0 | Substrate set incomplete + triplicated; misses `apply-comfort-posture.py`, the catalog itself, the generator live-list, the `serve-dashboards.py` mirror. | New **§2a — Substrate set (exhaustive, single source)**; `comfort-posture.yaml` screened by parsing the *resulting* YAML, not regex. |
| V3-3 | P0 | Full-payload screening never reconciled with the seat's **command-only egress backstop** (`thing-seat.sh:49,67-86`) — never-egress guarantee void for non-Bash. | New **§3a — payload-shaped seat + egress backstop**; no non-Bash seat may convene until it lands. |
| V3-4 | P1 | EDIT-deferral asserted, not proven against the `verdict="edit"` → `emit_edit` code path. | **§EDIT coercion** — aggregator coerces seat-`edit`→`deny` before `emit_edit` for any non-Bash shape; gated. |
| V3-5 | P0 | `WebSearch` is absent from EMISSIONS entirely (`apply-comfort-posture.py:204`); the network read/write split the doc assumed doesn't exist in the source of truth. | **§classify_payload** + Phase 3 adds `WebSearch` to EMISSIONS `network_read` (keep one source of truth). |
| V3-6 | P1 | Size-cap/base64 rule imprecise. | **§Payload caps** — `SCREEN_MAX_BYTES`/`SEAT_MAX_BYTES` pinned; oversize → DENY; base64 run-cap. |
| V3-7 | P1 | Sága-log & cache-key serialization sketchy; cache collision untested. | **§Serialization** — per-shape Sága `tool_input` table + `identity` spec + shared helper + a cache-collision gate case. |
| V3-8 | P1 | Fail-open fall-throughs not enumerated; `_screen_always` except-branch fails OPEN. | **§Fail-open enumeration table**; `_screen_always` except-branch fails CLOSED on a substrate target. |
| V3-9 | P1 | MCP server identity/verb classification under-specified. | **§MCP identity** — allowlist in `thing.yaml`, fixed read-verb set, author `mcp_tools` concern triggers before live. |
| V3-10 | P1 | Track A/B "share no code" false — 5 contended files. | **§Track sequencing** — A merges first, B rebases; second-merger regenerates. |
| V3-11 | P2 | Go-live checklist incomplete (SKILL.md multi-site, dashboard hardcoded count); no per-phase migration note; Bash-regression not a gate obligation; `schema_version`. | **§Go-live**, **§Migration**, **§Bash-regression**, **§schema_version**. |

## Review findings — v1 → v2 (history; still in force)

| # | Severity | Finding | Resolution |
|---|---|---|---|
| P0-1 | silent bypass | `classify()` is Bash-only (`thing-decision.py:110,124`) → new tools return `None` → orchestrator treats as "not enabled" → exit 0 (allow). | **Engine Foundation §1** — `classify_payload`. |
| P0-2 | silent bypass | Orchestrator's `tool_name != "Bash"` early-return (`thing-orchestrator.sh:68`) sits **above** the self-disable screen. | **§2** — self-disable runs above any tool-name gate. |
| P0-3 | silent bypass | Secret backstop + injection screen are command-string-shaped; a `Write` content blob reaches `claude -p` unscreened. | **§3 / §3a** — full-payload local screen + payload-shaped backstop. |
| P0-4 | won't ship | 14 `slm.*`/`spi.*` concerns lacked triggers AND `judgment_only`. | **RESOLVED (v3): authored + verified in PR #104.** |
| P0-5 | won't ship | "Gate 23" already taken (`audit-gates.sh:785`). | New fixtures are **Gate 24+**. |
| P1-1 | fail-open | Empty/unparseable payload hits `[ -z "$cmd" ] && exit 0` (`:71`) = allow. | Per-shape extraction-failure **DENY** for a toggled category (see §Fail-open table). |
| P1-2 | tier bypass | project↔global via realpath classify-time only → symlink/`..`/TOCTOU/case-fold downgrade. | **§4** path canonicalization; mis-classification may only bump tier, never skip the screen. |
| P1-3 | spoofing | MCP routing trusts the `mcp__server__verb` string. | **§MCP identity** — allowlist + verb set. |
| P1-4 | shared refactor | Self-disable extension touches shared `screen_always`. | **§Bash-regression** — Gate 14/15 green with zero fixture edits. |
| P2 | hardening | MultiEdit per-edit; Sága hardcodes `Bash`/`{command}`; cache key has no path; WebFetch `prompt` vs `pre_llm_deny`. | §Serialization, §Gate matrix, Resolved decision 4. |

## Core structural finding

Every layer is hardwired to a Bash **command string**: `thing-orchestrator.sh` gates
on `tool_name=="Bash"` + `tool_input.command`; `thing-decision.py classify()` parses
only `Bash(...)` EMISSIONS; `thing-concerns.py` regexes match a command string and
`revalidate` re-runs them on a rewritten command; **and `thing-seat.sh` wraps a single
`THING_CMD`, with its egress secret backstop (`:67-86`) scanning only that string.**
The extension introduces a **`payload` abstraction** (a shape tag + the reviewed
text/fields) threaded through *every* layer including the seat wrapper. The Bash path
is unchanged in behavior, but `screen_always` and the seat backstop are genuinely
**shared** and must become payload-shaped — so Bash regression is a real risk, gated
by Gate 14/15 parity (§Bash-regression), not assumed away.

## Engine Foundation (Phase 0) — prerequisites before ANY new shape goes live

These mechanisms are shared by all shapes and **must land + be fixture-gated before**
Phase 1, because each is otherwise a silent bypass.

### §1 — `classify_payload(tool_name, tool_input) → category | None`
A new classifier, **not** built on `_command_prefixes()`. Bash delegates to the
existing `classify()`. Otherwise, name-keyed:
- `Edit | Write | MultiEdit` → `file_edit_project` / `file_edit_global` by the
  canonicalized path (§4).
- `Read` → `file_read_project` / `file_read_global` by path.
- `WebFetch | WebSearch` → `network_read`. **Note:** `WebFetch` is in EMISSIONS
  `network_read`; **`WebSearch` is absent from EMISSIONS entirely** and
  `network_write` is Bash-curl-shaped (`apply-comfort-posture.py:204-209`). To keep
  the classifier and the permission translator from drifting, **Phase 3 adds
  `WebSearch` to the EMISSIONS `network_read` list** (the single source of truth) —
  it is not hard-coded only in `classify_payload`.
- `mcp__*` → `mcp_tools`, read/write by verb (§MCP identity).

`mcp_tools` EMISSIONS is empty `[]`; classification for MCP + network is name-keyed,
not EMISSIONS-prefix-keyed. **Fixture:** every supported tool name yields a non-`None`
category.

### §2 — Self-disable screen above any tool gate, path-aware
Remove the `tool_name != "Bash"` early-return as the first gate. Run
`xc.tribunal-self-disable` (`always_screen`) **first**, for every tool shape, against
the canonicalized target (§4) for file shapes. Category-independent: it fires even
when the file categories are off, and (per §Fail-open) even when `_screen_always`
itself throws on a substrate target.

### §2a — Substrate set (exhaustive, single source of truth)
The self-disable screen for **file shapes** fires when the canonicalized target *is*,
or is *under*, any of:

```
plugins/*/hooks/                              # orchestrator + adapters + all hooks
plugins/*/scripts/thing-*.{py,sh}             # decision/concerns/seat/decide
plugins/*/scripts/apply-comfort-posture.py    # the EMISSIONS source — breaks classify if rewritten
plugins/*/scripts/serve-dashboards.py         # served dashboard copy
plugins/*/knowledge/concerns-catalog.md       # the catalog the screen itself reads
scripts/generate-dashboards.py                # the dashboard + THING_LIVE_CATEGORIES generator
.ravenclaude/thing.yaml                        # advanced seat/tier config
```

Plus: a Write/Edit to `.ravenclaude/comfort-posture.yaml` is a self-disable **iff the
resulting document** flips `thing:` off for a live category, or alters
`command_review:` / `gate_floor:`. Because a `Write` replaces the whole file, screen
the **parsed YAML of the new content**, not a regex over it (a regex over content is
trivially evaded by reformatting).

**Single source:** this set lives in ONE constant (e.g. `THING_SUBSTRATE` in
`thing-concerns.py`) imported by the screen. The separately-triplicated *live-category*
list (`generate-dashboards.py:973` `THING_LIVE_CATEGORIES`, the Gate 21 #17 hardcode at
`audit-gates.sh:692`, and the Gate 15 fixtures) is its own drift hazard — §Go-live
requires all three move together; a follow-up should collapse them to one source too.

### §3 — Screen the full payload locally before any seat
`evaluate` + `screen_always` + the secret/injection screen run on the **entire**
reviewed payload (file content, URL, MCP args) before `claude -p` is ever invoked. The
base64-decode pass (`thing-concerns.py:99-131`) runs over content too.

### §3a — Payload-shaped seat + egress backstop (the never-egress fix)
The seat wrapper (`thing-seat.sh`) and its egress secret backstop (`:67-86`) currently
read `THING_CMD` and scan only that command string. For file/network/MCP, a secret in
`Write.content` (or a URL, or MCP args) would reach `claude -p` **unscanned** — the
never-egress guarantee (design §B.9.4) is silently void. Fix: the wrapper takes a
`THING_PAYLOAD` (shape tag + reviewed text); the backstop's secret ERE runs over the
**full reviewed text**, not just a command. **Until this lands, no file/network/MCP
category may convene a seat** — the deterministic full-payload screen + ALLOW/DENY-only
is the only permitted path. **Gate:** a secret embedded in `Write.content` is denied by
the backstop (mock seat, asserts no egress).

### §4 — Path canonicalization spec
Every file-shape target is normalized as:
1. **Reject** (DENY, toggled category) if the raw path string contains `..` as any
   segment or a leading `~`. (Lexical traversal is never legitimate for a reviewed
   write and defeats realpath ordering.)
2. `os.path.realpath()` against the consumer cwd; on case-insensitive platforms,
   compare case-folded.
3. **NFC-normalize** before any substring/glob match (defeats NFC/NFD Unicode
   equivalence evasion).
4. On Windows: strip a `\\?\` prefix, **reject** an `::` ADS suffix
   (`file.sh::$DATA`), and resolve 8.3 short names (`GetLongPathName`).
5. Self-disable matching (§2a) runs against the **lexical target AND its realpath AND
   `os.stat().st_ino` membership** in a precomputed inode-set of substrate files —
   realpath does *not* resolve a hardlink, so the inode check is what closes a hardlink
   to `thing-orchestrator.sh`.
6. **TOCTOU is accepted, explicitly:** a PreToolUse hook cannot lock the filesystem
   between classify-time and write-time, so the screen is advisory and the inode check
   is best-effort at hook time. We accept this because the alternative (FS lock) is not
   available to a hook; the residual is a narrow race, not a standing bypass.
7. **Mis-classification may only bump the tier, never skip the screen.** A path that
   ambiguously resolves is treated as `file_edit_global` (the stricter tier); a wrong
   *project* call costs a tier, never a screen.

### §Payload caps
- The local screen scans up to **`SCREEN_MAX_BYTES = 1 MiB`** of reviewed text in full.
  A payload larger than that **DENIES** for a toggled category (cannot fully screen →
  fail closed) — it does **not** truncate-then-screen.
- The seat prompt is independently capped at **`SEAT_MAX_BYTES = 64 KiB`** with a
  `[truncated]` marker. **Truncation applies only to the seat prompt, after the local
  screen has already run on the full ≤1 MiB text** — it never shrinks what the local
  screen inspects.
- The base64 decode pass caps at the **first 200 candidate runs** per payload (a large
  file has many `[A-Za-z0-9+/]{24,}` runs; this bounds the quadratic).

### §Fail-open enumeration table
Every `exit 0` / fallback is tabulated; for a *toggled* category every row resolves to
a verdict, never a silent allow.

| Location | Shape | Toggled? | v3 verdict |
|---|---|---|---|
| `orchestrator:46` empty hook stdin | any | — | allow (malformed hook input only) |
| `orchestrator:68` `tool_name!=Bash` | non-Bash | — | **REMOVED** — replaced by `classify_payload` + §2 |
| `orchestrator:79` short-circuit grep (no category toggled) | any | none | allow — opted-out consumers pay nothing (kept; §Migration) |
| `orchestrator:120` `enabled!=true` | matched | that cat off | allow — **but §2 self-disable already ran above this** |
| `orchestrator:71` `[ -z "$cmd" ]` | Bash | on | allow (Bash unchanged) |
| extraction-fail (new shapes) | file/net/MCP | on | **DENY** |
| `classify_payload`→None but tool matched a new matcher | new | on | **DENY** |
| `thing-decision.py:83` `_route` except | any | on | full panel (safe) |
| `thing-decision.py:96/106` `_screen_always` except | any | on | **fail CLOSED to self-disable-DENY when the target is a substrate path** (today returns no-deny) |

Only a genuinely unmatched tool name with **no** category toggled may fail open.

## Per-tool-shape design

Orchestrator hooking: extend the `PreToolUse` matcher to
`Bash|Write|Edit|MultiEdit|WebFetch|WebSearch|mcp__.*`.

| Tool | Payload reviewed | Category | EDIT? | Read? |
|---|---|---|---|---|
| Bash | `command` | EMISSIONS (unchanged) | yes (unchanged) | shell_readonly |
| Edit/MultiEdit | path + diff (`old/new_string`, or `edits[]`) | `file_edit_project`/`_global` (§4) | **no — ALLOW/DENY v1** | no |
| Write | path + `content` | same | no | no |
| Read | path | `file_read_project`/`_global` | n/a | **yes** |
| WebFetch / WebSearch | `url` (not `prompt` — decision 4) / `query` | `network_read` | **no** | **yes** |
| MCP (`mcp__*`) | tool name + args | `mcp_tools` (read/write by verb) | **no** v1 | verb-based |

### §EDIT coercion (proving the deferral airtight)
The orchestrator's `verdict="edit"` branch (`emit_edit`, `thing-orchestrator.sh:54`)
is reached whenever a **seat** returns `edit`. For any shape **!= Bash**, the aggregator
**coerces a seat `verdict:"edit"` to `deny`** (reason: "EDIT unsupported for this
shape") *before* the `emit_edit` path — `emit_edit` is never reached for non-Bash.
**Gate:** a payload-shape seat returning `edit` (mock) yields a `deny` decision, never
an `updatedInput`.

### §Serialization (Sága log + cache key)
**Sága `tool_input` per shape** (BOTH write sites — the self-disable early-write
`:111` and the main write `:438` — change; never a fabricated `{command}`):

| Shape | logged `tool_input` |
|---|---|
| Bash | `{command}` |
| Edit/MultiEdit | `{file_path, edits:[{old,new}]}` (content-hash if size-capped) |
| Write | `{file_path, content_sha256, bytes}` (never the full content) |
| network | `{url}` (never `prompt`) |
| MCP | `{name, args_sha256}` |

**Cache `identity`** (the key becomes `shape|identity|category|config_hash`, built by
**one shared helper** used at both the read `:201` and write `:466` sites so they can't
drift):
- file = `realpath` + `sha256(content | edits)`
- network = full URL
- MCP = `server__verb` + `sha256(canonical-json(args))`

`config_hash` (`thing-decision.py:565`) must additionally fold in **a hash of the §2a
substrate set + a `classify_payload` version tag**, so a cached file verdict is
invalidated when the substrate set or classifier changes.

### §MCP identity
- Server allowlist lives in `.ravenclaude/thing.yaml` `mcp.allowed_servers:`. Absent ⇒
  every server is `unverified` ⇒ write-tier / surfaced.
- Verb classification: a fixed read-verb prefix set
  (`get_ list_ read_ search_ describe_ fetch_`) ⇒ read; everything else ⇒
  write/escalated (per decision 3).
- A server not on the allowlist, OR a name colliding with another active server, ⇒
  **deny** write verbs (cite `mcp.unverified-server` / `mcp.tool-shadowing`).
- **Author `triggers`/`judgment_only` on all six `mcp_tools` concerns before the
  category goes live** — Gate 21 #17 fails the moment `mcp_tools` joins the live list
  otherwise (same prerequisite Track A satisfied for slm/spi).

## Security must-haves

1. Self-disable above any tool gate, path-aware (§2 / §2a / §4) — the #1 finding.
2. Fail-closed per shape (§Fail-open table).
3. Injection + secret over content/URL/args, including the **seat egress backstop**
   (§3 / §3a).
4. realpath hardening (§4): deny lexical `..`/`~`; symlink/ambiguous → global tier;
   mis-classification only bumps tier.
5. MCP identity (§MCP identity).
6. **No Bash regression** (§Bash-regression).

## Phasing

> **Tracks A and B share no *engine* code, but DO contend on five files** (§Track
> sequencing): `generate-dashboards.py` (`THING_LIVE_CATEGORIES` + the "three
> categories" prose), `SKILL.md`, `CLAUDE.md`, `plugin.json`, `marketplace.json`. They
> are not run truly concurrently to `main`.

- **Pre-phase (Track A) — flip `shell_local_mutate` + `shell_package_install` live.
  Now FLIP-ONLY (V3-1):** the 14 concerns are already authored + Gate-21-#17-clean
  (PR #104). Remaining work: (1) add the two categories to `THING_LIVE_CATEGORIES`
  (`generate-dashboards.py:973`) + the Gate 21 #17 hardcode (`audit-gates.sh:692`) +
  Gate 15 fixtures; (2) extend the Gate 21 corpus with FP/FN cases for the now-live
  regexes (e.g. `slm.rm-without-trash` must not FP on `npm`/`charm`; `spi.global-install`
  `-g`); (3) the full §Go-live surface. **No new constitution authoring** — risk
  profile is "live-flip + corpus," not "security-reviewed regex authoring."
- **Phase 1** — file Edit/Write/MultiEdit (**project**). ALLOW/DENY-only. Depends on
  all of Engine Foundation. Highest security value (closes the self-disable hole).
- **Phase 2** — `file_edit_global` + `file_read_project`/`_global` (reads, cheap).
- **Phase 3** — WebFetch/WebSearch → `network_read` (ALLOW/DENY-only). **Adds
  `WebSearch` to EMISSIONS `network_read`** (V3-5).
- **Phase 4** — MCP tools (verb-based read/write + server identity; ALLOW/DENY).
  Author the 6 `mcp_tools` concern triggers first.

### §Track sequencing (V3-10)
**Track A merges first** (flip-only, smaller). **Track B rebases on it.** Whoever
merges second re-runs `generate-dashboards.py` + repo-guide + copilot regen and
re-asserts Gate 13/11/20/8 before push — because both tracks bump the same
`plugin.json` + `marketplace.json` version field (Gate 8 cross-check fails on drift)
and edit the same dashboard/SKILL/CLAUDE prose. Do **not** run them concurrently to
`main`.

### §Bash-regression (V3-11 / P1-4)
The `screen_always` + seat-wrapper payload-shaping refactor must land in a PR whose
`audit-gates.sh` run shows **Gate 14 + Gate 15 green with zero fixture edits** to those
gates. If a Gate 14/15 fixture *needs* changing, that is by definition a Bash-behavior
change and must be called out as a migration note.

### §Migration (per phase)
Widening the `PreToolUse` matcher is a **consumer-visible behavior change**: the hook
now spawns on Write/Edit/WebFetch/MCP calls for anyone with the Thing enabled — adding
a `grep` short-circuit check (and, only if a category is toggled, a `jq`+`python3`
round-trip) per tool call. **Each phase that widens the matcher carries a migration
note.** Confirm the no-category-toggled short-circuit (`orchestrator:79`, a `grep` over
the posture file) still fires **before** any classify cost for the new shapes — a
fixture asserts a `Write` with no posture file exits 0 with no python call, so an
opted-out consumer pays nothing.

### §schema_version (V3-11)
No `schema_version` bump is required — new categories reuse the existing
`categories.<name>.thing` shape and the `command_review` block. Confirm a current
`thing.yaml` and a `comfort-posture.yaml` with only Bash categories toggled behave
identically post-change (add to the Bash-regression fixture set).

## Per-phase Gate matrix (Gate 24+, CI-safe via `THING_SEAT_MOCK_VERDICT`)

Each category ships with **all of**:
- (a) clean → allow
- (b) concerning → deny
- (c) **unparseable / empty payload → deny** (fail-closed, toggled)
- (d) **self-disable via the shape** (e.g. `Write` to `thing-orchestrator.sh` → deny
  *even with the category off*) — incl. a **hardlink** and a **`..`/symlink** variant
- (e) **cache non-collision** — two distinct payloads in the same category sharing
  everything but `identity` (two file paths; two MCP arg-sets) produce two distinct
  cache keys; the second is NOT served the first's verdict (writes file A → panel-deny
  cached, then file B same category → asserts a fresh panel)
- (f) **MultiEdit** — 3 edits where edit #2 targets `plugins/ravenclaude-core/hooks/`
  → whole call denied; malformed `edits[]` under a toggled category → deny, under an
  untoggled-unmatched tool → exit 0
- (g) **EDIT coercion** — a mock seat returning `edit` on a non-Bash shape → `deny`,
  never `updatedInput`
- (h) **seat egress backstop** — a secret in `Write.content` is denied by the backstop

Existing Gate 14/15 Bash fixtures must pass **unchanged** (§Bash-regression).

## Go-live surface area (per category) — the full checklist

Flipping a category live touches:
- `generate-dashboards.py` `THING_LIVE_CATEGORIES` (`:973`) **and** the hardcoded
  **"three categories" count** in `_render_thing_preview` (`:500` and `:519`) **and**
  `_render_thing_toggle` copy — the count is literal and becomes wrong on the first
  flip, so template it or update it.
- Gate 21 #17 hardcoded live list (`audit-gates.sh:692`) **and** Gate 15 fixtures —
  move with `THING_LIVE_CATEGORIES`.
- `SKILL.md` — **multiple sites**: the `description` frontmatter, the Categories table
  row, the toggle-list prose, and the "No file-edit review" caveat (`:109`). Grep
  `shell_|Bash|file-edit|categories|reviewed` and update every hit.
- `plugins/ravenclaude-core/CLAUDE.md` — the "T3 is live for…" paragraph.
- Version bump in **`plugin.json` AND `marketplace.json`** (Gate 8 cross-check).
- Regenerate `dashboard.html` (Gate 13 freshness), repo-guide (Gate 11), copilot
  (Gate 20).
- `.repo-layout.json` — already covers the affected dirs (no change for the flip; **new
  dirs in later phases must be added first**, per AGENTS.md).
- `thing.yaml` already lists all 12 categories in `category_tier_map` — no change.

## Resolved decisions (owner, 2026-05-26)

1. **EDIT-rewrite for file content → ALLOW/DENY-only v1.** Defer the rewrite. Residual
   risk: the machine-checked `concerns(revised) ⊆ concerns(original)` invariant does
   **not** exist for file content — a seat's reasoning + DENY + §EDIT-coercion are the
   only screen on edit content.
2. **URL/MCP EDIT disabled** (no verifiable rewrite) — consistent with #1.
3. **MCP unknown/unconventional verb → classify as WRITE at an escalated tier** (the
   real lever is `is_read` + tier; `mcp_tools` base tier is `medium`,
   `thing-decision.py:361`). Phase 4 adds the server allowlist (§MCP identity).
4. **WebFetch → review the URL only, not the `prompt`.** The actual
   prompt-injection-via-fetch threat is the *fetched content* reaching the model
   **after** the fetch, which a PreToolUse screen cannot observe; the `prompt` field is
   our own instruction, so screening it yields false `pre_llm_deny` hard-denies (no
   appeal) without catching the real threat. The URL screen covers SSRF, cloud-metadata
   endpoints, `localhost`, and credential-in-URL.

## Self-assessment vs 9/10

This v3 turns every "intent" statement the second-round reviewers flagged into a
concrete, implementable spec: the path-canonicalization algorithm (§4), the exhaustive
single-source substrate set (§2a), the payload-shaped seat backstop (§3a), the
per-shape fail-open table, the EDIT-coercion code-path guard, the Sága/cache
serialization with a collision gate, and the corrected flip-only Track A. The remaining
genuine unknowns are operational, not design (e.g. exact `SEAT_MAX_BYTES` tuning under
real latency, the eventual single-source refactor of the triplicated live-list) — both
flagged inline rather than hand-waved.

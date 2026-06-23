# Repo review — design-input questions (2026-06-22)

Autonomous multi-panel repo review. The clear mechanical fixes were implemented and
shipped in the accompanying PR (branch `claude/stoic-fermat-a4d4zb`). This document
collects the remaining issues that need a **human decision** before acting — each with
the evidence, an impact/effort read, and a recommended resolution (often a ready-to-apply
rewrite, so approval is one glance).

## How this was produced

- **Panel 1 (expert review)** — two parallel reviewers swept `scripts/` + the core
  plugin's `hooks/`, and the rest of `plugins/ravenclaude-core/` (agents/skills/commands/
  rules/knowledge/manifests). The CI gate surface was also run end-to-end.
- **Panel 2 (validation)** — every reported finding was re-checked against the actual
  file before acting; counts, line numbers, and behavior were verified this-session
  (`command + output` / `file:line`), per the repo's accuracy discipline. Findings that
  did not reproduce were dropped.
- **Implementation** — confirmed, mechanical fixes were applied (see PR). The items below
  are the ones that turned on a phrasing/policy judgment, a security-adjacent constitution
  edit, or a token-budget tradeoff — i.e. they need your call.

## Already fixed in the PR (for context — no action needed)

| Fix | Where | Severity |
|---|---|---|
| `feedback-report.html` stale vs. scenario corpus → **CI Gate 99 was failing** on a clean tree | `feedback-report.html` (regenerated) | **P1** |
| `guard-web-access.sh` collapsed every **native** Claude Code session into `runs/unknown/` (ignored payload `.session_id`), leaking the per-session web-allow + first-use trust state across sessions | `hooks/guard-web-access.sh:50` | **P1** |
| `check-md-links.py` `target.split()[0]` truncated any relative link path containing a space → false "broken link" | `scripts/check-md-links.py:91` | P2 |
| README/CLAUDE.md component counts stale (14→15 agents, 20→43 skills, 5→16 hooks, 4→5 rules, 4→7 commands; `viz-spec-reviewer` missing from roster) | `README.md`, `CLAUDE.md` | P2 |
| CHANGELOG top entry stale (0.155.0) vs plugin 0.157.0 → backfilled 0.156/0.157, added 0.158.0 | `CHANGELOG.md` | P2 |
| `format-on-write.sh` could abort the formatter under `set -e` if the file's dir vanished | `hooks/format-on-write.sh:17` | P3 |

Validation after the fixes: `audit-gates.sh` → **444 pass, 0 fail** (was 443/1-fail); prettier, ruff, frontmatter, md-links, marketplace-claims, layout all green.

---

## Q1 — Dashboard-server endpoint claims are stale **and** self-contradictory (P1, low effort)

**Evidence (this session):** `serve-dashboards.py` actually exposes **15** endpoints —
`/__save /__read /__classify /__run /__runs /__csrf /__concern /__knowledge /__saga
/__heimdall /__vidarr /__norns /__nidhoggr /__mimir /__sleipnir`. But:

- `CLAUDE.md:810` says serve-dashboards exposes "`/__save` + `/__read` + `/__classify`
  only, **no `/__run`**".
- `CLAUDE.md:862` says serve-dashboards "exposes an allow-listed `POST /__run`".
  → **The same file contradicts itself about `/__run`.**
- `README.md:39` tells a security-conscious consumer "endpoints limited to `/__save` +
  `/__read` + `/__classify` (no shell)" — also false (11 read endpoints + `/__run` exist).

This is a direct violation of the repo's own Accuracy Discipline, and the README line is a
**security claim** a consumer may rely on. The "no shell" intent is still true (`/__run` is
allow-listed to `install`/`update`/`status`, not arbitrary commands) — only the "limited to
these three" enumeration is wrong.

**Why this needs your call rather than an autonomous edit:** it edits the constitution's and
the README's *security framing*, which is exactly the kind of design/security wording the
`design_checkins` default reserves for a human. I did not want to silently rewrite a
security claim.

**Recommended rewrite (ready to apply):**

- `CLAUDE.md:810` — replace
  "`/__save` + `/__read` + `/__classify` only, no `/__run`, binds 127.0.0.1"
  with
  "binds 127.0.0.1; write surface is the CSRF-guarded `/__save` + `/__read` + `/__classify`
  + the allow-listed `/__run` (install/update/status — no arbitrary shell); the remaining
  `/__*` endpoints are read-only observability feeds (Heimdall/Víðarr/Norns/Níðhöggr/Mímir/
  Sleipnir/Sága)".
- `README.md:39` — replace "endpoints limited to `/__save` + `/__read` + `/__classify` (no
  shell)" with "writes via CSRF-guarded `/__save`/`/__read`; the only action endpoint is an
  allow-listed `/__run` (install/update/status — **no arbitrary shell**); other endpoints
  are read-only. Binds `127.0.0.1`."

**Decision:** Apply the recommended rewrite as-is / adjust wording / leave.

## Q2 — `plugin.json` + `marketplace.json` description omit `/forge` and `/reset-plugin-cache` (P2, low effort)

**Evidence:** both descriptions end "Slash commands: /init-agent-ready, /wrap, /set-posture,
/dashboard." The plugin ships **7** commands; `/forge` and `/reset-plugin-cache` (alias
`/ragnarok`) are missing.

**The tradeoff:** the agent `description` field has a hard **300-char cap** (gated by
`check-frontmatter.py`; it's loaded into the orchestrator's prompt budget). The core
description is already long. Adding two commands may push it over — needs a measure-and-trim
pass, not a blind append.

**Recommendation:** add `/forge` + `/reset-plugin-cache` and, if over budget, drop the
lower-value clause (e.g. the parenthetical Gate numbers in the viz blurb) to make room.
Low value, low risk — but it's a wording/budget judgment, so flagging rather than guessing.

**Decision:** Add both commands (trim to fit) / leave the description as-is.

## Q3 — `check-layout.py` over-accepts `**` vs `*` relative to the hook it claims to mirror (P2, medium effort)

**Evidence:** `scripts/check-layout.py:34-42` (`_matches`) normalizes `**`→`*` and lets a
single `*` span `/`, so `plugins/*/agents/*.md` would accept `plugins/a/agents/sub/deep.md`.
The docstring asserts parity with `enforce-layout.sh`, but the `**`-vs-`*` precision differs.
It is **latent** today (`forbidden_globs` is empty and the allow-list is permissive), so it
cannot currently mislabel anything.

**Recommendation:** decide whether the CI gate should enforce a true `**`-vs-`*` distinction
(tighter, but risks new false-negatives on legitimately-nested files) or **document** that
both intentionally span `/` for an allow-list and remove the "exact parity" claim from the
docstring. Given it's latent and the allow-list is intentionally permissive, the
documentation route is the lower-risk choice.

**Decision:** Tighten the matcher / document the intentional behavior (recommended) / leave.

## Q4 — `content-scan.py` SSRF guard validates the input URL, not the post-redirect host (P3, medium effort)

**Evidence:** `scripts/content-scan.py:139-159` (`fetch_body_excerpt`) checks
`urlparse(url).scheme` on the **input** URL only; `urllib.request.urlopen` follows HTTP
redirects by default, so a discovered URL that 3xx-redirects to `file://` or an internal
address is not re-validated, and there's no redirect-to-private-IP guard. The in-code
comment calls itself an "SSRF guard," overstating the protection. **Low severity** — this
script runs only on explicit operator invocation with a search API key, never in the agent
hot path.

**Recommendation:** either add a no-redirect / redirect-revalidation handler (if this is
meant to be a hardened SSRF boundary) **or** soften the comment to match the actual scope.
Needs a call on whether this surface is intended to be a real boundary.

**Decision:** Harden (no-redirect handler) / soften the comment / leave.

## Q5 — CLAUDE.md narrative "14 specialists / 40 skills" lines (P3, low effort)

**Evidence:** several CLAUDE.md prose lines still say "14 specialists" / "40 skills". Most
are **dated milestone snapshots** ("All 14 … as of 2026-05-21") and are defensible as
historical record; a few un-dated summary lines are simply stale. I fixed the one clearly-
current Layout bullet (`agents/ — 15 …`) but left the dated narrative as-is.

**Recommendation:** leave the dated milestone lines (they're historical record); optionally
sweep the handful of un-dated summary restatements in a later docs-only pass. Lowest
priority — purely cosmetic, no consumer impact.

**Decision:** Leave as historical / do a cosmetic sweep.

---

### Notes for the record

- No P0 (critical) issues were found. The codebase is unusually defensive (fail-safe
  sourcing, sanitized session ids, secret scrubbing, bidirectional gate teeth) and CI is
  green after the fixes.
- Panel 1 also positively cleared several scary-looking patterns (empty-array `match_host`
  calls, the `_scrub.sh` sed pipeline, `runaway-brake.sh` malformed-counter reads,
  `guard-destructive.sh` normalization, the `copilot-hook-adapter.sh` guard precedence) —
  recorded so a future review doesn't re-investigate them.

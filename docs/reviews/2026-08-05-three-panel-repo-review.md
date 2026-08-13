# Three-panel repository review — 2026-08-05

Autonomous whole-repo review run as a scheduled routine. Three expert panels
(find → adversarially verify → analyze → tie-break) swept the ~60K-line automation
code surface — `scripts/`, `plugins/ravenclaude-core/` code, `.github/workflows/`,
and root config. **32 findings raised, 31 confirmed** after adversarial verification;
24 had their priority set by a Panel-3 tie-breaker.

All automated CI gates were **green before and after** the review (JSON, shell,
frontmatter, version-drift, layout, markdown links, prettier, ruff, and every
specialized checker). The findings below are the semantic issues the gates don't see.

> **A note on notation.** Where a finding is *about* a dangerous command, this doc writes
> that command in a neutralized form (e.g. "a force-push", "a `curl`-into-shell pipe")
> rather than the literal token sequence — the repo's own content screen (correctly) can't
> tell prose-about-a-command from a command, and the literal forms trip the hard-rule deny.

> **Re-run fresh from current `main` (v0.236.1).** This review was re-verified against
> current `main` this session. Every finding below was re-checked; three were found
> **already fixed on `main`** and dropped (see "Already fixed upstream"). The rest split
> into a **landable subset** (this PR) and a **substrate-blocked subset** (the 3 P0s +
> three lower-priority fixes) that cannot be applied in a headless review environment.

## Why the P0s are not in this PR — and how to land them (≈2 min, interactive)

The 3 **P0 security fixes** all edit the tribunal's own substrate
(`plugins/ravenclaude-core/hooks/` + `plugins/ravenclaude-core/scripts/`). The
`xc.tribunal-self-disable` guard denies substrate edits when it cannot verify dev-repo
ownership — and in this headless environment `gh` is absent, so the dev-repo exemption
never clears. This session, the guard denied even a **read-only `git diff` that merely
named a substrate path**. This is the control working as designed; it was **not**
bypassed (faking `gh`, a merge back-door, or writing a disable toggle are all off the
table by the constitution).

**To apply the substrate fixes below:** open the comfort-posture **dashboard** (or run
with `gh` authenticated) so the exemption clears the guard, then either re-run this
review from `main` or cherry-pick the substrate hunks. The exact applied hunks live in
the **closed PR #833's commit `a9a9f5d6`** (`git show a9a9f5d6 -- <path>`), recoverable
from GitHub for ~90 days; they were written against the v0.191.1 base, so re-verify each
against current `main` before applying.

---

## ✅ Landed in this PR (non-substrate — green, auto-merging)

Every confirmed fix that does **not** touch tribunal substrate and needs no design
decision. Applied onto current `main` and re-verified present-and-needed.

### P1 — high

- **`svg-report-lint/lint.py` + `declarative-visualization/lint.py`** — the remote-href
  "security floor" missed protocol-relative URLs (`//host/x.svg`) and control-char-split
  schemes. Both patterns now flag `//` and strip tab/CR/LF before scheme-matching.
- **`brand-extraction/extract_brand.py`** — fetched site title / `og:site_name` / URL
  written unescaped into the generated HTML report (stored XSS); font-family names
  written unescaped into CSS. Now `html.escape`d, and font names stripped of
  CSS-breakout chars (`_css_font_safe`).
- **`visual-feedback-loop/driver.py`** — path guard used `abspath` (not `realpath`),
  diverging from the sandbox parity it claims with the layout linter, allowing a symlink
  escape. Now `realpath` on both sides; a symlink to an out-of-repo file is rejected.
- **`content-scan.py`** — `fetch_body_excerpt()` validated only the initial and final
  redirect hop, so an intermediate 3xx could land on a NEVER_FETCH host (LinkedIn/Reddit)
  or an internal SSRF target. A `_GuardedRedirectHandler` now re-screens scheme +
  never-fetch + host-public on **every** hop.
- **`rc-deep-research.js`** (both byte-identical copies) — the Verify-phase adversarial
  `agent()` calls lacked the `.catch()` the search/fetch phases already carry, so one
  rejected verifier vote crashed the whole run. Guards added; the copied
  dispatch-evaluator block (Gate 52) is untouched.
- **`two-panel-plan-review.js`** — Panel 1 / Panel 2 lens fan-outs lacked per-agent
  `.catch()`; one failed lens aborted the whole review. Guards added.

### P2 / P3 — medium / low

- **`generate-bi-report.py`** — HTML attribute-name injection via an unsanitized column
  `key`. Keys now constrained to a safe identifier grammar (`_safe_attr_key`); all shipped
  keys already comply, so `report.html` output is byte-identical (freshness gate green).
- **`check-lineup-citations.py`** — the context-window regex missed raw-digit token counts
  (`1,000,000 tokens`), silently passing uncited stale facts. Broadened; K/M forms kept,
  benign numbers (dates, versions, ports) not flagged.
- **`pbir-layout-engine/lint.py`** — `check_column_alignment` ignored the caller's tolerance
  when grouping rows (hardcoded 1px). Now uses `max(tolerance, 1)` like the sibling
  `check_equal_gap`.
- **`.repo-layout.json`** — added the documented `task-scope.json` / `self-heal-setup.md`
  feature files (the hook was self-denying them in this repo); removed three redundant globs
  subsumed by broader parents (`tests/fixtures/data-viz/**`, `scripts/generate-dashboards.py`,
  `scripts/serve-dashboards.py`).
- **`regenerate-artifacts.yml`** — the post-merge self-heal pushes to `main` with a
  skip-CI marker, bypassing all layout/link CI. Step 4f now also runs a layout allow-list
  check (inline, covers untracked new artifacts) and `check-md-links.py`, aborting the push
  on failure.
- **`check-run-actions-argv.py`** — the gate never asserted `argv` length ≥ 2, but
  `serve-dashboards.py` indexes `argv[1]` unconditionally. Length check added.

---

## ⛔ Blocked substrate fixes — apply from an interactive session

Confirmed-and-needed on current `main` (fix markers absent this session), but they edit
tribunal substrate and so cannot be applied headlessly. Descriptions are the ready-to-apply
spec; exact hunks in commit `a9a9f5d6`.

### P0 — security-critical

| Finding | File | Fix |
|---|---|---|
| The tribunal's category-independent hard-rule/self-disable screen never decoded base64, so an obfuscated remote-exec pipe / force-push / self-disable command classifying to `None`/an untoggled category bypassed the screen entirely | `plugins/ravenclaude-core/scripts/thing-concerns.py` | `screen_always()` scans the base64-decoded forms of the command too (shared `_iter_decoded_texts` generator; `evaluate()` path unchanged). Repro confirmed on the stale branch: a base64'd remote-exec pipe denied, benign untouched. |
| Binding decision-review verdicts never saw the AskUserQuestion `header` / option `description`, so a high-blast decision stating its stakes there (e.g. a force-push named only in the header, bland "Continue?" question) could auto-resolve without the human being asked | `plugins/ravenclaude-core/hooks/route-decision-review.sh` | `header` + `description` feed both the local high-blast grep and the engine `context` (size-capped). The §4a injection-echo hardener already treats them as untrusted, so the defense isn't weakened. |
| `guard-destructive.sh` had no deny for remote-branch deletion (the `--delete` flag and the colon-refspec form of `git push`) — an always-on guard whose stated scope is "git history / branch destruction" | `plugins/ravenclaude-core/hooks/guard-destructive.sh` | Order-independent `_is_dangerous_git_push_delete` helper (flag + colon-refspec forms) + audit-gates fixtures. Sanctioned escape hatch (`archive-branch.sh`, a subprocess) is unaffected. |

### P1 / P2 (substrate)

- **`guard-destructive.sh`** (P1) — `git clean` with a separated `-d` / `-f` token pair bypassed the
  contiguous-anchor regex. Replaced with order-independent `_is_dangerous_git_clean` + fixtures.
- **`thing-seat.sh` + `claude-orchestrate.sh`** (P2) — the inline secret-scrub fallback arrays were
  stale vs canonical `_scrub.sh` (missing `rk_live_` / `npm_` / `hf_` / `AccountKey=` /
  embedded-cred-URL; loose JWT / `-p`). Re-sync byte-for-byte to `_scrub.sh`.

> **Coupled to the above:** the `scripts/audit-gates.sh` fixtures for the `guard-destructive.sh`
> remote-delete / `clean` fixes are **not** in this PR (they would fail without the substrate fix).
> Land them together with the substrate changes.

---

## Already fixed upstream (re-verified, dropped)

- **`serve-dashboards.py` static-fallback DNS-rebinding gating** — fixed in v0.236.1 (design-input
  item #1 below is therefore **moot**).
- **`capability-orientation.py` `_fmt_rules` banner-injection sanitize** — fixed in v0.236.1.
- **`cleanup-branches.sh` delete-loop TOCTOU** — current `main` already carries the verdict-time tip as
  a 3rd tab-field and deletes via an **atomic SHA-guarded `git update-ref -d <ref> <oldvalue>`**, which
  is *stronger* than the reviewed assoc-array re-check (git enforces the guard with zero race window).
  Applying the reviewed fix would be a regression, so it was dropped.

---

## 👉 Needs your input — items deliberately NOT auto-merged

Confirmed findings the panels flagged `needs_design_input`, plus items that would require
regenerating large committed artifacts. Each has a concrete recommendation.

### 1. `serve-dashboards.py` static handler serves the entire repo tree (P1 — security) — **MOOT**

Superseded by the v0.236.1 fix (see "Already fixed upstream"). The static path is now gated.
No action needed unless you want the additional `.git`/dotfile denylist as defense-in-depth.

### 2. Decision-tally Thor-convene guards Heimdall (injection seat) but not Forseti (risk seat) (P2)

**File:** `plugins/ravenclaude-core/scripts/thing-decide.py` (`_tally`, ~L579) — **substrate**
If exactly one seat abstains and it's **Forseti** (the sole risk/security seat), no Thor convene is
forced and a binding yes/no can return with zero risk-focused review. The mirror-image Heimdall-abstain
case *is* guarded. **Recommendation:** compute `forseti_abstained` and add it to the Thor-convene
condition. **Design call:** whether Forseti-absence should force a *convene* or a *defer*.

### 3. `_HIGH_BLAST_RE` misses common destructive verbs (P3)

**File:** `plugins/ravenclaude-core/scripts/thing-decide.py` (~L71) + shell twin
`route-decision-review.sh` (~L100) — **substrate**
Omits `overwrite`, `terminate`, `disable`, `uninstall`, `downgrade`, `rollback`, `grant admin`,
`elevate`. It can only *add* a defer (defense-in-depth). **Design call:** the exact verb list is a
judgment about false-positive tolerance vs. coverage.

### 4. `rc-deep-research.js` MAX_FETCH budget bypassed for all "high"-relevance results (P2)

**File:** `plugins/ravenclaude-core/skills/rc-deep-research/rc-deep-research.js` (~L921, both copies)
`if (fetchSlots <= 0 && relRank[r.relevance] >= 1)` never fires for `high` (`relRank.high === 0`), so
high-relevance sources always bypass the `MAX_FETCH` budget — up to ~2× the cap. Cost/latency only.
**Design call:** is preserving high-relevance sources over budget *intentional*? If yes cap the overflow
explicitly (`fetchSlots > -N`); if no drop the `relRank >= 1` carve-out.

### 5. `archive-branch.sh` — `--skip-push` + `--delete-remote` breaks "recoverable forever" (P2)

**File:** `scripts/archive-branch.sh` (~L268)
Combining both flags creates the archive tag **locally only**, then deletes local + remote — so a later
clone loss permanently loses the work. **Recommendation:** refuse the flag combination, or force a tag
push before any remote delete. **Design call:** hard-refuse vs. gate behind
`--yes-i-know-this-is-unrecoverable`.

### 6. Full "Plugins" tab rebuilt uncached per schema-bearing plugin (P3 — perf landmine)

**File:** `scripts/generate-dashboards.py` (`_page_kwargs`, ~L178)
`_render_plugins_category(_all_plugin_dirs())` walks all plugins with no caching, once per schema-bearing
plugin. Only `ravenclaude-core` ships a schema today (one-time ~420KB embed), but a second makes generator
cost + artifact size scale O(P·S) with no CI signal. **Recommendation:** compute once in `main()` and
thread it through, or `functools.lru_cache`. **Design call:** invest now vs. add a CI size-guard and defer.

### Also deferred (mechanical, out of scope for an auto-merge)

- **`_index_dashboard_template.py` esc()-into-`onclick` idiom (P3).** Not exploitable today (values are
  on-disk plugin dir names), but the wrong escaping primitive for a JS-string sink. Fixing it changes the
  generated ~10 MB `index.html` and needs a full portal regeneration + render/router gate re-verification —
  best as its own change. **Recommendation:** migrate to the `data-*` + delegated-`addEventListener` pattern.
- **`audit-gates.sh` has no fixture coverage for `archive-branch.sh` / `cleanup-branches.sh` (P2).** The
  repo's only destructive-git scripts; two prior reviews found real data-loss bugs in them via manual review
  alone. Adding a fixture harness that safely exercises tag-then-delete / tip-matching against throwaway
  repos is worth its own PR.

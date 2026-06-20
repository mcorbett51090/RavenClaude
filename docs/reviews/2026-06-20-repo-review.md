# Repository review — 2026-06-20

A whole-repo expert review (multi-panel: independent expert scan → validation → tie-break)
of the RavenClaude marketplace. This document records the **issues found**, what was
**implemented in this PR**, and the **deferred items that need a decision or judgment call**
before they can be safely implemented. Each deferred item links to the code and carries a
priority + a concrete recommendation.

## Method

- **Panel 1 (expert scan)** — four parallel reviewers swept the high-risk surfaces gates can't
  catch: Python scripts, shell hooks/scripts, CI workflows + manifests, and plugin-content
  cross-references.
- **Panel 2 / 3 (validation + tie-break)** — every Panel-1 finding was re-verified against the
  actual code before it was trusted. **Two Panel-1 findings did not survive verification** and
  were rejected (see "Rejected findings" below) — a reminder that an un-verified finding is a
  hypothesis, not a defect.
- The objective gate suite (JSON validity, shell syntax, frontmatter, md-links, layout,
  marketplace-claims, mcp-attribution, prettier, ruff, and the 444-check `audit-gates.sh`
  meta-test) was run first; all were green **except** the one CI-blocking staleness fixed below.

## Implemented in this PR (verified, design-free)

Sorted P1 → P2.

### P1 — `feedback-report.html` was stale → blocked every PR's CI

`scripts/generate-feedback-report.py --check` (audit-gates **Gate 99**, a clean-tree
`must_pass`) failed: the scenario corpus grew 366 → 369 but the committed report was never
regenerated. Because Gate 99 runs at **PR time** inside `validate-marketplace.yml`, a stale
report fails **every open PR's** CI, not just one. Regenerated; deterministic and idempotent
(`--check` re-passes). **See the architectural follow-up D1 below — this artifact was left out
of the post-merge self-heal that protects its siblings, which is why it could go stale on the PR
path at all.**

### P1 — credit-card PAN detector never fired (two plugins)

`plugins/regulatory-compliance/hooks/scrub-confidential-pre-write.sh:81` and the copy-pasted
`plugins/finance/hooks/flag-finance-anti-patterns.sh:74` used PCRE non-capturing groups
`(?:…)` inside `grep -E` (POSIX ERE). GNU grep rejects this with
`warning: ? at start of expression` and then **never matches a real card number** — a silent
gap in a confidentiality control (the regulatory-compliance one runs `PreToolUse`, before the
write lands). Reproduced empirically (`4111111111111111` → no match before, match after) and
fixed by switching to plain capturing groups; verified it now matches all four major brands and
does not false-positive on SSNs or ordinary digit strings. Versions bumped
(regulatory-compliance `0.12.1`, finance `0.14.1`) with CHANGELOG entries.

### P2 — CI / script hardening

| Fix | File | Why |
|---|---|---|
| `git`-returncode guard | `scripts/check-layout.py` | The layout gate consumed `git ls-files` / `git diff` stdout without checking the return code — a git failure (bad ref, no HEAD) silently produced an empty path list and a **false "Layout OK — 0 files" pass**. Now fails loud. (Independently flagged by two panels.) |
| Config-file CI triggers | `.github/workflows/validate-marketplace.yml` | The `paths` filter omitted `.prettierignore` / `.prettierrc.json` / `ruff.toml` — yet the prettier and ruff gates **in this workflow** read them, so a config-only PR merged unvalidated. Added to both `pull_request` and `push` filters. |
| `None`-guard parity | `scripts/render-concepts.py` | `_normalize()` called `m.group(1)` with no guard; its sibling `render-trees.py:103` already has `if not m: return svg`. Malformed mermaid output would raise `AttributeError`. Back-ported the guard. |
| Broken doc references | `plugins/ravenclaude-core/skills/cross-platform-determinism/SKILL.md` | The skill's runnable "repro recipes" pointed at `generate-repo-guide.py` and `check-guide-fresh.sh`, both deleted when Gate 11 was retired (v0.124.0) — `No such file or directory` for any maintainer following them. Repointed to the live successor `generate-index-dashboard.py` (same `--check` strip-before-diff contract); core bumped to `0.158.0`. |

## Deferred — needs a decision or a judgment call

Ordered by priority. None were implemented because each either changes runtime behavior of a
scheduled job, touches the highest-blast-radius plugin for near-zero benefit, depends on a scope
decision (e.g. "do we support macOS bash 3.2?"), or is a large bulk edit that needs
per-item accuracy.

### D1 — [P1] `feedback-report.html` is on the PR critical path but excluded from the post-merge self-heal

`index.html`, `dashboard.html`, `concepts.json`, and `report.html` were deliberately moved
**off** the PR path into `.github/workflows/regenerate-artifacts.yml` (post-merge self-heal) to
kill cross-PR "freshness contagion." `feedback-report.html` was **missed** — it is still gated
at PR time by audit-gates **Gate 99** (clean-tree `must_pass`) and is **not** in
`regenerate-artifacts.yml`. This is the exact contagion that `concepts.json` + `report.html`
were relocated to fix on 2026-06-08.
**Recommendation:** add `feedback-report.html` to `regenerate-artifacts.yml` (a `--check`-gated
step + its source paths in the `on.push.paths` filter) and remove the PR-time clean-tree gate,
mirroring the 2026-06-08 treatment. Keep the teeth audit in `audit-gates.sh`.
**Why deferred:** changes the CI gating model — a design call for the maintainer.
Code: [`scripts/generate-feedback-report.py`](../../scripts/generate-feedback-report.py),
[`.github/workflows/regenerate-artifacts.yml`](../../.github/workflows/regenerate-artifacts.yml),
[`scripts/audit-gates.sh`](../../scripts/audit-gates.sh) (Gate 99).

### D2 — [P2] `index.html` committed copy is content-stale (edtech-partner-success templates 38 → 40)

The committed `index.html` reports `"templates":38` for `edtech-partner-success`; disk has 40
(two templates added without regenerating the portal). This is **not** a CI failure (the index
is self-healed post-merge by `regenerate-artifacts.yml`, and audit-gates regenerates it in-place
before its freshness check), and **this PR's trigger-path edits will cause the self-heal to
regenerate it on merge** — so no action is needed here. Flagged only because it means a prior
merge that touched edtech templates did **not** go through a path that fired the self-heal (or
the self-heal failed). **Recommendation:** confirm the self-heal fired after merge; if `index.html`
is still stale on `main`, run `regenerate-artifacts.yml` via `workflow_dispatch`.

### D3 — [P1] Fallback secret-scrub pattern array is stale (defense-in-depth gap)

`plugins/ravenclaude-core/scripts/thing-seat.sh` and `scripts/claude-orchestrate.sh` keep an
**inline fallback** `_secret_patterns` used when `hooks/_scrub.sh` can't be sourced. The fallback
is missing seven patterns the canonical `_scrub.sh` carries (Stripe `sk_live_`/`rk_live_`, `npm_`,
`hf_`, Azure `AccountKey=`, URL-embedded credentials) and its JWT/`-p`-flag thresholds are looser
(`{6,}` vs the tightened `{20,}`/`{16,}`). When the canonical file is unresolvable (broken install,
wrong `CLAUDE_PLUGIN_ROOT`), the egress backstop can miss those secret shapes.
**Recommendation:** have the fallback source `_scrub.sh` relative to `${BASH_SOURCE[0]}`, and if that
also fails, keep the inline array byte-identical — then add a CI drift gate
(`diff` the two `_secret_patterns=(` blocks).
**Why deferred:** security-sensitive and touches the core plugin's tribunal substrate — wants a
`security-reviewer` pass, not an autonomous edit. Only fires on the fallback path (canonical
`_scrub.sh` resolves normally today).
Code: [`plugins/ravenclaude-core/hooks/_scrub.sh`](../../plugins/ravenclaude-core/hooks/_scrub.sh),
[`plugins/ravenclaude-core/scripts/thing-seat.sh`](../../plugins/ravenclaude-core/scripts/thing-seat.sh),
[`plugins/ravenclaude-core/scripts/claude-orchestrate.sh`](../../plugins/ravenclaude-core/scripts/claude-orchestrate.sh).

### D4 — [P2] Monthly cron fires too often (`researcher-reminder.yml`)

`.github/workflows/researcher-reminder.yml` schedules `0 10 1-7 * 1`. In POSIX cron (which GitHub
Actions uses) day-of-month **and** day-of-week both non-`*` means **OR**, so this fires every
Monday *and* every day 1–7 — producing up to ~6 spurious `monthly-skill-gap-audit` issues a month.
**Recommendation:** use `0 10 * * 1` (every Monday) and gate the monthly path in the JS step on
`new Date().getUTCDate() <= 7` (first Monday).
**Why deferred:** changes the behavior of a scheduled job and needs the first-Monday guard logic —
a small judgment call worth a maintainer's eyes.
Code: [`.github/workflows/researcher-reminder.yml`](../../.github/workflows/researcher-reminder.yml).

### D5 — [P2] `cleanup-branches.sh` uses `mapfile` (bash 4.0+) — fails on macOS stock bash 3.2

`scripts/cleanup-branches.sh:106` (and `enforce-layout.sh:95,124` — Linux/Claude-only, lower
priority) use `mapfile`, absent on macOS's default `/bin/bash` 3.2.
**Recommendation:** replace with a `while IFS= read -r` loop **if** macOS is a supported dev
environment.
**Why deferred:** depends on a scope decision — is macOS-with-stock-bash a target? The devcontainer
is Linux. Code: [`scripts/cleanup-branches.sh`](../../scripts/cleanup-branches.sh).

### D6 — [P3] Low-impact hardening (batch — safe but not worth isolated churn)

Each is real but latent or near-zero-impact; recommend rolling into the next touch of the file:

- **`echo "$line"` → `printf '%s\n'`** in `claim-grounding-lint.sh` (lines 93/96/98/100) and
  `guard-recursive-spawn.sh:82`. *Verified the impact is negligible:* `echo` only eats a line that
  is **literally** `-n`/`-e`/`-neE` (a `-n foo` line with a space prints fine), which never occurs in
  real markdown — so the original "a `-no way…` bullet breaks it" claim was overstated. Defer because
  the ravenclaude-core blast radius outweighs the ~never trigger.
- **`generate-copilot-plugin.py` `FRONTMATTER_RE`** doesn't match CRLF (`^---\n…`); `check-frontmatter.py`
  uses `^---\r?\n`. Latent — the repo is LF-only — but on a CRLF checkout it would silently emit empty
  Copilot descriptions.
- **`check-marketplace-claims.py` skill count** counts every non-dot entry under `skills/`, so a
  `skills/README.md` would inflate the count. Latent — no plugin has one today.
- **`content-scan.py`** retries HTTP 429 but `_die()`s on the first `URLError` (transient network) —
  a single blip loses the run.
- **`brand-kit.schema.json`** is not structurally validated by `validate-schemas.yml` (only
  `plugin.json` / `marketplace.json` are). Trivial to add a `json.tool` + meta-schema step.
- **`check-run-actions-argv.py`** accepts any whitelisted dynamic expression as `argv[0]`, not just
  `sys.executable` — tighten the post-loop check.
- **Misc:** `$RANDOM` nonce fallback is 60-bit not 64-bit (`thing-seat.sh:178`,
  `claude-orchestrate.sh:211`); `pkill -f` is system-wide (add `-u "$(id -u)"` in `open-dashboard.sh`,
  `dashboard-launcher/dashboard.sh`); `_emit-event.sh` no-jq JSON fallback doesn't `\uXXXX`-escape all
  control chars; ruff pinned `0.15.8` vs current `0.15.18`; concepts step uses `set -e` not
  `set -euo pipefail`; stale `.prettierignore` exclusion comment for `researcher-reminder.yml`.

### D7 — [P3] 28 plugins have a `CHANGELOG.md` top entry behind their `plugin.json` version

AGENTS.md requires "if a plugin has a `CHANGELOG.md`, keep its top entry current on every version
bump." 28 plugins violate this (e.g. `ravenclaude-core` was 2 behind before this PR;
`skilled-trades-contracting` left an `[Unreleased]` heading for shipped 0.2.x work). Not
CI-gated (marketplace-claims passes), so non-blocking.
**Recommendation:** backfill each from `git log -- plugins/<name>/` since its last entry — a bulk
task that needs **per-plugin accuracy**, so it should be its own focused pass, not folded into a
review PR. (This PR brought `finance`, `regulatory-compliance`, and `ravenclaude-core` current.)

## Rejected findings (did not survive verification)

- **"`check-marketplace-claims.py` module-level `failures` list pollutes `--fix`" (claimed P0)** —
  false. In `--fix`, a count-drift `return 1`s at line 370 *before* `collect_structural()` runs at 375,
  so the lists never merge on the real path; and the gate is invoked as a fresh subprocess per run, so
  the "called twice" concern is moot.
- **"`echo "$line"` breaks on any `-n`-prefixed bullet" (claimed P2)** — overstated. Reproduced: only a
  line that is *entirely* `-n`/`-e`/`-neE` is eaten; ordinary `-n foo` prose prints fine. Downgraded to
  the D6 batch.

## Net

Objective gates are green (444/444 after the Gate 99 fix). The codebase is in good health; the
findings are a CI-blocking staleness, a real (verified) security-control regex bug duplicated
across two plugins, a handful of safe hardening fixes, and a backlog of judgment/scope-dependent
items captured above for the maintainer's call.

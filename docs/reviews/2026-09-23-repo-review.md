# Autonomous repo review — 2026-09-23

A scheduled multi-panel repository review ran on branch `claude/awesome-wright-c6xg9w`.

**Structure.** Four independent expert panels (Panel 1) scanned the tree for **gate-invisible**
defects — bugs the ~917-gate CI battery and the passing `audit-gates.sh` meta-test cannot see. The
orchestrator (Opus) served as Panel 2 (priority validation, impact/effort) and Panel 3 (tie-breaking
on ambiguous calls). Confirmed, low-risk findings were fixed and validated directly; findings that
touch the tribunal's own substrate, need a design decision, or carry regression risk are recorded
below as **design-input** rather than force-applied by an unattended session.

- **Lane A** — root Python CI checkers (`scripts/*.py`)
- **Lane B** — shell guards & hooks (`plugins/*/hooks/*.sh`, `scripts/*.sh`)
- **Lane C** — CI/CD security & config (`.github/workflows/*`, manifests)
- **Lane D** — docs/claims drift + plugin-internal Python

No **P0** surfaced; the tree remains unusually well-hardened. The highest-value finding (Lane B) is a
whole *class* of safety hooks that were silently inert.

---

## Implemented in the accompanying PR (confirmed, validated — no decision needed)

Every fix below was reproduced before and after the change. No version bumps and no generated-file
churn (following the 2026-09-22 precedent; the version-bump convention for doc-count corrections is
raised as an open question at the end).

### P1

| ID | Fix | Files | Validation |
|---|---|---|---|
| **A1** | `check-selfheal-push-safety.py` matched each push/admin-bypass shape only within a single physical line, so a `\`-continued `gh pr merge … --admin` (or `git push … main`) split across lines evaded **every** detector. Added `_join_continuations()` so continuations are merged into one logical line before shape-matching. | `scripts/check-selfheal-push-safety.py` | `--self-test` 12/12; reproduced the multi-line `--admin` now caught (exit 2), single-line still caught, sanctioned multi-line merge stays silent (no false positive). |
| **B1 (subset: 29 hooks)** | 58 `PreToolUse` anti-pattern hooks grep the **on-disk (pre-edit)** file instead of the **proposed edit**, so a `Write` to a new file silently `exit 0`s and an `Edit`/`MultiEdit` that *introduces* the pattern is checked against the old bytes — the hook can never fire on the content it exists to catch. The identical bug was fixed once in `flag-data-platform-smells.sh` (2026-09-03) and never propagated. This PR fixes the **29 simple-shape** hooks (where `$file` is used only for content-scanning): a `scan_target` temp file is built from `.tool_input.content` / `.new_string` / `.edits[].new_string` and scanned; the on-disk file remains the legacy no-stdin fallback. | 29 `plugins/*/hooks/check-*-anti-patterns.sh` (incl. `security-engineering`, `aws-cloud`, `gcp-cloud`, `cybersecurity-grc`, `auth-identity`, `fintech-payments-engineering`, `database-engineering`, `terraform-iac`, …) | `bash -n` all 29; reproduced on `security-engineering` + `terraform-iac`: new-file Write with a secret now **fires** (was silent), clean Write silent, Edit-introducing-secret fires, legacy arg-path still fires; `check-hook-stdin-fallback.py` and `check-hook-failclosed.sh` both green. |

### P2

| ID | Fix | Files |
|---|---|---|
| **D1** | `finance/README.md` "What's inside" table stale on 4 rows: Skills 9→**23**, Knowledge 10→**17**, Hooks 1→**2**, Templates 8→**9**. | `plugins/finance/README.md` |
| **D2** | `power-platform/README.md`: Skills 21→**23**; Hooks 1→**4** (documents the previously-undocumented `nudge-dataverse-preflight.sh` + 2 validators). | `plugins/power-platform/README.md` |
| **D3** | `ravenclaude-core/CLAUDE.md` layout said "15 specialist agents" → **17** (adds `scout`, `source-control-coordinator`, both documented as later additions elsewhere in the same file — an internal self-contradiction). | `plugins/ravenclaude-core/CLAUDE.md` |
| **D4** | `ravenclaude-core/README.md` slash-command lists (prose + table) omitted `/coordinate`, `/optimize`, `/repo-review` — three fully-shipped commands. Added, with a pointer to `commands/` as the authoritative list. | `plugins/ravenclaude-core/README.md` |

### P3

| ID | Fix | Files |
|---|---|---|
| **D5** | `regulatory-compliance/README.md` Skills 10→**11**. | `plugins/regulatory-compliance/README.md` |
| **D6** | `ravenclaude-core/CLAUDE.md` commands layout bullet listed 6 of the shipped commands (missing `/forge`, `/handoff`, `/coordinate`, `/optimize`, `/repo-review`). Added + authoritative-list pointer. | `plugins/ravenclaude-core/CLAUDE.md` |
| **D7** | `GETTING_STARTED.md` cited `spawn-team/SKILL.md:94-96`; the "Stakeholder document" playbook moved to lines **140-142**. (Gate-invisible: it's a backticked `file:line`, not a Markdown link, so `check-md-links.py` never sees it.) | `GETTING_STARTED.md` |

> The Lane D count claims in `plugin.json` descriptions / `marketplace.json` / the *core* README
> table are already covered by `check-marketplace-claims.py` (self-heals post-merge; passes now).
> The 7 items above are all in places that gate does **not** cover.

---

## Design-input — needs your decision (NOT auto-applied)

Each item below was confirmed by a panel but deliberately **not** force-applied by this unattended
session, for the reason stated. Recommendations and code links included so you can act quickly.

### 1. (P1) `check-workflow-hygiene.py` Rule 1 checks the `permissions:` *key*, not its *value*

- **Where:** [`.github/scripts/check-workflow-hygiene.py`](../../.github/scripts/check-workflow-hygiene.py), Rule 1 `[HARD]`.
- **Defect (reproduced):** the rule documents "least-privilege: every workflow MUST carry a top-level
  `permissions:` floor (deny-all `{}` or read-only)", but the implementation only asserts the key
  exists. A workflow with top-level `permissions: {contents: write, pull-requests: write, issues:
  write, actions: write}` — the exact anti-pattern named — passes with **zero** findings. The
  checker's own 7-case self-test never exercises the broad-permissions shape, so the gap is invisible
  to its internal audit too.
- **Why held:** this checker ships to every consumer via `ravenclaude init-agent-ci`, and a naive
  "top-level must be read-only/empty" fix would immediately redden **this repo's own**
  `quarantine-intake.yml` and `regenerate-artifacts.yml`, which legitimately carry broad top-level
  write because each is a **single-job** workflow. A correct fix needs job-count nuance (allow a broad
  top-level floor only when a single job needs it, else require per-job elevation) — a design call.
- **Recommendation:** add value inspection to Rule 1 that (a) flags a top-level write scope when the
  workflow has ≥2 jobs and any job needs less, and (b) extend the self-test with a broad-permissions
  must-fail fixture. Decide the single-job carve-out policy first.

### 2. (P1) The other 29 anti-pattern hooks + a systemic regression gate

- **Where:** 28 **routed-shape** `PreToolUse` anti-pattern hooks (they use `case "$file"` / `basename
  "$file"` for extension routing and reporting, so `$file` cannot simply be repointed) plus
  `plugins/tableau/hooks/flag-tableau-anti-patterns.sh` (non-uniform preamble). Full list in the run
  artifact `panel1-B-shell-guards.md`.
- **Why held:** each needs a per-hook fix (keep `$file` = real path for routing/reporting; route only
  the *content scans* to the proposed text). Doing 29 more safety-hook edits blindly in an unattended
  session is exactly the "chasing mirrors by hand" failure the 2026-09-22 review flagged.
- **Recommendation (the durable fix):** (a) extract the payload→`scan_target` logic into a shared
  helper (e.g. `plugins/ravenclaude-core/hooks/_edit-subject.sh`, sourced the way `_portable.sh`
  already is), so the pattern lives in one place; (b) add a **regression gate**
  (`check-pretooluse-payload-scan.py`) that fails any `PreToolUse` `Edit|Write|MultiEdit`
  anti-pattern hook that scans disk without reading the payload. The gate + the bulk fix must land
  **together**, or CI reddens on the still-broken hooks. This is the real fix; the 29 already landed
  in the PR are the proven, low-risk half.

### 3. (P2) `check-verdict-default-nonpermissive.py` — `FALLIBLE` regex misses bare commands

- **Where:** [`scripts/check-verdict-default-nonpermissive.py`](../../scripts/check-verdict-default-nonpermissive.py), `FALLIBLE = re.compile(r"\$\(|`|^\s*(cd|source|\.)\s+\S")` (~line 61), used by `check_trap_ordering()`.
- **Defect (reproduced):** the regex only treats command-substitution, backticks, or lines starting
  with `cd`/`source`/`.` as able-to-abort-before-the-trap. A bare external command (`mkdir -p …`)
  between `set -e` and the fail-closed `trap … EXIT` aborts before the trap arms — the exact
  fail-open shape this meta-gate exists to catch — and is not flagged. Latent (the live tree is clean
  today).
- **Why held:** widening `FALLIBLE` to catch bare commands needs shell-aware logic (distinguish
  assignments, keywords `if`/`while`/`{`, and `… || true` from genuinely fallible commands) and
  risks false-positives across the repo's many EXIT-trap hooks. A mis-tuned safety meta-gate is worse
  than a known gap.
- **Recommendation:** widen with an allow-list of non-fallible line shapes (assignment `^\w+=`,
  `local`/`readonly`/`declare`, control keywords, a trailing `|| true`/`|| :`), everything else
  fallible; add both a must-fail (`mkdir` before trap) and a must-pass (assignment before trap)
  fixture. Confirm it stays green on the current tree before merge.

### 4. (P2) `check-model-tier-fit.py` — `_IMPL_DESC` lacks `re.IGNORECASE` (its sibling has it)

- **Where:** [`scripts/check-model-tier-fit.py`](../../scripts/check-model-tier-fit.py), `_IMPL_DESC` (~line 124); sibling `_DECIDES_DESC` carries `re.I`.
- **Finding:** a lowercase-opener description ("Use to build the parser…") on a frontier tier is not
  matched by the hard-gate implementer detector.
- **Why held (this is the interesting one):** I applied `re.IGNORECASE`, and `--check` went **red** —
  it newly flags 5 agents on `opus`: `developer-tooling/build-systems-architect`,
  `esg-sustainability-reporting/ghg-accounting-analyst`, `game-development/gameplay-engineer`,
  `grants-management/grants-strategy-lead`, `trust-and-safety/abuse-detection-engineer`. Several are
  **architects / analysts / leads** whose descriptions merely *open* with a build-ish verb — i.e.
  false positives for a hard gate. This is exactly why the doctrine routes lowercase-prose
  `*-engineer`-on-frontier to the **`--report` pair-review queue for a human**, not `--check`. So the
  omission may be **deliberate**, and I reverted the change.
- **Recommendation (choose one):** (a) make only the `--report`/pair-review path case-insensitive so
  these surface for human tiering without hard-failing CI; **or** (b) if lowercase-build *should* be
  hard-gated, first tier each of the 5 agents (→ `sonnet`, or exempt with a reason in
  `tests/fixtures/model-tier-fit-exemptions.json`), then add `re.I` to `_IMPL_DESC`. Either way, the 5
  agents above want a per-agent tiering decision.

### 5. (P2/P3) Three tribunal-substrate hooks (`plugins/ravenclaude-core/hooks/`)

Confirmed by Lane B but **not** touched — editing the Thing's own substrate is tribunal-blocked in an
unattended session (and correctly so). Apply from a session with maintainer authority.

- **(P2)** [`enforce-layout.sh`](../../plugins/ravenclaude-core/hooks/enforce-layout.sh): the "jq not
  found" warning path is unreachable under the canonical stdin contract — the hook `exit 0`s before
  reaching its own warning when `jq` is absent and no legacy `$1` is supplied (a warn tier that
  reaches nobody — this repo's own documented failure class).
- **(P3)** [`guard-web-access.sh`](../../plugins/ravenclaude-core/hooks/guard-web-access.sh): an
  IPv6-literal host (`http://[::1]/x`) is mis-parsed by the `${host%%:*}` port-strip, so it can never
  match a configured `deny` entry (falls through to the normal ask-prompt, not an auto-allow — low
  severity).
- **(P3)** [`guard-premise.sh`](../../plugins/ravenclaude-core/hooks/guard-premise.sh): no `command -v
  python3` guard before its single `python3 -c` verdict; an entirely-absent `python3` fails open
  silently rather than honoring the file's own stated "BLIND → fail-closed" contract (python3 is a
  documented dependency, so low real-world likelihood).

### 6. Convention question — version bumps for README/CLAUDE.md count corrections

The D1–D7 doc fixes touch shipped plugin `README.md`/`CLAUDE.md` files. `AGENTS.md` rule 6 says "bump
the plugin's version on every user-visible change", but the 2026-09-22 run deliberately **skipped**
the bump for an identical count-fix to avoid the version-bump cascade (and, for `ravenclaude-core`, the
`generate-copilot-plugin.py` regeneration churn). This PR follows that precedent (no bumps).
**Question:** should documentation-accuracy corrections be exempt from the version-bump rule (with the
counts left to `check-marketplace-claims.py`'s post-merge self-heal), or do you want the bumps? A
one-line addition to the CHANGELOG convention in `AGENTS.md` would settle it.

---

## Panel artifacts

Full per-lane findings (reproduction commands, PLAUSIBLE items, and clean-lane notes) are in the
session run directory `.ravenclaude/runs/repo-review-2026-09-23/` (`panel1-A…D-*.md`, `decisions.md`)
— local-tier, not committed.

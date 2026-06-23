# Comprehensive repo review — 2026-06-16

Autonomous multi-panel review (scheduled routine). Panel 1 = three parallel
expert-review agents (core-engine Python/JS, hooks/shell, manifests/cross-refs);
Panel 2/3 = synthesis + independent re-verification of every finding by execution
before action. Branch: `claude/stoic-fermat-mtyjqy`.

## Headline

The repo is in **excellent mechanical health** — every defined gate is green
(JSON validity, version-drift, frontmatter, layout, marketplace-claims,
md-links, ruff, prettier, all 17 render/check scripts, all `*.py` compile, all
`*.sh` `bash -n`). The naive "tech-debt" signals (TODO markers, hooks "missing
`set -euo pipefail`") are **false positives or deliberate, documented choices**
(grep-for-TODO hooks; hooks that use `set -uo pipefail` precisely because they
inspect command exit codes; test harnesses that omit `set -e` to run all
assertions). The branch's apparent "51 commits ahead / no merge-base" vs
`origin/main` is a **shallow-clone artifact** (`.git/shallow` present; local
`origin/main` is a stale snapshot at PR #343), not a real divergence.

The genuine findings were **latent defects the gates cannot reach** — three of
them security fail-opens. The clearly-correct, contained ones are **fixed in this
PR** (below). The rest — needing a naming/API decision, eval-harness judgment, or
being latent/low-value — are itemized here with verified reproductions and
recommendations for your call.

---

## Implemented in this PR (verified by execution)

| # | Sev | Where | Fix |
|---|-----|-------|-----|
| 1 | P1 | `plugins/ravenclaude-core/hooks/route-decision-review.sh:139-` | Binding yes/no verdict mapped to an option **by index**, not semantics — `["Cancel","Proceed"]`/`["No","Yes"]` got a binding deny pointing at the **opposite** option (auto-resolved, so the human never saw it). Now maps by option polarity; ambiguous polarity fails safe to ALLOW. New reverse-ordered Gate 31 fixture. |
| 2 | P1 | `plugins/ravenclaude-core/scripts/thing-concerns.py` (`_match_variants`) | Catastrophe-floor `screen-always` hard rules (force-push, `curl\|sh`) bridge program→arg with `.*` but searched without `re.DOTALL` — a **newline (line-continuation)** between the program and the dangerous flag dodged the hard DENY. Now matches a newline-flattened variant (only ever ADDS a match). New Gate 15 fixture. |
| 3 | P1 | `scripts/process-scenario-submission.py:~219` | External-intake secret/PII gate scanned the **raw** field but the staged file is written from NFKC-normalized + `Cf`-stripped text — a zero-width-split `ghp_…` / fullwidth `ＡＫＩＡ…` passed the gate then reconstructed intact into the quarantine file. Now gates on the same normalized text it stages. |
| 4 | P2 | `plugins/finance/hooks/flag-finance-anti-patterns.sh:74` | Credit-card PAN check used PCRE `(?:…)` under `grep -E` → `warning: ? at start of expression`, **matched nothing** (fail-open PII check). Switched to plain ERE groups. |
| 5 | P2 | `plugins/regulatory-compliance/hooks/scrub-confidential-pre-write.sh:81` | Same PCRE-in-ERE fail-open in the SAR/STR-adjacent PII scrub. Same fix. Verified it now flags a 16-digit Visa with no false positive on a clean file. |
| 6 | P1 | `plugins/ravenclaude-core/scripts/apply-comfort-posture.py` (`_split_scalar_kv`) | PyYAML-less fallback parser split a quoted override key on its **inner** colon (`"Bash(ls:*)": deny` → key `"Bash(ls`), aborting `/set-posture` on a no-PyYAML consumer. Now quote-aware. Dormant here (PyYAML present). |

Version bumps (patch — all bugfixes): `ravenclaude-core` 0.157.0→**0.157.1**,
`finance` 0.14.0→**0.14.1**, `regulatory-compliance` 0.12.0→**0.12.1** (mirrored
in `marketplace.json`; CHANGELOGs updated). `process-scenario-submission.py` is
repo intake infrastructure (no plugin version).

> **⚠ Security-floor changes — please get `security-reviewer` eyes before merge.**
> Findings **1, 2, 3** touch the decision-review tribunal, the command-review
> catastrophe floor, and untrusted external intake respectively. Each fix only
> ever **closes** a hole (never relaxes a deny / never widens what stages), and
> each is covered by a fixture, but they are exactly the surfaces the constitution
> says should not change without a security pass.

---

## Follow-up — formerly-deferred items, now resolved

All five deferred items were actioned in a second commit on this branch (at the
owner's instruction "fix the items that still need fixing and then merge"). One —
D3 — was **not** changed because its recommended fix turned out to be wrong on
review (documented below); the rest are fixed.

### D1 (P2) — cross-plugin agent name collision: `partner-success-manager` — **FIXED**

Two plugins shipped an agent with the same `name:` — `ravenclaude-core` (generic,
`sonnet`) and `edtech-partner-success` (EdTech, `opus`) — colliding in the
subagent registry when both are enabled. **Fix:** `ravenclaude-core` keeps the
domain-neutral name (house rule #1); the EdTech agent was renamed to
`edtech-partner-success-manager` (file + `name:` + all `works_with` / `primary_agent`
/ prose references within the plugin; core-path references preserved). Because
core *keeps* the generic name, every external/doc reference still resolves. A new
**cross-plugin agent-name-uniqueness check** was added to `check-frontmatter.py`
(with a verified teeth-test). `edtech-partner-success` bumped 0.12.0 → 0.12.1.

### D2 (P2) — eval-harness stats under-count agents — **FIXED**

`rc-deep-research.js` (both byte-identical copies) now accumulates a real
`verifyAgentsFired` counter (`voteCount + escalation` per claim) and uses it in
place of `voted.length * VOTES_PER_CLAIM` at all four count sites. Baseline
(uniform policy, no escalation) yields the identical number, so no eval baseline
shifts; non-uniform policies now report accurately. Gate 52 (disabled-floor
opts-by-reference) is untouched and still green. Verified CI-safe: no gate runs
the eval grader, and the count semantics aren't asserted by any fixture.

### D3 (P2) — oversize non-Bash payload skips `_screen_always` — **NOT CHANGED (recommendation was wrong)**

On closer analysis the suggested "run `_screen_always` unconditionally" fix is
**unsafe**: when a payload is oversize, `screened` for a **file** shape is the
full file *content* (`"<path>\n<content>"`), so always-screening it would scan
large file bodies for shell-command patterns — creating **false-positive
hard-denies** (a doc file that merely contains the text `curl x | sh`) plus a
perf hit on >1 MiB files. The current skip is correct because (a) Bash command
screening is never gated by `payload_too_large`, and (b) the load-bearing
*path-based* substrate self-disable (`screen_substrate_path`) already runs
**unconditionally** at line 1160. No change made; the code is right as-is.

### D4 (P2) — `check-run-actions-argv.py` `-c` detection bypassable — **FIXED**

The check now rejects any `-c`-bearing short-flag cluster (`-c`/`-lc`/`-ec`/
`--login -c`, at any index) when argv[0] is a shell, not just the exact `-c` at
index 1. Verified: the real `RUN_ACTIONS` still passes; `bash -lc`, `sh -ec`, and
`bash --login -c` are all now caught.

### D5 (P3) — minor items — **FIXED**

- **`guard-destructive.sh`** — the `git push … -f` pattern was anchored so `-f`
  must be a standalone flag, not a branch name ending in `-f`. Force pushes
  (`-f`, `--force`) still blocked; `git push origin feature-f` no longer false-flags.
- **`two-panel-plan-review.js`** (both copies) — each result is now paired with
  its lens key before `filter(Boolean)`, so a null panel result can't misalign the
  surviving lens labels.
- **`thing-decision.py`** — `_posture_write_disables` now mirrors
  `thing_enabled_for`'s truthiness exactly, catching `thing: 0`/`"0"`/`disabled`/
  `none` self-disable writes (not just `off`/`false`/`no`); and the seat/panel
  timeout config now excludes `bool` so `seat_timeout_seconds: true` isn't coerced
  to a 1-second timeout.
- **`check-md-links.py`** — `LINK_RE` now captures one level of balanced parens in
  a target (`Foo_(bar)`), and the gate still passes on the full corpus.

---

## Verified sound (attacked, held up)

For the record, these were specifically probed and are **not** defective:
`thing-decision.py` Bash hard-deny / `pre_llm_deny` beating bypass+cache / the
`git -D` and `network_write` re-route overrides / MCP allowlist write-deny /
substrate self-disable incl. hardlink; `apply-comfort-posture.py` old-vs-new
posture diff + `security_deny` floor union/strip; `rc-deep-research.js`
disabled-dispatch byte-identical opts-by-reference + knob fallback;
`reset-plugin-cache.py` atomic swap + rollback; the WebFetch sanitizer / content
SSRF + size caps; `pseudonymize-brief` Luhn gating + round-trip; and the core
security guards (`guard-destructive` / `guard-web-access` / `enforce-layout` /
`runaway-brake`) deny-ordering and fail-closed posture.

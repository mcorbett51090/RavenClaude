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

## Deferred — needs your decision or judgment

### D1 (P2) — cross-plugin agent name collision: `partner-success-manager`

Two plugins ship an agent with the **same** `name:` —
[`plugins/ravenclaude-core/agents/partner-success-manager.md`](../plugins/ravenclaude-core/agents/partner-success-manager.md)
(domain-neutral, `model: sonnet`) and
[`plugins/edtech-partner-success/agents/partner-success-manager.md`](../plugins/edtech-partner-success/agents/partner-success-manager.md)
(EdTech-specialized, `model: opus`). With both plugins enabled, Claude Code's
subagent registry has a name clash and the orchestrator can't deterministically
route. No gate catches this (`check-frontmatter.py` validates each file
independently; there is no cross-plugin uniqueness check).

**Why deferred:** renaming a **shipped agent's public identity** is a
consumer-visible API change (muscle memory, any scripted invocation) and a
naming decision, not a rule-derivable bugfix.

**Recommendation:** keep the generic name on the core agent (house rule #1 — core
owns the domain-neutral name) and rename the EdTech one to
`edtech-partner-success-manager`, updating the `works_with` references in its
sibling agents; bump `edtech-partner-success` with a migration note. **Then** add
a cross-plugin agent-name-uniqueness check to `check-frontmatter.py` so the class
can't recur. I can implement this on your go-ahead.

### D2 (P2) — eval-harness stats under-count agents — `rc-deep-research.js`

`.claude/workflows/rc-deep-research.js` (lines ~1131, 1313, 1395, 1410) reports
`agent_count`/phase counts as `voted.length * VOTES_PER_CLAIM` (a flat constant),
but the verify phase actually fans out `resolveVerifyVotes(claim)` **per claim**
and never counts escalation votes. When `verify_policy` is non-uniform the eval
grader's token-bucket attribution is wrong. **Research results are unaffected —
only the reported stats.** Passes the baseline gate because baseline policy is
uniform (all 3). **Recommendation:** accumulate the real count
(`claimTierAudit.reduce((n,r)=>n+r.votes_fired,0)`). Deferred because it touches
the eval-harness contract — wants eval-harness eyes, and the bundled-skill mirror
must stay byte-identical.

### D3 (P2) — oversize non-Bash payload skips `_screen_always`

`plugins/ravenclaude-core/scripts/thing-decision.py:~1150` —
`if not payload_too_large: result.update(_screen_always(screened))`. On an
oversize (>1 MiB) non-Bash payload the category-independent self-disable +
hard-rule screen is skipped; `_screen_always` only scans the reviewed
command/URL/path (not the bulk content), so there is **no cost reason** to skip
it. No concrete exploit today (the hard-rule concerns are Bash-shaped and the
file-shape self-disable is still caught unconditionally by `screen_substrate_path`),
so this is defense-in-depth erosion. **Recommendation:** run `_screen_always`
unconditionally, or move the `payload_too_large` fail-closed deny above the
enabled-gate.

### D4 (P2) — `check-run-actions-argv.py` `-c` detection bypassable (latent)

`scripts/check-run-actions-argv.py:131` enforces "no shell `-c`" with
`if i == 1 and lit == "-c"` — only the exact token at exactly index 1. `bash -lc`,
`sh -ec`, and `bash --login -c` (where `-c` is index 2) all pass. **Latent** — the
gate guards an internal committed constant (`RUN_ACTIONS`), not untrusted input,
so the blast radius is "a future maintainer edit ships green." **Recommendation:**
for `bash`/`sh` launchers, reject any subsequent arg matching `^-[a-z]*c[a-z]*$`.

### D5 (P3, low) — minor, fail-safe or no-current-trigger

- `plugins/ravenclaude-core/hooks/guard-destructive.sh:142` — `git push … -f`
  pattern over-matches a branch ending in `-f` (e.g. `git push origin feature-f`).
  **Fails closed** (a benign push is blocked, never a destructive one allowed),
  so it's a rare false positive, not a hole. Recommend: leave as-is (fails safe)
  or anchor the short-flag form. **Do not loosen the force-push guard for a
  cosmetic FP without review.**
- `scripts/two-panel-plan-review.js:~430,577` — `panel.filter(Boolean)` then
  indexing `lenses[i]` by compacted position mislabels surviving lens results if
  a panel agent returns null. Fix: pair `{result, lens}` before filtering.
- `plugins/ravenclaude-core/scripts/thing-decision.py:~617` — `_posture_write_disables`
  misses non-canonical falsy `thing` values (`"0"`, `disabled`) that
  `thing_enabled_for` treats as off; `:760,762` accept `bool` as int for timeout
  config (`isinstance(True, int)`).
- `scripts/check-md-links.py:36` — `LINK_RE` misses links whose text contains
  nested `[]` and truncates targets containing `(`. No current doc triggers it.

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

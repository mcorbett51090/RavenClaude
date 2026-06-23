# Repository review — 2026-06-18 (multi-panel, autonomous fixes)

Three-panel review (expert fan-out → validation → tie-break) with autonomous fixes for the
unambiguous items. **Every objective gate was green going in** (JSON validity, version-drift,
shell syntax, prettier whole-tree, ruff, frontmatter, layout allow-list, md-links,
marketplace-claims, mcp-attribution, the full `audit-gates.sh` meta-test, and the dashboard
render/parity gates). The panels surfaced correctness/security defects the gates can't see —
because no gate inspects regex *semantics* inside an advisory hook, or runtime behavior of the
`scripts/*_calc.py` family, or doc-count phrases the claims-gate doesn't cover.

This doc records: **(A)** what was fixed in the accompanying PR, and **(B)** the items left for
your design input, each with a code link, the concrete impact, a recommendation, and why it
wasn't auto-fixed.

---

## A. Fixed autonomously in this PR (verified this session)

Grouped by priority. Each fix was reproduced before and verified after.

### P0 — security: PII credit-card scrubber silently missing cards

- **`plugins/regulatory-compliance/hooks/scrub-confidential-pre-write.sh:81`** — the credit-card
  PAN detector used PCRE non-capturing groups `(?:…)` inside `grep -Eni` (POSIX ERE). GNU `grep -E`
  misparses `(?:…)` (emits `warning: ? at start of expression` to suppressed stderr and drops the
  group), so **16-digit Visa (`4111111111111111`) and every Discover PAN slipped past** the
  pre-write confidentiality scrubber — the one check the hook's own docstring calls out as
  "false negatives are expensive (leak PII)." Fixed to pure POSIX ERE (`(?:…)` → `(…)`), which
  matches all five issuer shapes with no `grep -P` dependency (important: `grep -P` is absent on
  macOS/BSD, and this hook ships to consumers).

### P1 — security + correctness

- **`plugins/finance/hooks/flag-finance-anti-patterns.sh:74`** — same dead `(?:…)` PAN regex,
  same portable-ERE fix. (Finance's plaintext-PII card check.)
- **`plugins/applied-statistics/scripts/stat_calc.py:135`** — `samplesize --kind proportion
  --mde 0` raised an uncaught `ZeroDivisionError` traceback (`n = (numer / (p1 - p2)) ** 2` with
  `p1 == p2`) instead of the script's own `return 2` error path. Added an explicit `--mde != 0`
  guard, matching the existing `--d <= 0` guard on the mean branch.
- **`plugins/aws-cloud/scripts/aws_cost_estimator.py:197`** — the `rightsize` subparser froze
  `--hours` `default=HOURS_PER_MONTH` (730.0) at parser-build time, so the global
  `--hours-per-month` override (applied in `main()` after `parse_args`) never reached it —
  `--hours-per-month 100 rightsize …` silently still computed at 730 hr. Changed the default to
  `None` and resolved it at runtime in `cmd_rightsize` (explicit `--hours` still wins).

### P2 — security

- **`plugins/ravenclaude-core/scripts/pseudonymize-brief.py:168`** — the token→value map (the one
  artifact holding cleartext PII) was written with default `0644`. On a shared host the SSN/card/
  email map was world-readable for the scratch dir's lifetime. Now created `0600` via `os.open`
  (not a post-write `chmod`, so there is no brief world-readable window).

### P3 — doc accuracy (gate blind-spots)

- **`.claude-plugin/marketplace.json:8`** — `metadata.description` said "99 domain plugins"; the
  real count is **100** (101 total − core). Not gated (`check-marketplace-claims.py` validates the
  README "ships **N plugins**" claim, which is correct at 101, but not this phrase).
- **`README.md:172`** — "98 of the 99 plugins declare `requires.ravenclaude-core`" → corrected to
  "All 100 non-core plugins declare a `requires.plugins` dependency on `ravenclaude-core`"
  (verified: 100/100 declare it; the field path is `requires.plugins`, not `requires.ravenclaude-core`).
- **`README.md:391`** — "one of the 99 plugins above" → "one of the 101 plugins above".

> The audit agents also confirmed **no version drift**, all 101 plugins carry the three required
> files, all 96 `hooks.json` resolve to existing executable scripts, and the 7 zero-match layout
> globs are intentional (gitignored runtime paths + forward-looking permissions) — no action.

---

## B. Follow-up: all items below now IMPLEMENTED (2026-06-18)

> The items in this section were originally deferred for design input. On a follow-up
> pass they were all implemented in this same PR. Each entry keeps its original
> description; the **✅ Resolved** line records what was done.
>
> - **B1** ✅ converted all 14 dead `grep -E` lines across 12 hooks to `grep -Pzi` (PCRE +
>   NUL-multiline — semantics-exact, verified flagging + cross-line) **and** added a CI
>   guard (`scripts/check-grep-ere-pcre.py`, audit-gates **Gate 104** + a direct
>   validate-marketplace step) so the whole class can't regress.
> - **B2** ✅ both team-portfolio renderers now `sanitize_events()` at the load point —
>   a malformed event is dropped with a stderr warning (the documented fail-soft posture,
>   house opinion #5), never crashes the render.
> - **B3** ✅ `reset-plugin-cache.py` — EXDEV cross-mount swap now stages onto the target
>   filesystem then atomic-renames; the snapshot is cleaned up on a rolled-back swap
>   (kept only when it's the sole recovery anchor); newest-version selection is semver, not
>   lexical. Gate 44 still green.
> - **B4** ✅ `sanitize-webfetch-body.py` now resolves + root-contains **every** input
>   (absolute *and* relative), closing the relative-path gap.
> - **B5** ✅ data-platform `>30m JWT` regex now catches round tens (40m–90m) + 3-digit
>   minutes; edtech-psm Check 5 fires again (over-broad `key: value` qualifier removed,
>   plus a second never-fired `\<…\>` word-boundary bug the fix surfaced).
> - **B6** ✅ `portfolio-collect.parse_iso` coerces tz-less timestamps to UTC (no more
>   `TypeError`); `knowledge-health._bucket` caps the due-soon window at half the threshold
>   (no more negative lower bound flagging every fresh file). reset-plugin-cache lexical
>   version sort fixed under B3.

## B (original). Needs your design input (not auto-fixed)

### B1. (P1) Systemic dead-regex in the advisory anti-pattern hook family

**Same root cause as the two P0/P1 security fixes, but across ~12–24 *advisory* hooks.** GNU
`grep -E` is POSIX ERE and does not support PCRE lookahead `(?!…)`, non-capturing `(?:…)`, or
`[\s\S]`. Every such line prints a suppressed warning and returns "no match" on **all** input — the
check is dead, and a clean run looks like a pass (false assurance). Verified-dead examples:

- `plugins/backend-engineering/hooks/check-backend-engineering-anti-patterns.sh:12,15,18,21`
- `plugins/database-engineering/hooks/check-database-engineering-anti-patterns.sh:15,18`
- `plugins/cloud-native-kubernetes/hooks/check-cloud-native-kubernetes-anti-patterns.sh:18,21`
- `plugins/terraform-iac/hooks/check-terraform-iac-anti-patterns.sh:18`,
  `plugins/ml-engineering/hooks/check-ml-engineering-anti-patterns.sh:15`,
  `plugins/gcp-cloud/hooks/check-gcp-cloud-anti-patterns.sh:21`
- …plus ≥1 dead line each in `mobile-engineering`, `data-governance-privacy`,
  `analytics-engineering`, `experimentation-growth-engineering`, `product-management`,
  `technical-writing-docs`, `security-engineering`, `web-design`, `salesforce`.

**Why not auto-fixed:** two sub-classes need different treatment. The `(?:…)` ones convert
mechanically to `(…)` (semantics preserved) — safe to batch. The `(?!…)` lookahead ones express
"pattern X present **and** pattern Y absent," which a single ERE line genuinely cannot do; fixing
them right means restructuring each into two greps (`grep -q X && ! grep -q Y`), which is a
per-hook semantic judgment (what exactly should fire, and at what false-positive cost). These are
advisory (don't block), so the blast radius is false assurance, not a leak — lower urgency than the
two security PAN hooks already fixed.

**Recommendation:** (1) approve a batch PR converting the `(?:…)`-only hooks to plain ERE; (2)
triage the `(?!…)`/`[\s\S]` hooks one at a time; **(3) add a CI guard** — a `grep` over the hook
corpus for `grep -E.*(\(\?[:!=]|\[\\s\\S\])` — so the whole class can never regress (`bash -n`
passes dead regexes today, which is why this slipped in). This is the highest-leverage systemic fix.

### B2. (P1) team-portfolio renderers crash on a malformed event

`plugins/team-portfolio/scripts/portfolio-dashboard.py:80,129,184,188,190` and
`portfolio-report.py:53,112,123,136,140` index `event["type"]` / `event["repo"]` directly, so one
malformed event (hand-edited artifact, schema drift) aborts the whole render — violating the
plugin's documented fail-soft posture.

**Why not auto-fixed:** the fix is `.get()`, but the *desired* behavior for a malformed event is a
design choice — skip it silently, label it `unknown`, or warn to stderr and continue? Your call on
the posture before I apply it across both files.

### B3. (P2) `reset-plugin-cache.py` cross-filesystem rename + orphaned snapshot

`plugins/ravenclaude-core/scripts/reset-plugin-cache.py:157` — `os.rename(fresh_tree, version_dir)`
raises `EXDEV` when the fetched fresh tree (`/tmp` clone) and the cache (`~/.claude`) are on
different filesystems, so `--execute` can never succeed cross-mount (always
`RAGNAROK_ATOMIC_SWAP_PARTIAL`); separately the snapshot dir (line 148) is orphaned on the rollback
path. Fix: stage into `version_dir.parent` (same FS) then rename, or `shutil.move` on `EXDEV`; clean
up the snapshot in rollback.

**Why not auto-fixed:** this is the high-blast Ragnarök DR engine — its two-rename atomic-swap is a
deliberate safety envelope (snapshot → verify-with-`audit-gates` → swap → rollback). Changing the
swap mechanics touches that envelope and should go through `security-reviewer` + a Gate 44 fixture
update, not an autonomous edit.

### B4. (P2) `sanitize-webfetch-body.py` relative-path containment is weaker than its contract

`plugins/ravenclaude-core/scripts/sanitize-webfetch-body.py:127-145` — the stated contract ("reads
only an argv path under the repo root") is enforced for *absolute* inputs but not *relative* ones:
the `..` and `relative_to(repo_root)` containment checks are gated on `p.is_absolute()`, so a
relative path gets only a literal-`..` substring guard, no resolved-root containment. Read-only blast
radius keeps it P2. Fix: `resolve()` every input and assert `relative_to(repo_root.resolve())`
uniformly.

**Why not auto-fixed:** it's a security-boundary sanitizer; the hardening is straightforward but
should land with `security-reviewer` eyes and a containment test, not silently.

### B5. (P2) Two unique advisory-hook regex logic bugs

- `plugins/data-platform/hooks/flag-data-platform-smells.sh:78` — the ">30-minute JWT" filter
  `([3-9][1-9]m)` requires a non-zero *second* digit, so round values `40m/50m/60m/70m/80m/90m`
  are all missed (only `31m`, `45m` fire); the common `expiresIn: '60m'` slips through.
- `plugins/edtech-partner-success/hooks/flag-psm-anti-patterns.sh:112-132` — Check 5's "qualified"
  heuristic `…|:[[:space:]]+[A-Za-z]` matches *any* `key: value` line (including `status: red`),
  so the red/yellow-without-named-signals check auto-qualifies everything and never fires.

**Why not auto-fixed:** advisory-only, and best landed together with the B1 hook sweep.

### B6. (P3) Minor

- `reset-plugin-cache.py:79` — "newest version" uses lexical sort (`0.9.0` > `0.120.0`); on
  `--execute` with multiple cached versions it could operate on the wrong dir. Use an int-tuple
  semver key.
- `portfolio-collect.py:204` — `parse_iso` returns naive datetimes for tz-less timestamps →
  `TypeError` vs the tz-aware `since` (won't fire against GitHub `Z` timestamps; only hand-edited
  artifacts).
- `knowledge-health.py:107` — `due_soon` window hardcoded to 30 days regardless of
  `--threshold-days`; with a threshold < 30 the lower bound goes negative and every fresh file
  reports `due_soon`.
- **Recommendation:** extend `scripts/check-marketplace-claims.py` to also assert the
  `marketplace.json` `metadata.description` "N domain plugins" phrase against `len(plugins) - 1`,
  so the A-tier count fix can't silently drift again.

---

## Cleared as non-bugs (checked, no action)

`guard-destructive.sh` normalization/ordering; `_scrub.sh -p` pattern (redacts
`mysql -phunter2…`, leaves `ssh -p 22222`); `route-decision-review.sh` injection hardener;
`archive-branch.sh` tag→push→delete ordering; `cleanup-branches.sh`'s direct `git branch -D`
(by-design — the guard only sees the outer `bash …`); `worktree-*.sh` slug validation;
`evm_calc.py` / `recon_diff.py` / `slo_calc.py` arithmetic; the antipattern hooks flagged by a
naive `head -5` "no `set -euo pipefail`" scan (false positive — they carry it *after* their long
header comments). devcontainer.json "invalid JSON" is JSONC-with-comments (expected; CI doesn't
strict-parse it).

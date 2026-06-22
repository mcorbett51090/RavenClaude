# Repo review — 2026-06-14 (multi-panel)

A three-panel review (expert scan → analysis/validation → tie-break) over the whole
marketplace: all CI gates, ~140 Python + ~143 shell scripts, the 101 plugin manifests,
and the generated-artifact pipeline. This doc records (a) what was **fixed directly** in
the accompanying PR, and (b) the items that **need a decision from Matt** before
implementing, with a recommendation for each.

The starting state was actually **CI-red on a clean tree**: `scripts/audit-gates.sh` Gate
99 (`feedback-report freshness, clean tree`) was failing because the committed
`feedback-report.html` had drifted from the scenario corpus. That, plus a latent
PII-detection bug, is why this review produced shippable fixes rather than a clean bill.

## Method

- **Panel 1 (expert scan, parallel):** four lighter agents swept Python scripts, shell
  scripts/hooks, plugin manifests/consistency, and the domain anti-pattern hooks. Each
  returned `file:line`-grounded findings tagged P0–P3.
- **Panel 2 (validation):** every consequential claim was re-checked against the actual
  code before acting. This caught a false finding — the README "16 hooks" claim was
  reported as stale, but 16 is the correct count of hooks **registered in
  `hooks.json`** (the agent counted 17/19 `.sh` files including two `_`-prefixed
  helpers). Only "40 skills" was actually stale (→ 43).
- **Panel 3 (tie-break):** applied to the one genuinely ambiguous class — the
  PCRE-lookahead dead checks — where the *fix approach* (not the diagnosis) carries a
  real tradeoff. Conclusion: defer the approach choice to Matt (below).

---

## Fixed directly in the PR (no design input needed)

Grouped by priority. Each was verified before and after the change.

### P0
- **`scripts/generate-bi-report.py:101` — `band_of` tuple-unpack crash.** A hand-authored
  `bi-report/data.json` with a malformed band (`"green": 90`, or a 3-element list) crashed
  the whole report build via `ValueError: not enough values to unpack`. Now tolerates a
  malformed band and skips it. Output byte-identical on valid input (bi-report freshness
  gate still passes).

### P1
- **`feedback-report.html` stale → CI red (the original headline).** **Superseded on
  `main`** — between this review and the branch rebase, `main` independently fixed the
  staleness (commit `1460a84`) and added `feedback-report.html` to the
  `regenerate-artifacts.yml` self-heal (it chose to **keep** the PR-time Gate 99 as a teeth
  check rather than relocate it). This branch therefore **drops** its feedback-report regen
  + gate-relocation entirely and defers to main's design. Listed here for the record only.
- **Credit-card PAN check fail-open in two PII hooks** (`regulatory-compliance` /
  `finance`). The regex used PCRE non-capturing groups `(?:…)` inside a POSIX-ERE
  `grep -E`, so **Visa and Discover PANs were never detected** and `grep` warned to stderr
  on every run. The regulatory hook is designed to be flipped to `exit 2` to **block**
  SAR/STR writes, so this was a fail-open confidentiality gap for 2 of 4 card brands.
  Rewrote the two groups as ERE-safe capturing groups; all four brands now match, no
  stderr noise. Both plugins version-bumped (`finance` 0.14.1, `regulatory-compliance`
  0.12.1) with CHANGELOG entries.
- **`scripts/render-concepts.py:92` — unguarded `re.match(...).group(1)`.** mermaid-cli can
  emit a leading `<?xml?>`/comment before `<svg>`, making `re.match` return `None` →
  `AttributeError` aborting the render. Added the same `if not m: return svg` guard the
  sibling `render-trees.py` already has.
- **`scripts/generate-bi-report.py` — `c["key"]` `KeyError` + unknown-band donut
  corruption.** A `columns[]` entry with a `type` but no `key` crashed `_render_table`; a
  partner with an out-of-set `band` ("amber") silently made the donut segments not sum to
  total. Both now degrade gracefully. Output byte-identical on valid input.
- **`scripts/eval-adaptive-classifier.py:720` — bracket access on a fixtures key** crashed
  report emission *after* the (possibly paid Batch-API) grading completed. → `.get(...)`.
- **`README.md` stale counts** (recomputed against the rebased tree — `main` has since
  grown to **117 plugins**): `40 skills` → `43`; `98 of the 99 plugins` → `116 of the 117`;
  `99 plugins` → `117`. ("16 hooks" was left as-is — it is correct; see Panel 2 above.)

### P2
- **`scripts/content-scan.py:75` — userinfo host-spoof.** `_host` used `urlparse().netloc`,
  which keeps userinfo, so `https://linkedin.com@evil.com/x` yields host
  `linkedin.com@evil.com` and could satisfy a never-fetch/allow membership test against an
  attacker-controlled host. → `.hostname` (strips userinfo/port).
- **`scripts/generate-feedback-report.py:531` — unguarded `read_text`** on the `--check`
  gate path crashed on a corrupt/non-UTF-8 committed file instead of reporting "stale". →
  try/except → treat as stale.
- **`scripts/generate-bi-report.py:469` — `dq` mutated the parsed-JSON list in place**
  (duplicate banner flags accumulate across calls on the same dict). → copy.

### P3
- **`scripts/worktree-clean.sh` — `--help`/`-h` exited 2** (failure) instead of 0. Split
  the empty/invalid case (still exit 2) from an explicit help request (now exit 0).

---

## Needs a decision (not implemented — recommendation attached)

### D1 — PCRE negative-lookahead `(?!…)` under `grep -E`: ~18 dead anti-pattern checks across 14 plugins (P1)

**Finding (verified live against GNU grep 3.11):** 14 domain anti-pattern hooks embed a
Perl negative-lookahead `(?!…)` inside a `grep -nEi` (POSIX ERE). GNU grep does not
support lookahead in ERE — it prints `? at start of expression` to stderr and the group
matches **nothing**, so each affected check **never fires on the anti-pattern it exists to
catch**. Representative: `plugins/database-engineering/hooks/check-database-engineering-anti-patterns.sh:15`
(`create\s+index\s+(?!concurrently)` flags nothing). Affected files (line):

```
database-engineering:15,18   cloud-native-kubernetes:18,21   backend-engineering:12 (partial)
ml-engineering:15   product-management:18   technical-writing-docs:15   gcp-cloud:21
data-governance-privacy:15   terraform-iac:18   experimentation-growth-engineering:18
mobile-engineering:15   analytics-engineering:15
```

Many also use `[\s\S]{0,N}` cross-line context, which can't match in line-based `grep`
either — so even after fixing the lookahead, the multi-line intent won't work without
restructuring. **Why CI didn't catch it:** `audit-gates.sh` Gate 30 exercises only **one**
working check per hook, never these.

**The decision (this is why it's deferred, not the diagnosis):** the fix approach has a
genuine portability tradeoff and a blast radius.

| Option | Pros | Cons |
|---|---|---|
| **A. Switch to `grep -P` (PCRE)** | One-line per check; preserves intent incl. lookahead | `grep -P` is **not** available on BSD/macOS grep — would error for consumers on a Mac. Hooks are advisory (exit 0) so it won't block, but it's noisy and still doesn't fire. |
| **B. Restructure to positive-match + absence test** (`grep X && ! grep Y`, the pattern these same files already use elsewhere) | Cross-platform; matches existing idiom | More work per check; line-based so genuine cross-line checks need rethinking or dropping. |
| **C. Leave dead, document** | No version churn | Ships known-inert advisory checks. |

Also entailed: **14 plugin version bumps** (+ 14 CHANGELOG touches + marketplace.json), and
**expanding Gate 30** to assert each previously-dead check fires on a known-bad fixture (so
this can't regress). That fixture work is itself non-trivial.

**Recommendation:** **Option B**, batched as its own PR (one plugin family at a time so
each gets a fixture in Gate 30), because these are advisory hooks and cross-platform
correctness matters more than preserving the lookahead. I did **not** unilaterally pick A
(could break Mac consumers) or do a 14-file restructure without per-check fixtures (would
risk silently swapping one broken check for another). **Question for you:** B as a
follow-up PR — agree? Or accept A's macOS caveat for speed?

### D2 — `regulatory-compliance` PII scrubber ships **fail-open** by default (posture, not a bug)

`scrub-confidential-pre-write.sh` is **advisory (`exit 0`)** by default; the header and
`CLAUDE.md §7` document flipping the bottom `exit 0` → `exit 2` per engagement to actually
**block** a PII/SAR write. That is the designed, documented behavior — not a defect — but
it means a consumer who installs the plugin and drafts an SAR gets warnings, not blocking,
unless they hand-edit the script.

**Question for you:** should SAR/STR-bearing paths ship **blocking (`exit 2`) by default**,
with an opt-*out* for advisory mode (invert the current default)? It's a real posture call
— fail-safe-by-default vs. don't-surprise-the-consumer — so I'm leaving it to you rather
than routing it through the tribunal.

### D3 — Low-priority robustness items left for a follow-up (implementable, low value/risk now)

- `scripts/check-marketplace-claims.py:90` — skill-count counts every non-dotfile under
  `skills/`; a future `skills/README.md` (layout-allowed) would inflate it. No such file
  exists today, so it's latent. Deferred because it edits a **gate's** counting logic with
  zero current trigger — wants its own change + fixture.
- `scripts/generate-dashboards.py:1549` — tree "When this applies" is extracted from a
  fixed `section[:600]` window; a marker past offset 600 yields empty. Deferred because it
  could shift `dashboard.html` bytes and the freshness gate, so it belongs with a
  regenerate step, not bundled here.
- Assorted P3s (`check-md-links.py` regex truncates targets containing a literal `)`;
  default-encoding `read`; a couple of fixture-shape assumptions in eval scripts). Cosmetic
  on Linux CI.

---

## Verification run for the PR

Re-run after the rebase onto current `main` (note: this branch now defers feedback-report
/ audit-gates / index+dashboard ownership to `main`, and `finance` is bumped to **0.14.2**
to clear a same-version collision with main's 0.14.1):

`ruff` ✓ · `prettier --check .` ✓ · JSON validity ✓ · version-drift ✓ ·
`check-marketplace-claims` ✓ · `check-md-links` ✓ · `check-frontmatter` ✓ ·
`bi-report`/`render-concepts` freshness ✓ · both PII hooks now flag Visa+Discover with no
stderr noise ✓ · `audit-gates.sh` ✓ (main's design, unchanged by this branch).
</content>
</invoke>

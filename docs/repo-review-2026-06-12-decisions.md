# Repository review — 2026-06-12 (multi-panel) — findings, fixes, and decisions

**Scope:** full-repo review requested as a three-panel exercise (expert review → analysis/validation → tie-break), followed by autonomous implementation of every issue that did **not** require design input, and this summary for the issues that do.

**Headline:** the repo is in excellent health. Every standing validator passes — JSON validity, layout (`check-layout --all`: 7 087 files), frontmatter gate, markdown links, prettier (whole-tree), ruff, marketplace-claims, mcp-attribution, lineup-citations, run-actions-argv, dashboard-server-parity, Ragnarök. The only material findings came from the **gate-audit meta-test** (`scripts/audit-gates.sh`) and a **cross-plugin grep sweep** that the gates don't cover. Two were rule-derivable and have been fixed autonomously; the rest are genuine judgment calls and are queued below for your decision.

---

## Method — how the three panels were run

The "expert panel" here is the repo's own falsifiable infrastructure plus targeted inspection — that is the highest-signal review surface for a marketplace this size (102 plugins, ~141 Python + ~142 shell scripts, 5 565 markdown files), and unlike opinion it produces reproducible evidence.

- **Panel 1 (review):** ran the full validation suite from `AGENTS.md` + `scripts/audit-gates.sh`, then swept for bug patterns the gates don't catch (broken regexes, bare `except`, missing `set -euo pipefail`, TODO/FIXME markers).
- **Panel 2 (analysis):** for each finding, reproduced the failure, isolated the **mechanical cause** (vs. symptom), and assessed blast radius + effort.
- **Panel 3 (tie-break):** applied the repo's own rule — _rule-derivable → fix autonomously; genuine preference / behavior-risk → defer to Matt_ (the tribunal/decision-review posture in `CLAUDE.md`). Items where the "right" answer depends on intent are below, not silently chosen.

---

## Issues by priority

| ID  | Priority | Issue                                                                                  | Disposition          |
| --- | -------- | -------------------------------------------------------------------------------------- | -------------------- |
| F1  | **P1**   | `audit-gates.sh` Gate 47 (`validate-schemas`) has no tool-absence guard for `jsonschema` | ✅ Fixed in this PR  |
| F2  | **P1**   | CI (`validate-marketplace.yml`) runs `audit-gates.sh` but never installs `jsonschema`    | ✅ Fixed in this PR  |
| F3  | **P2**   | 20 antipattern hooks use a broken `grep -E` regex (`\|` is a literal pipe)               | ✅ Fixed in this PR  |
| D1  | **P3**   | 3 ravenclaude-core hooks lack `set -euo pipefail`                                         | ⏸ Needs decision    |
| D2  | **P3**   | No gate pins the antipattern-hook regex to its canonical form (F3 can silently recur)    | ⏸ Needs decision    |

---

## Fixed autonomously (rule-derivable, behavior-preserving)

### F1 — Gate 47 mis-reports a missing tool as a fixture failure (P1)

**Cause.** Gate 47 shells out to `python3 -m jsonschema …` against the `{good,bad}-{plugin,marketplace}.json` fixtures. When the `jsonschema` module is absent (a common local condition — it is **not** a default Python dep), the command exits 1 with `ModuleNotFoundError`. The gate read that as a verdict, so:

- the two **`must_pass`** "good fixture" checks reported as **FAILURES** (false alarm), and
- the two **`must_fail`** "bad fixture" checks **"passed" for the wrong reason** — a module error, not a schema rejection (false confidence).

Both are exactly the silent-miscategorization that this meta-test exists to prevent. Every sibling gate that shells out to an optional interpreter (Gate 10 actionlint; the 12 `.mjs` render gates) already routes through the `_skip_or_fail` helper — Gate 47 was the lone outlier.

**Fix.** `scripts/audit-gates.sh` — probe `python3 -c "import jsonschema"` first; on absence call `_skip_or_fail "Gate 47 (validate-schemas)"` (loud skip locally — _"THIS IS NOT A PASS"_ — hard-fail in CI). When present, the four fixtures run unchanged.

**Evidence.** With `jsonschema` installed all four fixtures behave correctly (good→exit 0, bad→exit 1); the meta-test went from **446 pass / 2 fail → 448 pass / 0 fail**. Both skip/fail branches were exercised directly.

### F2 — CI runs the gate but never provides its dependency (P1)

**Cause.** `audit-gates.sh` runs inside `validate-marketplace.yml` (which installs `ruff` but not `jsonschema`); `jsonschema` is installed only in the separate `validate-schemas.yml` job. So Gate 47 could not genuinely run in the meta-test CI job. With F1 in place this would now (correctly) hard-fail CI.

**Fix.** Added an `Install jsonschema` step in `validate-marketplace.yml` immediately before the audit-gates step — same pre-stage pattern already used for `ruff`.

### F3 — 20 antipattern hooks silently under-detect placeholders (P2)

**Cause.** `plugins/<plugin>/hooks/flag-<plugin>-antipatterns.sh` flags placeholder text. The canonical form (used by 21 plugins) is:

```sh
grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b'
```

20 plugins instead shipped:

```sh
grep -Eiq '\bTODO\b\|lorem ipsum'
```

Under `grep -E` (ERE), `\|` is a **literal pipe**, not alternation. So those 20 hooks match only `TODO` (and the literal string `TODO|lorem ipsum`) and **never** flag a standalone `lorem ipsum` placeholder or a `FIXME` — a behavior that silently differed by plugin. Proven both ways at the shell.

**Fix.** Aligned all 20 to the canonical form; 0 broken-form occurrences remain, 41 hooks now share the correct regex. `bash -n` clean on all; behavior verified (lorem ipsum + FIXME now flagged, clean prose still passes). Per the `AGENTS.md` semver rule, the patch version of each of the 20 plugins was bumped in **both** `plugin.json` and `marketplace.json` (parity gate green).

**Affected plugins:** architecture-aec, cannabis-operations, clinical-trials, commercial-real-estate, dental-practice, ecommerce-dtc, film-video-production, fleet-logistics, game-development, insurance-pc, legal-small-firm, medical-revenue-cycle, nonprofit-fundraising, precision-agriculture, procurement-sourcing, renewable-energy, restaurant-operations, senior-care-operations, skilled-trades-contracting, veterinary-practice.

---

## Needs your decision (deferred — behavior-risk or genuine preference)

### D1 — Three hooks lack `set -euo pipefail` (P3)

`AGENTS.md` says hooks are "bash with `set -euo pipefail`." Three do not:

- [`plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh`](../plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh) — envelope translator
- [`plugins/ravenclaude-core/hooks/dod-gate.sh`](../plugins/ravenclaude-core/hooks/dod-gate.sh) — Stop-hook definition-of-done gate
- [`plugins/ravenclaude-core/hooks/runaway-brake.sh`](../plugins/ravenclaude-core/hooks/runaway-brake.sh) — PreToolUse runaway brake

**Why deferred, not auto-fixed.** These are control-flow-sensitive: they emit specific exit codes (0 = allow, 2 = block) and JSON permission envelopes, and they run commands that are *expected* to return non-zero (e.g. a `grep` miss). Blindly adding `set -e` could abort a hook mid-decision and **flip a permission outcome** — a behavior change, not a cleanup. The omission may well be deliberate.

**Recommendation.** Audit each for the exact `set` flags it can safely adopt (likely `set -u` + targeted `|| true` rather than a blanket `set -e`), **or** record an explicit exception in `AGENTS.md` for self-managing hooks. Either is a ~1-hour, test-backed task. **Question: adopt-with-guards, or document-the-exception?**

### D2 — Nothing prevents F3 from recurring (P3)

F3 existed because hook regexes drifted with no gate pinning them. **Question:** add a small `audit-gates` fixture / `check-frontmatter`-style check asserting every `flag-*-antipatterns.sh` uses the canonical detection regex? Low effort, closes the class — but it is a new gate, and the `ci-gate-audit.md` discipline requires a fixture-pair, so it warrants a yes/no from you before I build it.

---

## What was checked and found clean (no action)

JSON validity (marketplace + 100 plugin manifests + layout) · `check-layout --all` (7 087 files) · frontmatter gate (descriptions ≤ 300 chars, scenario schema) · markdown relative links · prettier whole-tree · ruff · marketplace-claims (counts/rosters) · mcp-attribution (100 manifests) · lineup-citations · run-actions argv-integrity · dashboard-server-parity (14 endpoints) · Ragnarök fixtures · version parity (plugin.json ↔ marketplace.json) · bare `except:` (0) · TODO/FIXME markers in code (all intentional — dashboard feature code + antipattern detectors).

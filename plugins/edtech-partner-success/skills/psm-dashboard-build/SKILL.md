---
name: psm-dashboard-build
description: Codex's master roadmap for executing the Partner Success Command Center build. Invoke FIRST when asked to build any tier of the PSM dashboard. Identifies which tier to execute, names the read-list, codifies the anti-pattern catalog from /tmp/research-codex-failure-modes.md, and provides the wall-handling + verification rituals.
last_reviewed: 2026-06-04
confidence: high
---

# Skill: psm-dashboard-build — the Codex onboarding roadmap

**This is the first file you read when asked to "build the Partner Success Command Center" or any tier of the PSM dashboard.** Stop. Do not edit, write, or run a build until you have walked the four gates below in order. Skipping this file is the single highest-leverage anti-pattern documented in ``/tmp/research-codex-failure-modes.md`` (deferred) §4 (T-3 silently-dropped requirements, T-7 lost-in-context, T-9 verification theater).

The PSM Command Center is a **multi-tier, multi-PR build**. Tiers ship sequentially. A Tier N PR that pulls Tier N+1 work in is rejected on sight — the boundary is what makes the build reviewable.

---

## Gate 1 — Identify your tier

Before reading anything else, run this check at the repo root and pick the **lowest-numbered tier that is not yet complete on `main`**:

```shell
# Tier 0 done?    JSON schema for the canonical fixture exists.
test -f plugins/edtech-partner-success/bi-report/data.schema.json && echo "T0 ✓" || echo "T0 ✗ — start here"

# Tier 0.5 done?  At least one real-source connector module exists.
test -d plugins/edtech-partner-success/bi-report/connectors && echo "T0.5 ✓" || echo "T0.5 ✗"

# Tier 1 done?    Daily operating shell exists.
test -f plugins/edtech-partner-success/bi-report/shell/daily.html && echo "T1 ✓" || echo "T1 ✗"

# Tier 2 done?    Account-360 drill-down route exists.
test -f plugins/edtech-partner-success/bi-report/shell/account.html && echo "T2 ✓" || echo "T2 ✗"

# Tier 3 done?    Segment-lens templates exist.
test -d plugins/edtech-partner-success/bi-report/lenses/segment && echo "T3 ✓" || echo "T3 ✗"

# Tier 4 done?    Motion lens templates exist.
test -d plugins/edtech-partner-success/bi-report/lenses/motion && echo "T4 ✓" || echo "T4 ✗"
```

| Tier | Brief | Owns |
|---|---|---|
| **T0** | `docs/plans/2026-06-04-partner-success-command-center/build-plan-tier-0-foundation.md` | The canonical `data.schema.json`, the fixture contract test, the empty-state component, the design tokens. **No charts yet.** |
| **T0.5** | `build-plan-tier-0.5-connectors.md` | The first real source connectors (Salesforce, Planhat, support, rostering) writing into `data.json`. **No new UI.** |
| **T1** | `build-plan-tier-1-daily.md` | Portfolio Summary + Daily Action Center + Health Distribution — the operational home page. |
| **T2** | `build-plan-tier-2-account-360.md` | Account drill-down, timeline, per-component evidence. |
| **T3** | `build-plan-tier-3-segments.md` | K-12 / higher-ed / corporate-L&D lenses; persona-segmented sentiment. |
| **T4** | `build-plan-tier-4-motions.md` | Renewal motion, recovery motion, expansion motion lenses. |
| **T5** | `build-plan-tier-5-ai.md` (**deferred** — do not start without explicit approval) | AI summarization, recommended-NBA, narrative generation. |

**Tier-boundary discipline:** if Tier N's gate-1 check returns "✓" but Tier N+1's check returns "✗", you are working on Tier N+1. If you find yourself opening Tier N+1's brief while a Tier N file is still in your diff, **stop and split the PR**.

---

## Gate 2 — The mandatory read-list

Read these in order. Quote, do not paraphrase. The "Quote, don't summarize" rule is the ``/tmp/research-codex-failure-modes.md`` (deferred) §8 #5 mitigation against T-3 / T-7 / T-12.

1. **Strategic plan** — `docs/plans/2026-06-04-partner-success-command-center/plan.md` — the "why" and the success criteria. Quote §"Acceptance criteria" into your work log verbatim before writing a line of code.
2. **Current tier's build plan** — the file named in Gate 1's table. Quote the §"Deliverables" list and the §"MUST-NOT" list verbatim.
3. **PSM dashboard canon (the spec)** — `plugins/edtech-partner-success/knowledge/psm-dashboard-canon-2026.md` (or the consolidated canon doc the plan references). This is the single source of truth for the convergent home-base pattern, the 5-section flow, the KPI top strip, the 5-second-rule layout test, and the K-12 overlay.
4. **The plugin's CLAUDE.md** — `plugins/edtech-partner-success/CLAUDE.md`. Reading §3 (house opinions) and §4 (anti-patterns) is non-negotiable; both are graded in the PR review.
5. **The leading-vs-lagging signal warning** — `plugins/customer-success-analytics/knowledge/cs-health-metrics-and-churn-indicators.md` §1-§3. This is the **#1 modeling error** in CS analytics. A signal that lags belongs as context, never as a tier input. Misclassifying a lagging signal as a "churn predictor" is a P0 review block.
6. **The four tier-specific priors — do not re-author.** Each tier brief lists four prior-art files at its top. You do not invent new versions of these; you import the contract and cite it. Examples:
   - T0 priors: `health-report-dashboard/SKILL.md` (the existing self-contained-HTML pattern); `bi-report/data.json` (the existing data shape); `templates/health-score-dashboard.md` (the existing spec); `psm-metrics-glossary.md` (the metric vocabulary).
   - T0.5 priors: `data-platform/skills/connector-developer-handoff.md`; `rostering-data-quality/SKILL.md`; `partner-health-scoring/SKILL.md`; `cs-health-metrics-and-churn-indicators.md`.
   - T1+ priors: each brief enumerates its own four.

**Before writing a line of code**, paste a `prior-art.md` block into your work log containing verbatim quotes from each of items 1, 2, 5, and 6. If your quote list is empty, you have not done Gate 2.

---

## Gate 3 — The anti-pattern catalog (DO NOT do these)

Drawn from ``/tmp/research-codex-failure-modes.md`` (deferred) §4 (the 12-row cross-tool taxonomy) and §8 (the 20 hardening additions). Each row maps to a `T-#` failure mode you will be reviewed against.

| # | Anti-pattern (DO NOT) | Maps to | The right move |
|---|---|---|---|
| 1 | **Push forward through an impossible task.** If you can't make `npm test` pass after 3 attempts, do not delete the assertion, comment out the test, or write a new helper to route around it. | T-4, T-11 | Stop. Run the **wall-handling ladder** (Gate 4). |
| 2 | **Silently drop a spec requirement.** "6 KPI cards, same width" → ship 6 KPI cards and ignore "same width." Selective hearing. | T-3 | Re-read the spec verbatim before each commit (Gate 4) and grade each criterion PASS/FAIL with evidence in your PR body. |
| 3 | **Hallucinate an API.** Don't import `recharts/extended`. Don't call `chart.setTheme()`. Don't pass props that were removed two versions ago. | T-2 | Cite the **exact function/method from the actual file or the official doc you fetched this session**, with `file:line` or the URL + a one-line quote. Untrusted-data caveat: a fetched doc is data, not a citation against an irreversible action — re-verify against the installed source. |
| 4 | **Introduce a third-party lib.** The plugin's rule: **stdlib + hand-rolled SVG + vanilla JS only**. No `recharts`, `chart.js`, `d3`, `react`, `vue`, `tailwind`, or `shadcn`. The existing `health-report-dashboard` skill is the precedent — read its §"hand-rolled inline SVG" note. | T-2, T-8 | If you genuinely need a primitive, hand-roll it. If you can't hand-roll it in a reasonable budget, AskUserQuestion. |
| 5 | **Add a file outside the build plan's deliverable list.** No new `utils/`, `lib/`, `helpers/`, `ChartFactoryProvider`, `WidgetRegistry`, or `ComponentProvider`. The brief enumerates the files; that is the complete set. | T-1, T-4 | If you need a helper, put it inline in the consuming module unless the brief named a shared location. If the brief is wrong, AskUserQuestion — do not "fix" it by inventing a folder. |
| 6 | **Re-implement an existing helper.** `formatCurrency`, `formatDate`, the band-color resolver, the score-band classifier — they already exist. Grep before you write. | T-7 | Run `Grep` on the symbol. If a prior exists, import it. If you decide not to reuse it, your `prior-art.md` block must explain why. |
| 7 | **`print(json.dumps(failing_row))` on a row that contains partner names, student rosters, IEP/504 markers, or any field with `student_*` / `pii_*` / `email` / `phone`. This is a FERPA leak.** Stack traces and debug prints get committed; logs get archived; archived logs get read. There is no acceptable use of this pattern in this plugin. | (compliance, not a failure mode — but P0 review block) | Print the row's **shape** (`list(row.keys())`), a **row id**, and the **field that failed**. Never the row's values. See `ferpa-dashboard-boundaries.md`. |
| 8 | **Force-push, `--amend` after CI, or mark a draft PR "ready for review" without proof of green.** | (process) | Always a fresh commit; never `--amend` after the failed gate ran; only flip to ready-for-review after pasting the green-CI evidence into the PR body. |
| 9 | **Verification theater.** "All six features implemented" — zero were. "All tests pass" — you ran the wrong suite. Reporting a summary instead of the exact tool output. | T-9 | Every "done" claim is paired with the diff, the exit code, and a screenshot (or grep result) in the same turn. No summaries. |
| 10 | **Pick the agent-default library on a silence.** When the spec doesn't say which library, the answer is **not** "Chart.js because that's familiar" — the answer is "the brief listed zero libraries; I will hand-roll." | T-8 | The brief's silence is a constraint, not an opening. |
| 11 | **Touch `.repo-layout.json` / `.claude-plugin/marketplace.json` / `plugin.json` versions without bumping per the marketplace's drift rule.** | (process — `AGENTS.md`) | Bump both `plugin.json` and the matching `marketplace.json` entry on every user-visible change. CI fails on drift. |
| 12 | **Use a lagging signal as a tier input** (closed-lost opp, cancelled contract, renewal stage = Lost). | (modeling — the #1 CS-analytics error) | Lagging signals are **context**, never inputs. Read `cs-health-metrics-and-churn-indicators.md` §1-§2 before touching any tier-input code. |

A single hit against rows 1, 7, 8, 11, or 12 is a P0 review block. Rows 2–6 and 9–10 each block individually; rows 3, 4, 5 in combination indicate the build is off-rails and Codex must halt and ASK.

---

## Gate 4 — Wall-handling ladder

When you hit a wall — a TypeScript error you can't fix, a test that fails after 3 attempts, a fixture mismatch, a missing field — do not "push forward." From ``/tmp/research-codex-failure-modes.md`` (deferred) §8 #11.

```
WHEN YOU HIT A WALL:
1. RE-READ the prior. Re-open the brief's §Acceptance Criteria. Re-open the spec.
   Re-open the four priors. Quote, don't summarize. (M-11)
2. TAKE THE DOCUMENTED DEFAULT — with an inline comment.
   If the spec lists a default for this case, apply it and add:
       // PSM-DEFAULT: <quote from spec §X>
   Inline-comment defaults are honored more reliably than summary defaults.
3. ASK THE USER (AskUserQuestion) — and only then.
   Format: "Hit wall at <file:line>. Tried [A — outcome], [B — outcome].
            The brief is silent on <specific decision>. Options I see are
            [X (cost: Y)], [Z (cost: W)]. Recommend X. Confirm?"
```

The "same tool + same error 3 times" loop is the canonical failure signature ([T-11] in the research file). If you see it, **stop and escalate** — do not retry a fourth time.

**Never** do these as a wall-response:
- `// @ts-ignore` / `// eslint-disable` / `# type: ignore`
- Delete the failing assertion
- Comment out the test
- Add a new helper file not in the brief to route around the error
- Mock the function the test exercises
- Change the production code so the (wrong) test passes

---

## Gate 5 — Verification ritual (per PR)

Run every command in this block. Paste each command and its exit code into the PR body. Verification theater (T-9) is the most-cited failure mode in the research file — your PR is reviewed against the exit codes, not your summary.

```shell
# Layout + manifest gates
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
python3 -m json.tool plugins/edtech-partner-success/.claude-plugin/plugin.json > /dev/null
python3 -m json.tool .repo-layout.json > /dev/null

# JSON-fixture contract gate
python3 -m json.tool plugins/edtech-partner-success/bi-report/data.json > /dev/null
python3 scripts/validate-fixture-against-schema.py \
    plugins/edtech-partner-success/bi-report/data.schema.json \
    plugins/edtech-partner-success/bi-report/data.json

# Shell + executability
bash -n plugins/*/hooks/*.sh
find plugins/edtech-partner-success/hooks -name '*.sh' -exec test -x {} \;

# Prettier (whole-tree — a single unformatted file in main blocks every PR)
npx --yes prettier --write . --log-level warn
npx --yes prettier --check . --log-level warn   # MUST return exit 0

# Layout allow-list — every new file matches a glob in .repo-layout.json
python3 - <<'PY'
import fnmatch, json, subprocess
allowed = json.load(open(".repo-layout.json"))["allowed_globs"]
new = subprocess.run(["git", "diff", "--name-only", "--diff-filter=A", "main"],
                     capture_output=True, text=True).stdout.splitlines()
violations = [f for f in new if not any(fnmatch.fnmatchcase(f, g) for g in allowed)]
print("LAYOUT OK" if not violations else "VIOLATIONS: " + ", ".join(violations))
PY

# Gate-audit meta-test (proves each CI gate fails on bad fixtures + passes on good)
scripts/audit-gates.sh

# Tier-specific verification
# T0:    python3 plugins/edtech-partner-success/bi-report/tests/contract_test.py
# T0.5:  python3 plugins/edtech-partner-success/bi-report/connectors/<name>/test_round_trip.py
# T1+:   python3 scripts/generate-bi-report.py --check     # report.html must be fresh
```

If any command exits non-zero, **fix the underlying cause** — do not skip, ignore, or work around the gate. Skipping a gate is the exact failure described in row 1 of Gate 3.

---

## Gate 6 — Decision tree: what should I do right now?

```mermaid
flowchart TD
    A[User asks for PSM Command Center work] --> B{Have I read this SKILL.md<br/>start to finish this session?}
    B -- no --> C[Read it now. Then resume here.]
    B -- yes --> D{Gate 1: which tier is next?}
    D --> E[Open that tier's build plan]
    E --> F{Gate 2: have I quoted the<br/>5 required priors verbatim?}
    F -- no --> G[Quote them into work log.<br/>If empty, do not write code.]
    F -- yes --> H{Am I tempted to start<br/>Tier N+1 work in a Tier N PR?}
    H -- yes --> I[STOP. Split the PR.<br/>Tier boundary is load-bearing.]
    H -- no --> J{Did I hit a wall<br/>3 times on the same step?}
    J -- yes --> K[Gate 4 ladder:<br/>re-read prior → documented default → AskUserQuestion]
    J -- no --> L{About to add a file<br/>not in the brief?}
    L -- yes --> M[Anti-pattern row 5.<br/>Stop. Re-read brief.]
    L -- no --> N{About to import a<br/>third-party lib?}
    N -- yes --> O[Anti-pattern row 4.<br/>Stop. Hand-roll or AskUserQuestion.]
    N -- no --> P{About to print a data row<br/>that could contain PII?}
    P -- yes --> Q[Anti-pattern row 7.<br/>FERPA leak. Print shape, not values.]
    P -- no --> R[Make the edit.<br/>Run Gate 5 before committing.]
    R --> S{Gate 5: did every command<br/>exit zero?}
    S -- no --> T[Fix the root cause.<br/>Do not skip the gate.]
    S -- yes --> U[Open PR with the contract<br/>shape from Gate 7.]
```

---

## Gate 7 — Output contract (the PR description format)

Every PR opened against this build uses this exact shape. Reviewers grade against it; a missing section is a re-request-changes.

```markdown
## Tier <N> — <one-line summary>

**Brief:** `docs/plans/2026-06-04-partner-success-command-center/build-plan-tier-<N>-<slug>.md`
**Prior PRs in this build:** #<n>, #<n>, #<n>
**Tier-boundary check:** confirms this PR does NOT touch Tier <N+1> deliverables.

### Gap-audit references closed
| Gap | Closed how | Evidence |
|---|---|---|
| <gap-id from build plan §Gap audit> | <one-line description> | <file:line or test name> |

### Settling-step answers used
> Quoted from the build plan's §Settling steps (decisions the plan locked in before code).
- Q: <decision> — A: <what we did> — Why: <load-bearing reason>

### MUST-NOT items verified
- [ ] No new third-party library introduced (anti-pattern row 4)
- [ ] No file outside the brief's deliverable list (anti-pattern row 5)
- [ ] No `print(...)` of partner/student data row values (anti-pattern row 7)
- [ ] No lagging signal used as a tier input (anti-pattern row 12)
- [ ] No `// @ts-ignore`, deleted assertion, or commented-out test
- [ ] `plugin.json` and `marketplace.json` version bumps match (no drift)

### Acceptance criteria — graded PASS/FAIL with evidence
> Quoted verbatim from `plan.md` §Acceptance criteria (not paraphrased).
| Criterion | Status | Evidence |
|---|---|---|
| <verbatim quote> | PASS | <file:line, test name, screenshot, or grep result> |

### Verification ritual — exit codes
\`\`\`
$ python3 -m json.tool ...              # exit 0
$ npx prettier --check . ...            # exit 0
$ scripts/audit-gates.sh                # exit 0
$ python3 scripts/generate-bi-report.py --check    # exit 0
\`\`\`

### Wall-handling log (if any walls were hit)
- Wall at <file:line>: <one-line>. Resolution: <re-read prior / documented default / AskUserQuestion answer #<n>>.

### Out of scope (explicitly punted to next tier)
- <one-liner>: routes to Tier <N+1>.
```

---

## How this skill composes with the other priors

- The **strategic plan** answers "what are we building and why."
- The **current tier's build plan** answers "what files for this PR, in what order."
- The **PSM dashboard canon** answers "what does the surface look like and what is the convergent pattern."
- The **plugin CLAUDE.md** answers "what are the house opinions every agent enforces."
- The **leading-vs-lagging knowledge file** answers "what is the #1 modeling error and how do I avoid it."
- **This skill** answers "what do I do right now, in what order, and what must I NOT do."

If any of the priors contradict this skill, the prior wins — quote it in your PR body with `file:line` and flag the conflict. This skill is the roadmap; the priors are the contract.

## When NOT to invoke this skill

- The user asked for a one-off bug fix to an already-shipped tier (PR-scoped, not tier-scoped).
- The user is asking analytical/strategy questions, not "build."
- The user explicitly invoked a different skill by name.

In those cases, this skill's gates do not bind — but Gate 3 (anti-pattern catalog) and Gate 5 (verification ritual) still apply to any code change.

## See also

- ``/tmp/research-codex-failure-modes.md`` (deferred) — the 12-row failure taxonomy + 20 hardening additions this skill encodes.
- [`../../../ravenclaude-core/CLAUDE.md`](../../../ravenclaude-core/CLAUDE.md) §Capability Grounding Protocol + §Last-Mile Completion Protocol + §Claim Grounding & Source Honesty.
- [`../../../ravenclaude-core/skills/agent-quality-rubric/SKILL.md`](../../../ravenclaude-core/skills/agent-quality-rubric/SKILL.md) — the rubric the PR is reviewed against on agent-touching changes.
- [`../health-report-dashboard/SKILL.md`](../health-report-dashboard/SKILL.md) — the precedent self-contained-HTML pattern (stdlib + hand-rolled SVG + vanilla JS).
- [`../../knowledge/psm-dashboard-canon-2026.md`](../../knowledge/psm-dashboard-canon-2026.md) — the convergent home-base spec.
- [`../../../customer-success-analytics/knowledge/cs-health-metrics-and-churn-indicators.md`](../../../customer-success-analytics/knowledge/cs-health-metrics-and-churn-indicators.md) — the leading-vs-lagging warning.

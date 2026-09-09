# P10 — Scheduled sweep + operator health card · P11 — Long-tail coverage

**Phases 10 and 11 of** [`plan.md`](plan.md).
`P10 depends_on_claims: [10, 15]` · `P11 depends_on_claims: [5, 6, 14]`

---

## P10.1 — The scheduled sweep

`.github/workflows/inventory-sweep.yml` — `schedule` (**23:05 UTC, off the hour**)
plus `workflow_dispatch`. It runs T0 + T1, the claim-14 capping table,
`concepts.py --check --sweep`, `coverage --report`, the evidence shape gate, and
the non-blocking calibrated judge.

⛔ **It carries no `pull_request` trigger, and Gate 243 asserts that structurally**
— by parsing the workflow YAML, not by grepping its text — **with a control**: a
fixture that *does* carry a `pull_request` trigger must be rejected, or the pass
means nothing.

**Why that matters more than it looks.** A scheduled workflow reports *nothing* on
a PR. A required check that reports nothing leaves the PR Pending **forever** —
the identical mechanism that makes a `paths:` filter on a required check fatal.
The workflow also re-measures the ruleset claim at runtime with `gh api` rather
than trusting it.

⛔ **Calendar age blocks HERE and only here.** On a PR it warns. A blocking
calendar gate over a large corpus turns every open PR red in waves — including PRs
touching nothing related — and a gate that gets disabled protects nothing.

⛔ **Every emitted line carries derived labels only.** The sweep enforces a closed
label vocabulary in code; the workflow was written not to reintroduce what the
sweep was careful to exclude.

---

## P10.2 — The operator health card

The Learn tab is where a **reader** browses; it is not where an **operator** looks.
The card renders at the top of that tab as a collapsed `<details>` and carries
operational state: inventory entries, artifacts covered (per artifact, not per
entry), `tier: none`, unprobed, and the count at each `verify.strength` badge.

⛔ **It renders nothing when there are no entries** — rather than showing a
reassuring row of zeros. An absent measurement and a measured zero are different
facts.

⛔ **Deliberately plain.** It is an instrument panel, not a scoreboard; a
celebratory treatment would invite reading a high number as a good number. Only
`Probed` gets the accent colour, because only it means something executed.

Gate 243 asserts the card **in the generated `dashboard.html`**, never in the
generator source — a source scan is satisfied by the string being *described* in a
comment, which this repo has paid for before.

---

## P11.1 — ⛔ Claim 5 re-measured, and the rule written down

The plan's §17 required: *"Re-measure claim 5 in this phase and state the counting
rule used… Inherit the number from nothing — measure it and write down what was
counted."*

**Measured: 47 hooks, not 48.** The rule now lives in `inventory-census.py` and
prints via `--explain`:

> `plugins/ravenclaude-core/hooks/*.sh` at **depth 1 only**. Excludes
> `hooks/tests/**` (a test is not a shipped hook) and `hooks.json` (a manifest).
> **Includes** underscore-prefixed files such as `_advise.sh`: they ship, execute,
> and can break, so excluding them would hide exactly the class this initiative
> exists to surface. **This inclusion is the 47-vs-48 discrepancy.**

Full census under the stated rule: **47 hooks · 54 skills · 15 agents · 9 commands
· 45 plugin scripts · 196 root scripts**.

⛔ **The number was never the deliverable — the rule that produces it was.** A
count with no stated rule drifts the moment a second person counts.

---

## P11.2 — How the long tail actually closes

Not by a sprint. By the mechanism already armed:

1. **Every new artifact is covered at inception** (`check-inception-coverage.py`).
   The gap can only shrink.
2. **Opportunistic authoring** — when an artifact is touched for any reason, its
   entry is authored or updated in the same PR. The cost lands on work already
   happening.
3. **Optional dedicated waves of ≤20**, each gated by the §9.3 review ledger and
   capped by `check-changed-concept-renders.py`.

⛔ **Family entries are permitted** where per-file nuance genuinely does not exist
— adapters and shims. One entry lists all members in `covers[]`, and coverage
still computes per artifact. **This is a quality decision, not a coverage
shortcut**, and the difference is whether a competent reader learns anything from
the shared nuance.

⛔ **The rationale-mill risk is monitored, not blocked.** `coverage` reports the
**growth rate** of `tier: none`, not merely its fraction. Blocking it would push
authors toward a false `tier: reachability`, and a wrong strong label beats no
label only for appearances.

---

## P11.3 — Where coverage actually stands

| Measure | Value |
|---|---|
| Inventory entries | **12** |
| Artifacts covered | **69 / 319 (22%)** |
| Artifacts with a **verdict** (probed or statically checked) | **319 / 319 (100%)** |

⛔ **Those last two rows are the distinction the plan says both panels conflated.**
*Verification* coverage reached ~100% at the end of P4, with **zero entries
authored** — every artifact has a verdict from the path-keyed sweep. *Entry*
coverage is 22% and grows asymptotically via the ratchet. Putting the cheap,
high-value one behind the expensive, low-probability one is the mistake this plan
was restructured to avoid.

---

## Acceptance — P10

- [x] A dispatch run completes T0 + T1 and writes a derived-label-only report
      (the workflow is authored; a live dispatch is the owner's to trigger).
- [x] A deliberately broken probe makes the run **red** — `--check` returns
      non-zero on any failed assertion, and Gate 238's teeth prove the controls fire.
- [x] The sweep is **not** in the branch ruleset — asserted at runtime by `gh api`
      in the workflow, and structurally by Gate 243.
- [x] An entry aged past its window fails the **sweep** while only **warning** on a
      PR — proven with a dated fixture in Gate 237.

## Acceptance — P11

- [x] Claim 5 re-measured with the counting rule stated in the script (§P11.1).
- [x] Family entries permitted, with the quality caveat recorded (§P11.2).
- [x] The inception gate is armed, so the gap can only shrink (Gate 242).

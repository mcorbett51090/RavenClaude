# plan.md — CI gate health, effectiveness, efficiency & spend review

**Gate:** G6 (synthesis). **Status:** authoritative. This file supersedes `plan-A.md` and
`plan-B.md` for every question either answers. Where a gate artifact and this file differ, this
file is the plan of record and says below which artifact it overruled and why.

**Precedence applied, highest first:**
owner rulings (`scope.md` §"Owner rulings", plus the **fleet-spend ruling of 2026-08-17** recorded
in §1.2) → `tiebreak-architecture.md` + `tiebreak-spend.md` (BINDING) → `red-team.md` mitigations →
`critic-brief.md` as corrected by `critic-corrections.md` → `plan-A.md` / `plan-B.md`.

**Two corrections that must be read before anything downstream:**

1. `claims-settlements.md`'s **C3 reshape is FALSIFIED** by its own trailing CORRECTION block and by
   `tiebreak-spend.md` §0. `billable.*.total_ms` is **raw, un-multiplied, un-rounded** duration.
   A pure `billable` read silently under-reports macOS 10× and Windows 2×, and under-reports
   *everything* by ignoring per-job rounding.
2. `critic-corrections.md` §B2 is a **retraction** — the critic's count was substantially right and
   the orchestrator's "correction" was itself an instrument defect. The settled decomposition is
   `tiebreak-architecture.md` §1: **604 assertion sites, 17 non-literal names, 28 helper call sites.**

---

## §1 — Scoped intent

### 1.1 What is being built

A **methodical, repeatable review** of GitHub Actions workflows and CI/audit gates across four
owner-ratified axes — **health** (does each gate still have teeth), **effectiveness** (is it
catching anything or has it rotted), **efficiency** (wall-clock, critical path), **spend** (runner
minutes, portable to private repos) — delivered as the three owner-ratified surfaces:

| Surface | Artifact | Gated? |
|---|---|---|
| Script + its own registered Gate, with a must-fail half | `scripts/check-ci-gate-health.py` + **Gate 223** in `scripts/audit-gates.sh` | yes, static lane only |
| Skill carrying the periodic methodology | `plugins/ravenclaude-core/skills/ci-gate-health-review/SKILL.md` | no |
| Dashboard reader surface | `/__ci-health` endpoint + one panel | no |

Plus the docs correction (`AGENTS.md` stale required-checks count) as a rider.

**Sequencing ruling (`tiebreak-architecture.md` §7, from critic P1):** the owner ratified
*script+gate AND skill AND dashboard*. The owner did **not** ratify *all three in one change*.
The dashboard is the only surface behind an unobtained owner decision (DOM ratchet at **zero**
slack, measured 6217/7103 on both surfaces) and is the longest pole in both input DAGs. It lands
as a **separate change after one cycle**. All three still ship.

### 1.2 ⚑ NEW OWNER RULING (2026-08-17) — the fleet-wide spend lane

Live investigation this session found that the owner's actual Actions bill does **not** come from
this repo. It comes from **`RavenPower-Website` (private)**:

- **1,825 workflow runs since Aug 1**, driven by short crons:
  `change-request-sweep` at `4,19,34,49 * * * *` (4×/hr), `uptime-probe` at `7,37 * * * *` (2×/hr),
  plus hourly `change-request-agent` and `oauth-state-gc`.
- Each job runs **1–8 seconds** and bills a **full minute**, because **billing rounds per job**.
- `billable.total_ms` reports **0** for all of them, so the API surface shows nothing.

⇒ **Ruled: the spend surface must run ACROSS REPOS, not just this one**, and must use the
`Σ ceil(job_ms/60000) × multiplier` formula from `tiebreak-spend.md` — the formula that would have
caught this. It must surface three things this repo's own numbers can never show:

1. **per-repo run volume** (1,825 runs/17 days is the finding; a per-run average is not),
2. **cron cadence as a cost driver** (a `*/15`-shaped schedule is a spend line item, stated as such),
3. **job-count vs workflow-count** — under per-job rounding, consolidating N hourly jobs into **one
   job with N steps** is a **~N× saving**. This is the lever this repo's framing never had.

**Correction to `orchestrator-findings.md` F1 — corrected, not deleted.** F1 calls `concurrency:`
"the largest safe lever." That is true **and scoped**: it cancels runs for *superseded pushes*, and
the settled F1 probe in `claims-settlements.md` (check runs attach per SHA; `cancel-in-progress`
never cancels the newest run) remains correct and remains the basis for recommending it on the 9
workflows lacking it. But **`concurrency:` does nothing whatsoever for cron-driven spend** — a cron
fires on a schedule, not on a superseded ref, so there is never a superseding run to collapse into.
F1's lever addresses PR iteration burn on a CI-hot repo; it does not address the shape that is
actually generating the owner's bill. **Both statements ship, side by side, in the report and the
skill.** The corrected framing: *"`concurrency:` is the largest safe lever for push/PR-driven spend.
For cron-driven spend the levers are cadence, job consolidation under per-job rounding, and
`workflow_dispatch`-only for anything that does not need a schedule."*

### 1.3 What is explicitly NOT built

| Not built | Why |
|---|---|
| **`ASSERTS-NOTHING` as a new detector** | ⛔ **DISQUALIFIED ON SIGHT.** It already exists at `scripts/check-gate-registration.py:233-236` — `asserts = any(GATE_CALL_RE \| SKIP_CALL_RE)` over the block; a block with zero assertions never marks its numbers reachable. It is spelled `unreachable` there. **Both plan-A (§Phase 3) and plan-B (§0) named it as new; both are overruled.** The one real defect in the incumbent (a latent false RED, §5 Phase 0) is **contributed to that file**, not rebuilt beside it. A second implementation of Gate 195's logic is disqualified on sight — that rule is applied without exception below, including to plan-A. |
| **Suite-internal reachability, `Supported:`↔dispatcher-arm parity, gate-number collision, exit-2 specificity, batched-header handling** | All five owned by Gate 195, with its own `--self-test`. The producer **invokes** it and propagates its exit code as symptom `SUITE-META`. plan-B's headline acceptance test proves a property Gate 195 already proves. |
| **Rules 1/2 of `.github/scripts/check-workflow-hygiene.py`** (`permissions:` floor, action SHA pinning) | Invoked, never reimplemented. The NEW part is promoting its **advisory Rule 5** using required-checks context it structurally cannot see. |
| **Any `paths:` / `paths-ignore:` optimisation** | Forbidden by `scope.md` and AGENTS.md; C7 — it leaves a required check **Pending forever**, the unrecoverable direction. The reviewer FLAGS it and must never propose it. Encoded as a `--self-test` assertion on the remediation string, not left to discipline. |
| **A new required status check** | Ruleset changes are the owner's call. Gate 223 rides inside `Validate Marketplace`, already required. |
| **Any USD figure** | Per-minute price and plan-included minutes are unprobed and the account-level billing scope was refused (C3). `usd: null` + `usd_blocked_by[]`, never omitted. Preconditions to unblock in §9. |
| **A hard-coded `estimated_minutes`** | plan-A §0.4/Phase 4 seeded it from C8's aggregate, which came from the `per_page=100` window `orchestrator-findings.md` **itself disowns** as "a 6-hour sample presented as a rate." Deleted (CE-3 / R15). Never estimate a duration you can measure. |
| **`free_minutes_by_plan` / `per_minute_usd` in the policy file** | Cut with the USD ruling; the policy file narrows to multipliers + rounding rule with **per-fact** verified flags. |
| **A suppression / "unacknowledged CRITICAL" channel** | plan-B's escape hatch, named once and designed nowhere. Struck (`tiebreak-architecture.md` §7). Findings are RED or they are not findings. Suppression, if wanted, is a separate designed change. |
| **Auto-remediation (`--fix`)** | Every finding class here is a judgement call with blast radius. An auto-fixer for CI trust boundaries is a security regression with a convenience label. |
| **Refactor / consolidation of existing gates** | `scope.md`: this reviews them, it does not refactor them. The producer is read-only over `audit-gates.sh` — **with one exception, called out loudly**: the ~4-line trace sink in `gate()`/`_skip_or_fail()` (§7 Phase 2), which changes no verdict and is the owner's to refuse. |
| **Committing live spend/timing data into the repo** | Non-deterministic, per-machine, git-derived; it breaks the exact-byte dashboard freshness gate on contact. It lives only behind `--live` and `/__ci-health`. |
| **Agent/token-spend accounting for gate runs** | Owner listed it under spend; `[probed]` no workflow and no gate invokes an LLM today (only a mocked tribunal verdict). The producer emits `llm_invoking_steps: []` — a **measured zero**, not an unbuilt axis, so the day one appears it is visible. |
| **Injecting real failures into live required workflows to "prove" they can fail** | Real spend, real merge disruption on a repo at ~190 runs/day. Evidence-of-can-fail comes from historical non-success conclusions, labelled WARN/"unconfirmed" when absent. |
| **Fixing the `email` field in `.claude-plugin/marketplace.json`** | Explicitly out of scope — owner privacy call, separate change. Also not a CI-gate property, so the tool does not surface it either. |
| **A new scheduled workflow to force the periodic review** | That is new spend needing its own review. The skill states cadence and checks report recency. |

---

## §2 — Conflicts between binding documents, resolved

`red-team.md` identified places where two BINDING documents are mutually unsatisfiable. Each is
resolved here in place. **No dangling conflict remains.**

### 2.1 RT-4 — the stdout-invariant assertion vs THE RULE ⛔ RESOLVED

- `tiebreak-architecture.md` **§2** requires: *"Stdout stays byte-identical with the sink off; that
  invariant is itself a Gate 223 assertion."*
- `tiebreak-architecture.md` **§4** forbids: *"A gate registered inside `audit-gates.sh` may never
  execute `audit-gates.sh`. … Not even with a re-entrancy guard."*

Byte-identity of the suite's stdout under sink-on vs sink-off appears to require running the suite
twice, from a gate registered inside it. That is **B1** — the mode the critic rated BLOCKER, whose
realisation is in-place corruption of the tracked file `plugins/ravenclaude-core/dashboard.html`
via the mutate/restore pair at `audit-gates.sh:1816-1819`, inside required context #1 at ~190
runs/day. A builder obeying §2 literally commits B1.

**RESOLUTION — §2's scope is narrowed; §4 is untouched and remains absolute.**
The invariant is asserted on an **isolated extracted harness**, never on the suite:

1. `sed -n '/^gate()/,/^}/p'` (and the same for `_skip_or_fail()`) extracts the two function
   definitions from `scripts/audit-gates.sh` **as text**.
2. They are sourced into a 3-assertion driver script written into `mktemp -d`.
3. The driver runs twice — once with `AUDIT_GATES_TRACE` set, once unset — and `cmp`s the two
   stdouts.

This is a static extraction plus execution of *the extracted copy*. `scripts/audit-gates.sh` is
never invoked, so **THE RULE holds structurally, not by guard** — which is the only form
`tiebreak-architecture.md` §4 accepts (a guard converts unbounded recursion into a *silent skip*,
which is C14's exact class: shipping the disease as the cure). §2's sentence is hereby amended to
read "asserted on the extracted-harness fixture." Left as written it was an instruction to commit B1.

### 2.2 The two tiebreaks disagree on what spend OUTPUTS ⛔ RESOLVED

- `tiebreak-architecture.md` **§7** rules: *"Ship: raw `total_ms` per OS lane, labelled
  `not-billing-adjusted` … No dollar figure anywhere,"* on the stated ground that the multiplier
  claim is *"unprobeable here, because every sampled run reads 0."*
- `tiebreak-spend.md` **§0–§2** ruled **later and narrower on exactly this question**, and settled
  it **by primary documentation rather than by inference**: two docs.github.com pages retrieved
  2026-08-17 state that the usage figure excludes the multiplier and is not rounded. It therefore
  emits `billable_minutes_if_private = Σ ceil(job_ms/60000) × multiplier` through a dated, cited
  policy file.

**RESOLUTION — `tiebreak-spend.md` binds the spend output layer; `tiebreak-architecture.md` §7's
USD prohibition survives verbatim.** The architecture tiebreak's own stated reason for the narrower
ruling ("unprobeable here") was **removed by evidence**: the question was answerable from primary
documentation without a nonzero repo, which is precisely the standard CE-2 demanded. What survives
of §7 is its discipline and its cuts — no USD, no `estimated_minutes`, no undated table — all of
which `tiebreak-spend.md` §6 independently keeps. What is superseded is only the clause "raw
`total_ms` … and nothing more," because a raw-only report **is** the 10× silent under-report on the
private consumer repos portability exists to serve. The new fleet ruling (§1.2) is decisive here:
without the per-job ceiling and the multiplier, the fleet lane reports `0` for the repo that is
actually generating the bill.

**Both documents agree, and this plan enforces:** no dollar figure in v1, in any form — not a range,
not a `~$`, not behind a flag.

### 2.3 RT-5b — FLOORS has no spend key ⛔ RESOLVED

`tiebreak-architecture.md` §5's `FLOORS` table has five keys and no spend key;
`tiebreak-spend.md` §4 mandates a spend floor (0 classified runs ⇒ exit 2). As written, the first
`--live` run either raises `KeyError` (a traceback, which a naive `must_fail` launders into green —
hazard A2) or bypasses `_floor()` entirely (invisible to the self-test — RT-5a).

**RESOLUTION.** `FLOORS` gains `spend_runs: 1`, `spend_lanes: 1`, and — per §1.2 — `fleet_repos: 1`.
`_floor()` on an unregistered stage is a **named exit 2** (`FLOOR-UNREGISTERED: <stage>`), never a
`KeyError`. Every Gate 223 exit-code assertion greps its **specific symptom string** in addition to
asserting the code, so a traceback cannot satisfy it.

### 2.4 RT-3 — "DECLARED is 100% complete" is false ⛔ RESOLVED

`tiebreak-architecture.md` §2 claims DECLARED (`^\s*gate\s+`) is 100% complete; its own §1 counts
with a *different* anchor (`(?:^|[;&\|])\s*gate\s+`). Measured: **604 vs 601** — three live
assertion sites (`audit-gates.sh:4683, 4714, 4746`, all `cmp_rc=0; …; gate "…"` one-liners) are
invisible to the §2 anchor. They land in the **unchecked** direction (present in EXECUTED, absent
from DECLARED), so three assertion sites are permanently exempt from the execution check and
nothing prints that they are exempt.

**RESOLUTION.** One shared anchor constant, used by the DECLARED scan and by every document that
describes it: `(?:^|[;&|])\s*(gate|_skip_or_fail)\s`. `|DECLARED| == |grep -c <same anchor>|` is a
first-class floor. `EXECUTED \ DECLARED` is promoted from a discarded set to its own finding class,
**`UNDECLARED-EXECUTION`** — a non-empty one is proof the static reader has gone blind.

---

## §3 — NEW vs EXTENSION ledger

The question that decides the size of this project. Every row is **NEW**, an **EXTENSION** of an
existing owner, or **DISQUALIFIED**. Derived from `tiebreak-architecture.md` §6, with the fleet
ruling folded in as rows 24–27.

| # | Component | Verdict | Owner / rationale |
|---|---|---|---|
| 1 | One producer → three consumers; readers compute nothing | **NEW** (architecture) | Three surfaces with three implementations is the drift class this project exists to find. |
| 2 | `static` / `live` lane split; only `static` is ever gated | **NEW** | A gate that depends on the network is red for reasons unrelated to the repo. plan-B's `internal`/`fleet` split cuts on the wrong axis — it separates *subject*, not *determinism*. |
| 3 | **Assertion-execution trace, line-keyed** (`site = "${BASH_SOURCE[1]}:${BASH_LINENO[0]}"`) | **NEW** — the only new suite-internal capability | Gate 195 is a static reader by design and cannot know what ran. "Did this execute" is not reconstructible from text. |
| 4 | Post-suite reconciliation step (`DECLARED \ EXECUTED` + `UNDECLARED-EXECUTION`) | **NEW** | plan-B's germ, relocated: it was right that EXECUTED needs a real run, wrong about where to stand while reading it. |
| 5 | `dynamic/**` excluded from on-disk reconciliation, reason printed **inline in output** | **NEW** | plan-B §0 #1. plan-A has no exclusion anywhere and would emit a permanent false `GHOST-WORKFLOW` forever (A1). |
| 6 | `state != active` filter beside `dynamic/**` | **NEW** | Neither plan (critic CE-5). `dynamic/**` describes the two rows observed *here, today*; deleted/disabled rows are normal on any consumer repo. |
| 7 | Workflow-root reachability of executables (`UNRUN` / `PHANTOM`) | **NEW** | Gate 195 sees only inside `audit-gates.sh`; nothing today walks workflow → script. |
| 8 | Comments are not invocations (the `sanitize-webfetch-body.py` phantom in `quarantine-intake.yml:18`) | **NEW** | A grep is satisfied by the thing being *described*. Live specimen in-repo; pinned as a fixture. |
| 9 | **`ASSERTS-NOTHING`** | ⛔ **DISQUALIFIED** → one-hop-closure contribution to Gate 195 | `check-gate-registration.py:233-236`. Both plans claimed it as new. §7 Phase 0. |
| 10 | Suite-internal reachability, `Supported:`↔arm parity, number collision, exit-2 specificity, batched headers | ⛔ **DISQUALIFIED** | Gate 195 owns all five with its own `--self-test`. Producer invokes it, propagates exit code as `SUITE-META`. |
| 11 | `paths:`/`paths-ignore:` on a required check ⇒ RED, never a suggestion | **NEW** | Both plans agree; take plan-B's literal output wording — *"do not remediate by adding a paths filter"*. |
| 12 | `concurrency:` audit with the 2-name allowlist + inline rationale | **NEW** | plan-B §P3(4). `quarantine-intake` and `regenerate-artifacts` keep `cancel-in-progress: false` (cancelling those loses work, not time). An unexplained allowlist rots. **Scoped per §1.2: push/PR spend only.** |
| 13 | `permissions:` floor, action SHA pinning | **EXTENSION** of `.github/scripts/check-workflow-hygiene.py` | Invoke it; never reimplement Rules 1/2. NEW part = promoting its advisory **Rule 5** using required-checks context it cannot see. |
| 14 | `.github/required-checks.json` pin; AGENTS.md count asserted **against the pin** | **NEW** | Kills the C5 stale-count class permanently by making prose and pin each other's oracle (Gate 200 doctrine). |
| 15 | Pin **staleness** verdict in the static lane | **NEW** | Neither plan (critic A3). Ruleset `updated_at` is 2026-08-14 — it moves; staleness must fail without the network. Threshold ruling in §7 Phase 5 / R-RT8. |
| 16 | `AGENTS.md:311` *"None of these **three**"* corrected **and asserted** | **NEW** | Critic CE-6. Both plans fix only the numeral on l.309, leaving the load-bearing prohibition narrower than the tool — C5's shape recreated one line below C5. |
| 17 | `billable.{OS}.total_ms` + `job_runs[]` read path; **minutes-equivalent, never dollars** | **NEW** | `tiebreak-spend.md` §2 schema, binding. Neither plan shipped this shape. |
| 18 | Wall-clock / critical path as **max**, not sum, arithmetic stated in the output | **NEW**, advisory only, never RED | Identical in both plans. "Total minutes" is the number that invites the forbidden `paths:` fix. |
| 19 | Dashboard reads the **last generated JSON from disk**; no `gh` at request time | **NEW** | plan-B §P5; overrules plan-A Phase 7's live call per request. Cheaper and non-flaky. |
| 20 | `_read_ci_health` — `_read_` prefix, byte-identical dual copy, `_mimir_scrub_*`, nothing inlined at generate time | **EXTENSION** of the Heimdall/Níðhöggr/Norns pattern | `_BODY_DIFF_PREFIXES = ("_read_", "_mimir_")` (`check-dashboard-server-parity.py:67`) covers it with **zero** parity-checker edits. That is why it is named `_read_ci_health`. |
| 21 | Skill: cadence, triage order, who decides — **restates no rule** | **NEW** | A skill that re-derives a rule becomes a second implementation the moment the producer changes. Cites `audit-ci-gates`; does not restate it. |
| 22 | Cardinality **FLOORS** chokepoint + empty-tree `must_fail` | **NEW — mandatory** | Critic CE-1, the flagship finding. Without it the deliverable *is* the defect. |
| 23 | Gate 223 budgets and asserts **its own** wall-clock | **NEW** | Critic CE-4. A tool that measures CI cost and not its own has no standing — it runs on every PR inside the dominant required check and daily on the 10× macOS lane. |
| **24** | **Cross-repo (fleet) spend enumeration, paginated** | **NEW — owner-ruled §1.2** | Neither plan, no tiebreak. The bill is in another repo. Page-1-only enumeration is a measurement defect (§10). |
| **25** | **Per-repo run volume + cron-cadence cost driver** | **NEW — owner-ruled §1.2** | 1,825 runs since Aug 1 on `RavenPower-Website`, 4×/hr + 2×/hr crons. A per-run average hides this entirely. |
| **26** | **job-count vs workflow-count, with the consolidation saving stated** | **NEW — owner-ruled §1.2** | Under per-job rounding, N hourly jobs → 1 job with N steps is a ~N× saving. Not derivable from any workflow-level count. |
| **27** | **F1 re-framing: `concurrency:` is inert against cron-driven spend** | **NEW — owner-ruled §1.2** | Corrects `orchestrator-findings.md` F1 in place. Both statements ship side by side. |

**Score.** plan-A supplies the spine (1, 2, 7, 8, 13, 14, 18, 20, 21). plan-B supplies exactly three
substantive components (5, 12, 19) plus the germ of 4. Six rows come from neither panel (3, 6, 15,
16, 22, 23). Four come from the owner ruling (24–27). Two rows are disqualified duplicates of Gate
195 — **one of which plan-A also got wrong.**

**The size correction.** The genuinely new surface is rows 3–8, 11–12, 14–19, 22–27. Everything
suite-internal is Gate 195's and stays Gate 195's.

---

## §4 — Reconciled dependency DAG

```
  P0  Gate 195 one-hop closure  ── independent, ships first, smallest diff, highest value
        (no downstream phase depends on it; it is not on the critical path)

  P1  producer spine + FLOORS + --self-test
        │
        ├──────────────┬───────────────┬────────────────┬─────────────────┐
        v              v               v                v                 v
  P2 trace sink   P3 static      P4 pin + prose    P7 live lane      P8 fleet lane
   (gate(),        detectors      fence + AGENTS     (this repo         (cross-repo
    extracted      (inventory,     .md 309+311        spend, never       spend, never
    harness)       reachability,   cross-assert       gated)             gated)
        │          paths:, concur,      │                │                 │
        │          hygiene, SUITE-      │                │                 │
        │          META, ORPHANED-      │                │                 │
        │          REQUIRED-CONTEXT)    │                │                 │
        └──────────────┴───────────────┘                │                 │
                       v                                 │                 │
                 P5  Gate 223  (static reader only,      │                 │
                     4 fixtures, self-budgeted)          │                 │
                       │                                 │                 │
                       v                                 │                 │
                 P6  post-suite reconcile step           │                 │
                     in validate-marketplace.yml         │                 │
                     (if: always() + sentinel)           │                 │
                       │                                 │                 │
                       └──────────────┬──────────────────┴─────────────────┘
                                      v
                                P9  skill
                                      │
                                      v   (separate change, after one cycle)
                                P10 dashboard reader ⚑ owner ratchet decision
```

**Critical path:** `P1 → P3 → P5 → P6 → P9`. Five phases. P10 is deliberately **off** the critical
path by the §1.1 sequencing ruling; P0 is off it entirely.

**Blocks (hard):**
- **P5 blocks on P2, P3, P4.** Its assertion set covers the trace, the static detectors, and the
  pin↔prose cross-assert. Landing P5 before P4 makes the AGENTS.md assertion red on arrival.
- **P6 blocks on P2 and P5.** Reconciliation needs a trace to read and a registered gate to run beside.
- **P8 blocks on P7.** The fleet lane reuses P7's `convert(timing, policy, visibility) -> row` pure
  function verbatim; a second conversion implementation is disqualified by row 17's own logic.
- **P10 blocks on P5** (a stable, gate-asserted JSON contract) **and on the owner ratchet raise.**

**Parallelises:**
- **P2, P3, P4, P7 are mutually independent** once P1 freezes the document shape — four workstreams,
  disjoint function sets, each appending to `findings[]`. Merge order is irrelevant.
- **P0 parallelises with everything.** It touches only `check-gate-registration.py`.
- **P7 and P8 gate nothing.** Nothing on the critical path reads them.

**Longest pole, honestly:** P10, and not for engineering reasons — the byte-identical server edit
and the panel are mechanical. It is the only phase with an **external decision** in front of it and
the only one touching two generated surfaces at zero ratchet slack. Request the ratchet decision at
P1 so it resolves off the critical path.

---

## §5 — Phases

Every phase carries goal · files touched · acceptance test · pre-build gate · `depends_on_claims`.
`depends_on_claims: []` is written explicitly where there are none — **silence is not an answer.**
Claim ids are those of `claims-table.md`; `F<n>` are `orchestrator-findings.md` findings.

### Phase 0 — The Gate 195 latent false-RED fix (one-hop closure)

**This is a one-hop closure of an existing detector, not a new detector.** It is the single
highest-value thing this engagement found, it costs ~10 lines, and **neither panel would have found
it** because both were busy rebuilding what Gate 195 already does instead of measuring it.

**Goal.** `check-gate-registration.py:233-236` computes `asserts` as *"this block textually contains
a `gate`/`_skip_or_fail` call."* Measured consequence: Gate block **30** (`audit-gates.sh` l.3598
→ l.3719) carries **28 live assertions**, all arriving via `assert_hook_fires` /
`assert_hook_silent`, and is currently marked reachable **only because the two helper *definitions*
happen to sit inside the block**. That is an accident of file layout, not a detection. Hoisting
those 12 lines above the header — a behaviour-preserving refactor — makes Gate 195 emit a false
`unreachable` for a gate with 28 live assertions.

Extend `asserts` to a **closure**: a block asserts if it contains an assertion call **or** a call to
a function whose body (transitively) contains one.

**Two binding implementation constraints** (RT-10 — the attack is on the fix, not on the finding):

1. The closure keys on a **call site in command position**, never on a name occurrence. A naive
   name match re-greens Gate 30 for the same accident-of-layout reason it is green today (the
   definition line `assert_hook_fires() {` contains the name), and additionally marks a block that
   *defines* an assertion-bearing helper and never calls it as asserting — a **false green**. This
   obeys the file's own doctrine at l.63-73: *"the question is behavioural … not 'does a hook path
   appear here?'"*
2. Closure to **fixpoint**, not one literal hop. Two-hop indirection is one refactor away and costs
   a `while`.

**Files touched.** `scripts/check-gate-registration.py` (only).

**Acceptance test.**
```sh
# negative control FIRST — the instrument must be known-falsifiable before its clean means anything
cp scripts/audit-gates.sh /tmp/ag.sh
python3 scripts/check-gate-registration.py /tmp/ag.sh                    # exit 0, "clean"
# must_fail fixture (i): the hoist
#   move L3613-3624 (assert_hook_fires + assert_hook_silent, 12 lines) above the "── Gate 30:" header at L3598
bash -n /tmp/ag_hoist.sh                                                  # SYNTAX OK (refactor is valid)
python3 scripts/check-gate-registration.py /tmp/ag_hoist.sh               # PRE-FIX: exit 2 "[unreachable] Gate 30"
                                                                          # POST-FIX: exit 0
# must_fail fixture (ii): define-but-never-call
#   a block that DEFINES an assertion-bearing helper and never calls it
python3 scripts/check-gate-registration.py /tmp/ag_define_only.sh         # MUST still exit 2 "[unreachable]"
python3 scripts/check-gate-registration.py --self-test                    # unchanged, passes
python3 scripts/check-gate-registration.py scripts/audit-gates.sh         # real tree, exit 0
```
Fixture (ii) is not optional. Without it the fix is indistinguishable from a name match, and a name
match **restores the symptom and retires the defect.**

**Pre-build gate.** Reproduce the false RED end to end with its control, exactly as
`tiebreak-architecture.md` §3.1 and `red-team.md` RT-10 both did independently: unmodified copy →
exit 0; hoisted copy → exit 2 naming Gate 30. If the control does not produce the *distinguishing*
answer, the instrument is broken and nothing downstream of it means anything. Also record the blast
radius (`[measured]` 2 of 47 function definitions in `audit-gates.sh` contain an assertion call), so
"only two functions are affected" is a measurement rather than a hope.

`depends_on_claims: [C14]`

---

### Phase 1 — Producer spine: inventory, invocation graph, FLOORS, `--self-test`

**Goal.** Stand up `scripts/check-ci-gate-health.py` emitting a stable JSON document describing
*what exists and what invokes it*. **No health/spend opinions yet.** This is the artifact all three
surfaces read, so it lands first and alone. Readers compute nothing; anything a reader wants that
the producer does not emit is a **producer change**, never a second implementation.

Frozen document shape (downstream phases add fields, never rename):

```jsonc
{
  "schema": 1, "mode": "static", "generated_at": "<ISO-8601, mandatory>",
  "units": {"gate_number": 222, "dispatcher_arms": 120, "assertion_sites": 604},
  "coverage": {"workflows": "11/11", "gate_sites": "604/604", "hygiene_rules": "5/5",
               "spend": "unmeasured (static lane)"},
  "workflows": [...], "executables": [...], "findings": [], "counts": {}
}
```

**Three spine invariants, each a mechanism rather than a promise:**

1. **FLOORS chokepoint (CE-1, the flagship finding).** Every counting stage routes through
   `_floor(stage, n)`; below the floor is **COULD-NOT-RUN, exit 2**, never clean.
   `FLOORS = {workflows: 1, gate_sites: 1, executables: 1, hygiene_rules: 5, required_checks: 1,
   spend_runs: 1, spend_lanes: 1, fleet_repos: 1}` — the last three added by §2.3.
   `_floor()` on an unregistered stage is a **named exit 2** (`FLOOR-UNREGISTERED: <stage>`), never
   a `KeyError`.
2. **`--self-test` is non-circular (RT-5a).** The DECLARED side of `set(stages) == set(FLOORS)`
   comes from a **static scan of the producer's own source** for stage-emitting call sites; the
   EXECUTED side comes from runtime `_floor()` calls. Two genuinely different surfaces asserted
   against **each other** — the Gate 200 doctrine, applied to the producer itself. Collecting both
   sides from the same runtime is what lets a stage that bypasses `_floor()` be invisible to the
   check whose entire job is catching bypasses.
3. **The denominator is printed beside every verdict (P4).** `workflows 11/11 · gate sites 604/604 ·
   hygiene rules 5/5 · spend: unmeasured`. A verdict without its denominator is the thing that reads
   green falsely — and Gate 223's own green will otherwise be read as "CI is healthy" by exactly the
   reader `orchestrator-findings.md` F3 describes.

**Conventions fixed here, binding on every later phase:**
- **Exit codes — Gate 195's, overruling plan-A.** `0 = clean; 2 = a finding OR a parse ambiguity
  (fail-closed); 1 is never a finding.` plan-A inverted this while citing Gate 195; two sibling
  meta-gates in `scripts/` must not hold opposite meanings for exit 1.
- **The primary key is the source line that executed the assertion**, never the string it printed:
  `assertion_site = "${BASH_SOURCE[1]}:${BASH_LINENO[0]}"`. The name is **display-only and never
  participates in any join.** plan-B keyed on the name and moved from one label to another.
- **The shared anchor constant** (§2.4): `(?:^|[;&|])\s*(gate|_skip_or_fail)\s`, used by the
  DECLARED scan and by every document describing it. `|DECLARED| == |grep -c <anchor>|` is a floor.
- **The unit is declared in the output.** "Gate" denotes three different things here (222 highest
  number / 120 dispatcher arms / 604 assertion sites). A report that prints "N gates" without naming
  which N **is the next stale-count defect** — C5's own shape.

**Files touched.** `scripts/check-ci-gate-health.py` (new); `.github/required-checks.json` (new,
written by the pre-build gate).

**Acceptance test.**
```sh
python3 scripts/check-ci-gate-health.py --json > /tmp/a.json
python3 scripts/check-ci-gate-health.py --json > /tmp/b.json && cmp /tmp/a.json /tmp/b.json   # byte-stable
EMPTY=$(mktemp -d); python3 scripts/check-ci-gate-health.py --root "$EMPTY" --json; \
  test $? -eq 2 && grep -q 'FLOOR-VIOLATION: workflows 0 < 1' ...      # empty tree: exit 2, named
#   .yaml fixture: .github/workflows/ present, every file renamed .yml -> .yaml -> parses 0 -> exit 2
#     (proves the floor fires on CARDINALITY, not on a directory-existence shortcut)
#   hygiene-absent fixture: .github/scripts/check-workflow-hygiene.py deleted -> exit 2
#     FLOOR-VIOLATION: hygiene_rules 0 < 5   (this is the consumer-repo case)
#   unregistered-stage fixture: -> exit 2, FLOOR-UNREGISTERED: <stage>, never a traceback
python3 scripts/check-ci-gate-health.py --self-test                     # incl. the bypass case
python3 scripts/check-ci-gate-health.py --json                          # NEGATIVE CONTROL: real tree, exit 0
```
The negative control is mandatory: without it the four fixtures only prove the producer can die.

**Pre-build gate.** `gh api repos/mcorbett51090/RavenClaude/rulesets` read succeeds and yields the
required-check names; `.github/required-checks.json` is written **from that output** (names, ruleset
id, `probed_on`). **If `gh` is unavailable, STOP** — do not hand-author the pin from the job names
on disk. A guessed pin is worse than no pin, because Phase 3 and Phase 4 assert against it.

`depends_on_claims: [C4, C10, C12, C13, C14]`

---

### Phase 2 — The assertion-execution trace sink

**Goal.** Make "did this line run" answerable. `gate()` and `_skip_or_fail()` append
`site<TAB>frame<TAB>direction<TAB>rc` to `$AUDIT_GATES_TRACE` when that variable is set, and emit
nothing when it is unset. **~4 lines. It changes no verdict.** This is the one edit in the whole
design that touches the suite's core, and it is called out here so the owner sees it rather than
discovers it (§11 open item 1).

**Four measured landmines in those four lines:**

1. **`set -u` kills the suite at assertion site 1.** `audit-gates.sh` runs `set -euo pipefail`
   (line 26). A bare `"$AUDIT_GATES_TRACE"` is an unbound-variable abort on the *first* gate.
   Use `${AUDIT_GATES_TRACE:-}`.
2. **`set -e` + a trailing `&&`.** `[[ … ]] && printf …` as the **last** command of `gate()` returns
   1 when the sink is off, aborting the caller. It must be an `if` block, never a trailing `&&`.
3. **The sink must be `>>` to a file, never a shell array.** Measured under `/bin/bash` 3.2.57: a
   `gate` call inside `$( )` or a subshell still keys correctly, and an append-mode file sink
   survives the child process where any in-memory accumulator would not.
4. **Terminal sentinel (RT-2).** The suite writes `__SUITE_COMPLETE<TAB><sha256><TAB><n_sites>` as
   the last action of a normal exit path. Without it, an abort at site 12 of 604 yields a trace of
   12 rows and reconciliation prints **592 false UNRUN rows on top of the one real failure** — an
   alarm nobody can read is an alarm nobody keeps.

**Join integrity.** The producer records the SHA-256 of `audit-gates.sh` on **both** sides and exits
2 on mismatch, with the mechanical cause named: `SHA-MISMATCH: audit-gates.sh changed between run
and reconcile — re-run the suite`. Line numbers are a valid key only against identical bytes and are
**never persisted as an identity across commits** — this is a *within-run* join. (Red-team attack
F-1, "the key breaks on every rebase", was opened and **failed**: both sides are scanned from the
same bytes in the same job.)

**Files touched.** `scripts/audit-gates.sh` (`gate()` + `_skip_or_fail()` only).

**Acceptance test.**
```sh
bash -n scripts/audit-gates.sh
# RT-4 extracted-harness fixture — THE RULE holds structurally; the suite is NEVER invoked
sed -n '/^gate()/,/^}/p'          scripts/audit-gates.sh >  "$T/harness.sh"
sed -n '/^_skip_or_fail()/,/^}/p' scripts/audit-gates.sh >> "$T/harness.sh"
#   source into a 3-assertion driver; run twice (sink set / unset); cmp the two stdouts -> identical
# sink-off smoke: driver runs to completion under set -euo pipefail, exit 0
# full-suite PASS/FAIL/SKIP counts identical to the pre-change baseline recorded below
```

**Pre-build gate.** (a) Record `scripts/audit-gates.sh`'s PASS/FAIL/SKIP counts on a clean tree
**before** the sink lands, so a pre-existing red is not misattributed to the new four lines.
(b) Confirm line 26 still carries `set -euo pipefail` — the two landmines above are conditional on
it. (c) **Owner sign-off that `gate()` may be touched at all** (§11 open item 1). Four of the red
team's six high-severity modes live in this one 4-line edit — which is a reason to review those four
lines hard, not a reason to refuse them.

`depends_on_claims: [C10, C14]`

---

### Phase 3 — Static detectors (the whole gated surface)

**Goal.** Every finding class that is hermetic — no network, no `gh`, no clock. This is the only
lane Gate 223 ever calls.

| Symptom | Rule | Severity |
|---|---|---|
| `HANGING-RISK` | a **required** workflow's `pull_request` trigger carries `paths:`/`paths-ignore:` | **RED**. Remediation string states literally *"do not remediate by adding a paths filter — this makes it worse"* and must contain "remove the filter". |
| `ORPHANED-REQUIRED-CONTEXT` | a pinned required context matches no job `name:` in `.github/workflows/*.yml` | **RED**. RT-9: renaming a required job's `name:` hangs the PR **Pending forever** — the same unrecoverable direction as `paths:`, different trigger. |
| `UNRESOLVABLE-CONTEXT` | a job `name:` is templated — measured live: `"Every PreToolUse hook fails closed (${{ matrix.os }})"` | **WARN** with the literal template. Never a false MISSING. The CE-5 lesson applied to a second inventory. |
| `UNRUN` | an executable exists but no path reaches it from any **workflow root** | **RED**. A `--check N` dispatcher arm is *not* a root (reachable only by hand); nor is a mention in a comment or in Markdown. |
| `PHANTOM` | an invoked executable does not exist on disk | **RED** |
| `SUITE-META` | `check-gate-registration.py`'s exit code, propagated | inherits |
| `GHOST-WORKFLOW` | API-registered, absent on disk, **after** excluding `dynamic/**` and `state != active` | INFO |
| `NO-PERM-FLOOR`, `UNPINNED-ACTION` | delegated to `check-workflow-hygiene.py` Rules 1/2 | inherits |
| `DISPATCH-ONLY` | a check whose only PR-relevant trigger is `workflow_dispatch` is **not** a gate (C16) | **RED** |
| `UNTRUSTED-INTERP`, `CREDS-PERSIST` | untrusted `${{ github.event.* }}` inside a `run:` body; `persist-credentials: false` on untrusted-input workflows | **RED** |
| `NO-CONCURRENCY` | workflow lacks a `concurrency:` group | **WARN**, allowlisting `quarantine-intake` + `regenerate-artifacts` **with the F1 rationale inline** (untrusted intake mid-write / post-merge self-heal — cancelling those loses work, not time). Output must carry the §1.2 scoping: *this lever addresses superseded pushes only and does nothing for cron-driven spend.* |
| `CRON-NO-FILTER` | a `paths:`-filtered workflow whose `schedule:` trigger re-admits the whole surface (F2 — `validate-macos.yml:55`, `cron: "17 9 * * *"` on `macos-latest`) | **WARN**, and a spend line item on any private consumer |
| `PIN-STALE` | `.github/required-checks.json` `probed_on` age | see RT-8 in §6 |

**Two inventory rules that are the difference between a tool and a cry-wolf machine:**
- **`dynamic/**` is excluded from on-disk reconciliation, with the reason printed INLINE in the
  output** (not only in code). The two registered-but-fileless workflows are
  `dynamic/dependabot/dependabot-updates` and `dynamic/pages/pages-build-deployment` —
  GitHub-managed. **There is no file to find and there never was** (C13, falsified inference).
- **`state != active` is filtered beside it** (CE-5). `dynamic/**` describes the two rows observed
  *here, today*; `deleted` / `disabled_manually` / `disabled_inactivity` / `disabled_fork` rows are
  the normal condition of any repo with history — i.e. every consumer repo the portability
  requirement targets.
- **Comments are not invocations.** Invocations are extracted only from a workflow step's `run:`
  body and from executable lines of `audit-gates.sh`; comment lines are stripped first. Live
  specimen: `quarantine-intake.yml:18` names `scripts/sanitize-webfetch-body.py`, which does not
  exist at that path. A naive extractor reports a phantom invocation **and** a phantom missing file
  simultaneously.

**Bounded overlap.** The producer **invokes** `check-workflow-hygiene.py` for Rules 1/2 and
`check-gate-registration.py` for everything suite-internal. It owns only what needs the
required-checks context — including the promotion of hygiene **Rule 5 from advisory to RED**, which
that script structurally cannot do because it is a scaffolded consumer artifact that cannot see the
ruleset.

**Files touched.** `scripts/check-ci-gate-health.py`.

**Acceptance test — positive control per class, before any clean run means anything.**
```sh
# HANGING-RISK: tempdir copy, give validate-schemas.yml's pull_request: a paths: filter
#   -> exit 2, names HANGING-RISK: Validate plugin and marketplace JSON Schemas
# built-in negative control on the real tree: validate-macos.yml is paths-filtered + macOS +
#   NOT required -> must classify INFO/filtered-non-required, NOT RED. This single file is the
#   proof the detector can tell required from not-required.
# UNRUN:    add scripts/check-nothing-runs-me.py -> exactly one UNRUN naming it
# PHANTOM:  delete a script validate-marketplace.yml invokes -> exactly one PHANTOM
# ORPHANED-REQUIRED-CONTEXT: rename a required job's name: -> exactly one, RED
# UNRESOLVABLE-CONTEXT: the live matrix job name -> WARN with the literal template, never MISSING
# inventory: 13 registered / 11 on disk / 2 dynamic excluded BY NAME IN THE OUTPUT / ZERO orphans
# real tree: HANGING-RISK count == 0 (C6 — a nonzero count here means the detector is wrong,
#   not that the repo is)
```

**Pre-build gate.** (a) `python3 .github/scripts/check-workflow-hygiene.py` exits 0 on this tree
today — the producer *invokes* it, so a pre-existing red would be misattributed to the new code.
(b) Record `python3 scripts/check-gate-registration.py`'s exit code as the `SUITE-META` baseline
(post-Phase-0). Both are baselines, not assumptions.

`depends_on_claims: [C4, C6, C7, C9, C12, C13, C15, C16]`

> **C15 note.** C15 ("the 4 undocumented required checks are at elevated risk of acquiring a `paths:`
> filter") is **owner-gated and not probe-settleable** — it is a risk *prediction* about future
> author behaviour. **No part of this phase depends on the risk being elevated.** The reviewer checks
> every required workflow for `paths:`/`paths-ignore:` **unconditionally**; the check costs the same
> whether the risk is high or nil. The claim is cited for provenance, not as a load-bearing premise.

---

### Phase 4 — The pin, the prose fence, and the AGENTS.md correction

**Goal.** Kill the C5 stale-count class **permanently**, by making prose and pin each other's oracle
rather than each being independently hand-maintained.

Three parts, and the third is the one both plans missed:

1. `.github/required-checks.json` — the seven check names, the ruleset id, `probed_on`. It is a
   **pinned expectation**, explicitly *not* a source of truth for GitHub. It buys offline
   determinism for the static lane, a drift alarm in `--live`, and the cross-assert below.
2. `AGENTS.md:309` — "requires **three** checks" → seven, with the names.
3. **`AGENTS.md:311` — "None of these **three** may carry a `paths:` filter"** (critic CE-6). This is
   the **load-bearing prohibition**, and both plans left it saying "three" while fixing only the
   count one line above. Result if unfixed: the prohibition stays narrower in prose than the tool
   enforces, and a count-only assertion reads **green forever** — C5's own shape, recreated one line
   below C5.

**⛔ The mechanism must not be a prose scan (R11).** Measured: the count is spelled as an **English
word** in both sentences — *"requires three checks"*, *"None of these three"*. A cross-assert that
greps prose is the class this repo has been bitten by twice (source-scan gates match PROSE). The
count is therefore anchored on a **machine-readable fence** — an HTML comment delimiting a small
generated block inside the AGENTS.md section — and the assertion compares the fenced block against
`len(required-checks.json)`. The prose sentences are rewritten to reference the fenced list rather
than restate a number.

**Files touched.** `AGENTS.md`; `.github/required-checks.json`; `scripts/check-ci-gate-health.py`.

**Acceptance test.**
```sh
grep -c 'these three' AGENTS.md                       # == 0
python3 scripts/check-ci-gate-health.py --json        # exit 0, no PIN-PROSE-DRIFT
# NEGATIVE CONTROL — a docs gate that has never been seen red is not a gate:
#   in a tempdir copy, revert the fenced block to three entries -> exit 2, names PIN-PROSE-DRIFT
#   in a tempdir copy, add an 8th name to required-checks.json -> exit 2, same symptom
# both directions, because a one-directional cross-assert is a constant with extra steps
```

**Pre-build gate.** `.github/required-checks.json` exists **and was written from a live ruleset
read** (Phase 1's gate). Correcting prose from an unverified list replaces a stale number with a
confident wrong one — strictly worse, because the confident one stops anyone from checking.

`depends_on_claims: [C4, C5, C7]`

---

### Phase 5 — Gate 223 (the teeth)

**Goal.** Register the producer as a gate with bidirectional teeth **inside the existing required
check**. No new workflow, no new required check — `audit-gates.sh` already runs inside
`Validate Marketplace` (required context #1) and inside `validate-macos.yml`'s macOS lane.
`[measured]` **223 is free**: the `Supported:` list tops at 222; 219/220/221/223/224 occur 0 times.

**⛔ Gate 223 is a STATIC READER. It executes nothing it parses and it never invokes
`scripts/audit-gates.sh`** (THE RULE, §2.1). It reads `.github/workflows/*.yml`, `audit-gates.sh`
**as text**, its own `mktemp` fixture trees, and the extracted `gate()` harness.

Registration is **triple**: main-sequence block **and** a `223)` dispatcher arm **and** the
`Supported:` string. Gate 195 fails a dispatcher-only registration, and this plan does not get an
exemption from the gate it is contributing to.

| # | Assertion | Direction | Symptom grep |
|---|---|---|---|
| 1 | clean tree | `must_pass` | — |
| 2 | empty tree exits **2**, not 0, not 1 | boolean `[[ $rc -eq 2 ]]` → `must_pass` | `FLOOR-VIOLATION: workflows 0 < 1` |
| 3 | `.yaml`-renamed tree exits 2 | boolean → `must_pass` | `FLOOR-VIOLATION: workflows 0 < 1` |
| 4 | hygiene-script-absent tree exits 2 | boolean → `must_pass` | `FLOOR-VIOLATION: hygiene_rules 0 < 5` |
| 5 | injected `paths:` on a required check | `must_fail` | `HANGING-RISK` |
| 6 | orphan executable | `must_fail` | `UNRUN` |
| 7 | pin↔prose drift | `must_fail` | `PIN-PROSE-DRIFT` |
| 8 | the reconcile step declares `if: always()` in the workflow YAML | `must_pass` | static YAML read (RT-1 guard, so the guard itself cannot rot on a step reorder) |
| 9 | `--self-test` | `must_pass` | — |
| 10 | trace-sink stdout invariant, on the **extracted harness** | `must_pass` | §2.1 |
| 11 | **Gate 223's own wall-clock** under its budget | `must_pass` | prints the measured ms beside the budget |

**Every exit-code assertion is written as a boolean `[[ $rc -eq 2 ]] → must_pass` PLUS a grep for
its specific symptom string.** `gate … must_fail` accepts *any* nonzero, and a Python traceback is
nonzero (hazard A2). A `must_fail` that a crash can satisfy is a gate that asserts nothing —
precisely what this project exists to find.

**Assertion 11 is not decoration (CE-4).** Gate 223 runs on every PR at ~190 runs/day inside the
dominant required check, and daily on the 10× macOS lane. A tool that measures CI cost and does not
measure its own has no standing. The budget is set from a measured baseline at build time (R9 is
accepted as a build-time measurement, not a design defect — the trace sink is 604 file appends; the
four `mktemp` fixture trees are the unmeasured part).

Fixtures are built in `mktemp -d` inside the gate block (the suite's dominant pattern). Nothing is
committed under `scripts/fixtures/`.

**Files touched.** `scripts/audit-gates.sh` (one block + one `case` arm + the `Supported:` string);
`scripts/check-ci-gate-health.py` (`--self-test`).

**Acceptance test.**
```sh
scripts/audit-gates.sh --check 223                        # all 11 assertions pass
scripts/audit-gates.sh 2>&1 | grep -c 'ci-gate-health'    # == 11 in the FULL suite (reachability)
python3 scripts/check-gate-registration.py                # exit 0 — no collision, not dispatcher-only
bash -n scripts/audit-gates.sh
```
⛔ **Grep the full-suite output for the assertion NAMES, never for `"Gate 223"`.** That is the
2026-08-17 by-number trap, and this suite is where it happened. Key on the thing that executes.

**Pre-build gate.** `scripts/audit-gates.sh` passes on this tree *before* the block is added; record
PASS/FAIL/SKIP as the baseline. Then invert one `must_pass`/`must_fail` expectation by hand and
confirm the harness reddens — the repo's own "test the test" convention, applied before trusting the
new gate's green.

`depends_on_claims: [C10, C14, C16]`

---

### Phase 6 — The post-suite reconciliation step

**Goal.** Turn the trace into a verdict. **Reconciliation is structurally a post-suite step** — a
Gate 223 that reconciled in-process would see only the gates that ran *before* it and would report
every later gate UNRUN.

```yaml
# .github/workflows/validate-marketplace.yml, job "Validate manifests and hooks"
- name: Audit every gate
  run: scripts/audit-gates.sh
  env: { AUDIT_GATES_TRACE: "${{ runner.temp }}/gates.tsv" }
- name: Reconcile gate execution
  if: always()                       # RT-1 — MANDATORY, and Gate 223 asserts this line statically
  run: python3 scripts/check-ci-gate-health.py --reconcile-trace "${{ runner.temp }}/gates.tsv"
```

**RT-1 — measured, and purpose-defeating without this.** `[measured]` the workflow contains **zero**
`always()`-guarded steps today. GitHub Actions skips every later step in a job once one fails. So a
reconcile step without `if: always()` reddens **only on runs where nothing was wrong** — a coverage
verdict that switches itself off during incidents, which is exactly when "which gates actually ran"
is the question worth asking. And it is silent: the step reports `skipped`, not `failed`.

**Two constraints on the guard:**
- The reconcile step must **not mask** the suite's own failure. The job's conclusion stays driven by
  the suite step; the reconcile step's nonzero is **additive**.
- **RT-2 sentinel handling.** Read `__SUITE_COMPLETE` **first**. Absent ⇒ emit exactly one finding —
  `INCOMPLETE-TRACE (aborted after N of M sites; reconciliation not performed)` — and **zero**
  per-site UNRUN rows, exit 0. The suite's own failure is already the signal. `audit-gates.sh` runs
  `set -euo pipefail` and contains **73** explicit `exit N` sites, so a mid-file abort is ordinary,
  not exotic; without this, the tool's headline output on the worst day is 592 false positives.

**Findings emitted here:** `DECLARED \ EXECUTED` (RED), **`UNDECLARED-EXECUTION`** =
`EXECUTED \ DECLARED` (RED — proof the static reader has gone blind, §2.4), `INCOMPLETE-TRACE`
(single finding, exit 0), `SHA-MISMATCH` (exit 2).

**Files touched.** `.github/workflows/validate-marketplace.yml`;
`scripts/check-ci-gate-health.py` (`--reconcile-trace`).

**Acceptance test.**
```sh
# must_fail fixture: a 3-site harness whose second site aborts
#   -> output contains INCOMPLETE-TRACE and contains ZERO 'UNRUN' rows
# must_fail fixture: a trace with one site removed -> exactly one DECLARED\EXECUTED RED naming the line
# must_fail fixture: a trace row whose site is absent from DECLARED -> one UNDECLARED-EXECUTION
# cardinality parity: |DECLARED| == grep -cE '(^|[;&|]) *(gate|_skip_or_fail) ' scripts/audit-gates.sh
#   -> 604 on today's tree, NOT 601. The three one-liners at 4683/4714/4746 must be present.
# SHA guard: edit audit-gates.sh between run and reconcile -> exit 2, SHA-MISMATCH with the fix named
```
The cardinality-parity assertion is also the cheapest guard against the two latent mis-keying shapes
the red team opened and found **zero live instances of** (two `gate` calls on one line; a
line-continuation `gate \`): both are caught the day they appear, with no separate detector.

**Pre-build gate.** Confirm on a real CI run that the trace file is non-empty and that its site count
equals the static DECLARED count on the same SHA. A trace that silently writes nothing produces a
perfect 604-row UNRUN report, which is the failure this phase exists to prevent, wearing the mask of
a finding.

`depends_on_claims: [C10, C14]`

---

### Phase 7 — The live spend lane, this repo (`--live`, never gated)

**Goal.** Implement `tiebreak-spend.md` §2's schema exactly. **Measure raw, convert through a dated
cited policy file, emit minutes — never dollars.**

**The formula, which is the whole point:**
`billable_minutes_if_private = Σ over job_runs ceil(job_ms / 60000) × multiplier`
— **not** `ceil(total_ms)`. Billing rounds **per job**; the API rounds not at all, and the API number
excludes the multiplier (settled from two docs.github.com pages, retrieved 2026-08-17, quoted
verbatim and pinned in the policy file as `semantics_quote`). A workflow of many short jobs is
under-reported even at 1×.

**Four zero-states, never collapsed.** `free_public_hosted` / `free_self_hosted` /
`measured_zero_unexpected` (WARN) / `unmeasured` (WARN, never OK, **never printed as 0**).
Every state is **derived**; there is no fallthrough `else: state = "free"`; an unmatched combination
is `unmeasured`, reason `"unclassified"`.

**⛔ Banned on this path:** `int(x or 0)`, `sum(... or 0)`, `.get(k, 0)`, `defaultdict(int)`. These
are the exact idioms that manufacture a clean zero. `unmeasured` is `None` in the data model, and an
aggregate over a lane containing any `unmeasured` renders `≥ N min (M runs unmeasured)`, never a
bare total.

**Three inputs that still reach a numeral, closed here (RT-11):**
| trigger | ruling |
|---|---|
| `job_runs[]` present but empty | ⇒ `state: unmeasured`, reason `"job_runs empty"`. **Never `≥ 0 billable min`** — a lower bound of zero is not a measurement. |
| run still in progress | filter to `status == "completed"`; **count the excluded runs in the denominator** so the sample size is visible. |
| unknown OS key (larger runners, future lanes) | ⇒ `unmeasured`, reason `"multiplier unknown for lane <KEY>"`. **Never a default multiplier** — `.get(os, 1)` is CE-2's failure mode one key away. |
| `Σ job_runs.duration_ms != total_ms` | ⇒ `rounding: "total_only_lower_bound"`, render `≥`. Never silently fall back to `ceil(total_ms)`. |

**Files touched.** `scripts/check-ci-gate-health.py` (`--live`);
`.github/ci-cost-policy.json` (new — multipliers + rounding rule **only**, with **per-fact** verified
flags: `multiplier_verified: true` + `source_url` + `retrieved_on: 2026-08-17`,
`price_verified: false`); `tests/fixtures/timing-*.json` (new).

**Acceptance test — five controls, from `tiebreak-spend.md` §5.**
```sh
# 1 golden fixture: real-SHAPED /timing with nonzero MACOS.total_ms + populated job_runs[]
#     -> multiplier==10, billable_minutes_if_private == Σ ceil(job_ms/60000)*10, state=="measured"
# 2 POSITIVE CONTROL (mandatory, or #1 is theatre): flip the policy multiplier to 1
#     -> the golden test MUST FAIL. An assertion that cannot go red is the defect we cite as motivation.
# 3 rounding-shape control: 8 jobs x 20s -> per-job ceiling == 8 min; naive ceil(total_ms) == 3 min.
#     The test pins 8. This is the under-report NO position on the table had caught.
# 4 state-matrix control: 5 one-line fixtures (4 states + unknown-OS) -> 5 distinct renderings;
#     assert `unmeasured` never stringifies containing "0"
# 5 live-path proof on THIS repo: state == "free_public_hosted" AND raw_minutes > 0
#     -> raw minutes are nonzero even where billable is zero, so the live path DOES have a positive
#        control on the raw column. That is what proves the reader is reading and not returning empty.
# floor: 0 classified runs -> exit 2. A spend section that sampled nothing must not render as a
#        repo that spends nothing.
```
**Explicitly forbidden:** synthesising plausible numbers into a report on this repo; a `--demo` mode;
a "sample" row; any path where fixture data can reach rendered output. **The fixture proves the
conversion; the repo proves the read; nothing pretends to prove the bill.**

**Pre-build gate.** `gh auth status` succeeds and `gh api repos/{o}/{r}/actions/runs?per_page=1`
returns 200 — otherwise this phase is written blind against an unverified response shape. Then
re-check C2: `billable.UBUNTU.total_ms` is 0 for a long run. If it is *not* zero, the premise has
changed and the phase is re-scoped before code is written.

`depends_on_claims: [C1, C2, C3, C9, C12, C13]`

---

### Phase 8 — ⚑ The fleet spend lane (owner-ruled, §1.2)

**Goal.** Run the spend surface **across repos**. This repo bills nothing; the bill is in
`RavenPower-Website`. A spend tool scoped to one repo would have reported a healthy zero while the
owner was being billed for 1,825 runs of 1–8-second jobs.

**Reuses Phase 7's `convert(timing, policy, visibility) -> row` verbatim.** A second conversion
implementation is disqualified by row 17's own logic.

**Three outputs the owner ruled must be surfaced:**

1. **Per-repo run volume**, over a **dated, stated window** — never a per-run average, which is what
   hides a 4×/hour cron. The output states the window's start, end, and whether it was truncated
   (`orchestrator-findings.md`'s own measurement-validity caveat: a 6-hour sample presented as a
   rate is the defect `validating-a-measuring-instrument.md` exists to prevent).
2. **Cron cadence as a cost driver.** Parse every `schedule:` and emit derived runs/day per workflow:
   `4,19,34,49 * * * *` ⇒ **96/day**; `7,37 * * * *` ⇒ **48/day**; hourly ⇒ 24/day. Cadence is a
   line item, printed as one.
3. **job-count vs workflow-count**, with the consolidation saving stated in the output:
   *"N jobs × 1 run = N billable minutes under per-job rounding; the same N steps in one job = 1
   billable minute — a ~N× saving."* This lever does not exist at workflow granularity and is
   invisible to any workflow-level count.

**And the F1 correction, printed beside the `NO-CONCURRENCY` recommendations (§1.2):**
*"`concurrency:` addresses superseded pushes only. It does nothing for cron-driven spend — a cron
has no superseding run to collapse into. For cron-driven spend the levers are cadence, job
consolidation under per-job rounding, and `workflow_dispatch`-only for anything that does not need a
schedule."*

**⛔ Enumeration must paginate (§10).** `gh api /user/repos?per_page=100` returns **one page and
silently truncates**; the repo carrying the entire bill was missing from a page-1-only enumeration.
Use `--paginate` / follow the `Link` header, and **assert a repo-count floor** (`fleet_repos`) so a
truncated enumeration exits 2 rather than reporting a small, clean fleet.

**Files touched.** `scripts/check-ci-gate-health.py` (`--fleet`).
**Never gated.** `--fleet` is `--live`-class: network-dependent, non-deterministic, and a WARN that
a rate limit can cause must never block a merge.

**Acceptance test.**
```sh
# POSITIVE CONTROL, and it is the whole reason this lane exists:
#   --fleet must report RavenPower-Website with >= 1825 runs since 2026-08-01,
#   name change-request-sweep / uptime-probe / change-request-agent / oauth-state-gc,
#   derive 96/day + 48/day + 24/day + 24/day from their cron expressions,
#   and compute billable_minutes_if_private > 0 for runs whose billable.total_ms == 0.
# DIFFERENTIAL CONTROL: the same run set through naive ceil(total_ms) must produce a MATERIALLY
#   SMALLER number; assert the two differ. If they agree, the per-job ceiling is not being applied
#   and the lane is measuring nothing.
# pagination control: a mocked 2-page /user/repos -> repo count == page1 + page2, never page1
# floor control: force a 1-page truncated response -> exit 2, FLOOR-VIOLATION: fleet_repos
# consolidation arithmetic: a fixture of 4 jobs x 3s -> 4 billable min; the same 4 as steps of one
#   job -> 1 billable min; the report states the ~4x saving
```

**Pre-build gate.** Run `gh api --paginate /user/repos` and **assert `RavenPower-Website` appears in
the enumeration** before writing any aggregation code. A fleet enumeration that cannot see the repo
generating the bill is an instrument failure, and an empty or small result is a claim about the
probe until a positive control shows it can return the opposite.

`depends_on_claims: [C1, C2, C3, C16]`

---

### Phase 9 — The skill

**Goal.** `plugins/ravenclaude-core/skills/ci-gate-health-review/SKILL.md` — the **periodic**
methodology: cadence (monthly, and on any workflow or ruleset change), run order (`--report` →
triage RED before WARN before INFO), remediation per symptom code, the escalation boundary (a
ruleset change is the owner's, not the tool's), the `paths:` prohibition with C7's citation, and the
§1.2 cron-vs-concurrency lever split.

**⛔ It restates no rule.** A skill that re-derives a rule becomes a second implementation the moment
the producer changes. It carries only what a script cannot: cadence, triage order, who decides.

**Boundary against the existing skill.** `audit-ci-gates` already owns the event-driven,
fixture-based bidirectionality doctrine ("prove it can fail on a known-bad input"). The new skill
**cites** it and does not restate it; one cross-link line is added there. Two skills, one doctrine,
disjoint triggers.

**Files touched.** the new `SKILL.md`; `plugins/ravenclaude-core/skills/audit-ci-gates/SKILL.md`
(one line); `plugins/ravenclaude-core/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`
(version bump — a new skill is a user-visible change and CI fails on version drift).

**Acceptance test.**
```sh
python3 scripts/check-frontmatter.py
python3 scripts/check-md-links.py
npx --yes prettier@3.9.4 --check . --log-level warn
python3 scripts/generate-copilot-plugin.py --check     # version bump ⇒ copilot regen freshness
```

**Pre-build gate.** Phase 5 has landed, so the skill documents symptom codes that are
**gate-enforced**, not aspirational.

`depends_on_claims: []`

---

### Phase 10 — The dashboard reader surface (SEPARATE CHANGE, after one cycle)

**Goal.** `/__ci-health` + one panel, rendering the producer's last generated JSON **from disk**.
No `gh` at request time, nothing regenerated per request (plan-B §P5, overruling plan-A's live call).

**⛔ RT-6 — the floor must cross the file boundary, and the house pattern is fail-open-to-empty.**
`_read_ci_health` is an EXTENSION of the Heimdall/Níðhöggr/Norns pattern, and that pattern is
documented in-repo as *"a git failure / missing dir yields an empty signal, never raises."* Correct
for a web surface; catastrophic here — the producer refuses to report clean on an empty inventory
and the **third surface renders that same emptiness as clean**, on a fresh clone, a consumer repo
that has never run `--live`, or any CI checkout (`.ravenclaude/runs/` is gitignored).

**Binding mitigations, written into the design now even though the phase lands later:**
- The reader keeps fail-open (a dashboard must not 500) but returns a **typed** result:
  `{"state": "unmeasured", "reason": "<verbatim>", "generated_at": null}`. `state` is never absent
  and never defaults.
- `generated_at` is **mandatory** on the producer's JSON; the panel renders a staleness banner past a
  threshold. A three-month-old spend figure with no date is the same defect wearing a number.
- Fixture: call the reader against a missing file and a truncated file; assert `state ==
  "unmeasured"` and that the serialised result contains **no bare `0`** on any count field.

**Files touched.** `scripts/serve-dashboards.py` (`_read_ci_health` + a GET route);
`plugins/ravenclaude-core/scripts/serve-dashboards.py` (**byte-identical**, only `REPO_ROOT` ↔
`PROJECT_ROOT` may vary); `scripts/generate-dashboards.py` (one `<section>` + mount + tab button,
fetching on **activate**); `scripts/check-dom-budget.py` (one appended `RATCHET` row per surface).

The `_read_` prefix is load-bearing: `_BODY_DIFF_PREFIXES = ("_read_", "_mimir_")` in
`check-dashboard-server-parity.py:67` covers the new function with **zero parity-checker edits**.
Nothing is inlined at generate time — the output is git-, machine- and clock-derived and would break
the exact-byte dashboard freshness gate on the next commit.

**⚑ OWNER DECISION REQUIRED — a ratchet raise.** `[measured]` the last `RATCHET` rows are **6217**
(`dashboard.html`) and **7103** (`index.html`), and today's counts are exactly 6,217 and 7,103 —
**zero slack, by design.** A panel needs an owner-approved raise on **both** surfaces in lockstep,
with a **MEASURED** delta (≈ +4/surface expected — but the `check-dom-budget.py` docstring's own rule
is measure, never estimate, and a prior row records an estimate being wrong). If refused → §7
Alternative B ships the reader through the existing Runs card at zero DOM cost.

**Acceptance test.**
```sh
python3 scripts/check-dashboard-server-parity.py       # endpoint names + body-diff
python3 scripts/generate-dashboards.py --check
python3 scripts/generate-index-dashboard.py --check
python3 scripts/check-dom-budget.py --check
python3 scripts/check-dom-budget.py --check --surface plugins/ravenclaude-core/dashboard.html \
        --budget-override $(( MEASURED - 1 ))          # must FAIL — teeth derived, not literal
# live: curl /__ci-health | json.tool ; then RENAME the producer away and confirm the panel renders
#   a stated-unavailable state — not a spinner, not an empty card. A reader that cannot say
#   "I don't know" is the failure mode this whole plan is about.
```

**Pre-build gate.** (a) Owner approval for the ratchet raise, recorded. (b) A measured DOM baseline
captured **before** the panel exists, so the delta is a subtraction and not a guess. (c) One full
cycle of the producer + Gate 223 in production, so the ratchet is spent on a panel whose content has
proven stable.

`depends_on_claims: [C1]`

---

## §6 — Risk matrix (G4a R1–R15 ⊕ G5 RT-1–RT-11 ⊕ the fleet ruling)

**Every entry carries a mitigation or an explicit accepted-risk waiver. No entry is unmitigated.**
G4a's matrix is the input; the red team *verified* it (13 closed, 2 partial) rather than restating
it, and added eleven execution modes the tiebreaks did not reach. Both are merged here.

### 6.1 Inherited risks (G4a), status under the ruled design

| id | Risk | P×I | Status | Mitigation in this plan |
|---|---|---|---|---|
| R1 | Producer reports green on an empty/unreachable inventory | 9 | **CLOSED** (was PARTIAL) | FLOORS chokepoint (P1) + empty/`.yaml`/hygiene-absent fixtures (P5) + non-circular `--self-test` (RT-5a) + typed reader state (RT-6, P10). The two holes the red team found in the mitigation are themselves closed. |
| R2 | `audit-gates.sh` recursively self-invokes → CI hang + `dashboard.html` corruption | 9 | **CLOSED** (was PARTIAL) | THE RULE, structural not guarded (§2.1). The one clause that re-opened it (§2's stdout invariant) is rewritten to the extracted-harness fixture. plan-B's design is overruled entirely here. |
| R3 | 17 false UNRUN REDs from interpolated gate names | 8 | **CLOSED** | Line-keying makes the name display-only and never a join key. Verified by the bash-3.2 frame probe. The smaller opposite-direction hole (RT-3) is closed separately. |
| R4 | Spend reported at 1× where 10× applies | 7 | **CLOSED** | `tiebreak-spend.md` §0 settles multiplier semantics from two primary docs; per-job ceiling added; four zero-states; RT-11's three numeral paths closed (P7). |
| R5 | Stale required-checks pin reads green | 6 | **CLOSED**, cost named | Static-lane staleness verdict fails closed offline (P4). Its cost is a dated outage — see RT-8. |
| R6 | Permanent false `GHOST-WORKFLOW` on `dynamic/**` | 6 | **CLOSED** | Exclusion + reason printed **inline in output** (P3). plan-A had no exclusion anywhere. |
| R7 | plan-B duplicates Gate 195 → two sources of truth | 6 | **CLOSED** | Five duplicate detectors disqualified (§3 rows 9–10); the producer invokes Gate 195 and propagates `SUITE-META`. |
| R8 | Ratchet raise refused/delayed → dashboard stalls the plan | 4 | **CLOSED** | Sequencing ruling removes P10 from the critical path; §7 Alternative B is the designed fallback. |
| R9 | Gate 223 adds unbudgeted wall-clock to the dominant required check + the 10× macOS lane | 5 | **CLOSED in principle**, number pending | Assertion 11 (P5) budgets and asserts its own wall-clock, printing measured ms beside the budget. **Accepted as a build-time measurement**: the trace sink is 604 file appends (cheap); the four `mktemp` fixture trees are the unmeasured part and the budget is set from their measured cost. The red team judges G4a's "Medium-High" probability **overweighted** now that the design is a static reader plus one post-suite step — plan-A's six producer invocations are not in the ruled design. |
| R10 | `state != active` rows → false MISSING on consumer repos | 4 | **CLOSED** | `state` filter beside `dynamic/**` (P3); RT-9 applies the same lesson to the required-context inventory. |
| R11 | `AGENTS.md:311` left saying "these three" | 4 | **CLOSED**, mechanism hardened | P4 fixes l.311 **and** anchors the cross-assert on a machine-readable fence, not a prose sentence — the count is spelled as an English word in both sentences, and a prose scan is the class this repo has been bitten by twice. |
| R12 | Undesigned "unacknowledged CRITICAL" suppression channel | 5 | **CLOSED** | Struck. Findings are RED or they are not findings. |
| R13 | Exit-code convention split across sibling meta-gates | 3 | **CLOSED** | Gate 195's convention adopted (`2 = finding`, `1 never a finding`), overruling plan-A. Every assertion pairs the code with a symptom grep. The one place it was not yet honoured (RT-5b) is closed in §2.3. |
| R14 | Report prints "N gates" with an undefined unit | 4 | **CLOSED** | `units{}` emitted in the JSON and printed beside every count (P1): 222 numbers / 120 dispatcher arms / 604 assertion sites. |
| R15 | Checked-in `estimated_minutes` from a disowned 6-hour sample | 5 | **CLOSED** | Deleted. Never estimate a duration you can measure. |

### 6.2 Execution modes (G5), each with its binding mitigation

| id | Sev | Mode | Mitigation (binding) | Phase |
|---|---|---|---|---|
| RT-1 | HIGH | Reconciliation never runs when the suite is red — Actions skips later steps on failure; `[measured]` **zero** `always()` steps in the workflow today. The coverage verdict switches itself off during incidents, silently (`skipped` ≠ `failed`). | `if: always()` on the reconcile step; it must not mask the suite's failure (additive nonzero); **Gate 223 statically asserts the YAML declares it**, so the guard cannot rot on a step reorder. | P6, P5 #8 |
| RT-2 | HIGH | A truncated trace floods UNRUN — abort at site 12 of 604 ⇒ 592 false REDs on top of one real failure. 73 explicit `exit N` sites under `set -euo pipefail`. | `__SUITE_COMPLETE` sentinel written last on a normal exit; reconciliation reads it **first**; absent ⇒ one `INCOMPLETE-TRACE` finding and **zero** per-site UNRUN rows, exit 0. `must_fail` fixture: 3-site harness aborting at site 2. | P2, P6 |
| RT-3 | HIGH | DECLARED is 99.5% complete and the 0.5% is dropped **silently** — 604 vs 601; three live sites (4683/4714/4746) exempt from the execution check in the *unchecked* direction. | One shared anchor constant; `|DECLARED|` cardinality parity as a floor; `EXECUTED \ DECLARED` promoted to `UNDECLARED-EXECUTION`. §2.4. | P1, P6 |
| RT-4 | HIGH | **Two binding clauses mutually unsatisfiable** — §2's stdout invariant vs §4's THE RULE. A builder obeying the document literally commits B1 (tracked-file corruption in required context #1 at ~190 runs/day). | Resolved in §2.1: extracted-harness fixture; the suite is never invoked; §2's sentence amended. | §2.1, P2, P5 #10 |
| RT-5a | HIGH | The FLOORS `--self-test` is **circular** — both sides derived from the same runtime, so a stage that bypasses `_floor()` is invisible to the check whose job is catching bypasses. | DECLARED-stages from a **static scan of the producer's own source**; EXECUTED-stages from runtime. Two surfaces asserted against each other. | P1 |
| RT-5b | HIGH | `_floor()` `KeyError` on an unregistered stage — a traceback a naive `must_fail` launders into green; and the two tiebreaks disagreed on whether a spend floor exists. | Named exit 2 `FLOOR-UNREGISTERED`; `spend_runs`/`spend_lanes`/`fleet_repos` added to FLOORS. §2.3. | P1, P7, P8 |
| RT-6 | HIGH | The floor stops at the file boundary — the dashboard reader inherits the house fail-open-to-empty pattern and renders the producer's refusal-to-report as clean. | Typed `state` (never absent, never defaulting); mandatory `generated_at`; staleness banner; missing/truncated-file fixture asserting no bare `0`. Written into the design now, inherited by the later change. | P10 |
| RT-7 | MED | The trace sink kills the suite at gate 1 under `set -u`; and a trailing `&&` returns 1 with the sink off, aborting the caller under `set -e`. | `${AUDIT_GATES_TRACE:-}`; an `if` block, never a trailing `&&`; append-mode **file** sink, never a shell array; `bash -n` + sink-off smoke run as acceptance criteria. | P2 |
| RT-8 | MED | Pin-staleness RED is a **dated repo-wide outage** inside the dominant required check — on day N+1, with no code change, every open PR reddens until someone with ruleset access re-probes. | **RULING: option (a), two thresholds.** `probed_on` > **180 days ⇒ WARN**, printed with the exact refresh command; > **365 days ⇒ RED**. The date-free half (pin ↔ fenced-prose cross-assert) carries the real detection weight and costs nothing. *Recorded distinction:* this is **not** the `paths:` class — `paths:` yields Pending forever and is unrecoverable without a ruleset or workflow edit; this yields a **failed** check with a one-command in-repo fix. It fails in the safe direction. The 365-day RED date is written into the pin file as a human-readable field and into the skill's cadence, so the refresh is a scheduled chore rather than a surprise. | P3, P4, P9 |
| RT-9 | MED | Renaming a required job's `name:` hangs the PR **Pending forever** — the `paths:` class with a different trigger. Enumerated by nobody: not the plans, not the critic, not the tiebreaks. | `ORPHANED-REQUIRED-CONTEXT` (RED) via the pin, free once the pin exists; templated job names (measured to exist: `"Every PreToolUse hook fails closed (${{ matrix.os }})"`) emit `UNRESOLVABLE-CONTEXT` (WARN with the literal template), **never a false MISSING**. | P3 |
| RT-10 | MED | The Gate 195 closure, implemented as a **name match**, re-creates the defect it fixes (the definition line contains the name) and adds a false green (define-but-never-call). | Key on a **call site in command position**; iterate to **fixpoint**; **two** `must_fail` fixtures — the hoist *and* define-but-never-call. Blast radius measured: 2 of 47 function definitions. | P0 |
| RT-11 | MED | Three spend inputs still reach a numeral: empty `job_runs[]` ⇒ `≥ 0`; in-progress runs ⇒ partial duration as `measured`; unknown OS key ⇒ silent 1×. | Each ⇒ `unmeasured` with a verbatim reason; `status == "completed"` filter with excluded runs counted in the denominator; **no default multiplier ever**. Fifth state-matrix fixture. Bounded: spend is `--live` only and can never block a merge. | P7 |

### 6.3 New risks introduced by the fleet ruling

| id | Sev | Risk | Mitigation |
|---|---|---|---|
| FL-1 | **HIGH** | **Silent enumeration truncation.** `gh api /user/repos?per_page=100` returns one page and truncates without error; the repo carrying the entire bill was absent from a page-1-only enumeration. A truncated fleet renders as a small, healthy fleet. | `--paginate`/`Link`-header following is mandatory; `fleet_repos` floor; a **repo-count floor asserted by the reviewer**; pagination control fixture (mocked 2-page response). §10. |
| FL-2 | MED | **Cross-repo token scope.** The fleet lane needs read access to private repos; a scope failure could render as "no spend" rather than "not measured". | `unmeasured` state with the verbatim mechanical cause (`http-403-scope` / `http-404` / `gh-absent` / `rate-limit`) — the cause selects the fix and is not interchangeable. Never a zero. |
| FL-3 | MED | **The fleet lane becomes a spend line item itself.** Enumerating N repos × M runs × `/timing` per run is a lot of API calls. | `--fleet` is manual/periodic, never gated, never on a schedule this plan creates; run-window bounded and stated; per-run `/timing` calls capped with the cap printed in the denominator (a sampled fleet says it was sampled). |
| FL-4 | MED | **F1's corrected framing gets re-collapsed** — a future reader sees "concurrency: is the largest safe lever" and applies it to a cron repo, changing nothing while believing the problem is solved. | Both statements ship **side by side** in the report output and the skill, with the cron levers named explicitly. `NO-CONCURRENCY` findings carry the scoping sentence inline. |

### 6.4 Accepted risks (explicit waivers)

| id | Accepted risk | Why accepted |
|---|---|---|
| W-1 | **`job_runs[].duration_ms` may be 0 in practice** (unverified community report). | Self-checking rather than assumed: if `Σ job_runs.duration_ms != total_ms`, `rounding` becomes `total_only_lower_bound` and the value renders `≥`. Never a silent fallback to `ceil(total_ms)`. |
| W-2 | **Multiplier values (10×/2×) come from docs, not from an invoice.** | Policy file carries `source_url` + `retrieved_on: 2026-08-17` + the two doc sentences pinned verbatim as `semantics_quote`; a staleness check WARNs past 180 days. The conversion has never been validated against ground truth — which is exactly why minutes ship and money does not (§9). |
| W-3 | **GitHub could change the `/timing` endpoint's semantics.** | The pinned `semantics_quote` lets a future reader diff the doc against what the code assumes. Detection, not prevention. |
| W-4 | **Gate 223's own wall-clock ceiling is not yet a number.** | R9. Set from a measured baseline at build time; assertion 11 exists so the number is asserted rather than hoped for. Waived as a design defect; not waived as a build step. |
| W-5 | **C15 (elevated `paths:` risk on the 4 undocumented required checks) is unfalsifiable.** | A risk *prediction* about future author behaviour; waiting for an incident is the only "evidence" and that is the thing being prevented. **No phase depends on it** — the check is unconditional. |
| W-6 | **The trace sink touches the suite's core.** | ~4 lines in `gate()`/`_skip_or_fail()`, changing no verdict. Four of the red team's six high-severity modes live in these four lines — a reason to review them hard, not a reason to refuse them. **Owner's call** (§11 item 1); if refused, rows 3–4 are cut and C14's question has no honest answer in this repo. |

---

# G8 — Definition of Done addendum (orchestrator, 2026-08-17)

## Layout allow-list — VERIFIED, no edit needed
The plan mentions no `allowed_globs` check, which read as a gap. Probed instead of assumed: every
path this plan introduces already matches an existing glob in `.repo-layout.json` —
`scripts/check-ci-gate-health.py`, `.github/required-checks.json`, `.github/ci-cost-policy.json`,
`plugins/ravenclaude-core/skills/ci-gate-health-review/SKILL.md`, and
`tests/fixtures/ci-gate-health/**`. **No `.repo-layout.json` change is required.** Stated explicitly
so the build agent does not "helpfully" widen the allow-list for paths that are already covered.

## ⛔ Regen discipline — MANDATORY, because Phase 5 adds a skill
`plugins/ravenclaude-core/skills/ci-gate-health-review/SKILL.md` is a **counted artifact**. The
2026-06-03 three-PR hotfix chain (#244–#247) is what skipping this costs. Re-derived from the live
harness this session, **not** pasted from the cached reference (which the reference itself warns rots —
its item 4 named `generate-repo-guide.py`, **deleted in v0.124.0**):

| Step | Verified live this session |
|---|---|
| Quote `description:` in the new SKILL.md frontmatter if it contains `:` `{` `}` | `scripts/check-frontmatter.py` present |
| Bump skill-count strings in `.claude-plugin/marketplace.json` (top + plugin entry) **and** `plugins/ravenclaude-core/.claude-plugin/plugin.json` | Gate 12 `marketplace-claims`, 50 refs in `audit-gates.sh` |
| `python3 scripts/generate-dashboards.py` | EXISTS, 4 refs |
| `python3 scripts/generate-index-dashboard.py` | EXISTS, 5 refs |
| `python3 scripts/generate-copilot-plugin.py` | EXISTS, 3 refs |
| ~~`scripts/generate-repo-guide.py`~~ | **ABSENT, 0 refs — do NOT run it. Retired v0.124.0.** |
| Fix the `audit-gates.sh` must_fail fixture literal that hardcodes the old skill count | else the bad-input test silently passes |
| Strip session-bound `.ravenclaude/comfort-posture.yaml` mutations before committing | |

## G7 routing verdict (deterministic)
```
execution = consider_ultraplan   confidence 0.6   (size/scope=large; research already done)
landing   = pr                   engineering_signals = ["reserved-gate-slot"]
```
`landing=pr` because the plan reserves **Gate 223** — a concrete engineering pre-commitment that must
not sit canonically in `main` where it can go stale. This addendum and the plan land on
`forge/ci-gate-health-spend` as a **draft PR**.

`execution=consider_ultraplan` is **presented, not acted on** — `--auto-route` was not passed, so the
local-vs-Ultraplan call is the owner's.

## Outstanding `[unverified]` claims and the step that settles each
- **C15** — owner-gated; a risk *prediction*, not probe-settleable. Reshaped so nothing depends on it:
  the reviewer checks required workflows for `paths:` unconditionally. No settling step is possible or
  needed.
- **USD spend output** — blocked. Settles only on BOTH a cited per-minute price table AND one real
  nonzero private-repo `billable.MACOS` cross-checked against an invoice line. Until then the surface
  emits minutes-equivalent with `usd: null` + `usd_blocked_by`.
- **Actual Actions invoice** — the billing API needs an OAuth scope this session's token lacks.
  Settles via `gh auth refresh -h github.com -s user`, then `/users/{u}/settings/billing/actions`.

## Live validation of this plan's own thesis (2026-08-17)
The spend axis was exercised against production before the plan landed. `RavenPower-Website` was
carrying ~98% of the estate's Actions volume through three short crons billing a full minute each;
consolidating them (merged as PR #295, `3a63b6f5`) cut **168 → 96 billed min/day**. Two facts from
that exercise are load-bearing for Phase 4 and are already folded in above: `billable.*.total_ms`
reads **0** for those runs, and `gh api /user/repos?per_page=100` **silently truncates** — a page-1
enumeration missed the single repo carrying the entire bill.

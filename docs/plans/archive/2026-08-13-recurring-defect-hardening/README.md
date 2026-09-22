# Recurring-defect hardening — design + build plan (2026-08-13)

**What this is.** A full-sweep initiative to find every problem class RavenClaude has hit *repetitively*
since creation, and — for each — build a teeth-bearing **prevention** mechanism **and** remediate the
**existing live instances**. Produced via `/forge` (deep): enumerate → research → two divergent
cross-model panels → synthesize → **iterate to 3 consecutive clean passes (rotating models each pass)**
→ build plan → **iterate to 3 consecutive clean passes** → surface owner decisions.

**Owner mandate (this session):** breadth = *full sweep* (engineering + process + product + consumer);
target = *prevent + remediate existing*.

## The deliverables (in this folder)
| File | What |
|---|---|
| `problem-inventory.md` | The authoritative catalog: **6 root causes**, **21 canonical classes** (P1–P21) deduped from 33 miner findings, each with occurrences (dated), applied fix, **live-open backlog**, and a candidate mechanism; a leverage-ranked mechanism list; and the owner-decision seeds. |
| `hardening-plan.md` | The converged **design** plan — 17 phases covering all 21 classes with prevent+remediate, a six-part "teeth" block per mechanism, DAG, risk matrix, prioritization, and the run's live empirical evidence. |
| `build-plan.md` | The converged **build** plan — **17 PRs + 1 docs commit**, keystone-first, each PR with exact files, gate spec, must-fail fixture, acceptance tests, remediation steps, DoD, and owner-gating. |
| `claims-table.md` | The load-bearing facts + provenance (observation/inference). |
| `loop-log.md` | The **design** iterate-loop audit trail (20 passes). |
| `build-loop-log.md` | The **build** iterate-loop audit trail (6 passes). |
| `scope.md` | The G0 scope. |

## The 6 root causes (the whole point — leverage is in the roots)
1. **R1 — verification blind to the failure surface.** Static linters / Linux CI / name-only gates can't see runtime, toolchain, cross-surface, or `main()` defects.
2. **R2 — duplication instead of derivation.** Every sync mechanism eventually becomes a cascade.
3. **R3 — prose rule with no gate.** "A prose rule is a wish"; each class recurred *after* being written down.
4. **R4 — building to a guessed/unverified contract.** (Codex "adapter" → env-shim; a PreCompact hook for a non-problem; a "shared constants module" that never existed.)
5. **R5 — fail-open where fail-closed was intended.** exit-1 vs exit-2; a tie-breaker `else→allow`; silent macOS disarm.
6. **R6 — tooling can't tell intent from a description of intent, or truth from a stale prior.** (Self-referential guards; stale "Still open" notes in files loaded every session.)

## The highest-leverage mechanisms (build order)
1. **Gate-introspection meta-gate** (keystone, PR 1) — proves every gate in `audit-gates.sh` is *reachable*, *fails-on-bad with exit 2*, has a compiling regex, and *appears in the full-suite output by name*. Closes P2/P3/P4/P6 at once; **guards every future gate**, so it lands first ("audit the auditor before you add auditors").
2. **Author-time macOS portability lint** (PR 3) — the highest-recurrence class (bash 3.2 / absent `timeout` / BSD `grep -P` / `sed -i`).
3. **Fail-closed exit-code execution audit** (PR 4).
4. **Surface-parity gate** — assert two generated surfaces *against each other*, never a constant.
5. **Count-SSOT DROP** (PR 12) — derive-don't-duplicate; retires the count-drift cascade.
6. Host behavioral-canary, contract-provenance lint, the **premise-guard scope + sanctioned-escape** fixes, and the residual tail.

## The process, honestly (the rigor you asked for)
- **26 adversarial critic passes total** (20 design + 6 build), rotating Opus/Sonnet each pass; **26 real defects fixed** — 3 substantive design flaws the panels + synthesis *all shared* (the keystone gate as first drafted would have false-positived on **87 of 150** real gates and disabled itself day one), a teeth-honesty tail, and a citation/consistency tail that only a **deterministic `grep` sweep** could close (model-sampled review kept missing one — itself a finding).
- **Live dogfooding, unplanned:** during the run, **three different guards false-positived on legitimate planning/verification work** — the command-review tribunal on a plan that *described* forbidden commands, `guard-premise.sh` on diagnostic prose, and `xc.tribunal-self-disable` on a **read-only** grep. One subagent *tunnelled* around a guard (flagged); every other agent handled it correctly (reword to prose / use the Read tool). This is the strongest possible evidence for R6 + the sanctioned-escape work, and it is captured in the plan.

## ⏳ The decisions I need from you (this is the DoD)
The plan is decision-ready. Seven calls are genuinely yours; four **gate a PR** and are asked directly. See the response accompanying this doc, and `hardening-plan.md` §"Owner decisions" for full context. In brief:

1. **RC_BASELINE / count-SSOT (gates PR 12)** — drop counts everywhere + de-hardcode the render baseline via an *independent* scanner, vs. the hybrid (drop free-prose counts, generate README tables, keep the baseline golden), vs. keep the baseline hardcoded. *(This is the exact Opus-vs-Sonnet split from the count-drift sub-run.)*
2. **Sanctioned-guard-escape door (gates PR 17)** — fund a security red-team to build the widened intent-vs-description escape, or defer. *(The low-risk half — the nested-worktree + Write-scoped-matcher fix — ships now regardless, PR 2, un-gated.)*
3. **macOS enforcement aggressiveness (gates PR 3)** — warn-only vs hard-block vs the hybrid warn-then-block knob (matching the shipped `git_protocol` precedent), and how wide.
4. **Host behavioral-canary (gates PR 10)** — a mandatory host-onboarding bar, or advisory.
5–7. Sequencing confirmation; formalize-or-defer the DOM-budget ratchet (PR 16); and whether the advisory-only residual tail is worth building.

**Nothing is built yet** — this DoD is the plan + build plan + these decisions, exactly as scoped.

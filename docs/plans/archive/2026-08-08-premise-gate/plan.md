# Premise gate — plan

> ## ⛔ SUPERSEDED IN PART BY ITS OWN PHASE P-1 (run 2026-08-08, same day)
>
> **P-1 was executed before anything was built. It did not return a clean route, and it invalidates
> this plan's §8.1 claim that the mechanism fires on Incident 1 unconditionally.**
>
> `transcript_path` IS delivered to every hook (docs-verified 2026-08-08), so Route T's addressing
> and data halves are real — 801 `toolUseResult` lines and 49 carrying a 404 in this session's own
> transcript. **But the same source states the transcript is written ASYNCHRONOUSLY and may lag the
> in-memory conversation** — and `T-SHAPE` must see a probe from earlier in the *same turn*. Unmitigated,
> the hook reads a transcript missing the evidence and reports "no unresolved probe": it **fails open,
> silently, while its canary passes**. Route P (`tool_response`) remains **unverified** after two doc
> fetches.
>
> **`T-SHAPE` is BLOCKED** pending a freshness decision (see Q-6). P0, P3's `T-PROSE` half, P4, P5 and
> P6 are unaffected and remain day-one parallel.
>
> Full result: [`p-1-substrate-probe-result.md`](p-1-substrate-probe-result.md). Neither panel raised
> this, and neither did the probe's own first draft — it surfaced only on reading the source.

**FORGE G6 · run dir `.ravenclaude/runs/forge/premise-gate/`**
Inputs read from disk: `incidents.md`, `scope.md`, `claims-table.md`, `plan-A.md`, `plan-B.md`,
`gap-delta.md`. Repo state verified in-session on `feat/verification-discipline` @ `9ab4654f`,
`ravenclaude-core` **0.239.0**.

> **The one sentence.** A build phase must not stand on a sentence that is not a tool output — and
> the thing that detects "not a tool output" is **the shape of the tool-call sequence and the grammar
> of the written claim, never the author's confidence.**

---

## 0. What this document settles

Every disagreement between Panel A and Panel B ends here with a verdict and its evidential basis.
There are no split-the-difference outcomes. Where a panel wins, it wins on cited evidence; where both
lose, that is stated too.

| # | Contest | Verdict | Decided by |
|---|---|---|---|
| 1 | Core trigger: content-match (A) vs tool-call shape (B) | **Both, OR'd — B primary, A secondary** | §2.1 |
| 2 | FORGE claims-table classifier | **A** (`classify_claim.py`) | §2.2 |
| 3 | Un-testable-premise escape hatch | **A's three exits**, carrying **B's inline marker** | §2.3 |
| 4 | Probe-spec semantic check | **A** (`expected_if_true != expected_if_false`) | §2.4 |
| 5 | Blast-radius floor | **A's shape**, with B's LoC threshold **rejected** | §2.5 |
| 6 | Negative-result ledger substrate | **Neither as written** — both rest on an unverified premise | §2.6 |
| 7 | Portability / landing / release-DoD constraints | **A** (B is silent) | §2.7 |
| 8 | B's alleged defect in A (`depends_on_claims:`) | **CONFIRMED** — plus a second, worse form | §2.8 |
| 9 | Alternatives not resting on claim #11 | **A's probe-kit** primary; **B's dispatch-split** carried | §6 |
| 10 | Does A's DAG over-serialize P3? | **Yes, mildly — gap-delta §3 upheld** | §3 |

---

## 1. Goal, constraints, current state

### 1.1 Goal

Replaying Incident 1, the `/cdn-cgi/trace` control probe (or a real-browser render check) is forced
**before `Email.astro` is written** — not after 16 files, a pushed checklist item, and two turns of
owner-facing architectural advice.

### 1.2 Constraints (every element below satisfies these)

| # | Constraint | Source | Verified this session |
|---|---|---|---|
| C1 | **Fail-closed** — consistent with every other FORGE gate | scope §1 | — |
| C2 | **Proportional** — a `micro`/`quick` run touching one file with no risky premise pays **zero model calls and zero subprocesses** | scope §2 | §7 |
| C3 | **§0 artifact contract** — payload on disk, receipt back | scope §3, `SKILL.md:25-54` | read |
| C4 | **Un-testable premise has a defined path**, not a block | scope §4 | §2.3 |
| C5 | **Fires on a confident author with a real tool call behind them** | scope §5 | §2.9 |
| C6 | **Amend §2, do not restructure** | scope out-of-scope | §2.2 |
| C7 | Lands on `feat/verification-discipline`, extending **PR #849**; no second PR | scope §assumptions | `git branch --show-current` → `feat/verification-discipline` |
| C8 | **bash 3.2 / stock-macOS safe** — no `grep -P`, no GNU `timeout`, no `sed -i`, no `declare -A`, no `mapfile`, no `${x^^}`, no `shopt -s globstar` | CLAUDE.md doors 1–4 | `hooks/_portable.sh:37,55,83` provides `_rc_timeout`/`_rc_upper`/`_rc_pcre_match` |
| C9 | **Python 3.9-compatible** — `from __future__ import annotations`, no `tomllib`, no PEP-604 annotations | CLAUDE.md v0.194.0 / v0.216.0 | — |
| C10 | New gates take slots **177+**; the `--check` dispatcher **and** the `Supported:` list must both be updated | A's C10 | **CONFIRMED**: `audit-gates.sh:561` `Supported:` list ends at **176** |
| C11 | **No `render-trees.py`, no `regenerate-artifacts` battery, in the DoD** | Incident 2 (806 deletions reported as `ok`) | §9 |

### 1.3 Current state (file:line, verified in-session)

| What exists | Where | Why it did not catch Incident 1 |
|---|---|---|
| FORGE **G1**, tiered BLOCK/WARN | `skills/forge-pipeline/SKILL.md:116-129` | Keys on **provenance** ("is it sourced?"). The false claim *was* sourced. No notion of inferential distance. Columns are `claim · tier · source/marker · settling-gate` (`:127`) — **no `kind` column**. |
| **G2/G3** panel contract | `SKILL.md:131-138` | Requires per-phase acceptance tests, a dependency DAG, ≥2 alternatives. **Says nothing about a claims-dependency edge.** `grep -rn depends_on_claims skills/forge-pipeline/` → **0 hits**. This is §2.8. |
| **Depth ladder** | `SKILL.md:94-99` | `micro` = `G0·G6·G7·G8` (no claims table). `quick` (default) = `G0·G1-lite·G2·G3·G6·G7·G8`, `~calls 3-5`. A real insertion point exists between G3 and G6 at quick+; micro has none. A's placement claim checks out. |
| **`diff-budget` skill** | `skills/diff-budget/SKILL.md:32-38` (tiers), `:40-46` ("When invoked") | Prose only. Its own doc claims PreToolUse + pre-commit + CI. `grep -rn diff-budget hooks/hooks.json .claude/settings.json .github/workflows/` → **0 hits**. **None of the three is wired.** Incident 2's 806 deletions walked past it. Claim #8 upheld. |
| **`audit-gates.sh` `gate()` helper** | `scripts/audit-gates.sh:598-621` | The pattern to copy: `gate NAME must_fail|must_pass EXITCODE`. Claim #9/#10 upheld. Not wired to run pre-commit (Incident 2). |
| **`verification-discipline.md`** | `knowledge/verification-discipline.md` (PR #849) | **Prose.** Out of scope to restate. |
| **`_portable.sh`** | `hooks/_portable.sh:37,55,83` | `_rc_timeout`, `_rc_upper`, `_rc_pcre_match` — the C8 shims already exist. A new hook uses them; it does not re-open doors 1–4. |
| **Existing PreToolUse chain on `Write`** | `hooks/hooks.json` | `guard-destructive.sh`, `thing-orchestrator.sh`, `runaway-brake.sh`, `enforce-layout.sh`, `worktree-guard.sh` **already fire on every Write**. A sixth is being added to the hottest path. See R-9. |
| **Existing PostToolUse matchers** | `hooks/hooks.json` | `Edit\|Write\|MultiEdit` (×6) and `WebFetch` (×1). **There is currently no PostToolUse matcher on `Bash`.** Both panels propose adding one. See §2.6. |
| **`mark-web-domain-seen.sh` header** | `hooks/mark-web-domain-seen.sh:26-40` | Records a paid-for lesson: **native Claude Code does NOT export `CLAUDE_SESSION_ID`** — it is on stdin `.session_id`. Getting it wrong collided every session's marker into `runs/unknown/` while the reader looked elsewhere. Both panels' per-session ledgers key on session id. See R-6. |

---

## 2. The reconciled mechanism

Two lanes. The non-FORGE lane is primary, because **Incident 1 happened in ordinary agentic work, not
inside a FORGE run** — a mechanism that only fires inside FORGE would not have fired on the incident
that motivated it. The FORGE lane is adopted regardless, on B's own recommendation (gap-delta §5).

```
                          ┌──────────────────────────┐
   claims-table.md ──────▶│  classify_claim.py       │──▶ kind: observation | inference
   (+ new `kind` column)  │  + planted canary  [A]   │    (forced UPWARD only)
                          └────────────┬─────────────┘
                                       │ shared pattern set
            ┌──────────────────────────┴─────────────────────────┐
            ▼                                                    ▼
  ┌─────────────────────────┐                   ┌────────────────────────────────┐
  │ FORGE lane — G3b        │                   │ NON-FORGE lane — PRIMARY       │
  │ premise-gate.py         │                   │ guard-premise.sh               │
  │ 0 model calls unless    │                   │ PreToolUse Write|Edit|MultiEdit│
  │ a row trips             │                   │                                │
  │ conjuncts:              │                   │  T-SHAPE  [B]  ← primary       │
  │   1 kind==inference [A] │                   │   new source module created    │
  │   2 cited by a build    │                   │   AFTER an unresolved          │
  │     phase (depends_on_  │                   │   negative-result probe        │
  │     claims:) [A + §2.8] │                   │        OR                      │
  │   3 blast radius   [A]  │                   │  T-PROSE  [A]  ← secondary     │
  └───────────┬─────────────┘                   │   diagnosis + certainty stamp  │
              │                                 │   + no control citation        │
              │                                 └───────────────┬────────────────┘
              └────────────────────┬────────────────────────────┘
                                   ▼
                  .ravenclaude/runs/<sid>/premise-ledger.md
                  id · claim · kill_shot · control · expected_if_true
                     · expected_if_false · cost · status
                  status ∈ unsettled | settled | falsified
                         | partially-settled | owner-gated
```

### 2.1 The core trigger — **B primary, A secondary, OR'd. Not AND'd.**

**Verdict: B's tool-call-shape trigger is the primary conjunct set. A's content trigger is retained
as an independent, OR'd second conjunct set.**

**Why B wins the primary slot.** `scope.md`'s one-line success signal is *"the mechanism forces the
`/cdn-cgi/trace` control probe **before `Email.astro` is written**"* — the **file** is the thing that
must not exist yet, regardless of what its header says. B's trigger reads only the objective shape of
the tool-call sequence (a negative-result probe, then construction, with nothing disconfirming in
between) and satisfies that signal **unconditionally**. A's primary trigger satisfies it only if the
author happened to write the rationale prose first — and **A says so itself** (`plan-A.md` §8.3:
*"If the author had written `Email.astro` with no rationale comment... P3 does not fire at step 4...
designing on that is luck, not mechanism"*). A then bolts on P3b — which is B's trigger shape,
retrofitted as an optional phase behind an open Team-Lead question. gap-delta §1.1 is upheld: A told
itself this before B did.

**Why A's trigger is nevertheless kept, and not as a consolation prize.** `incidents.md`'s "critical
structural detail" is one sentence with two halves:

> "The wrong hypothesis was cheap and normal. The damage came from the hypothesis being **silently
> promoted to a premise by being written down**."

B's trigger catches the *first* half (the probe→construction sequence). A's catches the *second* (the
act of writing the diagnosis down as established fact). **Neither alone covers the sentence the
evidence base names as the target.** Concretely, A's trigger fires on a case B's structurally cannot:
a premise formed in a **prior session**, or before a context compaction, then written into a durable
artifact with a certainty stamp — B's session-scoped ledger has no open signal, so B is silent
(B admits this in its own §8, bullet 2). Two independent detectors OR'd raise recall; the
false-positive cost is bounded by the blast-radius floor (§2.5) and the escape hatch (§2.3).

**They are OR'd, not AND'd.** AND-ing them would reproduce A's contingency defect exactly — the shape
trigger would go silent whenever the prose was absent, which is the failure mode this section exists
to fix.

**A's `T-PROSE` conjuncts, adopted verbatim from `plan-A.md` §4c** (all four must hold):
1. Target is a **durable artifact** — not under `.ravenclaude/runs/**`, not `/tmp`, not a scratch path.
2. Content carries a **diagnosis-shaped assertion** — a defect predicate about a *named subject*.
3. Content carries a **certainty stamp** within ±6 lines — `measured` / `verified` / `confirmed` /
   `established` / an ISO date / a bare HTTP status.
4. **No control-probe citation** in the same block.

**`T-SHAPE` conjuncts** (both must hold — the substrate question is §2.6):
1. The Write **creates a new source module** (target does not exist on disk; not scratch/docs/run-dir).
2. An **unresolved negative-result probe** exists in this session's evidence (a 4xx/5xx, a zero-match
   search, a not-found) with **no differently-shaped, positive-capable probe** logged after it.

### 2.2 The FORGE claims-table classifier — **A wins outright**

**Verdict: adopt `classify_claim.py` as specified in `plan-A.md` §4b and P0.** B's Phase 3 is one
table row (*"add a `kind` column, BLOCK inference claims lacking 2nd grounding"*) with no pattern set,
no re-typing rule, and no canary. A specifies five grammatical families (causal connectives, defect
predicates, unenumerated quantifiers, population nouns, modals), **upward-only** re-typing, a planted
canary asserted at import time (verification-discipline Rule 6), and a must-pass/must-fail fixture
pair lifted from this run's own `claims-table.md`. gap-delta §1.1's reversal is upheld.

This is the piece that makes conjunct 1 not-self-report: Incident 1's claim #5 — *"The decoder is
broken, therefore every visitor sees a mangled address"* — carries `is broken` + `therefore` +
`every` + `visitor`, and types `inference` under any author.

**C6 compliance:** the G1 amendment is **one new column** on an existing four-column table
(`SKILL.md:127`), and the G3b block is ≤6 lines with detail in `reference/premise-gate.md`. Amend,
do not restructure.

### 2.3 The un-testable premise — **A's three exits, carrying B's inline marker**

**Verdict: A wins on structure (gap-delta §1.2 upheld and confirmed by reading both), B contributes
one element that A lacks.**

| Exit | When | Effect |
|---|---|---|
| **`probe-run`** | `cost ≤ CHEAP_FLOOR` (default 300 s) | Probe executed, result recorded. Claim → `settled` or `falsified`. A `falsified` claim voids every citing phase. |
| **`probe-deferred-with-cheapest-partial`** | full kill-shot needs prod/credentials, but a cheaper partial exists | The partial is **mandatory**. (Incident 1's partial: a real browser load of the **public** site — no credentials, ~10 s.) Status `partially-settled`. |
| **`owner-gated`** | genuinely needs the human | **Does not block — reshapes.** Every citing phase is (a) capped to a single reversible file, (b) feature-flagged, (c) the exact question is emitted into G0's open questions. Non-citing work proceeds. |

**B's contribution, adopted:** every exit other than `probe-run` **must write an inline
`[unverified — premise not disconfirmed: <reason>]` marker into the artifact's own header**, using
the repo's existing Claim-Grounding marker vocabulary (`plan-B.md` §1.1.2). This is not decoration —
the Memory Engineering Protocol Rule 1 and Claim Grounding Rule 1 both require the marker to be
**persisted inline**, because a basis spoken only in chat launders into an unmarked, trusted-looking
prior. That is precisely how Incident 1's header comment became repo fact. A's exits log to the
ledger; B's marker puts it where the next reader will actually see it. Both.

**B's single `--reason` override is rejected as the whole hatch.** Constraint 4 asks for a *defined
path*, and B's has no distinction between "a cheaper partial exists" and "genuinely needs the owner,"
and no mechanical blast-radius cap on the citing work.

### 2.4 The probe-spec semantic check — **A wins; B has nothing analogous**

**Verdict: adopt A's four-field probe spec (`plan-A.md` §5.1) including `expected_if_true !=
expected_if_false` as a string-inequality assertion.** gap-delta §1.3 identifies a real gap in B and I
confirm it by reading both: B's disconfirming-probe bar is "a differently-shaped tool call with a
positive result," which accepts a control that returns 200 regardless of the hypothesis under test.
A's check is the one *semantic* quality a deterministic gate can assert: **a control whose predicted
result is identical under both hypotheses is not a control.** It is cheap and it is exactly the
Incident-1 error (`/cdn-cgi/l/email-protection` 404s under *both* "decoder broken" and "decoder fine"
— it is a placeholder; that is why it was never a control).

Also adopted from A: `control` must differ from `kill_shot` (a re-run of the same probe is not a
control).

### 2.5 The blast-radius floor — **A's shape; B's LoC threshold rejected**

**Verdict: the floor is "creates a new source module." No LoC threshold.**

B's floor is *"new file AND (≥1 prior file this session OR this file's LoC > ~40)"*. Two defects:
- The `≥1 prior file this session` clause **exempts the first write of a session**, which is a
  gameable and arbitrary carve-out.
- The `>40 LoC` clause is a **proxy**. `verification-discipline.md` Rule 2 is *"assert the property
  that DEFINES the effect, never a proxy."* The property that defines the risk is **a new abstraction
  being introduced on an unfalsified premise** — not its line count. Incident 1's `Email.astro` was
  85 lines and would clear B's bar; a 30-line version of the same mistake would not, and there is no
  principled reason it should be exempt.

A's FORGE floor (`new module OR ≥3 files OR changes existing working behaviour`) is the right shape;
A simply never applies it in the hook lane. The merged hook floor is its first disjunct — **new source
module creation** — because that is the one a `PreToolUse(Write)` hook can evaluate with a single
`test -e` and no diff computation. Edits to existing files are deliberately exempt; that is the
friction budget being spent on purpose, and it is named in the residue (§10).

### 2.6 The negative-result ledger substrate — **neither plan as written; a probe settles it first**

**This is the finding neither panel made, and it is load-bearing for the primary trigger.**

Both panels' `T-SHAPE` implementations depend on the same unstated premise: **that a `PostToolUse`
hook receives a usable `tool_response` for `Bash` and `WebFetch` calls.** A's P3b logs "tool, host,
status class"; B's P0 classifies "HTTP 4xx/5xx from curl/WebFetch... an explicit not-found in Bash
stderr." Both require the tool's *result*, not just its input.

**What is actually verified in-repo:**

| Evidence | Finding |
|---|---|
| `docs/best-practices/hook-authoring.md:36-37` | `tool_response` is shown for `Edit\|Write\|MultiEdit`, annotated *"PostToolUse only"* |
| `docs/best-practices/hook-authoring.md:33` | The `PostToolUse for Bash` example is `{ "tool_name": "Bash", "tool_input": { "command": "ls" } }` — **no `tool_response`** |
| `grep -rn tool_response plugins/ravenclaude-core/hooks/` | **0 hits. No hook in this repo has ever read a tool result.** |
| `hooks/mark-web-domain-seen.sh` (the one PostToolUse-on-WebFetch hook) | reads `tool_input.url` only |
| `docs/plans/2026-07-28-multi-host-audit/round1/codex.md:30` | lists `tool_response` in the generic stdin field set |

So the premise is **plausible and undemonstrated**, with zero in-repo precedent. Building the primary
trigger on it without a probe would be this run committing Incident 1's exact error inside the plan
that exists to prevent it. It is therefore recorded as a claim with a settling gate, and **P-1 settles
it before anything is built.**

**The second, better route — and why it also changes the friction budget.** `transcript_path` is a
documented stdin field (`hooks/gemini-hook-adapter.sh:8` names it as an *identical* Claude Code stdin
field name). If the session transcript JSONL contains tool results in a scannable form, then
`T-SHAPE` can be evaluated **entirely inside the `PreToolUse(Write)` hook** by tailing the last N
transcript lines — with **no PostToolUse hook at all**.

That matters for C2. There is currently **no PostToolUse matcher on `Bash`** in `hooks.json`. Adding
one raises the floor on *every Bash call in every session* — the cost A honestly broke out as its own
phase with its own Team-Lead decision (`plan-A.md` §11 Q1), and which **B's friction budget silently
contradicts**: `plan-B.md` §7 claims *"**0 calls** to any path that never writes a new file"* while
its own P0 hook fires on every tool call. B's numeric floor is wrong as stated. The transcript route
makes B's claim actually true.

**Decision: P-1 is a mandatory pre-build probe phase with a defined fork.**

| P-1 outcome | Substrate for `T-SHAPE` |
|---|---|
| **Route T** — transcript carries scannable tool results | Tail-the-transcript inside `guard-premise.sh`. **No new PostToolUse hook.** Preferred; cheapest; satisfies C2 exactly. |
| **Route P** — transcript unusable, but `tool_response` present for Bash/WebFetch | A's P3b shape: a `PostToolUse(Bash\|WebFetch)` derived-labels-only logger → `probe-log.jsonl`. Costs ~2 ms per Bash call. Requires the Team-Lead decision A already scoped (Q-2 below). |
| **Route N** — **neither** exposes the result | `T-SHAPE` **cannot be built.** The mechanism degrades to `T-PROSE` only. This is stated plainly in §8 and §10; it is not papered over. |

**P-1 is cheap by construction** — it is a pipe-test of the shapes, per
`docs/best-practices/hook-authoring.md:77` (*"A hook that silently does nothing is worse than no
hook. Run a pipe-test before relying on it"*). It costs minutes, not a phase-width.

### 2.7 Portability, landing target, release DoD — **A wins; B is silent**

gap-delta §2 is upheld and confirmed. B's document never mentions macOS, bash 3.2, `grep -P`, GNU
`timeout`, `sed -i`, or Python 3.9. This repo has shipped and then patched that identical class four
separate times (doors 1–4, v0.193.0–v0.199.0), each one **silently disarming a guardrail on stock
macOS**. In a plan whose whole subject is silently-inert guardrails, that omission is disqualifying
for those elements. A's C8/C9/C7 and its P8 release mechanics are adopted wholesale (see §9).

`_rc_pcre_match` already exists at `hooks/_portable.sh:83`, so `T-PROSE`'s pattern matching has a
C8-safe engine with no new shim.

### 2.8 B's alleged defect in A — **CONFIRMED, and there is a second, worse form**

**I verified this myself rather than accepting it. B is right.**

Three independent checks:

1. `grep -rn "depends_on_claims" plugins/ravenclaude-core/skills/forge-pipeline/` → **0 hits.** The
   field does not exist anywhere in the current pipeline contract.
2. `SKILL.md:131-138` (the G2/G3 gate spec, read in full) requires panels to write *"per-phase
   acceptance tests + pre-build gates, a **dependency DAG**... and **≥2 alternative approaches**."*
   The DAG named there is a **phase→phase** dependency graph. There is **no claims-dependency edge**
   in the contract, and nothing instructs a panel to author one.
3. `plan-A.md` P2 (lines 283-289) lists exactly four edits: the ≤6-line G3b block, the depth-ladder
   `G3b` cell, `reference/premise-gate.md`, and a `commands/forge.md` step-ordering amendment.
   **None of them amends the plan-writing contract.**

**Consequence exactly as B states it:** A's conjunct 2 ("cited by ≥1 build phase") is **unsatisfiable
for every claim on every run**, `premise-gate.py` never trips at G3b, and A's own §8.1 FORGE replay —
which *assumes* the field exists on the plan it walks — is unreachable under A's execution plan.

**The second form, which B did not identify and which is worse.** A's Gate 178 supplies
`depends_on_claims: [5]` **in a synthetic fixture**
(`plan-A.md` P1 acceptance row 1: *"claims table with the falsified inference + a plan phase declaring
`depends_on_claims: [5]`"*). So the gate would go **green while the mechanism is inert in
production** — the script demonstrably trips on a fixture nothing in the real pipeline ever produces.
That is the exact silent-green shape A itself cites as the cautionary precedent (*"assert the
artifact exists, not that it works"*, Gate 144, `plan-A.md` §12), landing inside A's own gate.

**The fix, and it is two-part — a fixture alone does not close it:**
- **P2 gains a fifth edit:** amend `SKILL.md:131-138` so the G2/G3 panel contract requires each plan
  phase to declare `depends_on_claims: [<ids>]` (empty list allowed and meaningful — it asserts "this
  phase stands on no inference"), and mirror it in `commands/forge.md`.
- **Gate 179 gains a name-drift assertion:** the gate must read the **field name the SKILL text
  mandates** and assert `premise-gate.py`'s conjunct-2 parser matches that exact string. A rename on
  one side goes red. Without this, the two halves can drift apart while both fixtures stay green —
  the same two-surfaces-asserted-independently defect the repo has now shipped three times
  (v0.211.1, v0.216.0 MH-40).

### 2.9 Why this fires on a confident, wrong author (C5)

At the moment of Incident 1 the author was **confident**, **wrong**, and had **a real tool call behind
them**. Any mechanism keyed to self-reported uncertainty returns null. None of this mechanism's inputs
is the author's confidence:

| Input | What it reads | Why confidence cannot suppress it |
|---|---|---|
| `T-SHAPE` conjunct 2 | the **objective sequence of tool calls** | A 100%-certain author and an explicitly-hedging author produce **byte-identical hook input**. The gate cannot distinguish them and does not try. |
| `T-PROSE` conjunct 3 | the phrase `measured 2026-08-07` **itself** | **The trigger is the assertion of certainty.** Higher confidence makes it *more* likely to fire. A hedged draft (*"I think the decoder may be broken"*) does not trip; the confident, dated, authoritative version — the dangerous one — does. |
| `kind == inference` | the **grammar of the sentence** | `is broken`, `therefore`, `every visitor` are present regardless of certainty; re-typing is upward-only. The author was certain the inference was *true*; they were never confused about it being an *inference*. |
| conjunct: cited by a build phase | the **plan's own dependency edges** | a structural fact about an artifact, not a belief about the world |
| blast radius | the **file list** | arithmetic |

This inverts the usual relationship. Most verification aids ask the author to notice doubt, so they
are strongest where they are least needed and silent where the damage is. This one gets **stronger as
the author gets more certain**, because certainty is what leaves the mechanical trace.

---

## 3. Dependency DAG

```
P-1  substrate probe (Route T / P / N)          ← BLOCKS P1's T-SHAPE half only
  │  cheap: pipe-tests, no build
  │
  ├──────────────┐
  ▼              │
P0  classify_claim.py + canary   (Gate 177)     ← start day 1, parallel to P-1
  │              │
  ▼              ▼
P1  premise-gate.py            P3  guard-premise.sh      ← T-PROSE half starts day 1
   (Gate 178)                     (Gate 180)                (needs P-1 only for T-SHAPE)
  │                              │
  ▼                              │
P2  FORGE §2 G3b + the           │
    depends_on_claims: contract  │
   (Gate 179)                    │
  │                              │
  └──────────────┬───────────────┘
                 ▼
            P7  agent + doc wiring   (Gate 184)
                 │
 P4  pre-commit diff budget ──────┤   ← independent, day 1  (Gate 182)
 P5  review reopen ledger ────────┤   ← independent, day 1  (Gate 183)
 P6  rc probe (probe-kit) ────────┤   ← independent, day 1  (self-test gate 181)
                 ▼
            P8  release DoD
```

**Critical path:** `P-1 → P1 → P2 → P7 → P8` — five phases, of which P-1 is hours not days.

**Parallel from day one:** P0, P4, P5, P6, and **P3's `T-PROSE` half**.

**gap-delta §3 is upheld.** A's DAG draws `P3 → depends on → P0`, but A's own §5.4 describes
`guard-premise.sh`'s conjuncts as pattern-matched **in the hook** via `_rc_pcre_match`, entirely
independent of the Python module — the stated dependency is a *shared pattern vocabulary*, which is
conceptual, not a code or artifact edge. `_rc_pcre_match` is confirmed present at
`hooks/_portable.sh:83`, so P3's bash side can be authored and gated on day one. The pattern
vocabularies are reconciled at P7. This shortens the critical path by one phase-width.

**Serializations that are real and must not be collapsed:**
- **P1 before P2.** Writing the SKILL amendment first documents a gate whose trigger has not been
  proven to fire — the "assert existence, not that it works" defect (Gate 144, v0.216.0). The
  script's gate goes green **before** the pipeline advertises the gate.
- **P-1 before P1's T-SHAPE half.** Non-negotiable; it is the whole point of this plan.
- **P7 after P2 and P3.** The pointer must name the real hook filename, the real escape syntax, and
  the real reference path. Documenting an interface before it is final is the stale-doc defect this
  repo has paid for repeatedly (doors 2–3 supersession notes).

**Suggested batching:** batch 1 = `P-1 ‖ P0 ‖ P3(T-PROSE) ‖ P4 ‖ P5 ‖ P6`; batch 2 =
`P1 ‖ P3(T-SHAPE)`; batch 3 = `P2`; batch 4 = `P7`; batch 5 = `P8`.

---

## 4. Per-phase acceptance tests — every one has teeth

Every gate registers in `audit-gates.sh` using the existing `gate NAME must_fail|must_pass EXITCODE`
helper (`scripts/audit-gates.sh:598-621`), in **three** places (C10): the main sequence, the
`--check` dispatcher, and the `Supported:` string at `:561`. **A phase whose test cannot fail is not
accepted** — every `must_fail` half below has been specified as a concrete mutation, and must be
*observed red* before the phase is closed, not assumed red.

### P-1 — substrate probe · owner: `backend-coder` · **no gate; it is a probe, not a build**

**Do.** Pipe-test both routes with the shapes from `hook-authoring.md:77`:
(a) a `PostToolUse` on `Bash`/`WebFetch` reading stdin, dumping the keys present;
(b) a `PreToolUse(Write)` reading `.transcript_path` and tailing the last 40 JSONL lines, dumping
whether any carries a tool result with a status/exit field.

**Output.** A one-page `substrate-probe.md` in the run dir naming Route **T**, **P**, or **N**, with
the literal captured payload keys pasted in. **This artifact is the disconfirming probe this plan
owes its own premise** — it is the thing that stops P1 being Incident 1 with better paperwork.

**Failure mode:** if the probe is skipped and P1 is built on the assumption, the trigger ships inert
and green. That is the only phase-level failure this plan cannot gate around, which is why P-1 blocks.

### P0 — the claim classifier + its canary · owner: `backend-coder` · **Gate 177 `claim-classifier`**

**Build.** `plugins/ravenclaude-core/scripts/classify_claim.py` (stdlib-only, C9-safe). Add the
`kind` column (`observation | inference`) to the G1 claims-table schema at `SKILL.md:127`. Re-type
**upward only** via the §2.2 pattern set. Ship a **planted canary** asserted at import time.

| Direction | Fixture | Asserts | **How it fails** |
|---|---|---|---|
| `must_pass` | `tests/fixtures/premise-gate/claims-incident1.md`, row typed `observation` by the author | classifier returns `inference` | — |
| `must_pass` | `claims-clean.md` — 8 literal `<cmd> → <output>` rows | all 8 stay `observation` | the over-trigger assertion |
| `must_pass` | `classify_claim.py --self-test` | canary armed, exit 0 | — |
| **`must_fail`** | mutant deleting the causal-connective family (`therefore\|because\|hence\|means that`) | Incident-1 row types `observation` → **nonzero** | delete one word from the pattern set → red |
| **`must_fail`** | mutant stripping the canary `assert` | `--self-test` no longer proves the instrument → **nonzero** | blind the instrument → red |

### P1 — `premise-gate.py`: trigger + ledger · owner: `backend-coder` · **depends on P-1** · **Gate 178 `premise-gate-trigger`**

**Build.** `scripts/premise-gate.py`. Reads `<run-dir>/claims-table.md` + `plan-A.md`/`plan-B.md`,
applies the §2 conjuncts, writes `premise-ledger.md`, emits a §0 receipt on stdout. Exit **0** = no
trip, exit **2** = trip (fail-closed). Includes the four §2.4 shape checks.

| Direction | Fixture | Asserts | **How it fails** |
|---|---|---|---|
| `must_fail` (trips) | Incident-1 replay: falsified inference + a phase declaring `depends_on_claims: [5]`, `files: 16`, `new_module: true` | exit 2; ledger exists, non-empty, names claim 5, status `unsettled` | — |
| `must_pass` | same inference, **no phase cites it** | exit 0, **no subagent dispatched** | the friction floor, asserted not promised |
| `must_pass` | inference cited, citing phase touches **1 file, flag-guarded** | exit 0 | — |
| `must_fail` | ledger whose `control` **equals** its `kill_shot` | exit 2 | — |
| `must_fail` | ledger with `expected_if_true == expected_if_false` | exit 2 | — |
| **`must_fail`** | mutant dropping the `depends_on_claims` conjunct | the no-citation fixture now trips → **false-positive assertion goes red** | over-trigger teeth |
| **`must_fail`** | mutant dropping the `kind == inference` filter | the observations-only fixture trips → red | over-trigger teeth |

Both directions are gated. A trigger that only proves it fires is half a gate; the over-trigger half
is what protects the friction budget from a future "make it stricter" edit.

### P2 — FORGE §2 G3b **+ the `depends_on_claims:` contract** · owner: `backend-coder` · **depends on P1** · **Gate 179 `forge-ladder-wiring`**

**Build — five edits (the fifth is §2.8's fix and is not optional):**
1. A **≤6-line** `### G3b — Premise gate` block in `SKILL.md` §2, between G3 and G6.
2. The `G3b` cell in the §1 ladder rows for `quick`/`standard`/`deep` — **absent from `micro`**.
3. `skills/forge-pipeline/reference/premise-gate.md` + its `reference/` load-table row
   ("load when: `premise-gate.py` exits 2").
4. `commands/forge.md` step-ordering amendment.
5. **`SKILL.md:131-138` — the G2/G3 panel contract now requires each phase to declare
   `depends_on_claims: [<ids>]`** (empty list allowed and meaningful), mirrored in `commands/forge.md`.

| Direction | Asserts | **How it fails** |
|---|---|---|
| `must_pass` | §1 `micro` row does **not** contain `G3b`; `quick`/`standard`/`deep` do — **parsed from the ladder table**, not hardcoded | — |
| `must_pass` | the §2 G3b block is **≤6 lines** | fixed-prompt budget gated, not promised |
| `must_pass` | `reference/premise-gate.md` exists and is referenced exactly once from §2 | — |
| `must_pass` | `quick` depth `~calls` cell still reads `3-5` | C2 |
| `must_pass` | **the G2/G3 contract text mandates `depends_on_claims:`, AND `premise-gate.py`'s conjunct-2 parser matches that exact field name** | the §2.8 anti-drift assertion |
| **`must_fail`** | add `G3b` to the micro row | red |
| **`must_fail`** | grow the §2 block to 7 lines | red |
| **`must_fail`** | rename the field in `SKILL.md` but not in `premise-gate.py` | red — **this is the teeth that make §2.8's fix real rather than a fixture** |

### P3 — `guard-premise.sh` (the non-FORGE lane) · owner: `backend-coder` · **T-PROSE day 1; T-SHAPE after P-1** · **Gate 180 `guard-premise`**

**Build.** `hooks/guard-premise.sh`, `PreToolUse` on `Write|Edit|MultiEdit`, registered in **all
three wirings** (plugin `hooks/hooks.json`, dev-mirror `.claude/settings.json`, Copilot installer via
`copilot-hook-adapter.sh`). Deny = exit 2 with a message naming the kill-shot question and the ledger
path. `_emit_hook_event` on deny (rule `premise-unsettled`). Session resolved via
`_ee_resolve_session()` (**R-6**). C8-safe via `_rc_pcre_match`; **no `grep -P`**. Header carries the
honest limit: *no hook sees the chat answer; this catches the written-artifact subset.*

**Evaluation order is load-bearing for C2:** `test -e <target>` **first** (one stat), then the
short-circuit, then T-SHAPE/T-PROSE. See §7.

| Direction | Fixture (stdin JSON) | Asserts | **How it fails** |
|---|---|---|---|
| `must_fail` (denies) | Write of `Email.astro` with the **verbatim Incident-1 header** (`"…decoder is broken — measured 2026-08-07"`) | exit **2**; stderr names the control-probe demand + ledger path | T-PROSE fires |
| `must_fail` (denies) | Write of a **new** `Email.astro` with **no comment at all**, session evidence carrying an unresolved 404 | exit **2** | **T-SHAPE fires — this is the case A's plan could not cover** |
| `must_pass` (silent) | same + a `control: GET /cdn-cgi/trace → 200 ⇒ edge healthy` line | exit 0 | — |
| `must_pass` (silent) | plain `// TODO: wire this up` | exit 0 | — |
| `must_pass` (silent) | the same diagnosis prose written under `.ravenclaude/runs/<sid>/notes.md` | exit 0 — scratch tier exempt | — |
| `must_pass` (silent) | **edit to an existing file**, unresolved negative signal present | exit 0 | the deliberate floor (§2.5) |
| `must_pass` (silent) | `premise-ok: browser render check, run 2026-08-08` | exit 0 | — |
| `must_fail` (denies) | `premise-ok:` with **nothing after it** | exit 2 | an escape hatch nobody tested is one everybody uses |
| **`must_fail`** | mutant removing the **certainty-stamp** conjunct | plain-TODO fixture now denies → silent assertion red | over-trigger teeth |
| **`must_fail`** | mutant removing the **diagnosis** pattern | Incident-1 prose fixture passes → fires assertion red | detection teeth |
| **`must_fail`** | mutant removing the **new-file** check | the existing-file-edit fixture now denies → red | friction-floor teeth |

### P4 — pre-commit diff budget + orphan check (**Incident 2**) · owner: `backend-coder` · **Gate 182 `pre-commit-diff-budget`**

**Build.** Wire the existing `diff-budget` thresholds (`SKILL.md:32-38`) to a real `pre-commit` git
hook + a gate. **Count deletions as first-class** — Incident 2 was 806 *deletions* reported as `ok`.
Add the knowledge-file **orphan check** in the same phase.

| Direction | Asserts | **How it fails** |
|---|---|---|
| `must_fail` | staged fixture deleting **806** files → nonzero + prints the deletion count | — |
| `must_pass` | a 2-file docs edit → 0 | — |
| `must_fail` | an orphaned fixture knowledge file → nonzero | — |
| **`must_fail`** | mutant counting only **additions** | the 806-deletion fixture passes → red. **This is the exact Incident-2 shape; a gate that counts only additions is the bug wearing a gate's clothes.** |

### P5 — review-loop reopen ledger (**Incident 3**) · owner: `tester-qa` · **Gate 183 `review-reopen-ledger`**

**Build.** `review-ledger.json` per branch. Round *N* must read rounds `1..N-1` and mark every prior
closed finding `still-closed | reopened` **before** any new finding is accepted; the round is scoped
to the diff since round *N-1*, not the whole tree.

| Direction | Asserts | **How it fails** |
|---|---|---|
| `must_fail` | a prior finding demonstrably reopened in the diff and left unadjudicated → nonzero | — |
| `must_pass` | all priors adjudicated → 0 | — |
| **`must_fail`** | mutant ignoring the prior ledger | an unadjudicated reopen passes → red |

### P6 — probe-kit (`rc probe`) · owner: `backend-coder` · **Gate 181 `probe-kit-self-test`**

**Build.** `bin/rc probe <class> <target>` for the recurring runtime classes: **edge/CDN**
(`/cdn-cgi/trace` + the real decoder URL), **browser-render** (headless one-liner returning the
user-visible property), **API-health**, **mail/DNS**. Each class returns the *user-visible* property
(Rule 7), never the nearest proxy.

| Direction | Asserts | **How it fails** |
|---|---|---|
| `must_pass` | `rc probe --self-test`: every probe class returns **distinguishable verdicts on a known-good and a known-bad target** | — |
| **`must_fail`** | a probe class stubbed to return the same verdict for both | **a probe that cannot fail is not a probe** — rejected by its own self-test |

### P7 — agent + doc wiring · owner: `prompt-engineer` · **depends on P2, P3** · **Gate 184 `premise-gate-reachability`**

**Build.** One inline pointer each on `architect.md` and the coder agents → `reference/premise-gate.md`.
Amend `spawn-team` Step 7 (the PR #849 wiring point). Reconcile P0's and P3's pattern vocabularies.
**Do not restate the seven prose rules** (scope out-of-scope) — point, do not repeat.

| Direction | Asserts | **How it fails** |
|---|---|---|
| `must_pass` | each named agent file carries **exactly one** pointer and the path resolves | — |
| **`must_fail`** | delete the pointer | red |
| **`must_fail`** | add a **second, duplicate** pointer | red — duplication is how these drift |

---

## 5. Risk matrix

| # | Risk | Severity | Raised by | Mitigation |
|---|---|---|---|---|
| **R-1** | **A's `depends_on_claims:` is never mandated**, so the FORGE gate is inert by construction and its §8.1 replay unreachable | **HIGH** | **B (gap-delta §4) — CONFIRMED by three independent checks, §2.8** | P2's **fifth edit** amends the G2/G3 contract; **Gate 179's name-drift assertion** is what makes the fix real |
| **R-2** | **A's Gate 178 would go green on a synthetic fixture while the mechanism is inert in production** — the silent-green shape A itself cites (Gate 144) | **HIGH** | **Neither panel** | Gate 179 asserts the SKILL text mandates the field **and** that the parser matches its exact name. A fixture is not a wiring proof. |
| **R-3** | **Both plans' `T-SHAPE` rests on an unverified premise** (`tool_response` available for Bash/WebFetch). Zero in-repo precedent; the repo's own doc shows Bash PostToolUse stdin *without* it | **HIGH** | **Neither panel** | **P-1 blocks P1's T-SHAPE half.** Three named outcomes (Route T/P/N), Route N stated plainly as a degradation, not hidden |
| **R-4** | A's primary trigger fires only if the rationale prose was written first — *"luck, not mechanism"* | **HIGH** | **A, self-disclosed (§8.3)** | Closed: B's shape trigger is primary and A's is secondary/OR'd (§2.1) |
| **R-5** | **B's friction budget is internally inconsistent** — §7 claims "0 calls to any path that never writes a new file" while its own P0 fires PostToolUse on **every** tool call. There is currently no PostToolUse matcher on `Bash` at all | **MED** | **Neither panel** (B contradicts itself; A priced it correctly as Q1) | Route T needs **no PostToolUse hook**; Route P re-opens A's Q1 as a real Team-Lead decision (Q-2) with the ~2 ms/Bash-call cost stated |
| **R-6** | **Session-id resolution.** Native Claude Code does **not** export `CLAUDE_SESSION_ID`; it is on stdin `.session_id`. Getting this wrong once already collided every session's marker into `runs/unknown/` while the reader looked elsewhere | **MED** | **Neither panel** (`hooks/mark-web-domain-seen.sh:26-40`) | Reuse `_ee_resolve_session()` from `_emit-event.sh`; **never** resolve from the env var alone. Assert it in Gate 180. |
| **R-7** | The classifier over-triggers and every row types `inference` | MED | A | Gate 177's `claims-clean.md` must_pass is a standing over-trigger assertion; conjunct 2 makes over-typing nearly free (an uncited inference costs nothing) |
| **R-8** | `guard-premise.sh` denies legitimate prose and gets disabled — *"then it protects nothing"* | MED | A + scope C2 | Narrow conjuncts + the `premise-ok: <named control>` escape (empty does **not** clear) + Gate 180's six silent fixtures. Rollback = one line out of `hooks.json` + the dev mirror; no state to unwind |
| **R-9** | **A sixth PreToolUse deny on the hottest path.** `guard-destructive`, `thing-orchestrator`, `runaway-brake`, `enforce-layout`, `worktree-guard` already fire on every Write | MED | **Neither panel** | New-file `test -e` is the **first** check (§7); measure the added latency with the pipe-test harness and record the number in the PR body — do not assert it |
| **R-10** | **The DoD itself deletes 806 files** if it invokes `render-trees.py` or the full regen battery on a host with no renderer | **HIGH** | Incident 2 | **C11: explicitly excluded from the DoD (§9).** The generator *reported success* while deleting; a green report is not evidence |
| **R-11** | Platform portability — a new hook silently no-ops on stock macOS | MED | **A** (B silent) | C8 sweep in the DoD; `_rc_pcre_match` already exists; the `macos-latest` runner (v0.197.1) executes hooks under `env -i PATH=/usr/bin:/bin` |
| **R-12** | The premise-ledger becomes a durable store nobody prunes | LOW | **Neither panel** | Lives under gitignored `.ravenclaude/runs/<sid>/` — session-scoped by construction, bounded by the run dir's own lifecycle. Stated, per Memory Engineering Protocol Rule 4 |
| **R-13** | A future edit widens the trigger into universal friction | LOW | A | Gates 178/179/180's over-trigger halves + the ≤6-line cap. Nothing defends against **removing** those gates — that residue is named in §10 |
| **R-14** | Reversibility / one-way doors | — | A | Every phase is additive: new scripts, one new hook, one SKILL block, new gates. The only consumer-visible change is a **new deny path**, shipping with a documented, tested escape. Rollback = revert the commits. **No one-way doors.** |

---

## 6. Alternatives

### Alternative 1 (primary alternative) — **probe-kit as activation-energy**, does **not** rest on claim #11

Ship `rc probe <class> <target>` plus a small library of one-command controls. No rule, no block, no
prose.

- **The bet:** the probe wasn't run because *composing* it cost more thought at that moment than the
  wrong conclusion cost. Lower the activation energy to one verb and it gets run.
- **#11-independence:** claim #11 asserts *prose < fail-closed gate*. This is **neither**. If #11 is
  wrong — if a prose rule in an agent file is in fact as effective as a gate — this still works,
  because it asks nobody to believe anything. It changes the cost of the right action.
- **Trade-off:** *zero enforcement — it fires only if the author reaches for it, and Incident 1's
  author felt no need to reach.* That is why it is the alternative and not the primary — and why it
  **ships anyway** (P6) as the remediation payload the deny message points at.

**Verdict: this is the better of the two panels' #11-independent alternatives.** B's Alternative A
(prose-only reinforcement) is rejected by B itself and by scope's out-of-scope list. B's Alternative B
is carried below but B concedes it *"would not have fired on the actual replay."*

### Alternative 2 (carried from B) — **dispatch-boundary role separation**

Split any "diagnose a reported defect" task into a read-only **diagnose** sub-agent (no `Write` tool)
returning a Structured-Output payload with `disconfirming_probe_attempted: bool`, and a **build**
sub-agent the Team Lead refuses to dispatch unless that field is `true` (`spawn-team` Step 4.5's
existing gating pattern).

- **Genuinely novel axis** — organizational/dispatch-shaped rather than artifact/content-shaped. A's
  three alternatives never consider it (gap-delta §2 upheld).
- **#11-independence:** it rests on the repo's already-proven SOP pattern, not on "gates beat prose."
- **Honest weakness, B's own words:** Incident 1 happened inside a **single continuous session** with
  no diagnose/build dispatch boundary to gate. It would not have fired. Carried as a FORGE-side
  reinforcement that dovetails with P2 — **not** a substitute.

### Alternative 3 (carried from A) — **blast-radius containment via the already-wired task-scope gate**

Give up on detecting the false premise; bound what can be built on one. Any work justified by a defect
diagnosis lands as a single reversible, flag-guarded file until a user-visible measurement confirms
the defect. Enforced by `.ravenclaude/task-scope.json` + `enforce-layout.sh` — **already wired,
already fail-closed, zero new hook.**

- **Why it is carried:** this is the **true fallback if claim #11 is wrong *and* the new gate gets
  disabled.** It needs no new code at all.
- **Trade-off:** *the wrong belief survives intact and still reaches the owner as advice — only the
  file count is capped.* It would have prevented 15 of Incident 1's 16 files and the anti-scraping
  regression, but not the two turns of wrong architectural advice, which cost the owner's attention
  directly.

### Rejected — a falsifier seat as the *trigger*

Dispatching an adversarial subagent before every build phase is a model judging a model: correlated
failure, and it costs a call on every plan rather than only on a trip. It is retained only as the
**content** of G3b's conditional dispatch, which is where this plan puts it.

---

## 7. Friction budget — a `micro`/`quick` run touching one file with no risky premise

**FORGE lane:**
- `micro` → G3b is **not in the gate set** (verified: `micro` = `G0·G6·G7·G8`, no claims table).
  **Cost: zero.**
- `quick` → `premise-gate.py` runs **deterministically, zero model calls**, and emits its own §0
  receipt. It dispatches a subagent **only** if ≥1 row trips. Gate 178's no-citation fixture asserts
  *exit 0 with no dispatch* — the floor is gated, not promised.
- Fixed-prompt cost: the §2 block is capped at **≤6 lines**, gated by Gate 179. The `reference/`
  file loads **only when the script exits 2**. The `quick` `~calls` cell must still read `3-5`.

**Non-FORGE lane — the hook, in evaluation order:**

| Step | Cost | Reached on a one-file, no-risky-premise run? |
|---|---|---|
| 1. `test -e "$target"` — is this a **new** file? | one in-process bash builtin, no fork | **yes** — and an edit to an existing file **exits here** |
| 2. Short-circuit: does the evidence source exist at all? | one `stat` | only on new-file creation |
| 3. `T-SHAPE` scan (Route T: tail N transcript lines; Route P: grep the probe log) | bounded read, no fork under Route T | only on new-file creation with evidence present |
| 4. `T-PROSE` `_rc_pcre_match` over the payload | one `perl` fork | only on new-file creation |

**The number:** a `micro`/`quick` run that edits one existing file pays **one `test -e` per Write —
zero forks, zero subprocesses, zero tokens, zero model calls, zero prompts.** A run that creates one
new file with a clean evidence source pays **one `test -e` + one `stat`**. This is the same
short-circuit cost class as `runaway-brake.sh` and `guard-web-access.sh`-when-unconfigured.

**This ordering is why it is cheap, and it inverts B's.** B checks the ledger first; that makes every
Write pay a ledger read. Checking `test -e` first means the *overwhelming* common case — editing an
existing file — never touches the ledger at all.

**Under Route P only,** add ~2 ms per `Bash` call for the PostToolUse logger. That is a real,
non-zero raise on a path that currently has **no** PostToolUse matcher, and it is the substance of
open question **Q-2**.

---

## 8. The replay test — Incident 1, walked through the merged mechanism

### 8.1 Non-FORGE lane — what actually happened

| Step | Event | Mechanism |
|---|---|---|
| 1–3 | Observe the HTML; `curl /cdn-cgi/l/email-protection` → **404**; conclude *"decoder broken, P1"* | The 404 opens an **unresolved negative signal**. The *conclusion* is reasoning — **no hook sees it, and none should.** Stated plainly, not glossed. |
| **4** | `Write src/components/Email.astro` — new file, 85 lines, header *"…decoder is broken — measured 2026-08-07"* | **`guard-premise.sh` PreToolUse:** step 1 `test -e` → new file ✓ · **`T-SHAPE`**: unresolved 404 with no disconfirming probe after it ✓ → **exit 2, DENY**. Independently, **`T-PROSE`**: durable artifact ✓ · diagnosis-shaped (`is broken` + named subject) ✓ · certainty stamp (`measured 2026-08-07`) ✓ · no `control:` citation ✓ → **also DENY**. |
| — | stderr | *"This write follows an unresolved negative-result probe (`curl → 404`) and asserts a diagnosis as established fact. Name the control that distinguishes 'the mechanism is broken' from 'you probed the wrong thing' — or run `rc probe edge www.ravenpower.net`. Record it in `.ravenclaude/runs/<sid>/premise-ledger.md`."* |
| — | author runs `rc probe edge www.ravenpower.net` (P6) | `trace: 200 · decode-script: 200 · rendered mailto: matt@ravenpower.net · __cf_email__ remaining: 0` — **the premise dies in ~10 seconds** |

**Firing point: the `PreToolUse` of the very first `Write` of `Email.astro`. The file is never
created.** ✓ Two independent triggers fire; either alone would have sufficed.

**The prose-free variant** (author writes `Email.astro` with no rationale comment): `T-PROSE` is
silent, **`T-SHAPE` still fires at step 4** — this is the hole A conceded in its §8.3 and it is
closed, **conditional on P-1 returning Route T or P.**

**Route N, stated plainly as the brief requires:** if P-1 finds that neither the transcript nor
`tool_response` exposes a tool result, **`T-SHAPE` cannot be built.** In that world the mechanism
degrades to `T-PROSE` alone: it fires on the incident **as it actually happened** (the header comment
was written), but **not** on the prose-free variant — where the first catch is P4's pre-commit diff
budget at 16 files, *after* construction but before `main`, before the owner's checklist, and before
the two turns of advice. That is a real weakening and it is not papered over.

### 8.2 FORGE lane — had the work gone through `/forge`

| Step | Event | Mechanism |
|---|---|---|
| G0 | scope: *"fix the mangled email addresses on production"* | — |
| G1 | row #1 `GET /cdn-cgi/l/email-protection → 404` | `kind: observation` (literal `<cmd> → <output>`) |
| G1 | row #5 *"The decoder is broken, therefore every visitor sees a mangled address"* | author may type it `observation`; **`classify_claim.py` forces `inference`** — `is broken` + `therefore` + `every` + `visitor` |
| G2/G3 | Panel phase 1: create `Email.astro`, convert 10 call sites, 15 markers across 5 files — **`depends_on_claims: [5]`, `files: 16`, `new_module: true`** | the field exists **because P2's fifth edit put it in the contract** (§2.8). Without that edit this row is empty and the gate is inert. |
| **G3b** | `premise-gate.py`, **0 model calls** | row #5: `inference` ✓ · cited by a build phase ✓ · new module + 16 files ✓ → **TRIP, exit 2**, `premise-ledger.md` written |
| G3b | conditional subagent (the only model call this gate ever makes) authors the spec | `kill_shot`: load prod in a real browser, read `span.__cf_email__` count + rendered `href`. `control`: `GET /cdn-cgi/trace`. `expected_if_true`: non-200 (edge unhealthy). `expected_if_false`: **200** (edge healthy ⇒ a 404 on one path is not a decoder failure). `cost`: **10 s**. Shape checks pass: `control != kill_shot` ✓, `expected_if_true != expected_if_false` ✓ |
| G3b | `cost ≤ CHEAP_FLOOR` ⇒ **`probe-run`: the probe is mandatory** | `/cdn-cgi/trace` → **200**. Browser: `__cf_email__ remaining 0`, `href mailto:matt@ravenpower.net`, `"[email protected]" in body: false` |
| G3b | row #5 → **`falsified`**; every citing phase voided | receipt `{"gate":"G3b","status":"fail","blockers":["claim #5 falsified — all citing phases void"]}` — fail-closed, does not reach G6 |

**Firing point: G3b, immediately after the panels return, before G6 synthesis and before any build
phase runs.** `Email.astro` is never authored. ✓

---

## 9. Definition of Done

- [ ] **Gates 177–184** registered in **all three** places: the main `audit-gates.sh` sequence, the
      `--check` dispatcher, **and** the `Supported:` list at `audit-gates.sh:561` (verified: currently
      ends at **176**). *This exact omission has shipped before.*
- [ ] **Every gate's `must_fail` half observed RED** by actually stripping the teeth — not assumed.
      *(verification-discipline Rule 6: prove the instrument.)*
- [ ] `scripts/audit-gates.sh` **green end-to-end**.
- [ ] `python3 scripts/check-layout.py --all` clean. `.repo-layout.json` needs **no edit** — verified
      in-session that `plugins/*/scripts/**`, `plugins/*/hooks/**`, `plugins/*/skills/**`, and
      `tests/fixtures/**` are all already in `allowed_globs` (75 globs total).
- [ ] `npx --yes prettier@3.9.4 --write .` then `--check .` → exit 0; `ruff check .` → exit 0.
- [ ] `plugin.json` + `marketplace.json` bumped **in lockstep** `0.239.0 → 0.240.0` (CI fails on drift).
- [ ] **`scripts/generate-copilot-plugin.py` re-run** — required by the "copilot: package freshness"
      audit gate on **any** version bump, and this change alters the hook count (33 → 34).
- [ ] **`scripts/generate-codex-agents.py --check`** — run it; it must pass. Agent count is unchanged
      (15) and skill count is unchanged (50), so no agent-description-budget impact; but run the
      `--check` rather than reasoning about it.
- [ ] **⛔ DO NOT run `scripts/render-trees.py` or the full `regenerate-artifacts` battery.** Incident
      2: `render-trees.py` **printed `ok`** while deleting 800+ tree SVGs and 186 concept visuals on a
      host with no renderer. No decision tree, concept diagram, or `.mmd` source is touched by this
      change, so neither generator has any input here. **A generator's own success report is not
      evidence.**
- [ ] **C8/C9 sweep on every new file:** no `grep -P`, no GNU `timeout`, no `sed -i`, no `declare -A`,
      no `mapfile`, no `${x^^}`, no `shopt -s globstar`; `from __future__ import annotations` on every
      new `.py`.
- [ ] **The replay is EXECUTED, not asserted:** run `premise-gate.py` against the committed Incident-1
      fixture and paste the exit code + the resulting ledger into the PR body. Run the
      `guard-premise.sh` pipe-test against the verbatim Incident-1 header and paste `exit=2`.
- [ ] **`substrate-probe.md` (P-1) committed to the run dir** with the literal captured payload keys —
      the disconfirming probe this plan owes its own premise.
- [ ] The seven prose rules of `verification-discipline.md` are **pointed at, never restated**.
- [ ] Lands on `feat/verification-discipline`, extending **PR #849**. No second PR.

---

## 10. What this does NOT catch — the honest residue

**Non-FORGE lane:**
1. **A premise never written down that stays under the blast-radius floor.** A confident-wrong edit to
   an *existing* file, with no rationale prose, sails through both conjunct sets. **By design** — that
   is the friction budget being spent deliberately (§2.5).
2. **A "positive-shaped but wrong" premise.** `T-SHAPE` keys on negative-result shapes. A false
   inference drawn from a **misread 200** — a response body that is actually an error page, a log line
   misread as confirming — never opens a signal. Real, named, uncovered. (B's finding; upheld.)
3. **A premise formed before a context reset, then acted on with no fresh probe.** `T-SHAPE`'s
   evidence is session-scoped; a new session loses it. `T-PROSE` partially covers this **only if** the
   author writes the certainty stamp down — which is exactly why A's trigger is kept.
4. **A fabricated premise with zero tool-call grounding.** `T-SHAPE` requires a negative probe to
   exist. In FORGE this is already BLOCK-tier under G1's provenance rule; outside FORGE it is
   uncovered here and uncovered by anything else proposed.
5. **A premise inside a subagent's private reasoning.** No hook sees a subagent's chat prose — only
   its writes. Same irreducible limit `claim-grounding-lint.sh` and `delegation-nudge.sh` already
   document in their own headers.
6. **Hosts where the hooks do not run.** Copilot without the adapter wiring; an **untrusted Codex
   project** (hook-hash trust — and every `git pull` that changes a hook byte re-disarms it, per
   v0.216.0 MH-17); a bare `git commit` outside any agent session — **that last one P4 does cover**,
   because it installs as a real git hook.
7. **The prose-free variant, under Route N** (§8.1). Caught at commit by P4, not before construction.

**FORGE lane:**
8. **A wrong *observation*.** The gate never re-verifies a claim typed `observation`; a stale fixture
   or a lying tool passes. Rule 6's planted canary is the only defense and it is behavioral.
9. **A probe spec that is well-shaped but semantically hollow.** The gate checks shape.
   `control != kill_shot` and `expected_if_true != expected_if_false` catch the two mechanical
   degenerate cases; a plausible-but-irrelevant control still passes.
10. **`owner-gated` premises.** The mechanism caps blast radius and surfaces the question; the wrong
    belief survives until the human answers.

**Both lanes:**
11. **Incident 3's stopping rule.** P5 makes the loop converge on regressions; *"when is round N
    negative-value?"* remains human judgment.
12. **A future edit that removes the over-trigger gates.** Gates 178/179/180's must_fail halves defend
    the friction budget; **nothing defends against deleting those gates.**
13. **The override path is honesty-dependent.** An agent can supply a `--reason` or a `premise-ok:`
    that misrepresents "genuinely untestable." Logging, the inline marker, and Heimdall visibility
    raise the cost; nothing makes it impossible. (B's framing, adopted: an author who overrides is now
    *on the record* in a way Incident 1's silent construction never was — a real improvement even in
    the worst case.)

---

## 11. Claims settled and outstanding

Per the G6 contract, every `[unverified]` marker carries the step that settles it.

| Claim | Status | Settling step |
|---|---|---|
| #1–#5, #7, #9 (`claims-table.md`) | settled | — |
| #6 — FORGE G1 as written would have passed claim #5 | settled | re-verified this session: `SKILL.md:116-129` keys on provenance only; `:127` columns carry no `kind` |
| #8 — `diff-budget` did not fire on the 806-file deletion | **settled this session** | `grep -rn diff-budget hooks/hooks.json .claude/settings.json .github/workflows/` → **0 hits**. None of its three claimed wirings exists |
| #10 — gate teeth are Rule 6 mechanized | settled | `audit-gates.sh:598-621` read; `gate()` takes an explicit `must_fail`/`must_pass` direction |
| **#11 — a prose rule in an agent file is weaker than a fail-closed gate** | **`[unverified — asserted, not measured]`** | **Settled by measurement after P8, not before build.** The mechanism emits `_emit_hook_event` on every deny. After 30 days, compare the `premise-unsettled` deny count against citations of `verification-discipline.md`'s Rule 7 in the same window. **Design does not block on it**: Alternative 1 (probe-kit, §6) is #11-independent and ships regardless as P6, and Alternative 3 is a zero-new-code fallback if #11 is wrong |
| **NEW — `tool_response` is available to a PostToolUse hook for `Bash`/`WebFetch`** | **`[unverified — no in-repo precedent]`** | **P-1** (§2.6). Zero hooks read it; the repo's own `hook-authoring.md:33` shows Bash PostToolUse stdin **without** it |
| **NEW — the session transcript at `transcript_path` carries scannable tool results** | **`[unverified — field name confirmed, content not]`** | **P-1** (§2.6). Field name confirmed at `hooks/gemini-hook-adapter.sh:8`; contents unverified |
| **NEW — `.repo-layout.json` needs no edit** | **settled this session** | all four required globs present in the 75-glob allow-list |
| **NEW — gate slots 177+ are free** | **settled this session** | `audit-gates.sh:561` `Supported:` list ends at 176. ⚠ Still confirm no concurrent branch has claimed them (Q-4) |

---

## 12. Open questions for the Team Lead — each stated as a decision with a recommendation

| # | Decision | Recommendation | Blocks |
|---|---|---|---|
| **Q-1** | **Does P-1 gate the whole build, or only P1's `T-SHAPE` half?** | **Only the `T-SHAPE` half.** P0, P3's `T-PROSE` half, P4, P5, P6 all start day one; P-1 is hours, not a phase-width. Gating everything on it would serialize a five-phase critical path behind a pipe-test. | P1 |
| **Q-2** | **If P-1 returns Route P** (transcript unusable, `tool_response` available), do we accept a **new `PostToolUse(Bash\|WebFetch)` matcher** — the first PostToolUse-on-Bash hook in this repo, ~2 ms on every Bash call? | **Yes, accept it.** The alternative is Route N, where the replay's success becomes contingent on the author writing the rationale first — *"luck, not mechanism"* in A's own words. But the cost is real and must be measured and recorded, not assumed. (This is A's Q1, re-scoped as a *conditional* rather than an unconditional ask.) | P1, P3 |
| **Q-3** | **`CHEAP_FLOOR` default.** Below it the probe is mandatory; above it the plan routes to `probe-deferred` / `owner-gated`. | **300 s**, as A proposed. Too low ⇒ everything escalates to the owner; too high ⇒ the gate demands expensive probes inline. Revisit after the first ten trips using the ledger's own `cost` column. | P1 |
| **Q-4** | **Does a `falsified` claim at G3b hard-`reject` the run, or return `fail` with blockers so G6 can synthesize a *narrowed* plan from the surviving phases?** | **Return `fail` with blockers.** Less destructive, keeps non-citing work, and matches every other FORGE gate's receipt shape. A hard reject would throw away correct planning because one premise died. | P1, P2 |
| **Q-5** | **Gate slots 177–184.** Verified free against `audit-gates.sh:561` this session. | **Confirm no concurrent branch has claimed them** before P0 lands. This repo has ≥3 worktrees active; a slot collision is a merge conflict in the `Supported:` string, which is cheap to fix but only if noticed. | P0–P7 |
| **Q-6** | **P4 (Incident 2) and P5 (Incident 3) are secondary scope.** Ship in this PR or split? | **Ship in.** P4 is also §8.1's Route-N backstop and therefore **not optional to the primary mechanism**. P5 is genuinely separable and could split if the diff gets large — but it is small and thematically coherent with PR #849. | P4, P5 |

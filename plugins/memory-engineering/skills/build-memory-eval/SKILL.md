---
name: build-memory-eval
description: "Prove a memory system earns its write path — golden set with provenance, judged failure modes, the runnable bake-off, and cost per correct answer. Reach for this before adopting, replacing or retiring any memory system."
---

# Skill: Build a memory eval

**Decision 6 of the six-decision spine — *how would you know it works?*** There is no trustworthy public leaderboard for agent memory. That is not a reason to skip the measurement; it is the reason this skill ships a **procedure you run yourself**.

Every published memory-system ranking is self-reported by its vendor or reported by a competitor, none is independently corroborated, and no neutral head-to-head was located (§3 #8). So the deliverable here is not a citation. It is a bake-off on your data, with your queries, at your budget.

> **`cost-per-correct` is shared with [budget-memory-costs](../budget-memory-costs/SKILL.md) and owned by neither skill.** This one supplies the **accuracy** half; that one supplies the **cost** half. Neither is the mode's home, and a reader landing here must not conclude the cost half lives somewhere else.

---

## Part A — The golden set

### Step 1 — Build it before you build the memory system

A memory project with no golden set cannot tell you whether it improved anything, which is why Tree 1 in [the decision trees](../../knowledge/memory-engineering-decision-trees.md) opens with a stop. Fifty well-chosen items beat five hundred scraped ones.

Every item carries, at minimum — the sheet for this is [`memory-eval-sheet.md`](../../templates/memory-eval-sheet.md):

| Field | Why |
|---|---|
| The query, verbatim | Paraphrasing at judging time is how a system gets credit for the wrong answer |
| The expected answer, or the acceptance criteria | "Looks right" is not a criterion |
| **The session or turn where the fact was established** | Without this you cannot tell recall from a lucky guess |
| **How many sessions ago that was** | Memory decays with distance; a single-session set measures nothing durable |
| Provenance and date of the ground truth | And who decided it |
| The failure mode it is there to catch | Step 2's taxonomy |

**Cover the long horizon deliberately.** A set whose facts were all established in the previous turn is a context-window test wearing a memory system's clothes. Include items whose fact was established many sessions back, items where the fact **changed** since it was written, and items that should return **nothing**.

**No user data, no real memory-store contents, no PII** in the golden set (§4). Synthesize or de-identify.

### Step 2 — Label every item with the failure mode it is there to catch

Six modes. An eval that only measures "right answer / wrong answer" cannot distinguish them, and they have completely different fixes.

| Failure mode | What it looks like | Where the fix lives |
|---|---|---|
| **Stale fact** | Was true when written, is not now | [design-forgetting-policy](../design-forgetting-policy/SKILL.md) — TTL, decay, re-verification |
| **Unresolved contradiction** | Two entries disagree; the answer picks one silently | Same skill — detect, never auto-merge, surface for a human |
| **Confabulated recall** | Confidently recalls something never stored | Extraction or grounding defect; check the write path's logic |
| **Poisoned recall** | Recalls something that was **never true** and could have come from untrusted input | [memory-poisoning-review](../memory-poisoning-review/SKILL.md) — this is a security incident, not an eval miss |
| **Over-retention / leak** | Surfaces something that should have been deleted, or crosses a tenant or user boundary | Retention **and** access scoping; a boundary crossing is a Blocker |
| **Under-retention / amnesia** | Cannot recall something it was supposed to keep | The bound is too tight, or the write never happened |

**Poisoned recall and stale fact look identical in a transcript.** The discriminator is *"was this ever true?"* — and if the answer is no *and* untrusted input could reach that write path, stop the eval and open a security review.

### Step 3 — Decide who judges, before you see any results

- **Two judges, blind to which arm produced the answer.** Adjudicate disagreements by a written rule agreed in advance, not by whoever cares most.
- If a **model** is a judge, it is an instrument that needs its own calibration: run it against a human-labelled slice first and report its agreement rate. A new checker's first output is a claim about the checker.
- **Freeze the rubric before the first run.** A rubric edited after seeing results measures the editor.

---

## Part B — The bake-off (run this)

The answer to "no trustworthy leaderboard exists" is a procedure, not a warning. This one is deliberately small enough to actually run.

### Step 4 — Fix everything that is not the memory system

One variable moves. Write down and hold constant: the **model and version**, the **corpus**, the **golden set**, the **retrieval budget** (top-*k*, context allowance), the **prompt template**, and the **judging rubric**. Record every one of them in the results sheet — a bake-off whose configuration was not written down is not reproducible, which makes it an anecdote.

### Step 5 — Define the arms. Three are mandatory

| Arm | What it is | Why it is mandatory |
|---|---|---|
| **A0 — stateless** | No injected history at all | Sizes the gap. Note it is **not the same job** — it cannot answer a memory-dependent query at any accuracy |
| **A1 — flat lexical retrieval** | BM25 or an embedding index over the same history, no LLM in construction | The humbling baseline: in the published suite this shape was both the most accurate **and** the cheapest per correct answer |
| **A2 — the candidate** | The memory system you are actually considering | — |
| **A3…An** | Any further candidates | Optional; the same rules apply to each |

**A1 is not optional.** Skipping it is how a team spends a quarter building something a keyword index would have beaten.

### Step 6 — Run each arm and record two numbers plus a receipt

For each arm, over the whole golden set:

1. **Accuracy** — correct items ÷ total items, by the frozen rubric.
2. **Total cost over the run** — and this must include the **construction / write-path** cost, not only query cost. Excluding the build is the single most common way a bake-off flatters a memory system, because that is where the money lives (§3 #1).
3. **The receipt** — per-item outcome and failure-mode label, so a later argument is settled by data rather than memory.

Also record, because they are decisions in disguise: **build wall-clock**, **per-query latency (p50 and p95)**, and **footprint at the end of the run**.

### Step 7 — Rank on cost per correct answer, never on either half alone

```
memory_engineering_calc.py cost-per-correct \
  --total-cost-a 240.00 --queries-a 2000 --accuracy-a 0.62 --system-name-a "memory build" \
  --total-cost-b 90.00 --queries-b 2000 --accuracy-b 0.20 --system-name-b "lexical baseline"
```

With those inputs the tool reports `memory build : $0.193548 per correct answer` against `lexical baseline : $0.225`, and then prints:

```
>> NOTE: the raw cost-per-query ranking DISAGREES with this one.
```

Which is exactly the case worth catching: on raw cost the lexical arm is less than half the price and still loses. Run the mode once per pair of arms. System-B flags are all-or-nothing, and an accuracy of `0` or above `1` exits `2` rather than producing a number.

**Accuracy without cost and cost without accuracy are both unfalsifiable.** That is why the mode belongs to neither skill.

### Step 8 — Report the axes a benchmark will never cover

Rank on cost per correct answer, then report these beside it. Each maps to a failure mode from step 2 and none appears on any published leaderboard:

| Metric | How to compute it | What it catches |
|---|---|---|
| **Staleness rate** | Items whose stored fact was outdated at answer time ÷ items whose fact changed | Retention that never fires |
| **Contradiction rate** | Items where two stored entries disagreed ÷ total | Consolidation that merges silently |
| **Confabulation rate** | Confident answers with no stored support ÷ total | Grounding failure |
| **Erasure verification rate** | Deleted items still recoverable — from the row, the vector, a derived summary, or the version history — ÷ deletions attempted | An erasure story that stops at the row (§3 #7) |
| **Recall-by-distance** | Accuracy bucketed by how many sessions ago the fact was established | The long-horizon claim, tested |
| **Cost per correct answer** | Step 7 | Whether it should exist at all |

**Erasure verification is measured by reading back, never by checking a return code.** A redaction call can return success and leave the value in place.

### Step 9 — Freeze, re-run, report the delta

- **Freeze the golden set and the rubric.** Version them beside the code.
- **Every change to the memory system re-runs the whole set** and reports a before/after delta. No eval, no ship.
- **Every production failure becomes a permanent item**, labelled with its failure mode. This is the only mechanism that makes the set get better over time.
- **Re-run the baselines too**, not just the candidate. A model upgrade can quietly make the stateless arm win, and nobody notices if it stopped being measured.

## Guardrails

- **Do not cite a vendor or paper leaderboard as evidence that a memory system works here.** Every one of them is self- or competitor-reported, and the two most-cited benchmarks are contested on methodology (§3 #8).
- Report the configuration with every number. A result without its model, corpus, budget and query count is not transferable, and a number stripped of its conditions makes a claim it cannot support.
- No user data or memory-store contents in the set, the receipts, or the write-up (§4).
- Mark anything you did not measure this run as unmeasured, with the route that would settle it.

## Output

A frozen golden set with provenance and failure-mode labels, a bake-off with at least the stateless and lexical arms, cost per correct answer per arm from the calculator, the six uncovered metrics reported beside it, and a named next action with owner, date and expected movement.

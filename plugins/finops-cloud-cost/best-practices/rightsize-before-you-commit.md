# Rightsize before you commit

**Status:** Pattern
**Domain:** Cloud cost optimization — compute and commitment sequencing
**Applies to:** `finops-cloud-cost`

---

## Why this exists

An over-sized instance costs more on-demand and costs even more with a commitment, because the
commitment locks in the waste for 1–3 years. A t3.xlarge that should be a t3.medium costs roughly
2× the correct instance size on-demand. Buying an RI on that instance locks in 2× the cost for the
commitment term. The rightsizing saving (one-time) and the commitment saving (amortized over the
term) are not additive if you commit before rightsizing — you are committing to the wrong baseline.

The sequence matters: rightsize first, then measure the post-rightsizing baseline, then commit to
that baseline. This is not a preference — it is the optimization path that maximizes total savings
without creating new waste.

## How to apply

1. Pull 14–30 days of P90 CPU and memory utilization data per instance or VM.
2. Identify candidates: P90 CPU ≤25% or P90 memory ≤30% are clearly oversized.
3. Recommend target instance sizes in the P90 CPU target band (40–70%) and memory band (50–80%).
4. Phase the migration: resize one instance in each family, monitor 48 hours, then roll out.
5. Re-measure the P0 baseline on the new rightsized fleet before purchasing any commitments.
6. Only then: proceed to the commitment-vs-on-demand tree in the knowledge bank.

**Do:**

- Use P90 utilization (14–30 days) as the rightsizing signal. P90 captures typical high-water
  marks without being distorted by one-time peaks.
- Check both CPU and memory — an instance may be CPU-undersized but memory-oversized.
- Phase the rollout; don't resize the entire fleet simultaneously (one-time production risk).
- Recalculate the commitment baseline on the post-rightsizing fleet — don't extrapolate from the
  pre-rightsizing data.

**Don't:**

- Use peak utilization as the rightsizing target — this over-provisions.
- Use average utilization as the target — this under-provisions during peak periods.
- Rightsize memory below P90 memory utilization — OOM kills are expensive in availability terms.
- Skip the rightsizing step because "we're in a hurry to buy the RI before the discount window
  closes" — a 1-week delay is trivially small compared to 12 months of over-committed waste.

## Edge cases / when the rule does NOT apply

Some latency-sensitive or CPU-burst-dependent workloads (real-time trading, interactive query
engines, event-driven compute) need headroom above P90 to absorb spikes without degraded
performance. In these cases, rightsize conservatively (target P90 at 50–60% rather than 70%) and
document the headroom rationale. The principle — rightsize before committing — still applies; the
target band widens, it does not disappear.

## See also

- [`./commit-only-to-your-steady-state-baseline.md`](./commit-only-to-your-steady-state-baseline.md)
- [`../skills/rightsizing-and-commitments/SKILL.md`](../skills/rightsizing-and-commitments/SKILL.md)
- [`../knowledge/finops-cloud-cost-decision-trees.md`](../knowledge/finops-cloud-cost-decision-trees.md) — rightsize-before-commit tree

## Provenance

Reflects FinOps Foundation optimize-phase sequencing guidance and the practical finding that
commitment savings calculations that skip rightsizing consistently over-estimate the effective
discount received.

---

_Last reviewed: 2026-06-08 by `claude`._

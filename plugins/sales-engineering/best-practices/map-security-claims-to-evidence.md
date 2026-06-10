# Map every security claim to evidence

**Status:** Absolute rule.

**Use when:** answering any security / vendor-risk questionnaire (SIG, CAIQ, VSA, bespoke).

## The rule

**Every "yes" on a security questionnaire maps to an actual control and its evidence** (a SOC 2 report section, an ISO 27001 Statement-of-Applicability item, a written policy, a system config). A "yes" you can't evidence is not a "yes" — it goes to the verification queue and to `ravenclaude-core/security-reviewer` before it ships.

## Why

A security questionnaire is a **legal artifact**, not marketing copy. A claim that can't survive an audit is a contractual liability: an inflated control surfaces in the buyer's risk review or in an incident post-mortem, where it becomes grounds for clawback, breach of warranty, or a fraud finding. The honesty bar here is higher than anywhere else in the sale, because the answer is binding.

## How

1. Identify the framework (SIG/CAIQ/…) and reuse your mapped control set rather than answering cold.
2. For each answer, state the truth boundary: implemented / roadmap (dated) / N-A (with why) / compensating control — and the evidence behind any "implemented."
3. Where the buyer will accept it, point to the SOC 2 Type II report / trust center instead of re-answering 300 cells.
4. Capitalize every answer into the reusable library with an **owner + freshness date** (stale security answers are a liability).

## Exceptions

None. The only acceptable variation is *which* evidence you cite, never whether you cite any.

## See also

[`../knowledge/security-questionnaire-and-trust.md`](../knowledge/security-questionnaire-and-trust.md) · [`honesty-over-the-fabricated-yes.md`](./honesty-over-the-fabricated-yes.md)

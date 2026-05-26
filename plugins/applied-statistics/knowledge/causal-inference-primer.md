# Knowledge — Causal-inference primer

> **Last reviewed:** 2026-05-26 · **Confidence:** High on the concepts (textbook causal inference); the value here is knowing *when to escalate from correlation to a causal design*, not deep estimator theory.
> This is the differentiation play — it separates a statistician from a chart-maker. Lower-frequency in SMB work, but high-value when the client asks "did X *cause* Y?" rather than "is X *associated with* Y?".

---

## The core distinction

- **Correlation / association** answers "do X and Y move together?" — a regression coefficient, a correlation, an A/B difference *without* randomization.
- **Causation** answers "if we *intervene* on X, does Y change?" — requires either a **randomized experiment** or a **causal design** that defends against confounding.

The agent's rule: **the word "drives / causes / because / impact" triggers a causal-design check.** A correlation alone never licenses a causal claim. The advisory hook flags correlation→causation language in analysis docs.

---

## When correlation is *not* enough — the three threats

| Threat | What it is | Tell |
|---|---|---|
| **Confounding** | A third variable causes both X and Y | The X→Y relationship changes when you control for Z |
| **Selection bias** | Who's *in* the sample depends on the outcome | The comparison groups aren't exchangeable |
| **Reverse causation** | Y causes X, not X causes Y | Timing / plausibility argues the other direction |

If any of these is live and you can't randomize, you need a **causal design**, not a richer regression.

---

## The toolkit (primer depth — recommend, then route to the agent for the build)

| Design | When to use | One-line caveat |
|---|---|---|
| **Randomized experiment (A/B)** | You *can* randomize the intervention | The gold standard — prefer it; see [`experiment-design-and-ab-testing.md`](experiment-design-and-ab-testing.md) |
| **Difference-in-Differences (DiD)** | A treatment hit one group at a known time; you have before/after for treated + untreated | Requires the **parallel-trends** assumption (the groups would have moved together absent treatment) |
| **Matching / propensity scores** | Observational; you want to compare "similar" treated vs untreated units | Only balances **observed** confounders — unobserved confounding still bites |
| **Instrumental variables (IV / 2SLS)** | A variable affects treatment but not the outcome directly | A valid instrument is rare and the assumptions are strong; `linearmodels` implements it |
| **Regression discontinuity (RDD)** | Treatment assigned by a sharp cutoff on a running variable | Estimates a *local* effect near the cutoff only |

For SMB engagements: **push hard toward a randomized experiment when feasible** (it sidesteps all three threats). When it isn't, DiD and matching are the most defensible/communicable; IV and RDD need the right natural setup and careful assumption defense.

---

## How the agent uses this file

1. On any "does X cause/drive/impact Y?" question, state plainly whether the available data supports a **causal** or only an **associational** claim.
2. If causal and randomization is possible → route to experiment design.
3. If causal and only observational data exists → name the most defensible design (usually DiD or matching), state its key assumption, and flag the residual risk (unobserved confounding). Implementation of IV/panel models → `linearmodels` (Tier 2, [`statistics-tooling-2026.md`](statistics-tooling-2026.md)).
4. Never let a regression coefficient be reported as a causal effect without the design to back it.

---

## Provenance

- Standard causal-inference framing (confounding / selection / reverse causation; experiment > DiD/matching > IV/RDD): textbook consensus per the 2026-05-26 research brief. Tier 2 (strong-but-contextual). Refresh trigger: low urgency — concepts are stable; revisit estimator tooling with [`statistics-tooling-2026.md`](statistics-tooling-2026.md).

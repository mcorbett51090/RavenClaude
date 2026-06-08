# Measure relevance with judgment sets, not vibes

**Status:** Absolute rule
**Domain:** Relevance evaluation
**Applies to:** `search-relevance-engineering`

---

## Why this exists

"Search quality improved" is not a statement — it is an opinion about a sample of queries
that happened to be salient to whoever checked. Anecdotal validation is structurally broken:
it overweights head queries (which are already good) and underweights tail queries (which are
usually the worst). It is also unverifiable: you cannot reproduce "it felt better" in a future
session or across a team.

A graded judgment set with nDCG@k is the only falsifiable claim of relevance improvement. It
captures the full query distribution (head + torso + tail), produces a number that is
reproducible, and makes regression detectable. Without it, every tuning cycle is faith-based.

## How to apply

- Build a judgment set **before** the first tuning cycle, not after. The baseline must exist
  before there is a treatment to compare it to.
- Use a graded 4-point relevance scale (0–3, NIST standard). Binary (0/1) is acceptable for
  RAG recall@k; graded is required for nDCG@10 on a ranked list.
- Compute inter-annotator agreement (Cohen's kappa) on a ≥ 20% overlap set.
  Target kappa ≥ 0.6. Below 0.4 means the guidelines are wrong, not the search system.
- After every change: re-compute nDCG@10, MRR, recall@k, precision@k with `scripts/search_eval.py`.
  If the delta is < 0.02 nDCG@10 on the held-out set, the change is not reliably better.

**Do:**

- Sample queries across head, torso, and tail distributions — don't judge only head queries.
- Treat the judgment set as a versioned artifact (date + annotator + retrieval system version).
- Use the worst-10-query list from the baseline as the primary input to tuning.

**Don't:**

- Declare a search system "better" based on manual spot-checking of 5–10 queries.
- Use CTR as a proxy for relevance quality — high CTR can coexist with bad results if the
  top-ranked document is confidently titled even when its content is irrelevant.
- Skip inter-annotator agreement because "we know the domain" — unverified annotation
  consistency makes the nDCG score untrustworthy.

## Edge cases / when the rule does NOT apply

- A new system where no judgment set exists yet and a quick operational check is being done
  to confirm the index is working at all. In this case, spot-checking is acceptable as
  a smoke test — but the judgment set must be built before any tuning cycle starts.
- Highly exploratory prototyping where the query distribution is unknown and the corpus is not
  yet stable. Build the judgment set once the corpus is production-representative.

## See also

- [`./evaluate-retrieval-separately-from-generation.md`](./evaluate-retrieval-separately-from-generation.md)
- [`../skills/retrieval-evaluation/SKILL.md`](../skills/retrieval-evaluation/SKILL.md) — how to build the judgment set.
- [`../scripts/search_eval.py`](../scripts/search_eval.py) — metric computation.
- [`../templates/relevance-judgment-set.md`](../templates/relevance-judgment-set.md) — the artifact format.

## Provenance

IR evaluation best practice going back to TREC (Text REtrieval Conference, 1992–present); the
nDCG@k metric formalized by Järvelin & Kekäläinen (2002); NIST relevance scale widely adopted
in academic and industrial search evaluation. The "vibes-based tuning" failure mode is
documented repeatedly in search engineering retrospectives.

---

_Last reviewed: 2026-06-08 by `claude`._

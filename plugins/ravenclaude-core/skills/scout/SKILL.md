---
name: scout
description: "Discover great-but-low-visibility ideas — the fringe excellence mainstream search buries under popularity. Given a seed (a name, repo, post, or topic), traverse its citation/collaborator graph + the periphery sources, score each candidate on depth × novelty × practitioner-grounding MINUS a popularity penalty, dedup against the idea-board + installed plugins, and emit a ranked shortlist that routes the best finds into /forge. Use when you spot a promising fringe idea (often on LinkedIn / X / GitHub) and want the cluster around it, or to periodically sweep a niche for under-the-radar excellence."
---

# Skill: scout — the fringe-idea scout

## Why this exists

Mainstream search ranks on **popularity** (SEO, backlinks, stars, virality) — which is **orthogonal to quality**. Great-but-low-visibility ideas are invisible to it *by construction*: a single-maintainer "WIP" GitHub repo, a niche practitioner's blog, a LinkedIn post from someone who actually ships. The canonical example this skill was extracted from: **Kurt Buhler's `data-goblin/power-bi-agentic-development`** — genuinely excellent, low stars, surfaced on LinkedIn, missed by every "best Power BI tools" listicle. Scout **inverts the ranking: seek HIGH depth + LOW reach.**

## The score (decoupled from popularity)

> **great-but-obscure ≈ depth × novelty × practitioner-grounding − popularity_penalty**

| Factor | Up-rank | 
|---|---|
| **depth** | technical specificity, a real mechanism, production detail — not a listicle |
| **novelty** | diverges from the mainstream consensus; a non-obvious angle |
| **practitioner-grounding** | born of real shipped work, not theory or marketing |
| **popularity_penalty** | **DOWN-rank the already-famous** — a 10k-star repo, an official vendor doc, a conference-keynote name is *not fringe*. The whole point is the under-the-radar do-er. |

Rank **high-depth + low-reach** to the top. A high-depth + high-reach item is good but not *this skill's* job; a low-depth + low-reach item is just obscure, not a gem.

## Method (5 steps, in order)

1. **Seed.** Take the input — a name / repo / URL / LinkedIn post / topic. If it's a bare topic, find 1–2 known-great seeds first (a respected practitioner or a deep repo), then proceed.
2. **Traverse the graph — highest yield.** From the seed, follow the **edges**: who it cites, links to, is built on, collaborates with, and *who cites it*. **Fringe excellence clusters** — the neighbours of a great fringe source are disproportionately great-fringe. This beats keyword search by a wide margin; do it first.
3. **Sweep the periphery** (source map below) — GitHub by **recently-updated, not stars**; niche blogs/newsletters; LinkedIn/X practitioner posts; Hacker News **"new"**; niche subs/Discords; conference abstracts; arXiv.
4. **Score + dedup.** Apply the rubric. Drop anything RavenClaude already has (check [`../../../../docs/idea-board.md`](../../../../docs/idea-board.md) + the installed plugins) and anything plainly mainstream.
5. **Emit + persist + route.** A **ranked shortlist** — each find: *what · why-great · why-invisible · source URL · RavenClaude-fit*. Then, in order:
   - **Persist the full run — don't let it die in the chat.** Write the complete report to **`docs/research/<YYYY-MM-DD>-scout-<slug>/report.md`** (`<slug>` = a short kebab of the seed; the *same committed research-persistence home* `rc-deep-research` uses, e.g. the DAX report — `docs/` commits straight to `main`, **no PR**). The report captures what the distilled idea-board row can't: the full ranked shortlist with per-find reasoning, the **dropped-and-why** and **ToS-flagged** items, the per-lane / per-source detail, the **load-bearing finding(s)**, and the Structured Output block. This is the durable, fuller record a later dedup or `rc-deep-research` pass actually reads — the idea-board points at it.
   - **Append the keepers to the committed curated index.** Add each keeper as a row to **`docs/idea-board.md`** (*find · what · why-fringe · RC-fit · status*), and have the run-section header **link to the report** from the bullet above. Two tiers, both committed: the idea-board is the *distilled, shared* index; the report is the *full* detail.
   - **Research before the gate.** Hand the top find(s) to **[`rc-deep-research`](../rc-deep-research/SKILL.md)** to deepen each keeper — fan-out across the source's wider footprint, fetch + adversarially verify the "why-great" claim (a fringe gem's depth must survive scrutiny, not just look deep), and surface the maturity / adoption / risk signal a one-pass scout can't. The research report **feeds `/forge`**: `/forge` decides whether (and how) to build, now grounded in a verified brief rather than a single-source impression (the same seed→plan path Buhler took, with the verification step added).

## Periphery source map (look here, not Google-top)

| Source | How to query for fringe |
|---|---|
| **GitHub** | `search_repositories` / `search_code` sorted by **updated**, filtered by topic; favour single-maintainer / "WIP" / low-star repos — the star-bias bypass |
| **Practitioner blogs** | the author's own site + their blogroll / links section |
| **LinkedIn / X** | the practitioner's posts + who they engage with |
| **Hacker News** | **"new"** + a niche keyword (never "top") |
| **Newsletters / Substack** | niche-specific, practitioner-authored |
| **Conference abstracts** | niche conferences' schedules (not the keynotes) |
| **arXiv / preprints** | recent + niche |
| **Reddit / Discord** | niche practitioner communities |

## Tools

- **WebSearch** with `allowed_domains` to target GitHub + niche sources; recency-tuned queries.
- **The GitHub MCP** (`search_repositories` / `search_code`) sorted by **updated** — the deterministic star-bias bypass (load it via tool-search first; it's deferred).
- **The [`rc-deep-research`](../rc-deep-research/SKILL.md) fan-out harness, RE-TUNED** — from *verify-a-claim-across-sources* to *discover-the-cluster-around-a-seed* (breadth over a niche, scored for great-but-obscure). Reuse its parallel-fetch shape; swap the verification grader for the rubric above.

## Anti-patterns

- **Ranking by stars / views / followers** — that's the popularity bias scout exists to defeat.
- **Surfacing the already-famous** — down-rank it; if it's on the front page it isn't fringe.
- **Inventing obscure-sounding names to look thorough** — every find **MUST** carry a real, fetched URL. An unverifiable "fringe gem" is a hallucination — the exact failure this skill must avoid (claim-grounding applies: cite the fetched source or drop the find).
- **Skipping the dedup** — re-surfacing what RavenClaude already has wastes a slot.
- **Stopping at keyword search** — if you didn't traverse the seed's graph, you skipped the highest-yield move.
- **Letting the run die in the chat transcript** — a scout whose detail was never written to `docs/research/<date>-scout-<slug>/report.md` (and whose keepers never reached `docs/idea-board.md`) can't be deduped against, handed to `rc-deep-research`, or audited later. The distilled idea-board row is *not* the full record. **Persist both before you route.**

## Composition

Scout is the **front door** of the idea pipeline; `rc-deep-research` is the **deepening pass**; FORGE is the **gate**: scout *finds* great-but-invisible ideas, `rc-deep-research` *verifies and enriches* the keepers, and `/forge` decides whether (and how) to build them. The flow is **`/scout <seed>` → ranked shortlist on the idea-board → [`rc-deep-research`](../rc-deep-research/SKILL.md) on the top find(s) → verified brief → `/forge <top find>` → routed plan.** Buhler is the worked example: spotted on LinkedIn → scout-traversed → researched → `/forge`'d into the pixel-perfect-reporting plan. Research sits **between** scout and forge so the build decision is made on a verified brief, never on a single fetched source — and so a fringe find whose depth *doesn't* survive scrutiny is dropped before it consumes a forge slot.

## Output Contract

**Three persisted artifacts, then the handoff:**

1. The **full run report** at `docs/research/<YYYY-MM-DD>-scout-<slug>/report.md` — the ranked shortlist with per-find reasoning, the dropped-and-why + ToS-flagged items, the per-lane/per-source detail, and the load-bearing finding(s). Committed to `main` (docs, no PR).
2. The **distilled keepers** appended as rows to `docs/idea-board.md` (*find · what · why-fringe · RC-fit · status*), the run-section header **linking to** artifact 1. Committed to `main`.
3. The top find(s) handed to [`rc-deep-research`](../rc-deep-research/SKILL.md), whose verified brief then routes to `/forge`.

End the handoff with the cross-plugin Structured Output JSON block per [`../structured-output/SKILL.md`](../structured-output/SKILL.md) (`{status, summary, deliverables, handoff_recommendation, confidence, next_actions}`) — list the **report path** and the idea-board update in `deliverables`, and set `handoff_recommendation.to_specialist` to `rc-deep-research` (the next stage), not `/forge`.

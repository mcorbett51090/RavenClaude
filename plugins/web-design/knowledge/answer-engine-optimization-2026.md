# Answer Engine Optimization (AEO / GEO) — 2026

**Last reviewed:** 2026-05-28 · **Confidence:** medium — the AI-search field is moving fast and much best practice is still emergent/vendor-claimed (flagged inline). Re-verify on the Researcher sweep. Sources: 2026 GEO/AEO guides + the existing technical-SEO skill.
**Owner:** `content-strategist` + `web-architect`. **Complements** (does not replace) the [`seo-technical-audit`](../skills/seo-technical-audit/SKILL.md) skill — that skill owns *classic* technical SEO (crawl/index/schema/sitemaps); this doc owns the *AI-answer* discoverability surface.

## What changed (why this is its own surface)
Classic SEO targets a **rank** on a results page. **AEO / GEO** (Answer Engine / Generative Engine Optimization) targets a **citation inside the AI-synthesized answer** — Google **AI Overviews / AI Mode**, ChatGPT, Perplexity, Gemini, Claude, Copilot. The user often never sees ten blue links; they read one synthesized answer and maybe click a cited source. So the goal shifts from "rank #1" to "**be the source the model quotes**."

> **House-opinion alignment:** this is the 2026 face of opinion #10 (SEO + a11y converge) — semantic structure, headings, and schema now also serve *machine extraction by LLMs*, not just crawlers.

## SEO is the foundation, GEO is the layer on top
Both matter. The strongest GEO performers have strong technical-SEO foundations (crawlable, indexable, fast, structured) — run the `seo-technical-audit` skill first. AEO/GEO then adds answer-extractability + entity authority on top. Don't trade one for the other.

## The tactics (highest-impact first)
1. **Answer-ready content structure.** Lead sections with a direct, self-contained answer (the "inverted pyramid"); short declarative paragraphs an LLM can lift verbatim; clear H2/H3 questions; tables for comparisons; **quantified claims** ("cuts X by 40%") and **dates** beat vague prose. Pages with clear entity definitions + answer-ready paragraphs + FAQ structure consistently out-cite keyword-stuffed pages.
2. **FAQPage / structured data (JSON-LD).** `FAQPage` Q&A pairs are machine-readable citation candidates and the highest-impact structured-data type for GEO. Layer `Article`, `HowTo`, `Product`, `Organization`, `Person` as relevant. (This overlaps the technical-SEO skill's schema work — coordinate.)
3. **Entity reinforcement / knowledge graph.** A single isolated schema block doesn't earn citations — a **connected entity graph** does: `Organization` → `founder`/`Person` → external corroboration (LinkedIn, Crunchbase, Wikipedia/Wikidata, authoritative press) → back to your domain (`sameAs`). AI engines follow the entity graph to decide who's authoritative. Consistent NAP/brand entities across the web reinforce it.
4. **E-E-A-T signals.** Author bios with credentials, citations to primary sources, original data/research, clear sourcing — the things that make a model trust (and quote) you.
5. **`llms.txt`** *(emerging, honestly hedged).* A proposed root file (`/llms.txt`) listing priority pages/markdown for AI crawlers. **Adoption is uneven and major engines don't uniformly honor it as of 2026** — treat it as low-cost, low-certainty hygiene, not a guaranteed lever. Don't oversell it to a client; pair it with `robots.txt` clarity about AI crawler access (a real decision: allow vs block GPTBot/ClaudeBot/PerplexityBot/Google-Extended).
6. **Freshness + crawlability for AI bots.** Ensure AI crawler user-agents aren't blocked if you *want* citations; keep content current (models favor fresh, dated material).

## Measurement (you can't manage what you don't track)
- **AI Share of Voice** — test 50-100 representative buyer/topic prompts across ChatGPT / Perplexity / Gemini / Claude / AI Overviews; count how often your brand is cited vs competitors; Share of Voice = your citations ÷ total category citations. Re-run on a cadence.
- **AI referral traffic** — segment analytics for referrals from `chatgpt.com` / `perplexity.ai` / `gemini` / `copilot`, and AI-Overview-attributed clicks where exposed.
- Tooling is young + churny (LLM-rank trackers); cite tool names with retrieval dates, don't hard-recommend.

## The honest caveat
Much GEO "best practice" in 2026 is **emergent and vendor-marketed**; the engines are opaque and change monthly. Lead clients with the **durable** moves (strong SEO foundation, answer-ready structure, real entity authority, E-E-A-T) — these help regardless of how any single engine weights things — and treat `llms.txt`/specific-tactic claims as experiments to measure, not guarantees. (House opinion: cite volatile claims with a retrieval date.)

## Sources (retrieved 2026-05-28)
2026 GEO/AEO guides (llmrefs.com, mersel.ai, stackmatix AEO-vs-SEO-vs-GEO, cubitrek); Schema.org `FAQPage`; the `llms.txt` proposal. Re-verify on the Researcher sweep — this field dates quickly.

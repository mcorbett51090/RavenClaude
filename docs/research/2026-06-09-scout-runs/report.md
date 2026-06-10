# Scout runs — full reports (2026-06-09)

> **Provenance:** four `/scout` runs on 2026-06-09, each a 4-lane parallel periphery sweep (general-purpose subagents with web access). This file is the **full detail** that the distilled `docs/idea-board.md` rows point back to — the ranked finds with per-find reasoning, the *dropped-and-why* + ToS-flagged items, and the load-bearing finding(s).
> **Evidence grade:** SCOUT-level — every find carries a **real URL the lane agent fetched this session**, but findings are **single-pass, not adversarially verified**. Star counts, MRR figures, and "traction" claims are as-reported and must survive an `rc-deep-research` pass before any weight is placed on them. This is the *front door* of the pipeline, not a verified brief.
> **Distilled keepers:** `docs/idea-board.md` §"Scouted fringe finds — 2026-06-09" (×4 run-sections). **Skill:** `plugins/ravenclaude-core/skills/scout/SKILL.md`.
> **Backfill note:** these four runs predate the v0.147.0 scout-persistence change (PR #386) that made writing this report a standard step; this file applies that convention retroactively so the detail isn't lost to the chat transcript.

---

## Cross-run synthesis

Four seeds of decreasing specificity, then a domain pivot:

1. **"make money with X using Claude"** → X-platform, Claude (model).
2. **"…using Claude Code"** → X-platform, Claude Code (two readings: X-tools-with-CC + make-money-with-CC).
3. **"make money with X"** → X-platform, any method (AI optional).
4. **"power platform"** → home turf, high RC-relevance.

**The three structural truths that repeated across runs 1–3 (X-money):**
- **The durable money is pick-and-shovel + data-substrate + pricing-arbitrage**, never "post threads / grow followers" (the 90–95% slop). Sell *to* the sellers; build on *owned* data not scraped; exploit the 2026 pricing structure.
- **Platform dependency is the killer.** Restagno's micro-SaaS, JohannesHoppe's bot, and DereWah's bot-farm all died on X's API/enforcement changes. Durable plays minimize dependence on X's graces (consent-data-commons, BYOK-on-the-buyer's-key).
- **The "I got rich shipping a SaaS with Claude Code" genre is pure slop** — agency lead-gen with zero disclosed revenue, guides-selling-guides, and posts that fabricate tool capabilities.

**Run 4 is the one that's RavenClaude-actionable** (runs 1–3 are personal-revenue scouts). Its load-bearing finding: **Microsoft is racing official agentic tooling into Power Platform** (official Dataverse MCP + skills, blogged 2026-06-08), so the durable fringe value is the un-subsumed territory (schema-write/ALM, Power Automate construction, gotcha-knowledge-skills) — and the *pattern* itself, since these solo MCP/skill builders are doing exactly what the `power-platform` plugin should.

---

## Run 1 — "make money with X using Claude" (X platform + Claude model)

Four lanes: GitHub · indie writeups · X/LinkedIn builders · communities/micro-SaaS.

### Keepers (ranked)
1. **Pulse — Septim Labs** · https://dev.to/septim_labs/i-read-the-x-twitter-algorithm-source-for-4-days-and-built-a-claude-code-sub-agent-that-scores-1ipb — *surfaced in 2 lanes.* A Claude Code sub-agent (single `.md`, no SaaS/key) that scores an X draft against the **leaked X-ranker weights** read from `twitter/the-algorithm` (reply-engaged-by-author **+75** vs like **+0.5**, negative-feedback **−74**). Sold $49→$79, $999 team. ToS-clean (local drafting aid). Low reach (DEV account days old). Mirrors RavenClaude's own "sell a verifiable Claude skill" pattern.
2. **OpenTweet — Branko Petric** · https://news.ycombinator.com/item?id=47165601 · https://opentweet.io/twitter-mcp-server — *2 lanes.* Compliant MCP server (`@opentweet/mcp-server`) — Claude schedules tweets/threads/analytics via the official X API. **84 disclosed paying users**, $11.99/mo. Novel wedge: drafts from real activity (RSS, GitHub commits, **Stripe revenue milestones**).
3. **The-Focus-AI/twitter-skill** · https://github.com/The-Focus-AI/twitter-skill (2★) — by-the-book auth: OAuth 2.0 PKCE, 1Password creds, multi-account isolation. Lowest-ToS-risk substrate for a legit ghostwriting/scheduling service.
4. **JohannesHoppe/x-autonomous-mcp** · https://github.com/JohannesHoppe/x-autonomous-mcp (2★) — *valuable as evidence.* Safety-railed autonomous MCP (server-enforced daily budget caps, dedup, protected-accounts) **+ a candid field report**: X's Feb-2026 "Operation Kill the Bots" 403s programmatic replies/quote-tweets, calling the paid API "a honeypot." Author flags his own tool non-operational.
5. **LinkedDraft — Naveen (@proto8875)** · https://medium.com/@proto8875/i-built-a-mcp-ai-linkedin-ghostwriter-in-one-weekend-heres-what-happened-a2a6f8796af7 · https://linkeddraft.xyz — MCP ghostwriter w/ "Tone Profile" voice-capture; live, weekend-built. Medium bio **"0 followers."** (LinkedIn, adjacent.)

### Dropped / flagged
- 🔴 **nirholas/XActions** (308★) — 140-tool X MCP + an **x402 pay-per-call agent-economy** hook (agents micropay your endpoint ~$0.001/scrape). Novel monetization, but **ToS-violating DOM automation** (auto-follow/like/comment, scraping); README says "educational/research only." Mechanism-of-interest, not a gem.
- `rohunvora/x-research-skill` (1.1k★) — too famous; read-only research, "never posts."
- Slop genre (down-ranked): "$2K–$15K/mo with Claude" listicles (aibusiness.vc, Medium "getting rich" pieces), the aioperator2026 "10–20x margin" post selling a 35-page guide with zero revenue figures.
- *Fortune* on Claude-MCP ghostwriting — real but mainstream (fails the obscure bar); not opened.
- Coverage gaps: Substack practitioner leads (growthwithalex, sabahudinmurtic, doneyli) returned HTTP 403 — not counted.

### Load-bearing finding
2 independent sources converge: X's API clampdown is foreclosing the auto-poster thesis; the durable money is **selling the packaged tool to other creators** (Pulse, OpenTweet, LinkedDraft), not running an auto-poster.

---

## Run 2 — "…using Claude Code" (two readings)

Deduped against Run 1's six. Reading A = X-tools-built-with-CC; Reading B = make-money-with-CC.

### Reading A keepers
1. **Lugo — self-editing Twitter newsroom** · https://medium.com/@eduardojld/subagent-orchestration-with-claude-code-self-editing-twitter-newsroom-bfdf6519362d — *strongest new find.* 5-subagent CC pipeline (Manager→Writer→Fact-Checker→Editor→Copy-Editor) iterating thread quality to a bar with **no human handoff**; templates in a gist. The production-pipeline counterpart to Pulse. Author **42 Medium followers**.
2. **STGime/posta-skill** · https://github.com/STGime/posta-skill (0★) — CC skill scheduling X posts (9 platforms) by fronting the paid Posta SaaS. The "CC skill as front-end to a monetized SaaS" shape.
3. **armatrix/twitter-mcp** · https://github.com/armatrix/twitter-mcp (1★) — *re-find* (surfaced in Run 1's GitHub lane, never boarded). Hybrid cheap-reads (twitterapi.io) / official-API writes, cookie fallback. 🟡 cookie-auth ToS-gray flag.

### Reading B keepers
1. **Capafy** · https://capafy.ai/ · https://www.testingcatalog.com/capafy-launches-new-ai-skills-marketplace-for-creators/ — *most novel mechanism.* Closed-source, **pay-per-execution** skill marketplace: skills run server-side (CC/Codex), buyers get output not files, creator paid per run. Directly solves "markdown skills copy for free." Launched ~May 2026; traction unproven. (Founder appears to be Md Santo per an X post.)
2. **Abhishek Ray — Claude Code Camp** · https://workshop.claudecodecamp.com/ · https://github.com/abhishekray07/claude-md-templates — $249 30-seat cohort on CC internals (token econ, caching, hooks) + free OSS (`claude-md-templates`, `claude-meter`) + newsletter. **OSS-credibility-moat → sell the cohort.** Solo ex-Robinhood eng; students from Disney/Asana/Databricks. The closest model to RC's "proof-of-craft → consulting."
3. **manja316 — skill-selling teardown** · https://dev.to/manja316/how-to-build-a-claude-code-skill-that-actually-sells-on-gumroad-4kdm — candid economics of selling CC SKILL.md on Gumroad ($7–15). The insight: **"the prompt is ~20% of the value; the bundled reference material is the other 80%."** Self-reports ~$200/mo, "not life-changing."

### Dropped / flagged
- Adrian Wedd / `lemonsqueezy-claude-skills` (~7★) — best *depth* example (6 real merchant-ops skills) but **MIT/free** (book lead-magnet), so not a paid artifact; down-ranked.
- Mark Kashef Gumroad "Claude Agent Teams Guide + Skill" — listing bundles a skill but Gumroad page didn't render; unverified lead.
- Reading-B SaaS-revenue lane = **pure slop.** Boldare (https://www.boldare.com/blog/claude-code-production-case-study/) + FutureProofing (https://www.futureproofing.dev/blog/claude-code-production-rag-case-study/) = real velocity metrics, **zero disclosed revenue**, agency lead-gen. Several first-person Medium posts **fabricated CC capabilities** (e.g. a terminal-invoked `/frontend-design skill` that doesn't exist). Ryan Doser's "$5K/50 days" $99 bundle is real but he has 33K+ YouTube subs (fails the small-do-er bar). Verdict from that lane: **route none to /forge.**

### Load-bearing finding
The real money-with-CC clusters on (a) teaching/cohorts behind an OSS moat (Ray) and (b) distribution infra that defeats copyable markdown (Capafy metering; manja316 reference-material-as-moat). **This is marketplace-relevant to RC:** "how do you monetize a Claude Code artifact when the markdown copies for free?" is RavenClaude's own latent question.

---

## Run 3 — "make money with X" (any method, AI optional)

Most slop-saturated seed; real fringe depth lives *beneath* the guru layer. 4 lanes (tools/data · indie writeups · creator-economy · communities).

### Keepers (combined, clean / ToS-OK)
1. **Community Archive + semantweet-search** · https://github.com/TheExGenesis/community-archive (120★) · https://github.com/sankalp1999/semantweet-search (58★) — *top find; only one with RC tooling relevance.* A **consent-based, user-owned X-data commons**: on-device archive → RLS Postgres (~1M+ tweets), "build commercial apps on it." Sidesteps X's $100→$5k→$42k API wall by building on *owned* data. `semantweet-search` is the worked app (hybrid BM25 + vector via LanceDB, switchable paid/free embeddings). Lowest ToS risk.
2. **Scrape Creators — Adrian Horning** · https://www.indiehackers.com/post/growing-a-scraping-api-to-10k-mrr-in-12-months-6iF8SJRF4WpciDff9aYi (corroborated: wearefounders.uk interview + his own blog) — solo **$10K MRR** social-data API. The X-native gem is a **closed loop**: X is both the data the product sells *and* the manual-DM acquisition channel (scrape-own-followers → DM → 10k free credits).
3. **BYOK + xAI-credit arbitrage — Ayush Chaturvedi** · https://superframeworks.com/articles/x-api-pay-per-use-pricing-indie-hackers — *most novel current mechanism, clean ToS.* Post-Jan-2026 pay-per-use: sell **BYOK** one-time tools (buyer connects own X key → maker carries zero API cost), then recycle the **20% xAI compute-credit rebate** to subsidize the tool's AI features. **[verify-at-use — the 20% rebate claim is single-source and load-bearing.]**
4. **Inboxs/Hivoe — Luca Restagno** · https://www.indiehackers.com/post/i-sold-2-micro-saas-built-on-the-side-of-9-5-job-4k-mrr-in-12-months-61a3abd5c9 — pick-and-shovel: a better DM client for the money-Twitter crowd who DM-sell. ~$3k/2mo. Honest postmortem: X's API price hike killed both products.
5. **NontechAna — $898/24h from 1,000 followers** · https://www.indiehackers.com/post/how-i-made-1k-in-24-hours-by-launching-an-info-product-on-twitter-with-a-reasonably-small-audience-of-1000-followers-d8075cbf52 — most replicable for a non-dev: $19 Notion playbook + 6 founder endorsements → tag-the-featured-founder threads + retweet discount codes → 41 sales/24h.

### Mechanism-gold but person-famous (down-ranked)
- **Tony Dinh / BlackMagic.so** · https://www.indiehackers.com/post/i-turned-my-twitter-banner-into-a-saas-gained-9k-followers-5k-users-and-300-mrr-in-4-months-ama-b540c8ac32 — *your profile chrome IS the ad* (live dynamic banner → viral → SaaS). Captured early but Dinh later sold for $128K. Takeaway, not a fringe person.

### Dropped / 🔴 flagged ToS-violations
- 🔴 **DereWah** · https://derewah.dev/projects/twitter-automation — multi-account **greentext bot farm** milking Creator Payouts (€200–300/account, "5M views/28d"), scraping Reddit/IG, auto-posting; accounts getting banned one by one. Hard ToS-violation; cautionary, not recommendable.
- 🔴 `Veeeetzzzz/twitter-impression-bot` (impression inflation), Sorsa-style scraped-data resale (https://api.sorsa.io/blog/why-is-twitter-api-so-expensive — funded multi-company, fails obscure bar + ToS-risky), the auto-DM-everyone-who-engages pattern.
- Harsh Strongman / Life Math Money (https://lifemathmoney.com/...) — real X ad-rev-share receipts ($5/1000 *verified* followers; $131 + $78 over ~70 days) but course-funnel-adjacent + commoditized insight.
- Coverage gaps: Reddit hard-blocked (HTTP 400) across lanes; x.com/linkedin profile pages mostly 403'd. Cam Martinez (bulk SaaS-license resale) / The DuLab (funnel-commission) surfaced *observed-about*, not first-person — need direct verification.

### Load-bearing finding
Durable fringe money on X = pick-and-shovel + data-substrate + pricing-arbitrage; platform dependency is the killer. RC relevance low except the Community-Archive cluster (consent-data-commons + hybrid-vector-search, adjacent to the `data-platform` plugin).

---

## Run 4 — "power platform" (home turf, high RC-relevance)

Scoped to the app/automation/Dataverse/Copilot-Studio + agentic side (prior Buhler run mined Power BI/Fabric; deduped vs it). 4 lanes incl. a dedicated **graph-traversal** lane. Down-ranked famous (XrmToolBox, FakeXrmEasy 1.4M dl, big MVPs, MS-official).

### Cluster 1 — agentic Dataverse / Power-Platform-MCP frontier (most RC-relevant)
1. **neronotte / Greg.Xrm.Mcp + PACX** · https://github.com/neronotte/Greg.Xrm.Mcp (19★) · https://github.com/neronotte/Greg.Xrm.Command (143★) — *top find, converged in 2 lanes.* C# Dataverse MCP framework — AI-driven FormXML/LayoutXML/FetchXML/SiteMap manipulation w/ metadata + a baked-in non-determinism/backup caveat. PACX = pac-CLI extension *platform* (XrmToolBox model, NuGet-shipped commands). Found via: seed → neronotte in a Dataverse-Git-ALM post → his GitHub; PACX README credits Daryl LaBar's XrmToolCast ep.
2. **mwhesse/dataverse-mcp** · https://github.com/mwhesse/dataverse-mcp (18★) — **schema-WRITE + solution-aware MCP**: creates tables/columns (11+ types)/relationships/option-sets/security-roles bound to an active solution+publisher; Mermaid ER from live schema. Owns territory MS's *read*-oriented official MCP doesn't. 70 commits, npm, documented test campaign.
3. **rcb0727/powerautomate-mcp-docs** · https://github.com/rcb0727/powerautomate-mcp-docs (52★) — **109-tool Power Automate lifecycle MCP** (flow-from-NL, test/debug, DLP, 400+ connector intel); name hides it's a real server. Power Automate is the thinnest-covered surface by official tooling. (Adjacent commercial: Flow Studio MCP.)
4. **zyborc/power-apps-code-apps-skill (A. Siedler)** · https://github.com/zyborc/power-apps-code-apps-skill (**0★**) — *converged 2 lanes; most RC-pattern-shaped.* A Claude/agent **SKILL** teaching the gotchas of the new Power Apps **Code Apps** framework (SharePoint choice fields, People-Picker UPN, Copilot Studio header bug). Literally the knowledge-bank-as-skill pattern RC uses.

### Cluster 2 — pro-dev plugin-craft depth (reference patterns)
- **Grant-Archibald-MS/dataverse-opentelemetry** · https://github.com/Grant-Archibald-MS/dataverse-opentelemetry (3★) — W3C `traceparent` distributed tracing across PP → App Insights. Novel (cross-component correlation is a known blind spot); **but semi-official author** (MS Power CAT lineage).
- **phuocle/Dataverse-Dialog-Builder** · https://github.com/phuocle/Dataverse-Dialog-Builder (21★) — reverse-engineered *undocumented* `Xrm.Navigation.openDialog`/`formContext.ui.moveTo` from 326 first-party dialog files. Practitioner archaeology.
- **Data8/DataverseClient** · https://github.com/Data8/DataverseClient (37★) — WS-Trust on-prem Dataverse client for .NET Core (deep auth internals, NSspi fork workaround).
- **Dominik-Wesolowski/CrmBasePluginFramework** · https://github.com/Dominik-Wesolowski/CrmBasePluginFramework (0★) — base plugin framework; env-var-driven prod tracing without redeploy.
- **khoait/DCE.PCF** · https://github.com/khoait/DCE.PCF (69★) — production PCF controls (PolyLookup, Lookdown, TimePicker); most mature, actively shipped (v1.1.2, Mar 2026).
- **daryllabar / DLaB.Xrm + XrmUnitTest** · https://github.com/daryllabar/DLaB.Xrm — a citation-hub node (cited in PACX's README).

### Cluster 3 — practitioner knowledge sources
- **Franco Musso** · https://francomusso.com/ — Power Pages / Liquid deep craft (FetchXML in Liquid, per-partner branding, anonymous-user previewing).
- **Ellis Karim** · https://elliskarim.com/2026/02/08/power-automate-json-bizarre-looking-query-expressions-that-actually-work/ — 45 empirically-tested PA JSON query-expression forms. (Caveat: used ChatGPT to *generate* permutations, then tested.)
- **Alexander Siedler — Copilot Studio dynamic adaptive cards** · https://zyborc.github.io/blog/2026-03-copilot-studio-dynamic-adaptive-cards/ — schema-bypass via `System.Activity.Value`.

### Dropped / down-ranked
- Famous, deliberately excluded: XrmToolBox, FakeXrmEasy (1.4M dl), scottdurow/dataverse-gen, DynamicsWebApi, Jonas Rapp (Plugin Trace Viewer), Grant Archibald/Power CAT, Tom Riha, Low Code Lewis, Matthew Devaney, Power-Maverick.
- 🟢 **Subsumed by Microsoft (intentionally dropped):** official Dataverse MCP server (read/query, "tool-shape" reshuffle **blogged 2026-06-08**), `microsoft/Dataverse-skills`, `microsoft/power-platform-skills`, the Dataverse plugin on the Claude marketplace, Power Pages Claude plugin (GA).
- AetherFlowDev/PluginFramework (1★) — real but ~18 months quiet (stale-flagged). MattCollins-Jones/PowerAutomateArtemisFramework (34★, 5 commits) — a wiki/standards framework, not code.
- Reddit/X were snippet-only (not directly fetched) — community-practitioner cluster under-sampled.

### Load-bearing finding
**Microsoft is racing official agentic tooling into Power Platform** (2026-06-08 blog). Durable fringe value = un-subsumed territory (schema-write/ALM, Power Automate construction, gotcha-knowledge-skills) **+ the pattern itself** — these solo builders are doing what the `power-platform` plugin should. **Subsumption is the gate** — verify each find still owns un-subsumed ground before investing (MS iterates weekly). Unlike runs 1–3, this is a "study these, fold patterns into the plugin's agentic direction + the parked Dataverse-token work" set.

---

## Recommended next step

Per the `scout → rc-deep-research → /forge` pipeline, deepen **Run 4 Cluster 1** (neronotte/Greg.Xrm.Mcp + mwhesse/dataverse-mcp + zyborc/power-apps-code-apps-skill) — the deepening doubles as competitive intel for the `power-platform` plugin's agentic roadmap, and the central question is the **MS-subsumption gate** (what un-subsumed territory each still owns). Strongly preferred over deepening the runs 1–3 X-money finds. The ToS-violating finds (XActions, DereWah, impression bots) are explicitly excluded from any deepening.

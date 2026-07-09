# STRATEGY.md — RavenClaude direction

> **Last reviewed:** 2026-06-02. Decision memo, not a pitch. Written for the next session that opens this repo and asks "what's the plan?" Re-read when (a) the public/private boundary feels wrong, (b) a real consulting engagement asks "can we have this?", (c) a domain plugin matures past its first engagement and the boundary calls itself into question, or (d) the SaaS direction stops feeling like a long bet and starts feeling like a real one.

## TL;DR

**Public core, private domain plugins.** `ravenclaude-core` stays open — it's the proof-of-craft and the dogfooding loop. Domain plugins (`power-platform`, `finance`, `regulatory-compliance`, `edtech-partner-success`, `web-design`, `data-platform`, `applied-statistics`, `microsoft-fabric`, `claude-app-engineering`, `azure-cloud`, `salesforce`, `microsoft-365-copilot`, `project-management`) stay private — they're the engagement IP.

The marketplace is a **consulting front-door**, not a catalog browser. The public layer says "this is how I build agentic systems for Microsoft-stack clients." The private layer is the playbooks I bring to the engagement.

## The choice that's already been made

Re-litigating this is the trap. The current state already says public-core/private-domain — what's actually changed:

- `ravenclaude-core` ships on a public marketplace `marketplace.json` entry; agents, skills, hooks, the dashboard, the tribunal, the Capability Grounding Protocol — all visible to anyone who can read this repo.
- The domain plugins all live in `plugins/<name>/` under the same repo. Today the **repo itself is private** (see [`AGENTS.md`](../AGENTS.md) § PR conventions: "the marketplace is private by default"). That's the seam.
- Everything is currently *available* in the same repo, but the public/private split is a directory-and-visibility decision, not an architectural one. The boundary is the bag of files, not the code.

**What "public core, private domain plugins" means concretely going forward:**

1. The public artifact is `plugins/ravenclaude-core/` + the marketplace catalog as a thin shell.
2. The private artifact is everything else (the 12 domain plugins) — engagement IP.
3. When something earns its way out of a domain plugin into the core (because it's domain-neutral craft), it moves. The reverse is rare — core stuff that gets too domain-specific gets factored *into* a domain plugin.

## Why this framing wins

### 1. Proof-of-craft without giving away the playbooks

A prospective consulting client doesn't get to evaluate me by reading my Power Platform decision trees, my Dataverse-token-acquisition workaround, or my PBIR Enhanced infinite-spinner debug runbook. Those are the *deliverable*. They evaluate me by reading the framework that makes that work possible — the tribunal, the comfort-posture system, the Structured Output Protocol, the Capability Grounding rules. That's the public layer.

The framework is hard. Anyone can copy a decision tree. Almost no one builds a working multi-agent guardrail system, an audited CI gate harness, a posture engine, and a Norse-themed event substrate that ends up shipping in a real engagement. The framework is the proof.

### 2. The Microsoft-stack consulting angle

The domain plugins are heavily weighted to Microsoft: Power Platform, Microsoft Fabric, Azure Cloud, Microsoft 365 Copilot, Dataverse, Power BI, Salesforce (the explicit other). That's not an accident — it's the engagement market: $25–50k per engagement, 4–6/year solo, mid-market companies that have committed to Microsoft and need someone who can ship under that stack with AI augmentation.

The framework happens to be Microsoft-flavored for that reason. The *content* in the public layer (`ravenclaude-core`) is not Microsoft-specific — agents like `architect`, `code-reviewer`, `security-reviewer`, `data-engineer`, `project-manager`, `partner-success-manager` are domain-neutral. The Microsoft specialization lives one layer down, in the *private* plugins, where it earns its keep on engagements.

If I were optimizing for the open-source community, the framework would be more vendor-neutral and the showcase plugin would be something general. I'm not — I'm optimizing for the consulting funnel.

### 3. SaaS as a long bet, not the current bet

The SaaS direction is real but it isn't the present concern. The consulting income comes first; the SaaS extracts the most-reused private-domain pattern *after* it's been proven on 3+ engagements. The strategy isn't "build the SaaS, then sell it" — it's "do the engagements, watch which playbook gets reused, and only then productize."

Which is why STRATEGY.md doesn't lead with packaging or pricing — the next 12 months of decisions are engagement-shaped, not product-shaped.

## What's open, what's gated

| Layer | Examples | Visibility | Why |
|---|---|---|---|
| **The marketplace shell** | `.claude-plugin/marketplace.json`, `AGENTS.md`, root `CLAUDE.md`, `repo-guide.html`, the dashboard | Public when the marketplace publishes | The boundary is on the wrapper, not the contents — anyone evaluating consulting work needs to see the shape |
| **`ravenclaude-core`** | 14 specialist agents, 25+ skills, the tribunal, the comfort-posture engine, the event substrate, the dashboard generator, the hooks, the templates, the knowledge directory | Public | Proof-of-craft. The framework that makes the domain work *good*. |
| **Domain plugins** | `power-platform`, `finance`, `regulatory-compliance`, `edtech-partner-success`, `web-design`, `data-platform`, `applied-statistics`, `microsoft-fabric`, `claude-app-engineering`, `azure-cloud`, `salesforce`, `microsoft-365-copilot`, `project-management` | Private — engagement IP | The playbooks. Brought to the engagement, not given away. |
| **The website** (separate repo) | `ravenpower.net` — marketing site, partner constellation aesthetic, consulting front-door | Public | The pitch surface that points at the public layer above |
| **Engagement-specific artifacts** | Client RAID logs, client RLS policies, client semantic models, deployment evidence | Engagement-private (in client repos) | Not RavenClaude IP — client IP |

The visible boundary at any future point is: **"can a stranger reading this evaluate whether I can do this work?"** Yes → public. **"Is this the work itself?"** Yes → private.

## How we'd actually do this — packaging options

When the time comes to *physically* split (today: not yet; the private-by-default repo is the current packaging), there are three credible shapes. Listed in order of how much work they need, not how much they're worth — the cheapest one is the right one *until something specifically demands more*:

### Option A — Two repos, one marketplace (recommended when we split)

- `RavenClaude` (this repo) stays the source of truth for the domain plugins; private.
- `RavenClaude-core` becomes the public mirror — a generated repo containing the marketplace shell + `plugins/ravenclaude-core/` only. CI pushes the public mirror on every release of core.
- The marketplace.json in the public mirror points at `ravenclaude-core` only.
- Consumers do `/plugin marketplace add github:mcorbett51090/RavenClaude-core` and get just core. Engagement clients get pointed at the private repo for the relevant domain plugin via a one-shot grant.

**Why this:** preserves the public/private separation cleanly while keeping authoring in one place. The mirror is generated, never hand-maintained.

### Option B — One repo, branch-based visibility

- One repo, `main` is private. A `public` branch contains only `plugins/ravenclaude-core/` + the shell.
- A CI workflow on `main` mirrors core changes to the `public` branch (subtree-style).
- The "marketplace" is the `public` branch URL.

**Why this:** lighter on ceremony (no second repo, no GitHub-Actions cross-repo push). Harder to explain to anyone reading the URL ("just look at the `public` branch") and gives up GitHub's discoverability features.

### Option C — Three repos: framework, domain plugins, engagement vault

- Framework (open).
- Domain plugins (private, one-or-many sub-repos by domain cluster).
- Engagement vault (per-client repos).

**Why not this yet:** premature. Domain plugins haven't accreted enough that splitting them further pays off. Reach for this when the `power-platform` plugin is being maintained on a different cadence than `finance`/`salesforce`, which is not now.

**The default position until a real trigger appears: stay one repo, private by default.** The boundary is implicit in the repo's private setting; the public artifact ships only when an engagement asks for it. Move to Option A on the first event that needs a real public marketplace URL — a marketing-site link, a conference talk, a public conversation that points at "the framework I built."

## What this strategy *doesn't* say

These are deliberately left for later:

- **Pricing the SaaS.** Long bet. Not the next 12 months.
- **Open-source contribution model for the core.** The core is open for *reading and copying*, not for community PRs — at least not until there's bandwidth to triage them. The README doesn't beg for contributors; that's intentional.
- **Trademark / brand strategy.** RavenClaude as a name is fine for now; if a real SaaS direction emerges, that's the renaming-and-trademark moment, not now.
- **A "community edition" vs "pro edition" split.** That's a product split, and there's no product. Don't pre-shape the codebase for a packaging decision that hasn't been forced.
- **Microsoft-partner / certification angles.** Useful eventually for credibility — book a Microsoft partner status review *after* the third engagement, not before.

## Open questions (the things to watch)

These are the signals that should make the next session re-read this file:

1. **Does a real engagement want the framework but not me?** That is, a prospective client says "we already have a vendor; we just want to use the RavenClaude tribunal under MIT." That's the SaaS-direction signal — the framework is generating standalone value. Until it happens, the SaaS is still a long bet.
2. **Does a domain plugin's knowledge base accrete to the point where it's a deliverable on its own?** `power-platform/knowledge/` is the closest — production decision trees, sempy.fabric reference, PBIR Enhanced build + debug. If a client says "license me just this knowledge base for $X/year," that's the moment the boundary moves.
3. **Does someone *fork* the public core and ship a competing private add-on layer?** That's the validation moment — the framework is good enough that the pattern itself is reusable. Either embrace it (collaborate, dual-license, accept a sub-marketplace) or accept the optimization-for-funnel position and not chase it.
4. **Does a single engagement *consume* enough of the private plugins that it costs more to manage the boundary than to drop it?** If a client engagement needs `power-platform` + `microsoft-fabric` + `azure-cloud` + `data-platform` + `applied-statistics` and they're paying enterprise-level, the right move may be to fold all five into a single client-specific bundle, drop the marketplace seam for them, and move on. The marketplace shell is overhead until the next engagement.

## Tactical near-term

The next 90 days don't change the strategy; they execute it. In rough order:

1. **Keep dogfooding `ravenclaude-core` on real engagements** — the Contoso customer DEV run is the canonical loop. Every lesson learned ships back as a `knowledge/` entry on the right plugin.
2. **Ship a recognizable demo of the framework on the marketing site** (`ravenpower.net`) — the dashboard, the tribunal panel, the constellation aesthetic. The site is the front-door; right now it's an empty room.
3. **Resist adding more domain plugins on speculation.** Twelve is already plenty. The next plugin earns its way in on a real engagement signal, not on "this would be cool to have."
4. **Continue the v0.101.0 followup discipline** — small, focused PRs that close real gaps. The discipline of the marketplace's CI gates + audit-gates meta-test is exactly the *kind* of work the public layer should keep showing off.
5. **When a real engagement asks for the public marketplace URL, ship Option A** (two repos, public mirror). Until then, stay one repo, private.

## Cross-references

- [`AGENTS.md`](../AGENTS.md) — cross-tool agent conventions; PR + privacy + house rules.
- [`CLAUDE.md`](../CLAUDE.md) — Claude-Code-specific addendum.
- [`plugins/ravenclaude-core/CLAUDE.md`](../plugins/ravenclaude-core/CLAUDE.md) — the team constitution. The framework's load-bearing prose.
- [`docs/architecture.md`](architecture.md) — current technical architecture of the marketplace.
- User memory: `project_business_direction.md` — the $25–50k consulting-first framing that this STRATEGY makes explicit.

## Decay triggers (when to re-read)

- A real consulting engagement asks for the framework as a deliverable (not via me).
- A domain plugin grows past its first engagement and the boundary feels arbitrary.
- The marketing site goes live and starts producing inbound — the inbound mix decides whether SaaS or consulting is the dominant pull.
- A second person joins the work, in any capacity — the implicit "I know what's private" boundary breaks the moment a teammate has to ask.
- 12 months from "last reviewed" passes with no trigger event — the strategy is probably still right, but read it anyway and confirm.

# New-plugin research & buildout — 2026-07-09

> Scheduled-routine deliverable: research 10 net-new plugins for the RavenClaude
> marketplace, prioritize them, and build the highest-priority ones. This doc is
> the research + prioritization record; the buildout ships in the same PR.
>
> **Last reviewed:** 2026-07-09 · **Author:** automated routine (Claude Code on the web)

## Method

The marketplace already ships **144 plugins** spanning engineering disciplines,
industry verticals, and knowledge-work functions. Candidate selection therefore
optimized for **genuine, verified gaps** rather than restatements of covered
ground. Each candidate was checked against the full `marketplace.json` roster by
keyword (`seo`, `bioinformatic`, `funeral`, `self-storage`, `waste`, `museum`,
`grant`, `dsp`, `red-team`, `digital twin`, …) and, where a near-neighbor
existed, a boundary was drawn against it (e.g. technical SEO vs `web-design`'s one
SEO-audit skill; AI red-teaming vs `llm-evaluation-engineering` and
`trust-and-safety`; grants-management vs `nonprofit-fundraising`).

Feasibility note: every candidate is a **knowledge/advisory plugin** in the house
pattern (2 agents on a *decide* vs *build/run* seam + a decision-tree knowledge
bank + skills + templates). None requires a bundled MCP server or runtime, so all
ten are buildable to the marketplace's shipping bar within this routine.

## The 10 candidates

| # | Plugin | Category | Gap it fills | Nearest neighbor (boundary) |
|---|---|---|---|---|
| 1 | `ai-red-teaming` | AI/Eng | Adversarial testing of LLM/agent systems — OWASP LLM Top 10, prompt injection, jailbreaks, agent tool-abuse, automated red-team harnesses, remediation | `llm-evaluation-engineering` (quality regression), `trust-and-safety` (content policy), `security-engineering` (app/infra pentest) |
| 2 | `technical-seo-engineering` | Eng | Crawlability, indexation, JS rendering for crawlers, structured data, Core Web Vitals as a ranking factor, migrations, hreflang | `web-design` (full build; has one SEO-audit skill), `search-relevance-engineering` (internal search), `marketing-operations` (paid/campaigns) |
| 3 | `self-storage-operations` | Vertical | Revenue management (ECRIs, dynamic pricing, occupancy), delinquency/lien process, facility ops for storage operators | `commercial-real-estate` (leasing/investment), `property-management` (residential), `field-service-management` |
| 4 | `funeral-home-operations` | Vertical | FTC Funeral Rule/GPL, at-need vs pre-need arrangement, cremation authorization, vital records, case logistics | `behavioral-health-practice` (clinical grief), `accounting-bookkeeping`, `senior-care-operations` |
| 5 | `grants-management` | Function | Grantee-side lifecycle: funder fit, proposal assembly, 2 CFR 200 post-award compliance, indirect costs, subrecipient monitoring, reporting | `nonprofit-fundraising` (individual/major donors), `public-sector-govtech` (grantmaking policy) |
| 6 | `bioinformatics-engineering` | Eng/Science | Genomics pipelines (Nextflow/nf-core, Snakemake, WDL), GATK best practices, FASTQ/BAM/VCF, reproducibility, HPC/cloud scaling, validation | `ml-engineering` (generic MLOps), `clinical-trials` (trial ops), `data-platform` (warehouse) |
| 7 | `waste-recycling-operations` | Vertical | Collection route density, fleet, transfer/landfill/RCRA Subtitle D compliance, MRF & commodity economics, diversion/EPR laws | `esg-sustainability-reporting` (corporate reporting), `fleet-logistics` (generic telematics) |
| 8 | `audio-dsp-engineering` | Eng | Real-time-safe DSP, filters/FFT, plugin formats (JUCE/VST3/AU/CLAP), latency budgets, SIMD, spatial audio | `streaming-media-engineering` (delivery/codecs), `conversational-ai-voice-engineering` (voice agents), `embedded-iot-engineering` |
| 9 | `digital-twin-engineering` | Eng/IoT | Asset/process/system twins, fidelity level, physics vs data-driven models, telemetry sync, DTDL/Azure Digital Twins/ISO 23247, simulation | `embedded-iot-engineering` (device firmware), `data-platform` (BI), `robotics-autonomous-systems-engineering` (control) |
| 10 | `museum-cultural-institution-operations` | Vertical | Collections stewardship, exhibitions, membership/development, digital collections/IIIF, AAM accreditation | `nonprofit-fundraising` (donor strategy), `event-management`, `grants-management` (grant admin) |

## Prioritization rationale

Ranked by **user demand × technical feasibility** (all ten are feasible; the axis
that separates them is demand + strategic fit with the marketplace's vertical +
engineering strategy):

- **P0 — build first (highest demand, strong fit):**
  1. `ai-red-teaming` — the fastest-rising AI-safety/security discipline of 2026; the marketplace covers eval *quality* and platform *T&S* but not adversarial security of the model/agent itself. High reuse across every team shipping an AI feature.
  2. `technical-seo-engineering` — evergreen, broad demand; `web-design` only grazes it with a single audit skill.
  3. `self-storage-operations` — clean SMB-vertical gap matching the marketplace's vertical playbook; revenue management (ECRIs) is a well-documented, high-leverage domain.
  4. `funeral-home-operations` — clear vertical gap with a crisp regulatory spine (FTC Funeral Rule) that makes it defensible and useful.

- **P1 — build next (real demand, slightly narrower):**
  5. `grants-management` — broad reach across nonprofits, universities, and public agencies; distinct from donor fundraising.
  6. `bioinformatics-engineering` — high-value technical domain, strong public best-practice corpus (nf-core, GATK, GA4GH).
  7. `waste-recycling-operations` — solid vertical gap; route density + commodity economics are concrete and teachable.

- **P2 — build to complete the set (narrower but genuine):**
  8. `audio-dsp-engineering` — a real engineering gap; audience is narrower than SEO/red-teaming.
  9. `digital-twin-engineering` — emerging; overlaps adjacent IoT/manufacturing plugins at the edges, so boundaries matter.
  10. `museum-cultural-institution-operations` — niche vertical, but well-defined and unserved.

## Implementation approach (per plugin) & dependencies

Each plugin follows the shipping house pattern and requires
`ravenclaude-core@>=0.7.0` (no other runtime dependency):

- `.claude-plugin/plugin.json` (semver `0.1.0`), `CLAUDE.md` (team constitution),
  `README.md`.
- **2 agents** on a *decide/architect* vs *build-run/implement* seam, each with the
  gated scenario-authoring frontmatter schema and a ≤300-char routing description.
- **2 knowledge docs** — a Mermaid decision tree + a dated `*-patterns-2026`
  reference (confidence-marked; volatile facts carry retrieval dates).
- **3 skills** (`choose/design/implement`-shaped) and **2 templates**.
- Central registration: `marketplace.json` entry, `docs/architecture.md` Status
  row, README count.

The only cross-cutting risk is the strict frontmatter gate (agent scenario schema
+ ≤300-char descriptions + cross-plugin name uniqueness), validated by
`scripts/check-frontmatter.py` before commit.

## Progress

See the PR for the shipped buildout and the final gate results. Blockers, if any,
are recorded in the PR description.

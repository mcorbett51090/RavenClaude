# FORGE plan — PBIP report fast-solve system (power-platform)

> Synthesized from the FORGE run (scope + G1 grounding + two cross-model panels + gap-delta + the owner's MCP-ban constraint). Goal: the agent reaches the verified PBIP/PBIR **report** fix in 1–2 steps, not 6 — and it works **even where all MCPs are banned**.

## Context
The PBIP knowledge is deep but **scattered** across ~10 `knowledge/` files with no symptom→fix router, so the agent trial-and-errors (the card-color bug = 6 attempts). Fix = a triage router + a graceful-degradation authoritative-source chain + a consult-first agent prior.

## ⚠️ Load-bearing constraint: MCP-optional, never MCP-dependent
The owner's client org (BTCSIReporting) **bans all MCPs**. The Microsoft Learn MCP is therefore an **optional accelerator**, never the authoritative route. **Every official fact the router relies on must be either (a) captured in our reference, or (b) reachable by a cited direct URL (WebFetch) — never *only* via the MCP.** The system must work with MCPs banned AND degrade further if network egress is also restricted (our captured reference is the zero-dependency floor).

## Source precedence — graceful degradation (the heart of the design)
| Tier | Source | Needs | Role |
|---|---|---|---|
| 1 | **Our captured reference** (`pbir-enhanced-reference.md` + the pitfall docs) | nothing | **Floor — always works.** Holds the official-schema facts statically + the diagnosed production gotchas (prototypeQuery, resourcePackages, silent-zero) that aren't in official docs at all. |
| 2 | **Official Microsoft, non-MCP** — the **cited exact** Learn-article / schema-JSON URL via **WebFetch** | network | Canonical check for "what IS the current property/schema." Reference + router must cite the exact URLs (e.g. `learn.microsoft.com/...`, the `formattingObjectDefinitions/*/schema.json` raw URL) so the agent fetches them **without** the MCP. |
| 3 | **Official Microsoft via Learn MCP** (`microsoft_docs_search`/`_fetch`/`_code_sample_search`) | MCP allowed | Same authority as Tier 2, faster — **only if the org permits MCPs**. Explicitly labeled optional. |
| 4 | **data-goblin** `pbir-format/references` (cited URLs + captured facts) | network (or captured) | Deep-practitioner complement for real-world shapes not in official docs. **GPL — read for reference, re-express, never copy prose. Never the canonical source; official MS wins every conflict.** |

For **canonical-property questions** ("what's the object name / literal suffix?") Tier 2/3 (official schema) leads. For **diagnosed production gotchas** (spinner, silent-zero) Tier 1 leads — that knowledge is not in official docs. The prior splits these two question types explicitly (Panel B's correction).

## Deliverable 1 — the fast-triage router (new file)
`plugins/power-platform/knowledge/pbip-report-fast-triage.md` (a standalone debug *hub*, ~6 KB cap — NOT a section in the already-88KB build reference). Two tables, **zero duplicated fix content** (links only):
- **Symptom → cause → fix-location** keyed on what the agent *observes* (infinite-spinner / zero-vs-blank / missing-rows / wrong-or-missing-color / first-deploy-fail / filter-wrong-scope / deployment-var-ignored). Each cell = one-line cause + a **file-level link** + a `§N.N`-as-**plain-text** pointer (Panel B: file-level links so CI's existing `check-md-links.py`/Gate 29 catches dead links; §-as-text avoids drift-prone `#anchor` links → **no new gate needed**).
- **Formatting/theming property-location** sub-table covering the surface **broadly** via a **generalizing decision rule** (not just the 6 known bugs): *chrome (title/border/shadow/background) → `visualContainerObjects`; data content (axes/labels/colors/data-labels) → `objects`; a setting that silently no-ops → suspect the open-schema silent-discard or a wrong literal suffix → check `pbir-enhanced-reference §9.x`.* The rule is what catches **new** formatting bugs, not a finite bug list.

## Deliverable 2 — the dual authoritative-source fallback (wired into the router + reference)
- Add the **non-MCP official-MS routes**: cite the exact Learn-article + official-schema URLs in the router's fallback section so they're WebFetch-able without the MCP; note the Learn MCP as the optional faster path "*if your org permits MCPs*."
- Add the **data-goblin** pointer (the last-message ask): the `pbir-format/references` tree, cited URL, GPL-complement framing.

## Deliverable 3 — the consult-first prior (the load-bearing behavior change)
A **compact inline prior** in `power-bi-engineer.md`'s knowledge-bank body (NOT the ≤300-char `description`), inserted before the existing PBIR priors, with explicit trigger language: *"For ANY PBIP/PBIR **report** symptom, read `knowledge/pbip-report-fast-triage.md` FIRST — before editing any report file. Follow its source chain: our reference → official Microsoft (cite-and-WebFetch the schema/Learn URL; the Learn MCP only if your org permits MCPs) → data-goblin. Verify the fix against a Desktop-saved `.pbip` file. Never guess-and-check on report metadata."* (Panel B: the router file is inert unless the agent body points at it with FIRST-language — this prior is the piece that actually changes behavior.)

## Dependency DAG
```
captured-reference facts (exist) ─┐
official-MS URLs cited ───────────┼→ pbip-report-fast-triage.md (router) → power-bi-engineer prior → version bump + regen → DoD
formatting decision-rule ─────────┘            (file-level links only → existing md-links gate covers it)
```

## Alternatives considered
- **New standalone router file (chosen)** vs a top-of-reference section — the reference is 88 KB and is a *build* companion; a *debug* hub is a different job + must stay cheap to load.
- **File-level links + §-as-text (chosen)** vs `#anchor` links + a new anchor-checking gate — anchors drift silently and the new gate is over-build; file-level links are already CI-covered.
- **MCP-optional captured-first chain (chosen, owner-mandated)** vs MCP-first — MCP-first fails in MCP-banned orgs; rejected.

## DoD
- New `knowledge/pbip-report-fast-triage.md` + the `power-bi-engineer` prior + the data-goblin/official-MS pointers.
- Bump `power-platform` `plugin.json` + `marketplace.json` entry (lockstep; read CURRENT main version, bump minor — likely `0.37.0`/`0.38.0` after the night's merges; rev on collision). Regenerate dashboards + copilot package; knowledge-bank row in `CLAUDE.md`; scenario/frontmatter intact.
- **CI green:** `check-md-links.py` (every router link resolves — the mis-routing guard), `check-frontmatter.py`, `check-md-links`, prettier, json valid, `audit-gates.sh`.
- A PR for Matt's review (not auto-merge).

## Risks
- **Mis-routing** (router → wrong/dead target): mitigated by file-level links (CI-covered) + §-as-plain-text (no silent anchor drift).
- **MCP-ban** (the owner constraint): mitigated by Tiers 1–2 being load-bearing + MCP explicitly optional; the captured reference is the zero-dependency floor.
- **Network-also-banned**: Tier 1 (captured reference) still solves the common cases offline; the router says so.
- **GPL** (data-goblin): re-express facts, cite, never copy prose; official MS wins all conflicts.
- **Staleness:** the captured official-schema facts carry `[verify-at-use]` markers + the cited URL, so a reader can re-confirm against the live schema.

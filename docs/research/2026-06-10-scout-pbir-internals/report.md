# Scout Run: PBIR Enhanced Internals & Fabric-Specific Quirks
_Run date: 2026-06-10 · Skill: `ravenclaude-core:scout` · Slug: `pbir-internals`_

---

## Seed and Brief

Hunt for **great-but-low-visibility** practitioner blog posts, GitHub repos, and tool documentation that deeply document PBIP/PBIR Enhanced internals and Fabric-specific quirks at the implementation level. Target: visual.json properties, theme schema gotchas, the `objects` vs `visualContainerObjects` split, Fabric-vs-classic rendering differences, `getDefinition`/deployment quirks.

**Rank by:** depth × novelty × practitioner-grounding − popularity_penalty  
**DOWN-rank:** big-name vendor blogs, Microsoft official docs, conference keynotes  
**UP-rank:** under-the-radar do-ers who actually ship

**Practitioner graph seeds:** Kurt Buhler, Štěpán Rešl, Rui Romano, Marc Lelijveld, Sandeep Pawar, Kévin Dujarrié, Tabular Editor blog, Nikola Ilic (Data Mozart)

**Dedup baseline:** all finds must add something NOT already in `plugins/power-platform/knowledge/pbir-enhanced-reference.md`

---

## Method: The Core Problem

Mainstream search for PBIR internals returns only Microsoft official docs and high-SEO overview articles. Graph traversal from the practitioner seed list was **largely unproductive** for PBIR-specific deep content — Rešl, Romano, Lelijveld, Pawar, Ilic, and Dujarrié have not published PBIR internals blog posts at the required depth. Their public content is announcement/overview level at best.

**The pivot that worked: tool-traversal instead of blog-traversal.**

The actual deep knowledge lives in the **tools these practitioners build**, specifically:
1. `data-goblin/power-bi-agentic-development` SKILL.md files (Buhler's agent-facing documentation)
2. Tabular Editor blog (Kurt Buhler's employer, Nov 2025 posts)
3. `maxanatsko/pbir.tools` and `TemplateMechanics/pbi-pilot` (fringe repos surfaced from Buhler's X posts)
4. `sqlswimmer.com` (independent practitioner blog, 2024)

---

## Sources Traversed

### Graph traversal (practitioner seeds)
- Kurt Buhler: LinkedIn profile → `data-goblin/power-bi-agentic-development` (SKILL.md files), Tabular Editor blog, `maxanatsko/pbir.tools` X post reference, `TemplateMechanics/pbi-pilot` X post reference
- Štěpán Rešl: GitHub + blog search → no PBIR-internals-specific published content at required depth
- Rui Romano: GitHub + LinkedIn → active in PBIR space but public content is announcement/overview level
- Marc Lelijveld: blog + GitHub → no PBIR-internals-specific content found
- Sandeep Pawar: LinkedIn + Fabric notes → no PBIR implementation-level content found
- Kévin Dujarrié: search → no PBIR-specific content at required depth
- Tabular Editor blog: searched → found two Nov 2025 posts (Kurt Buhler author)
- Nikola Ilic (Data Mozart): blog → no PBIR-specific deep content

### Periphery sweep
- GitHub: `pbir visual.json objects visualContainerObjects`, `pbir queryState nativeQueryRef`, `pbir reportExtensions fabric`, sorted by `updated`, stars:1..50
- WebSearch: `pbir visualContainerObjects objects split practitioner`, `pbir nativeQueryRef active flag implementation`, `pbir queryState projection roles`, `pbir reportExtensions.json thin-report visual-calculations`, `pbir prototypeQuery Fabric breaking change`, `pbir fabric deployment getDefinition quirks`
- SQLSwimmer.com: deployment-specific PBIP practitioner blog

### Fetch attempts (failed)
- `https://lukasreese.com` PBIR posts: 403 Forbidden on both — excluded
- `https://lobehub.com/pbir-cli` skills page: 403 Forbidden — excluded
- Kurt Buhler's X tweet detail: 402 Payment Required — excluded

---

## Ranked Shortlist (5 verified finds)

### #1 · Tabular Editor Blog: "Hidden secrets in the Power BI report metadata" + "C# scripting PBIR" (Kurt Buhler, Nov 2025)

**URLs (both fetched):**
- https://tabulareditor.com/blog/hidden-secrets-in-the-power-bi-report-metadata
- https://tabulareditor.com/blog/c-scripting-pbir

**What:**

Post 1 — "Hidden secrets":
- **`strokeColor` Literal→Measure swap** — setting a formatting property's expression to a Measure binding (not a Literal) in the `objects` block enables per-segment gradient line coloring not available in the PBI UI. The post shows the JSON diff. Fragility warning: works for line charts; fails silently for other visual types — documented explicitly.
- **`dataViewWildcard` selector scoping triangle** — distinct from `matchingOption:1` (already in reference §14b). Three scoping modes: all-series (matchingOption:0), per-data-point (matchingOption:1), and per-series (third variant). The existing reference only covers the first two.

Post 2 — "C# scripting PBIR":
- **Desktop sync lag** — C# script changes don't take effect until Desktop close/reopen; no incremental sync.
- **Schema fragmentation admission** — Tabular Editor's PBIR support uses partial schema knowledge; some properties discovered by experimentation.
- **Git-only rollback** — no transactional undo for script changes; git revert is the only recovery.

**Why great:** Exposes a real UI-inaccessible mechanism with specific JSON path + honest fragility warnings. Author is Kurt Buhler (Data Goblins / Tabular Editor).

**Why invisible:** Tabular Editor blog, no Power BI SEO keywords in titles; Nov 2025 pre-GA PBIR.

**Dedup:** Reference §14b covers matchingOption:1 only. This adds: strokeColor Literal→Measure swap, per-series scoping variant, Desktop sync lag, git-only rollback.

**RC fit:** HIGH — adds to pbir-enhanced-reference.md §14/objects and pbir-enhanced-report-loading.md debug runbook.

**Recency:** Nov 2025

---

### #2 · `data-goblin/power-bi-agentic-development` PBIR-format SKILL.md (Buhler + co-authors, active 2026)

**URL (fetched):** https://github.com/data-goblin/power-bi-agentic-development (plugins/pbip/skills/pbir-format/SKILL.md)

**What:** Agent-facing documentation of PBIR internals from building a real production agent tool:
- **`mobile.json` per-visual phone layout** — stored co-located with each `visual.json`, NOT in a central mobileState artifact. Agents that only read `visual.json` miss mobile layout.
- **Column/measure binding type mismatch** → runtime "something is wrong with fields" error. Passes schema validation, fails at report open. The SKILL.md names this as a production discovery.
- **Reference lines dual-entry** — requires two entries in visual config (one for range binding with ID, one for styling with same ID). Single-entry fails silently.
- **Error bars dual-entry** — same pattern as reference lines.
- **`reportExtensions.json` lifecycle** — thin-report measures (DAX in report) + visual calculations (RUNNINGSUM, RANK, WINDOW) managed via this file; documents which operations require Desktop vs. file-only edit.
- **Theme cascade full order** — defaults → wildcards (`*`) → visualTypes → bespoke visual.json; bespoke overrides theme visualTypes which overrides wildcards.
- **Measure-driven CF via theme tokens** — `"good"`/`"bad"`/`"neutral"` tokens in CF config resolve to theme-defined colors; enables theme-level CF control across all visuals.

**Why great:** Multiple specific non-obvious mechanisms documented as discovered-from-real-reports, not from reading specs.

**Why invisible:** SKILL.md buried inside a marketplace plugin structure at a specific GitHub path; not indexed as a blog or findable by PBIR-internals web search.

**Dedup:** All items above are new to the existing reference.

**RC fit:** VERY HIGH — several items directly extend both knowledge files.

**Recency:** Active (weekly updates)

---

### #3 · `TemplateMechanics/pbi-pilot` (unknown author, active 2026)

**URL (fetched):** https://github.com/TemplateMechanics/pbi-pilot

**What:** AI-powered PBIR development harness documenting Desktop internals:
- **TOM local port discovery** — Power BI Desktop runs a local Analysis Services engine on a **random port**; the harness programmatically discovers it (via process list / named pipe). This port enables pushing semantic model changes via TOM without restarting Desktop.
- **Dual-path refresh** — report layout changes (PBIR file edits) require Desktop restart; semantic model changes (table/column/measure) can be pushed live via TOM to the discovered port.
- **Timing constraint** — "Do not run restart and open back-to-back" — rapid close+reopen causes duplicate Desktop instances. Deliberate wait/check between close and reopen is required. Documented as a production constraint.

**Why great:** Undocumented Desktop internal (TOM local port, random) + specific discovery method + timing gotcha for automated restart cycles.

**Why invisible:** 0 stars, no blog, no SEO; surfaced only via Buhler's X post reference.

**Dedup:** Not covered anywhere in the existing reference or runbook.

**RC fit:** MEDIUM-HIGH — extends pbir-enhanced-report-loading.md with Desktop live-refresh mechanism.

**Recency:** Active 2026

---

### #4 · `maxanatsko/pbir.tools` (Maxim Anatsko, co-author with Buhler, beta April 2026)

**URL (fetched):** https://github.com/maxanatsko/pbir.tools

**What:** CLI tool for PBIR manipulation, revealing internals through its design:
- **Hierarchical path syntax** `Report.Report/Page.Page/Visual.Visual` — the addressing model that maps PBIR's multi-file structure to agent-addressable paths.
- **`pbir validate` exposes "hidden fields that waste query resources"** — fields bound to roles in visual.json that contribute no visual output (e.g., dead projections from visual type switches). Named explicitly as a production concern: hidden fields add query cost without rendering.
- **Safety warnings around PBIR fragility** — backup required before any manipulation; malformed edit = report load failure with no in-app recovery.
- **Reference lines/error bars dual-entry** — corroborates Find #2.

**Why great:** "Hidden fields wasting query resources" is a real production concern not documented elsewhere.

**Why invisible:** Beta tool, minimal GitHub presence; surfaced only via Buhler's X post.

**Dedup:** Hidden-fields concept is new. Path abstraction is new.

**RC fit:** MEDIUM — adds hidden-fields validation concept and path abstraction.

**Recency:** Beta April 2026

---

### #5 · SQLSwimmer: "So You Want to Deploy Power BI Project Files (PBIPs)?" (2024)

**URL (fetched):** https://sqlswimmer.com/2024/07/01/so-you-want-to-deploy-power-bi-project-files-pbips/

**What:** Deployment internals from production PBIP work:
- **256-char Windows path limit** — custom visuals use long GUID-based subfolder names; PBIP at a deep project root path crashes on save with a cryptic file-not-found error (not "path too long"). Mitigation: keep project root shallow.
- **Build pipeline vs. release pipeline architecture** — build = assemble + validate payload; release = execute deploy. Mixing into one pipeline causes hard-to-rollback partial-deployment failures.
- **Semantic model must pre-exist before report deployment** — deploying report-first (or in parallel) causes "model not found" at report load. Model deploy must complete first.
- **`cache.abf` not in source control** — auto-generated; must be gitignored to prevent merge conflicts and repo bloat.
- **Cross-environment connection update** — after deploying to a new environment, the data source connection string must be updated via a post-deploy step; it's not automatic.

**Why great:** 256-char path limit is a production gotcha that crashes saves with a non-diagnostic error; build/release pipeline separation is the correct CI/CD architecture.

**Why invisible:** 2024 practitioner blog, pre-GA PBIR, no PBIR-specific SEO in title; the path-limit gotcha isn't in the PBIR format itself.

**Dedup:** All items above are new to the existing runbook.

**RC fit:** MEDIUM-HIGH — extends pbir-enhanced-report-loading.md deployment section.

**Recency:** July 2024 (Windows path limit unfixed; pipeline architecture still valid)

---

## Dropped Finds (with reasons)

| Source | Why dropped |
|---|---|
| lukasreese.com — PBIR schema version 404s, properties via experimentation | 403 Forbidden on both posts — unverifiable |
| Marc Lelijveld, Sandeep Pawar, Nikola Ilic, Kévin Dujarrié | No PBIR-internals-specific published content found at required depth |
| Rui Romano | Active in PBIR space; public content is announcement/overview level |
| Štěpán Rešl | No PBIR-specific deep content found |
| Microsoft official PBIR docs | Explicitly excluded per scout brief |
| nickyvv.com | Governance/operations, not technical internals |
| draftbi.com | Introductory, defers to MS docs |
| lobehub.com/pbir-cli skills page | 403 Forbidden |
| Kurt Buhler's X tweet detail | 402 Payment Required |
| data-goblin `visual-container-formatting.md` companion file | 404 — referenced in SKILL.md but file doesn't exist at the URL |

---

## Load-Bearing Finding

**Tabular Editor "Hidden secrets in the Power BI report metadata" (Nov 2025)**

This is the highest-value find because it exposes a genuinely undocumented mechanism — dynamic line chart CF via `strokeColor` Literal→Measure swap — that enables something the PBI UI won't let you do. Fetched and verified. Written by Kurt Buhler (Data Goblins / Tabular Editor), a practitioner with real shipped work. The mechanism is specifically about what you CAN do with PBIR that the UI blocks — exactly the depth × novelty × practitioner-grounding the scout was looking for.

The `data-goblin` SKILL.md (Find #2) is close behind — it covers more ground but the mechanisms are operational (prevent pain) rather than capability-unlocking (do something new). Both are RC-actionable.

---

## Method Notes

Key insight from this run: **practitioners who know PBIR deeply write their knowledge into tools, not blog posts.** Blog-traversal from the seed list returned almost nothing at the required depth. Tool-traversal (SKILL.md files, CLI tool documentation, AI harness READMEs) was the high-yield move. For future PBIR scout runs: start with GitHub search for recently-updated PBIR-adjacent tools rather than practitioner name + blog searches.

---

## Structured Output

```json
{
  "status": "complete",
  "summary": "5 verified PBIR internals finds ranked by depth × novelty × practitioner-grounding. Top find: Tabular Editor's strokeColor Literal→Measure swap (UI-inaccessible dynamic line coloring). Key method insight: tool-traversal (SKILL.md/CLI docs) outperforms blog-traversal for PBIR depth.",
  "deliverables": [
    "docs/research/2026-06-10-scout-pbir-internals/report.md",
    "docs/idea-board.md (PBIR section appended)"
  ],
  "handoff_recommendation": {
    "to_specialist": "rc-deep-research",
    "seed": "https://tabulareditor.com/blog/hidden-secrets-in-the-power-bi-report-metadata",
    "verification_questions": [
      "Does strokeColor Literal→Measure swap work in current Fabric PBIR Enhanced (post-June 2026 schema)?",
      "Is dataViewWildcard per-segment vs per-series scoping accurately documented?",
      "Was the Desktop sync lag fixed in a subsequent TE/PBI Desktop version?"
    ]
  },
  "confidence": 0.82,
  "next_actions": [
    "Append finds to pbir-enhanced-reference.md: strokeColor mechanism, dataViewWildcard scoping triangle, mobile.json co-location, reference lines dual-entry, theme cascade order, theme-token CF, hidden fields concept",
    "Append finds to pbir-enhanced-report-loading.md: Desktop sync lag, TOM local port + timing constraint, 256-char path limit, build/release pipeline split, semantic-model-first deployment order",
    "Hand Find #1 to rc-deep-research for adversarial verification"
  ]
}
```

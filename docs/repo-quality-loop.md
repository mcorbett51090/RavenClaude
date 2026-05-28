# Repo-quality self-improvement loop

**Started:** 2026-05-28 · **Goal:** drive the repo-quality score above **90/100** via repeated gap-analysis → build-plan → expert-review → execute → re-score rounds.

## Scoring rubric (weighted, /100)
1. Plugin completeness & convention consistency (15)
2. Knowledge freshness & citation discipline (15)
3. Cross-plugin seam integrity (10)
4. CI / gate coverage & correctness (15)
5. Docs accuracy & navigability (10)
6. Security & safety posture (10)
7. Marketplace hygiene (10)
8. Agent/skill quality (10)
9. Verification depth (5)

Two independent expert agents score each round; the synthesized score is their average, reconciling divergences.

---

## Round 1 — 2026-05-28

### Scores
| Auditor | Score | Headline |
|---|---|---|
| Expert A | 87 | Mature repo; point loss = stale docs + a class of unguarded broken links + ungated new/domain hooks |
| Expert B | 79 | Strong engineering substrate; hand-maintained narrative docs are the dominant drag |
| **Synthesized** | **~83** | Substrate excellent (gates/seams/safety/catalog 9-10); narrative-doc drift + 2 ungated defect classes cost ~17 pts |

### Synthesized gap list (both auditors), prioritized
| # | Gap | Dim | ~pts | Fix |
|---|---|---|---|---|
| G1 | `docs/architecture.md` Status table + diagram stale (8/11 plugins wrong versions; skill/hook/agent counts wrong; finance/EdTech labelled "future") | 5 | ~3 | Rewrite the Status table from current `plugin.json` versions; fix the diagram counts + "future" labels |
| G2 | Root `README.md` undercounts ("five plugins"; only 6/11 detailed; stale skill counts) | 5 | ~2.5 | Update to 11; add 6 missing plugin sections; correct skill counts |
| G3 | Broken cross-plugin CLAUDE.md skill links in 6/11 plugins (`scenario-retrieval.md` is a dir → needs `/SKILL.md`+correct depth; `grounding-protocol` only in power-platform) + edtech `qbr-deck.md`→`qbr-deck-outline.md` | 3 | ~3 | Correct each link to its real target |
| G4 | **No markdown-relative-link gate** (root cause of G3 — broken links shipped green) | 4 | ~2 | Add a link-resolution gate to `audit-gates.sh` over `plugins/**/*.md` + `docs/**` (exclude generated `copilot/`, `<placeholder>` paths) |
| G5 | No behavioral gate for the new `route-decision-review.sh` hook (v0.49.0) or the 10 domain anti-pattern hooks | 4+9 | ~3 | Add gate(s): route-decision-review off→allow / binding→deny / multiselect→allow; one fire+no-fire fixture per domain hook |
| G6 | **No doc-drift gate** (CI rotted while green) | 4 | ~2 | Extend `check-marketplace-claims.py` (or new check) to assert `architecture.md` Status versions + README plugin count match `plugin.json`; wire into `validate-marketplace.yml` |
| G7 | CHANGELOG drift/inconsistency (core ~22 versions behind; only 4/11 plugins have one) | 1+5 | ~1.5 | Add CHANGELOG.md to the 7 older plugins (current entry + "see CLAUDE.md milestones/git history" for prior); make it a documented convention |
| G8 | finance CLAUDE.md missing `## 8a. Knowledge bank` header (has a `knowledge/` dir) | 1 | ~0.5 | Add the §8a section |
| G9 | Scenario frontmatter (`scenarios:`/`quickstart:`) present on all agents but ungated | 9 | ~0.5 | Add presence checks to `check-frontmatter.py` |

### Build plan (execution order)
- **P1 (docs):** G1, G2, G8 — rewrite architecture.md table+diagram, README, finance §8a.
- **P2 (links):** G3 fix all broken links, then G4 add the link gate (proves the fixes + prevents regression).
- **P3 (gates):** G5 hook gates, G6 doc-drift gate, G9 frontmatter scenario check.
- **P4 (changelog):** G7 — CHANGELOG hygiene.
Each P closes with the full local gate suite (audit-gates 257→N/0, prettier, frontmatter, claims, guide-fresh) + a commit.

### Plan review (expert tweak applied before execution)

Reordered for **proof-carrying execution** — fix the defect first, then ship the gate that would have caught it, so each gate's `must_pass` is exercised against the just-fixed tree:

1. **G3** (fix all broken cross-plugin links) → **then G4** (add `check-md-links.py` — proves the fixes + locks them in).
2. **G1 + G8 + G2** (narrative-doc rewrites: architecture.md version-less table, finance §8a, README 11-plugin rewrite) → **then G6** (extend `check-marketplace-claims.py` with architecture-completeness + README-count checks — the gate now forces those rewrites correct on every PR).
3. **G9** (frontmatter scenario schema) and **G5** (hook behavior gates) — pure additive gates over an already-clean tree.
4. **G7 — backfill CUT.** Instead of adding `CHANGELOG.md` to 7 plugins (churn with low signal), document it as an **optional** convention in AGENTS.md (version field + git history are the source of truth). Closes the "inconsistency" gap without manufacturing 7 files.

### Execution (2026-05-28) — all shipped, full gate suite green

| Gap | What shipped |
|---|---|
| G3 | Fixed every broken relative link the new gate found — **17** total: 14 microsoft-fabric agent hrefs (`[../knowledge/X.md](X.md)` → href corrected), 2 README `spawn-team.md`→`spawn-team/SKILL.md`, 1 stale build-plan link → the `cross-platform-determinism` skill. |
| G1 | architecture.md Status table rewritten **version-less** (11-plugin roster; versions live only in marketplace.json) + mermaid diagram/counts fixed. |
| G8 | finance `## 8a. Knowledge bank` section added. |
| G2 | README rewritten: "five plugins" → **11**; 6 missing per-plugin sections added; core skills 10→22, hooks 5→11; stale agent names corrected. |
| G6 | `check-marketplace-claims.py` Check 4 added — architecture.md lists every plugin **+** README "ships **N plugins**" == actual count; 2 bidirectional audit-gates fixtures (Gate 12). Also wired `check-marketplace-claims.py` + `check-md-links.py` as **explicit CI steps** in validate-marketplace.yml. |
| G4 | New `scripts/check-md-links.py` (resolves every relative link in boundary docs + docs/** + plugins/**/*.md; skips externals/anchors/placeholders/generated copilot+concepts/templates); audit-gates **Gate 29** (bidirectional). |
| G9 | `check-frontmatter.py` now requires the full scenario-authoring schema on every `agents/*.md` (audience/works_with/scenarios-with-item-keys/quickstart); audit-gates **Gate 18** must_fail fixture added. |
| G5 | **Gate 30** — fire + no-fire fixtures for all 10 domain anti-pattern hooks; **Gate 31** — route-decision-review off→allow / binding-yes/no→deny / multiselect→allow (deterministic via `THING_DECIDE_MOCK_VERDICT`). Found + fixed a real bug: `flag-statistical-smells.sh` aborted under `set -o pipefail` on any clean file (applied-statistics 0.1.0→0.1.1). |
| G7 | CHANGELOG documented as an **optional** convention in AGENTS.md (backfill cut). |

**Gate audit:** 257 → **285 pass / 0 fail** (bidirectional). Full local suite green: JSON, shell-syntax, prettier (exit 0), marketplace-claims, frontmatter, md-links, repo-guide/dashboard/copilot/concepts freshness, version parity.

### Re-score (Round 2)
_(two independent expert agents re-score the post-execution tree below)_

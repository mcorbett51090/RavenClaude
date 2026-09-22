# G6 — Synthesized plan: `graph-engineering`

**Slug:** `graph-engineering`
**Owner:** Matt
**Date:** 2026-08-14
**Depth:** `quick` (G4a critic and G5 red-team **were not run**)
**G1 verdict:** yes-with-conditions — ship a client-first craft plugin; no live graph runtime
**G3b:** tripped Phase 8→36 and Phase 8b→35; exit **owner-gated**, not stop. C31 was not cited on a construction phase and is not a blocker.

**Implementation landing**

| Field | Value |
|---|---|
| Worktree | `/Users/matthewcorbett/.grok/worktrees/matthewcorbett-ravenclaude/graph-engineering/.claude/worktrees/forge-graph-engineering` |
| Branch | `forge/graph-engineering` |
| Plugin version | `0.1.0` |
| Catalog | append `plugins[]`; bump `metadata.version` `0.92.0` → `0.93.0` |
| Landing | **pr** (new plugin + marketplace.json + named branch) |
| Size | **large** (many files under `plugins/graph-engineering/` plus catalog/prose regen) |
| Privacy | clean — no customer data |
| Research | done (G0–G3b on disk) |

Confirm `git branch --show-current` prints `forge/graph-engineering` (non-empty) before any write. Do not implement on `main` in `~/RavenClaude`.

---

## Verdicts (no dangling conflict)

| Decision | Verdict | One-line why |
|---|---|---|
| Plugin name | **`graph-engineering`** | Scope slug; client-first; does not imply RDF-only; collision with `graphql-engineering` is a keyword/NOT-line problem, not a longer name |
| Agent count | **2** — `graph-data-modeler` + `graph-query-engineer` | Geospatial analog; ~15K orchestrator description budget; owner asked GraphRAG *included* — skills + knowledge + one command count as included |
| GraphRAG | **Craft, not a third agent** | Construction skill + knowledge + `/construct-retrieval-graph`; query patterns live on the query engineer + `write-graph-query`. Candidate `graphrag-engineer` is optional 0.2.0 only if post-ship routing under-dispatches |
| Language posture | **GQL is the standard; Cypher is the lingua franca taught first**; SPARQL/Gremlin in the dated map | C15/C16; clients type Cypher; do not name the slash command `/write-gql` |
| Sequencing | **Linter ∥ knowledge** after scaffold | Hook needs a real script to call (or mirror); knowledge examples get shape-checked before bulk prose |
| Hook vs linter | **Linter is Python stdlib; hook is grep-only POSIX ERE** | PreToolUse may lack `python3`; `check-grep-ere-pcre.py` gates hook greps |
| PR granularity | **One PR** on `forge/graph-engineering` | Not two plugins; not GraphRAG-later stacked PRs; 8/8b are optional same-PR files |
| C35 / C36 | **Optional, one reversible file each** | G3b owner-gated. `[unverified — premise not disconfirmed: documenting internals (36) and dual-write-as-defect (35) are design inferences; phases stay one reversible file each and may be skipped]` |

Do **not** promote C31–C36 into multi-file construction.

---

## Alternative approaches

| # | Approach | Agents | GraphRAG | Sequencing | Language | PR | Trade-off |
|---|---|---|---|---|---|---|---|
| **A** | 3-agent full candidate | modeler + query + `graphrag-engineer` | Dedicated agent | Knowledge-first; linter mid | Cypher lead in client copy; GQL named as standard | One PR | Clearest GraphRAG routing; +1 description (~75 tokens) against the 15K budget; risk the third agent re-decides memory III.a |
| **B** | 2-agent full candidate | modeler + query | Dual skill + command | **Linter-first** (lint ∥ knowledge) | GQL-first docs; Cypher as dialect | One PR | Cheaper budget; GraphRAG still ships; Team Lead may under-route pure GraphRAG asks |
| **C** | Research-only or GraphRAG-deferred | none / 2 without GraphRAG | Deferred or docs-only | n/a | n/a | Docs or stacked 0.2.0 | Correct **only** if owner rejects C31; fails G0 “full candidate including GraphRAG” |

**Chosen: B’s 2-agent ship + A’s catalog/regen DoD + A’s hook depth + mixed language posture (GQL standard, Cypher taught first).** Approach A is the 0.2.0 promotion path if routing evidence shows under-dispatch. Approach C is the reject path, not this plan. G3b did not reject C31.

---

## Reconciled plugin shape (v0.1.0)

**Requires:** `ravenclaude-core@>=0.7.0` (same floor as geospatial).

**Contract:** **Advisory only.** Agents emit Cypher / ISO GQL / openCypher / Gremlin / SPARQL snippets the user runs. No driver, no MCP graph server, no CI that requires Neo4j / Fabric / Spanner / Neptune to be up.

**Not Neo4j-only.** ISO/IEC 39075:2024 GQL is the property-graph standard (C15). Cypher/openCypher is the lingua franca evolving toward it (C16). Gremlin (C19) and SPARQL 1.1 (C18) stay in the dated map. **Do not teach archived Kuzu as the 2026 embed default** (C28).

**Shape analog:** `plugins/geospatial-engineering/` (2-agent domain craft, decision trees, advisory PreToolUse hook, no hosted runtime). Commands follow `plugins/memory-engineering/`. Stdlib linter follows `plugins/email-engineering/scripts/email_auth_lint.py`.

### Directory tree (no new `.repo-layout.json` globs — C13)

```
plugins/graph-engineering/
├── .claude-plugin/plugin.json
├── CLAUDE.md
├── README.md
├── CHANGELOG.md                          # ## [0.1.0] — 2026-08-14
├── agents/
│   ├── graph-data-modeler.md
│   └── graph-query-engineer.md
├── knowledge/
│   ├── graph-vs-relational-decision-tree.md
│   ├── lpg-modeling-catalog.md
│   ├── graph-languages-and-engines-2026.md
│   ├── graphrag-construction.md
│   └── ravenclaude-internal-uses.md      # Phase 8 only — owner-gated
├── skills/
│   ├── choose-graph-or-not/SKILL.md
│   ├── model-property-graph/SKILL.md
│   ├── write-graph-query/SKILL.md        # Cypher first, then GQL, then Gremlin/SPARQL; GraphRAG query section
│   └── construct-retrieval-graph/SKILL.md
├── commands/
│   ├── choose-graph-or-not.md
│   ├── model-property-graph.md
│   ├── write-graph-query.md
│   └── construct-retrieval-graph.md
├── scripts/
│   ├── lint_graph_shape.py
│   └── fixtures/                         # good_bounded.cypher, bad_unbounded.cypher, bad_untyped.cypher, bad_anonymous.cypher
├── hooks/
│   ├── hooks.json
│   └── flag-graph-smells.sh
├── best-practices/
│   ├── README.md
│   ├── type-every-relationship.md
│   ├── bound-variable-length-paths.md
│   ├── model-for-supernodes.md
│   ├── gql-is-the-standard-cypher-is-the-lingua-franca.md
│   ├── algorithms-are-a-library-not-the-query-language.md
│   ├── graphrag-needs-a-humbling-baseline.md
│   └── prefer-projection-over-dual-write.md   # Phase 8b only — owner-gated
├── templates/
│   ├── graph-data-model.md
│   ├── query-language-decision.md
│   └── retrieval-graph-design.md
└── scenarios/
    ├── README.md
    ├── 2026-08-14-unbounded-star-path.md
    ├── 2026-08-14-this-is-relational.md
    └── 2026-08-14-graphrag-before-bm25-lost.md
```

**Always-ship inventory (encode these counts):** 2 agents, 4 skills, 4 commands, 4 knowledge, 6 best-practices, 3 templates, 3 scenarios, 1 advisory hook, 1 stdlib linter. Optional extras (Phase 8 / 8b) are **not** in the gated count sentence.

### Agents (2)

| Agent | Owns | Distinctive NOT |
|---|---|---|
| `graph-data-modeler` | Graph-vs-relational; LPG vs RDF; labels / rel types / identity / temporal edges / supernodes; **GraphRAG construction** (extract → index architecture) | SQL OLTP → `database-engineering`; GraphQL → `graphql-engineering`; Microsoft Graph API → `microsoft-graph`; **whether** a memory graph beats BM25 → `memory-engineering` |
| `graph-query-engineer` | Bounded traversals in **Cypher (taught first)**, ISO GQL, openCypher, Gremlin, SPARQL; path cost; algorithm-library vs traversal; **GraphRAG local/global/DRIFT query patterns** | Not a query engine; not GraphQL; not Neo4j-only; not schema-first modeling (modeler) |

Each agent: `description` ≤ 300 chars; explicit `tools:`; `model: opus`; `audience` / `works_with` / ≥3 `scenarios` (`intent` / `trigger_phrase` / `outcome` / `difficulty`) / `quickstart` (C12). Suggested `tools:`: `Read, Edit, Write, Grep, Glob, Bash, WebFetch, WebSearch`. **Do not** grant a graph-DB MCP.

Draft descriptions (count before ship):

- **graph-data-modeler:** `Use for property-graph vs RDF modeling — 'should this be a graph?', labels/rel-types, identity, supernodes, temporal edges, GraphRAG construction. Traverses graph-vs-relational first. NOT SQL OLTP (database-engineering), GraphQL, or Microsoft Graph API.`
- **graph-query-engineer:** `Use for Cypher, ISO GQL, openCypher, Gremlin, SPARQL — bounded traversals, path cost, GraphRAG local/global query patterns, when to project into an algorithm library. Advisory snippets only. NOT Neo4j-only. NOT GraphQL. Untyped ()-[]-() and unbounded * paths are bugs.`

`works_with` lists the sibling plus `database-engineering`, `ai-rag-engineering`, `memory-engineering` (not GraphQL / MS Graph as collaborators). Escalation **must** name `memory-architect-lead` (paradigm III.a vs II) and `rag-architect-lead` / `retrieval-eval-analyst` (chunking / recall@k / hybrid lexical).

Example triggers (≥3 per agent: starter / advanced / troubleshooting):

- modeler: “Should this workload be a graph?”; “LPG or RDF?”; “This celebrity node kills traversals”; “Stand up GraphRAG over this corpus”
- query: “Write this Cypher/GQL”; “Why is this `*` path slow?”; “Gremlin vs SPARQL for this hop”; “Local vs global GraphRAG search?”

### GraphRAG placement (chosen)

- **Not** a third agent in v0.1.0.
- `skills/construct-retrieval-graph` + `commands/construct-retrieval-graph.md` + `knowledge/graphrag-construction.md` owned primarily by **modeler**.
- Retrieval-query patterns are a **section of** `write-graph-query` + the query-engineer body (no fifth skill — keeps gated counts at 4/4).
- CLAUDE.md routing: “GraphRAG / multi-hop corpus synthesis / community summaries” → modeler first for *should we build a retrieval graph and how?*; query engineer for *write the traversal / DRIFT-local pattern*.
- Hard hand-off: “should we pay for a **memory** graph / III.a vs BM25?” → `memory-engineering`. Hybrid lexical eval / chunking / recall@k → `ai-rag-engineering`.
- Architectures (C21–C23) are cited as families, **not** bake-off winners. Author-reported metrics stay disclaimed.

### Knowledge (4 always-ship + 1 optional)

| File | Role |
|---|---|
| `graph-vs-relational-decision-tree.md` | Mermaid tree starting from C04’s “specialized engine” leaf |
| `lpg-modeling-catalog.md` | Labels, typed directed rels (C17, C29), identity, temporal edges, supernodes |
| `graph-languages-and-engines-2026.md` | Dated map: GQL vs Cypher vs Gremlin vs SPARQL; engines; Kuzu archived |
| `graphrag-construction.md` | Extract → index → local/global search; cites memory III.a; does not re-decide paradigm |
| `ravenclaude-internal-uses.md` | **Phase 8 only** — three LPG sketches. Examples, not a runtime |

### Linter + hook

`scripts/lint_graph_shape.py` — stdlib (`argparse`, `re`, `sys`, `pathlib`). Shape checks, **not** a parser. No network.

1. Unbounded variable-length path — Cypher `-[*]->` / `-[*..]->` / `-[*1..]->`; GQL `{1,}` without upper (C20) — ERROR
2. Missing relationship type — `-[]-`, `-[]->`, untyped `--` (C17, C29) — ERROR
3. Anonymous `MATCH ()-` expansion / supernode scan heuristic (C29) — ERROR
4. Pre-GQL `*` syntax is not GQL-conformant (C20) — WARNING, not ERROR

CLI: paths, `--stdin`, `--strict` (warnings-only default; `--strict` → exit 1 on ERROR), `--self-test`. Print `file:line: LEVEL: message`. `--self-test` embeds fixtures (clean bounded typed path; unbounded `*`; untyped `-[]->`; anonymous `()-[]-()`). Also keep `scripts/fixtures/` for hook / human tests. SPARQL/Gremlin get thinner “unbounded + untyped” heuristics where grep-able; do not pretend to validate SPARQL 1.1. `.graphql` files: exit 0 with a “wrong plugin” note.

`hooks/flag-graph-smells.sh` — **grep-only POSIX ERE** (no `\d` `\s` `\b` look-around). Dual-source path (`$1` then stdin JSON `.tool_input.file_path // .tool_input.path`). Filter: `*.cypher` `*.cyp` `*.gql` `*.sparql` `*.rq` `*.groovy` `*.py` `*.js` `*.ts` `*.md`. Three greps matching ERROR-class smells. Advisory default; `GRAPH_SMELLS_STRICT=1` → `exit 2`. **Do not** shell out to Python from the hook (sandbox / missing `python3`).

`hooks/hooks.json` — PreToolUse `Edit|Write|MultiEdit`, `${CLAUDE_PLUGIN_ROOT}/hooks/flag-graph-smells.sh "$CLAUDE_TOOL_FILE_PATH"` (geospatial wiring; dual-source still required because `$CLAUDE_TOOL_FILE_PATH` is often empty).

### Seams (CLAUDE.md §2 and README — this plugin only in v0.1.0)

| Adjacent | Discriminator | Owner |
|---|---|---|
| **`database-engineering`** | Multi-row transactions, ad-hoc SQL, known-schema records — **when NOT a graph** | That plugin. This one owns the specialized-engine leaf C04 points at |
| **`ai-rag-engineering`** | Vector / BM25+vector hybrid, chunking, recall@k, token cost | That plugin. This one owns graph construction + traversal used **in** retrieval |
| **`memory-engineering`** | **Whether** a memory graph (paradigm III.a) beats no-memory and BM25 | That plugin. This one owns **model/query of a retrieval graph** after that “yes” |
| **`graphql-engineering`** | GraphQL schema / resolvers / query-cost — **not a property graph** | That plugin (C07) |
| **`microsoft-graph`** | Microsoft Graph API / Entra / M365 OData — **not an LPG** | That plugin (C08) |
| **`microsoft-fabric`** | Fabric Graph **SKU / ops / OneLake / CU billing / Data Agent preview** | That plugin (C11). This plugin teaches the LPG/GQL **craft** that SKU runs |
| `data-platform` | Warehouse / ELT of non-graph facts | Mention, do not deep-link (C10 — weak seam) |

**Do not** edit neighbor `CLAUDE.md` files in 0.1.0 (version-cascade). Reciprocal one-liners are a follow-up PR.

### Constitution house opinions (CLAUDE.md)

1. Decide graph-vs-relational before labels. Multi-row txns + ad-hoc SQL + known schema → `database-engineering` (C03, C04).
2. Type every relationship; give it a direction. Untyped `()-[]-()` is a model bug (C17, C29).
3. Bound every variable-length path. Unbounded `*` is a latency bomb (C20).
4. Treat supernodes as modeling, not vendor trivia (C29).
5. **GQL is the standard; Cypher is the lingua franca taught first; Gremlin and SPARQL stay in the field** (C15, C16, C18, C19).
6. Algorithms live in libraries (projection + run), not as language trivia (C30).
7. GraphRAG constructs a retrieval graph; it does not pick a memory paradigm (C06, C21). Needs a humbling non-graph baseline first.
8. Advisory snippets only. No live store in this marketplace.
9. Date every engine / GA / version claim. Fabric Graph GA stays `[verify-at-use]` (C11 vs C25).
10. Do not teach archived Kuzu as the default embed (C28).

### Naming table (frozen — do not mix panel A/B names)

| Surface | Authoritative name |
|---|---|
| Linter | `lint_graph_shape.py` |
| Hook | `flag-graph-smells.sh` |
| Languages knowledge | `graph-languages-and-engines-2026.md` |
| GraphRAG knowledge | `graphrag-construction.md` |
| Internals knowledge | `ravenclaude-internal-uses.md` (Phase 8) |
| Dual-write BP | `prefer-projection-over-dual-write.md` (Phase 8b) |
| Choose skill/command | `choose-graph-or-not` |
| Model skill/command | `model-property-graph` |
| Query skill/command | `write-graph-query` |
| GraphRAG skill/command | `construct-retrieval-graph` |
| Query command is **not** | `write-gql` |

---

## Unverified / unsettled G1 claims — settle or live with

| id | Marker | Step that settles or lives with it |
|---|---|---|
| 11 / 25 | Fabric Graph **GA** word is marketplace-dated, not on the Learn overview fetched 2026-08-14 | Phase 3 knowledge: keep `[verify-at-use]`. Never print unmarked “GA” |
| 18 gap | SPARQL 1.2 / RDF 1.2 not fetched | Phase 3: date SPARQL **1.1** only. Do not invent 1.2 |
| 22 / 23 | HippoRAG / LightRAG numbers are author-reported | Phase 3 + construct skill: design-intent, not bake-off winners |
| 28 adjacent | `docs.kuzudb.com` DNS-failed; Kuzu repo archived | Phase 3: “archived 2025-10-10 — do not default.” No live-docs URL |
| wide-map | TigerGraph not fetched; Memgraph intro 404 | Phase 3: omit, or `[unverified — not fetched 2026-08-14]` |
| 20 | Path-cost is documented behavior, not a worktree repro | Phase 2 linter implements the documented smell; live with no local query-plan |
| 31 | Ship-plugin inference | G3b did **not** trip. This plan ships. If owner later rejects: stop, land `docs/research/graph-engineering-2026-08-14.md` only |
| 32 | Advisory-only / no live runtime | Encoded as house opinion #8 + every phase’s “no Neo4j in CI.” Not a construction `depends_on` |
| 33 | Do not absorb memory III.a | Encoded as agent NOT-lines + skill hand-off. Not a construction `depends_on` |
| 34 | Relational default | Encoded in decision tree + house opinion #1. Not a construction `depends_on` |
| **35** | `[unverified — training knowledge]` dual-write-as-defect | **Phase 8b only** — one reversible file, skippable. Must keep the marker; ground the *allowed* pattern in C25/C26 |
| **36** | Internals-as-examples usefulness | **Phase 8 only** — one reversible file, skippable. `[unverified — premise not disconfirmed: documenting internals (36) …]` |

---

## Dependency DAG

```
Phase 0  Preconditions
    │
    ▼
Phase 1  Scaffold
    │
    ├──────────────► Phase 2  Linter + fixtures ─────────────┐
    │                                                         │
    └──────────────► Phase 3  Knowledge (4 files) ───────────┤
                         │                                    │
                         ├─► Phase 4  BP / templates / scenarios
                         │         │
                         │         └─► Phase 5  Skills + commands
                         │                   │
                         │                   └─► Phase 6  Agents (2)
                         │
                         ├─► Phase 8   Internals (1 file, owner-gated, C36)
                         └─► Phase 8b  Dual-write BP (1 file, owner-gated, C35)

Phase 2 ─────────────────► Phase 7  Hook (grep-only; mirrors linter smells)

Phase 4 + 5 + 6 + 7 ─────► Phase 9  Catalog + counts + metadata 0.93.0
                                      │
                                      ▼
                                 Phase 10  Verify / DoD
```

**Parallel after Phase 1:** Phase 2 ∥ Phase 3.
**Phase 4 waits on 3** (and uses 2 to lint any example snippets).
**Phase 5 waits on 3+4** (skills fill templates; cite knowledge).
**Phase 6 waits on 5** (agent bodies link real skill paths).
**Phase 7 waits on 2** (smells exist); may run ∥ 5/6.
**Phase 8 / 8b wait on 3**, run ∥ everything else, **may be skipped**.
**Phase 9 waits on 4+5+6+7** so encoded counts match disk. Does **not** wait on 8/8b.
**Phase 10 is the critical-path tail.**

**Critical path:** 0 → 1 → 3 → 4 → 5 → 6 → 9 → 10.

---

## Phase 0 — Preconditions

depends_on_claims: [02, 13, 14]

**Goal:** Prove the landing surface before any plugin file is written.

**Work (verify only — no product files):**

1. `git branch --show-current` is `forge/graph-engineering` in the named worktree (non-empty; detached HEAD is a fail).
2. No existing `plugins/graph-engineering/` and no marketplace `name` of `graph-engineering` or `graph-knowledge-engineering` (C02).
3. `.repo-layout.json` already allows standard plugin globs (C13) — **no glob edit**.
4. Read `plugins/geospatial-engineering/` constitution section order.

**Acceptance:**

```shell
test "$(git branch --show-current)" = "forge/graph-engineering"
test ! -d plugins/graph-engineering
! rg -n '"name": "graph-engineering"|"name": "graph-knowledge-engineering"' .claude-plugin/marketplace.json
```

**Pre-build gates:** not on detached HEAD; do not write under `plugins/` until Phase 1.

---

## Phase 1 — Scaffold

depends_on_claims: [01, 02, 09, 12, 13, 14]

**Goal:** Installable empty craft plugin with constitution skeleton, manifest, README, CHANGELOG. No agents yet (frontmatter gate is vacuous until Phase 6).

**Create:**

- `plugins/graph-engineering/.claude-plugin/plugin.json` — `name: graph-engineering`, `version: 0.1.0`, author Matt Corbett, homepage `https://github.com/mcorbett51090/RavenClaude`, MIT, `requires.plugins: ["ravenclaude-core@>=0.7.0"]`. Keywords: `graph`, `property-graph`, `lpg`, `cypher`, `gql`, `opencypher`, `gremlin`, `sparql`, `rdf`, `graphrag`, `neo4j`, `neptune`, `spanner-graph`, `janusgraph`, `supernode`. **Do not** put `graphql` or `microsoft-graph` in keywords (C07, C08). Description names **2 agents** + GraphRAG as skill/command + advisory + seams; keep ≤ 1024 chars.
- `plugins/graph-engineering/CLAUDE.md` — geospatial section map (stubs ok): roster, routing, seams table, house opinions, anti-patterns, CGP, output contracts, hooks, skills, knowledge bank. Inherit `../ravenclaude-core/CLAUDE.md`.
- `plugins/graph-engineering/README.md` — client-first “you ask / it returns” table; multi-language advisory stance; install snippet; seam ASCII block; **NOT GraphQL / NOT Microsoft Graph API**.
- `plugins/graph-engineering/CHANGELOG.md` — `## [0.1.0] — 2026-08-14` initial release.

**Do not yet** append marketplace.json (Phase 9 — counts must match finished inventory).

**Acceptance (exit 0):**

```shell
python3 -m json.tool plugins/graph-engineering/.claude-plugin/plugin.json > /dev/null
test -f plugins/graph-engineering/CLAUDE.md
test -f plugins/graph-engineering/README.md
test -f plugins/graph-engineering/CHANGELOG.md
```

**Pre-build gates:** JSON parses; no new top-level dirs; kebab-case names; no `.repo-layout.json` edit.

---

## Phase 2 — Shape linter

depends_on_claims: [12, 13, 20, 29]

**Goal:** Stdlib shape checker exists **before** knowledge files grow example queries. This is the script the hook’s smells are specified against.

**Create:**

- `plugins/graph-engineering/scripts/lint_graph_shape.py`
- `plugins/graph-engineering/scripts/fixtures/good_bounded.cypher`
- `plugins/graph-engineering/scripts/fixtures/bad_unbounded.cypher`
- `plugins/graph-engineering/scripts/fixtures/bad_untyped.cypher`
- `plugins/graph-engineering/scripts/fixtures/bad_anonymous.cypher`

Behavior as specified in “Linter + hook” above. Module docstring states false-positive/negative expectations (not a parser).

**Acceptance (exit 0):**

```shell
python3 plugins/graph-engineering/scripts/lint_graph_shape.py --self-test
python3 plugins/graph-engineering/scripts/lint_graph_shape.py plugins/graph-engineering/scripts/fixtures/bad_unbounded.cypher ; test $? -eq 0
python3 plugins/graph-engineering/scripts/lint_graph_shape.py --strict plugins/graph-engineering/scripts/fixtures/bad_unbounded.cypher ; test $? -ne 0
python3 plugins/graph-engineering/scripts/lint_graph_shape.py plugins/graph-engineering/scripts/fixtures/good_bounded.cypher
python3 -m ruff check plugins/graph-engineering/scripts/lint_graph_shape.py
# stdlib only
python3 - <<'PY'
from pathlib import Path
text = Path("plugins/graph-engineering/scripts/lint_graph_shape.py").read_text()
bad = [ln for ln in text.splitlines() if ln.startswith(("import ", "from ")) and not any(s in ln for s in ("argparse", "re", "sys", "pathlib", "typing"))]
assert not bad, bad
print("stdlib-only ok")
PY
```

**Pre-build gates:** ruff clean; no third-party imports; no network.

---

## Phase 3 — Knowledge

depends_on_claims: [03, 04, 05, 06, 11, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

**Goal:** Dated, cited knowledge bank. Client-first. **No** RavenClaude runtime sketches here (those are Phase 8).

**Create:**

- `knowledge/graph-vs-relational-decision-tree.md`
  - Mermaid tree that **starts from** `database-engineering-decision-trees.md` leaf “Specialized engine for that one need” (C04).
  - Branches: path/variable-depth traversal → LPG; shared-IRI interchange / entailment → RDF+SPARQL (C17, C18); multi-hop corpus synthesis → retrieval-graph craft **after** BM25 lost (C06, C21); else stay relational / KV / document.
  - Honest “not a graph” list: transactions, single-key, whole-document, lexical RAG.
- `knowledge/lpg-modeling-catalog.md`
  - Nodes + labels + properties; directed typed property-bearing rels (C17, C29).
  - Identity (stable business keys); temporal edges as first-class rels or valid-time properties.
  - Supernode / dense-node: type the edge, vertex-centric / local index, never `()-[]-()` from a celebrity (C29).
- `knowledge/graph-languages-and-engines-2026.md`
  - **Lead with GQL** (ISO/IEC 39075:2024 + Cor 1:2026, C15) as the standard; then Cypher/openCypher as the lingua franca evolving toward it (C16); then Gremlin (C19); SPARQL 1.1 only — do not date SPARQL 1.2.
  - Engines as existence + fetched facts: Neo4j + GDS library-not-language (C30); Neptune Gremlin+openCypher+SPARQL (C24); Fabric Graph LPG+GQL, GA word `[verify-at-use]` (C11, C25); Spanner Graph GQL, Enterprise/Enterprise Plus, no PG interface (C26); Cosmos Gremlin + Fabric steer for OLAP (C27); AGE / FalkorDB / JanusGraph named; **Kuzu archived 2025-10-10** (C28).
  - Retrieval date **2026-08-14**. Every volatile row `[verify-at-use]`.
  - Omit TigerGraph / unverified Memgraph, or mark `[unverified — not fetched 2026-08-14]`.
- `knowledge/graphrag-construction.md`
  - Microsoft GraphRAG: extract → Leiden communities → global/local/DRIFT (C21).
  - HippoRAG: KG + Personalized PageRank; author-reported cost — design intent, not a bake-off (C22).
  - LightRAG: dual-layer KG + vectors (C23).
  - **Mandatory cite:** `plugins/memory-engineering/knowledge/memory-engineering-paradigms.md` III.a + BM25 humbling baseline. This file does **not** re-decide paradigm.
  - **Mandatory cite:** `ai-rag-engineering` for chunking, judgment sets, hybrid lexical/vector.

Each file: `Last reviewed: 2026-08-14`, source URLs from the claims table. Intentional bad examples live **only** under `scripts/fixtures/`. Good snippets in knowledge must pass advisory `lint_graph_shape.py`.

**Acceptance (exit 0):**

```shell
test -f plugins/graph-engineering/knowledge/graph-vs-relational-decision-tree.md
test -f plugins/graph-engineering/knowledge/lpg-modeling-catalog.md
test -f plugins/graph-engineering/knowledge/graph-languages-and-engines-2026.md
test -f plugins/graph-engineering/knowledge/graphrag-construction.md
test ! -f plugins/graph-engineering/knowledge/ravenclaude-internal-uses.md   # not yet — Phase 8
! grep -nE 'require[sd].*(neo4j|bolt://|gql://)|must be running' plugins/graph-engineering/knowledge/*.md
python3 plugins/graph-engineering/scripts/lint_graph_shape.py plugins/graph-engineering/knowledge/*.md
```

**Pre-build gates:** markdown tables/lists; Mermaid in the decision-tree file; no layout-glob change; no invented Fabric GA word.

---

## Phase 4 — Best-practices, templates, scenarios

depends_on_claims: [09, 17, 20, 21, 29, 30]

**Goal:** Observation-backed rule cards, fill-in templates, three worked scenarios. Dual-write rule is Phase 8b.

**Create:**

- `templates/graph-data-model.md` — fill **before** DDL/Cypher `CREATE`
- `templates/query-language-decision.md` — GQL vs Cypher vs Gremlin vs SPARQL + engine
- `templates/retrieval-graph-design.md` — extraction, index architecture, search mode, baseline-eval checkbox, hand-off to memory / ai-rag
- `best-practices/README.md`
- `best-practices/type-every-relationship.md`
- `best-practices/bound-variable-length-paths.md`
- `best-practices/model-for-supernodes.md`
- `best-practices/gql-is-the-standard-cypher-is-the-lingua-franca.md`
- `best-practices/algorithms-are-a-library-not-the-query-language.md`
- `best-practices/graphrag-needs-a-humbling-baseline.md`
- `scenarios/README.md`
- `scenarios/2026-08-14-unbounded-star-path.md`
- `scenarios/2026-08-14-this-is-relational.md`
- `scenarios/2026-08-14-graphrag-before-bm25-lost.md`

Best-practice files follow geospatial `always-store-an-srid.md`: Status / Domain / Applies to / Why / How / Don’t. Absolute rules for type-every-rel / bound-paths / supernodes; pattern (strong default) for GQL-vs-Cypher, algorithms-as-library, and humbling-baseline.

**Edit:** `CLAUDE.md` § templates / best-practices.

**Acceptance (exit 0):**

```shell
test -f plugins/graph-engineering/best-practices/type-every-relationship.md
test -f plugins/graph-engineering/best-practices/graphrag-needs-a-humbling-baseline.md
test -f plugins/graph-engineering/templates/graph-data-model.md
test -f plugins/graph-engineering/scenarios/2026-08-14-this-is-relational.md
test ! -f plugins/graph-engineering/best-practices/prefer-projection-over-dual-write.md   # not yet — Phase 8b
```

**Pre-build gates:** kebab-case filenames; no new globs; example snippets lint-clean or live only in fixtures.

---

## Phase 5 — Skills and commands

depends_on_claims: [01, 04, 12, 15, 16, 17, 20, 21, 29]

**Goal:** Four procedures + matching slash surfaces. GraphRAG is the fourth skill + fourth command (included). No fifth skill.

**Create skills:**

| Skill | Primary agent |
|---|---|
| `skills/choose-graph-or-not/SKILL.md` | modeler — walk the C04-derived tree; one-screen verdict + neighbor hand-off |
| `skills/model-property-graph/SKILL.md` | modeler — labels, typed directed rels, identity, supernode plan; fill `templates/graph-data-model.md` |
| `skills/write-graph-query/SKILL.md` | query engineer — **Cypher examples first**, then GQL equivalent, then Gremlin/SPARQL stubs; bound every quantified path; type every rel; GraphRAG local/global/DRIFT query section; pre-GQL `*` WARNING (C20) |
| `skills/construct-retrieval-graph/SKILL.md` | modeler — stop if BM25/no-graph baseline was not beaten; else extract → index → search mode; hand eval to `ai-rag-engineering`; paradigm to `memory-architect-lead` |

**Create commands** (thin wrappers: `description` + `argument-hint` + numbered steps that **call** the matching skill):

- `commands/choose-graph-or-not.md`
- `commands/model-property-graph.md`
- `commands/write-graph-query.md`
- `commands/construct-retrieval-graph.md`

Guardrails on every command: advisory, no live DB, cite-or-mark engine versions.

**Edit:** `CLAUDE.md` § skills table.

**Acceptance (exit 0):**

```shell
test -f plugins/graph-engineering/skills/choose-graph-or-not/SKILL.md
test -f plugins/graph-engineering/skills/model-property-graph/SKILL.md
test -f plugins/graph-engineering/skills/write-graph-query/SKILL.md
test -f plugins/graph-engineering/skills/construct-retrieval-graph/SKILL.md
test -f plugins/graph-engineering/commands/construct-retrieval-graph.md
python3 scripts/check-frontmatter.py
```

**Pre-build gates:** skill frontmatter `name` + `description`; no consumer-repo paths; no shell-out to a graph DB; commands are definitions (not README leftovers).

---

## Phase 6 — Agents

depends_on_claims: [01, 09, 12]

**Goal:** Two routed specialists with gated frontmatter. Bodies point at Phase 3 knowledge and Phase 5 skills.

**Create:**

- `plugins/graph-engineering/agents/graph-data-modeler.md`
- `plugins/graph-engineering/agents/graph-query-engineer.md`

Frontmatter per C12 + `tools:` + `model: opus` + ≤300-char `description`. Body: mission, discipline order (traverse the tree first), personality, skills driven, CGP, output contract, escalation table (seams above).

Output contracts:

- **Modeler:** store decision (graph vs not) / model (LPG\|RDF) / sketch / supernode plan / GraphRAG construct notes if any / neighbor hand-off / verdict.
- **Query engineer:** language (Cypher\|GQL\|Gremlin\|SPARQL) / bounded pattern / index advice / algorithm-vs-traversal / lint result / GraphRAG query mode if any / verdict.

**Edit:** `CLAUDE.md` roster + routing + output-contract rows to match the two files. GraphRAG dual-surface routing bullets required.

**Acceptance (exit 0):**

```shell
python3 scripts/check-frontmatter.py
python3 - <<'PY'
from pathlib import Path
import re
fm = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
agents = list(Path("plugins/graph-engineering/agents").glob("*.md"))
assert len(agents) == 2, agents
for p in agents:
    text = p.read_text()
    m = fm.match(text)
    assert m, p
    desc = re.search(r'^description:\s+"(.*)"\s*$', m.group(1), re.M)
    assert desc and len(desc.group(1)) <= 300, (p, len(desc.group(1)) if desc else None)
    assert re.search(r'^tools:\s+\S', m.group(1), re.M), p
    assert re.search(r'^model:\s+opus\s*$', m.group(1), re.M), p
print("agent frontmatter ok")
PY
```

**Pre-build gates:** `check-frontmatter.py`; description budget; knowledge + skill paths referenced must exist.

---

## Phase 7 — Advisory hook

depends_on_claims: [09, 13, 20, 29]

**Goal:** PreToolUse smell detection that does **not** require Python or a database. Mirrors Phase 2 ERROR-class checks in POSIX ERE.

**Create:**

- `hooks/flag-graph-smells.sh` — `#!/usr/bin/env bash` + `set -euo pipefail`; dual-source path; file filter; three ERE greps; advisory default; `GRAPH_SMELLS_STRICT=1` → `exit 2`
- `hooks/hooks.json` — PreToolUse `Edit|Write|MultiEdit`, `${CLAUDE_PLUGIN_ROOT}/hooks/flag-graph-smells.sh "$CLAUDE_TOOL_FILE_PATH"`

**chmod +x** the hook (CI fails otherwise).

**Edit:** `CLAUDE.md` § hooks / automated checks.

**Acceptance (exit 0):**

```shell
chmod +x plugins/graph-engineering/hooks/flag-graph-smells.sh
bash -n plugins/graph-engineering/hooks/flag-graph-smells.sh
test -x plugins/graph-engineering/hooks/flag-graph-smells.sh
python3 -m json.tool plugins/graph-engineering/hooks/hooks.json > /dev/null
python3 scripts/check-grep-ere-pcre.py
tmp=$(mktemp /tmp/graph-smell.XXXX.md)
printf '%s\n' 'MATCH (a)-[*]->(b) RETURN a' > "$tmp"
plugins/graph-engineering/hooks/flag-graph-smells.sh "$tmp"
# previous line must exit 0 (advisory)
rm -f "$tmp"
```

**Pre-build gates:** hook executable; `bash -n`; POSIX ERE only; Phase 2 linter already exists as the specified twin; no Neo4j.

---

## Phase 8 — Internal uses (one file, owner-gated)

depends_on_claims: [36]

**[unverified — premise not disconfirmed: documenting internals (36) and dual-write-as-defect (35) are design inferences; phases stay one reversible file each and may be skipped]**

**Goal:** Document RavenClaude internals as LPG **examples**. If owner declines C36, **skip this file** — the plugin still ships. One reversible file only. Do **not** expand into hooks, CI, or a second plugin.

**Create (only this file):**

- `plugins/graph-engineering/knowledge/ravenclaude-internal-uses.md`

Contents: three labeled-property-graph sketches (plugin dependency / enablement topology; memory/knowledge graph as already described by `memory-engineering`; FORGE claim/decision graph). Each sketch is Cypher-like `CREATE` the reader could paste into **their** playground — not a marketplace service. Closing paragraph: *wiring these to a required graph server is out of scope; no hook/CI depends on this file.*

**Edit (one pointer only, if owner accepts):** `CLAUDE.md` knowledge-bank table adds one row. Do **not** bump the gated “4 knowledge” marketplace count unless the description is rewritten to say “4 + optional internals.”

**Acceptance (exit 0) — only if not skipped:**

```shell
test -f plugins/graph-engineering/knowledge/ravenclaude-internal-uses.md
! grep -nE 'required (runtime|server)|CI.*neo4j|fail unless' plugins/graph-engineering/knowledge/ravenclaude-internal-uses.md
```

**Pre-build gates:** owner accept C36 before merge of this file. Revert is `git rm` of one path.

---

## Phase 8b — Dual-write anti-pattern (one file, owner-gated)

depends_on_claims: [35]

**[unverified — premise not disconfirmed: documenting internals (36) and dual-write-as-defect (35) are design inferences; phases stay one reversible file each and may be skipped]**

**Goal:** Optional best-practice: prefer a **projection** (Fabric Graph / Spanner Graph over tables — C25, C26) over a second writable copy of an OLTP system of record. If owner declines C35, **skip**. One reversible file.

**Create (only this file):**

- `plugins/graph-engineering/best-practices/prefer-projection-over-dual-write.md`

Must mark the general consistency claim `[unverified — training knowledge]` and ground the *allowed* pattern in C25/C26 (graph-over-tables, not ETL dual-write).

**Acceptance (exit 0) — only if not skipped:**

```shell
test -f plugins/graph-engineering/best-practices/prefer-projection-over-dual-write.md
grep -q 'unverified — training knowledge' plugins/graph-engineering/best-practices/prefer-projection-over-dual-write.md
```

**Pre-build gates:** owner accept C35; otherwise delete before merge.

---

## Phase 9 — Catalog, counts, versioning

depends_on_claims: [02, 13, 14]

**Goal:** Register the plugin and heal every **gated** count. Inventory numbers in `plugin.json` / marketplace description must match files on disk (C14 + `check-marketplace-claims`).

**Create / edit:**

- `.claude-plugin/marketplace.json`
  - Append a `plugins[]` object: `name: graph-engineering`, `source: ./plugins/graph-engineering`, `version: 0.1.0`, author Matt Corbett, keywords matching `plugin.json`, description that **encodes real counts** (“2 agents”, “4 skills”, “4 commands”, “1 advisory hook”, “1 stdlib linter”).
  - Bump `metadata.version` **`0.92.0` → `0.93.0`**.
  - Recompute `metadata.description` domain-plugin integer (today stale **“144 domain plugins”** — total `plugins[]` minus `ravenclaude-core`) and rewrite that clause.
- `README.md` — gated totals (today **180**):
  - `ships **180 plugins**` → `**181 plugins**`
  - `179 of the 180 plugins` → recompute `requires.ravenclaude-core` with a script, do not assume
  - any other exact `N plugins` total claim
- `AGENTS.md` — `~180 plugins` is gated to the exact plugin count → `~181 plugins`. Leave `600+` / `630+` agent hedges unless a gate names an exact integer.
- `docs/architecture.md` — add Status-table row with link `](../plugins/graph-engineering/)`. Update stale `Active plugins (166)` to actual `len(plugins/)`.
- `docs/plugin-candidates-2026-06-13.md` — mark candidate #4 **BUILT** (docs-only; not a ship blocker).
- Confirm `plugin.json` / `CLAUDE.md` / `README.md` inventory numbers match disk.

**Do not** touch `.repo-layout.json` (C13).
**Do not** reciprocal-edit six neighbor plugins.
**Do not** sneak a dashboard regen (`scripts/generate-dashboards.py` / `generate-index-dashboard.py`) into this PR unless a gate requires it; if generators are dirty after the JSON edit, regen and commit; if not, the PR body says “no regen required.”

**Acceptance (exit 0):**

```shell
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
python3 scripts/check-marketplace-claims.py
python3 - <<'PY'
import json
from pathlib import Path
cat = json.loads(Path(".claude-plugin/marketplace.json").read_text())
plug = json.loads(Path("plugins/graph-engineering/.claude-plugin/plugin.json").read_text())
entry = next(p for p in cat["plugins"] if p["name"] == "graph-engineering")
assert entry["version"] == plug["version"] == "0.1.0"
assert cat["metadata"]["version"] == "0.93.0"
assert "144 domain" not in cat["metadata"]["description"]
print("version mirror + stale-144 healed")
PY
```

**Pre-build gates:** prettier on the JSON; marketplace↔plugin.json version mirror; architecture roster link; README/AGENTS count regexes.

---

## Phase 10 — Verify / DoD

depends_on_claims: [12, 13, 14]

**Goal:** Whole-tree gates green on the implementation worktree. Counts encoded in prose match disk. Then open **one** PR.

**Run (all exit 0), from the `forge/graph-engineering` worktree:**

```shell
scripts/check-checkout-fresh.sh                    # advisory
test "$(git branch --show-current)" = "forge/graph-engineering"
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
python3 -m json.tool plugins/graph-engineering/.claude-plugin/plugin.json > /dev/null
python3 -m json.tool plugins/graph-engineering/hooks/hooks.json > /dev/null
python3 -m json.tool .repo-layout.json > /dev/null
bash -n plugins/graph-engineering/hooks/flag-graph-smells.sh
test -x plugins/graph-engineering/hooks/flag-graph-smells.sh
python3 scripts/check-frontmatter.py
python3 scripts/check-marketplace-claims.py
python3 scripts/check-layout.py                    # or the layout snippet in AGENTS.md
python3 scripts/check-grep-ere-pcre.py
python3 plugins/graph-engineering/scripts/lint_graph_shape.py --self-test
npx --yes prettier@3.9.4 --write . --log-level warn
npx --yes prettier@3.9.4 --check . --log-level warn
python3 -m ruff check .
python3 - <<'PY'
import fnmatch, json, subprocess
allowed = json.load(open(".repo-layout.json"))["allowed_globs"]
new = subprocess.run(["git", "diff", "--name-only", "--diff-filter=A", "main"],
                     capture_output=True, text=True).stdout.splitlines()
violations = [f for f in new if not any(fnmatch.fnmatchcase(f, g) for g in allowed)]
assert not violations, violations
print("Layout OK")
PY
```

`scripts/audit-gates.sh` is recommended before the PR but is not unique to this plugin. If the environment cannot download prettier/ruff/actionlint, name the skip honestly — CI still must be green.

**DoD checklist**

- [ ] Plugin slug `graph-engineering`, version `0.1.0`, catalog entry + `metadata.version` `0.93.0`
- [ ] **2 agents**, each `description` ≤ 300, `tools:` present, `model: opus`, ≥3 scenarios, full schema
- [ ] **4 skills, 4 commands, 4 knowledge** (+ optional Phase 8 file)
- [ ] Advisory hook (3 ERE smells) + stdlib `lint_graph_shape.py --self-test`
- [ ] Seams written in CLAUDE.md / README for: `database-engineering`, `ai-rag-engineering`, `memory-engineering`, `graphql-engineering`, `microsoft-graph`, `microsoft-fabric`
- [ ] GraphRAG **included** as skill + knowledge + command; **cites** memory-engineering III.a; does not re-decide paradigm
- [ ] GQL named as the standard; Cypher taught first in `write-graph-query`; Kuzu not defaulted
- [ ] No live graph runtime, no MCP driver, no layout-glob change, no neighbor version bumps
- [ ] **Regen — encoded counts:**
  1. `README.md` `ships **N plugins**` (180 → 181)
  2. `README.md` `M of the N plugins` (`requires.ravenclaude-core` — recompute)
  3. `README.md` any other exact `N plugins` total claims
  4. `AGENTS.md` `~N plugins` (gated to `len(plugins/)`)
  5. `AGENTS.md` `~180 plugins / 600+ agents` hedge — bump N only
  6. `.claude-plugin/marketplace.json` `metadata.description` domain-plugin integer (heal stale **144**)
  7. marketplace + `plugin.json` **2 agents / 4 skills / 4 commands / 1 hook** claims
  8. `docs/architecture.md` `Active plugins (N)` + new Status row
  9. `docs/plugin-candidates-2026-06-13.md` candidate #4 status
  10. Generated surfaces only if already dirty — else PR states “no regen required”
- [ ] Phase 8 / 8b either skipped (owner decline) or one-file each with the unverified markers intact
- [ ] Implementation landed on branch `forge/graph-engineering` in the named worktree — **not** on `main`
- [ ] **One PR** `forge/graph-engineering` → `main`, title `feat/graph-engineering-v0.1.0`

---

## Risk matrix

G4a (critic) and G5 (red-team) **were not run** — depth=`quick`. Residual risks below are unred-teamed. Treat high-impact rows as implementer watch-items, not as a substitute for those gates.

| ID | Risk | Likelihood | Impact | Mitigation in this plan |
|---|---|---|---|---|
| R1 | Team Lead under-routes pure GraphRAG asks (no third agent) | M | M | Command + CLAUDE.md routing + modeler description keywords + scenario trigger phrases that include “GraphRAG”; promote `graphrag-engineer` only with post-ship evidence |
| R2 | Name collision with GraphQL / Microsoft Graph API | M | H | Keywords omit those tokens; first-line NOT; seams table; `.graphql` linter no-op |
| R3 | Marketplace count regen miss (180→181, stale 144) fails CI | H (without this DoD) | H | Phase 9 copies the gated regen list; `check-marketplace-claims.py` is acceptance |
| R4 | Hook uses PCRE or shells to missing `python3` | M | H | Hook is grep-only POSIX ERE; `check-grep-ere-pcre.py` in Phases 7 and 10 |
| R5 | Linter false positives on prose / markdown | M | L | Extension filters; advisory default; fixtures document edges; `--strict` opt-in |
| R6 | C35/C36 files land without owner accept, or get expanded into multi-file work | M | M | Phases 8/8b are skippable one-file; flagged unverified; no hook/CI depends on them |
| R7 | GraphRAG agent-equivalent re-decides memory III.a | M | H | Hard hand-off sentences in knowledge + both agents + construct skill; no third agent to “own the paradigm” |
| R8 | Reciprocal neighbor CLAUDE edits explode scope | M | H | Explicit ban in Phase 9 / out-of-scope |
| R9 | Fabric Graph marked GA without `[verify-at-use]` | M | M | Phase 3 mandate; C11 vs C25 living-with step |
| R10 | Kuzu taught as current embed | L | M | House opinion #10; C28 in languages file |
| R11 | Unbounded `*` examples leak into knowledge | M | M | Linter-first; Phase 3 acceptance runs linter on knowledge |
| R12 | **No critic pass** on phase coupling / inventory drift | — | M | G4a not run. Phase 9 waits on finished inventory; counts are acceptance-tested |
| R13 | **No red-team** of hook bypass, snippet injection, or “just connect Neo4j” helpfulness | — | M | G5 not run. Advisory contract + “no live store” repeated; hook cannot start a server |
| R14 | Description-budget creep if a later session adds the third agent in the same PR | L | M | This plan freezes 2 agents; recount + new description required before any 0.2.0 add |

---

## Engineering pre-commitments (for G7)

| Knob | Value |
|---|---|
| Plugin version | `0.1.0` |
| Marketplace `metadata.version` | `0.92.0` → `0.93.0` |
| Branch | `forge/graph-engineering` |
| Catalog | new `plugins[]` entry `graph-engineering` |
| Landing | **pr** |
| Size | **large** |
| Privacy | clean |

---

## Out of scope (so implementers do not “helpfully” add them)

- Connecting to the consumer’s Neo4j / Fabric / Spanner / Neptune
- A second plugin for RavenClaude internals
- A third agent `graphrag-engineer` in this PR
- Absorbing `memory-engineering` paradigm III.a selection
- GraphQL or Microsoft Graph API craft
- Computational / autodiff / ML graphs
- Teaching Kuzu as the current default embed
- Reciprocal version-bumping edits to neighbor plugins
- Full Cypher/GQL/SPARQL parser
- SPARQL 1.2 / RDF 1.2 dating (not fetched)
- Fabric Graph **GA** as an unmarked fact
- New `.repo-layout.json` globs
- Promoting Phase 8 / 8b into multi-file construction

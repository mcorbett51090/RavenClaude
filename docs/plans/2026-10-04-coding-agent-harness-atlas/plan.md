# Plan · coding-agent-harness-atlas

G6 synthesis of a FORGE `standard` run. Author: the G6 synthesizer, who wrote none of the inputs. Date: 2026-10-04.
Run dir: `/home/user/RavenClaude/.ravenclaude/runs/forge/coding-agent-harness-atlas/` · worktree `/home/user/RavenClaude/.claude/worktrees/forge-coding-agent-harness-atlas` · branch `forge/coding-agent-harness-atlas` (scope.md header).
Inputs, in order of authority: `owner-decisions.md`; `tiebreaks.md` (including "Revisions after the red-team") with `tiebreak-T1.md`, `tiebreak-T2.md`, `tiebreak-T3.md`; `red-team.md` and `critic-brief.md`; `scope.md` (with Amendment 1) and `claims-table.md` (36 rows); `plan-A.md`, `plan-B.md` and `gap-delta.md`; `decisions.md`.

**Blockers: none.** All ten red-team modes have a home phase. The three High modes are mitigated in named phases: RT1 (sanitizer truncation) in P1 and P3; RT2 (scout Write channel) in P1, P4 and every scout wave (P5, P7, P8); RT3 (no durable state) in P0 and every phase close. See "Red-team mitigations".

**How to read this plan.** "row N" is row N of `claims-table.md` (1 to 36). "[obs]" is what a tool returned, with its source; "[inf]" is a conclusion; "[unverified — …]" marks a claim nobody has checked. A fact used here that is not in the 36 rows is labelled "claim to add" and listed with its source under "Open claims and what settles them". Every number marked "estimate" carries its basis and a range. "A" and "B" are `plan-A.md` and `plan-B.md`; E1, L2, T3 and so on are the rulings in `tiebreaks.md`.

## Goal and non-goals

**Goal (scope.md).** A harness atlas: self-contained HTML pages under `docs/research/2026-10-04-coding-agent-harness-atlas/`, generated from one data set, documenting with dated primary-source evidence every aspect and feature of the harness around each coding agent (the loop, tools, context and memory, permissions and sandbox, hooks, extension points, modes, sessions, execution surfaces, model selection, reasoning effort, cost, limits and observability, enterprise controls) in one shared taxonomy, so the agents are comparable. It answers the owner's two questions:

- **Can we enhance it?** For each harness, where the extension points RavenClaude can use or improve are, and what the ceiling is.
- **Which levers, when?** For each harness and task shape, where model, reasoning effort, mode and parallelism physically live (flag, settings key, env var, frontmatter field, per-dispatch parameter), and which are not exposed at all.

**Success signal (scope.md line 38).** A maintainer opens `index.html` and, for any facet of any harness, sees what the feature is, its exact configuration or lever surface, the dated primary-source quote with a link, and the RavenClaude enhancement implication. They can choose model, effort and mode for a stated task shape in each harness. No load-bearing cell is uncited; every unverifiable cell is explicitly marked.

**Roster: eight surfaces (the atlas columns).**

| column | product | basis |
|---|---|---|
| `claude-code` | Claude Code | row 1 |
| `codex-cli` | OpenAI Codex CLI | row 1 |
| `copilot-cli` | GitHub Copilot CLI | row 1; split from the VS Code surface because the repo already treats them as distinct (row 12) |
| `copilot-vscode` | Copilot agent and chat in VS Code | row 1; its own docs corpus (row 30) |
| `cursor` | Cursor | row 1 |
| `gemini-cli` | Gemini CLI | row 1 |
| `grok-build` | Grok Build CLI | row 1 |
| `grok-bot` | Grok Bot | Amendment 1. A full entry: the fold rule needs both "same runtime" and "no distinct harness features", and the second is falsified (rows 20, 22, 26). Whether its loop is code-shared stays open as an F21 cell (row 24). Covered as a harness, weighted to its coding-relevant facets. |

Copilot is one product page carrying two columns.

**Output.** The atlas plus a ranked, evidence-linked backlog of RavenClaude updates (the enhancement register).

**Non-goals.**
- **The RavenClaude updates themselves are a follow-on, not built here.** Every register entry ships `status: proposed`. The one exception is the routing-matrix extension the owner chose as a precursor of the lever guide (Decision 2); it lands as its own reviewed PR (P6) and is not a backlog item.
- No benchmark, quality ranking, harness score or numeric confidence. Routing judgments are labelled judgment, not measured.
- No research into what the models themselves can do; no pricing beyond what a lever decision needs; no security audit of the agents (scope.md).
- No agent beyond the eight columns. Aider and Windsurf/Devin appear only as footnotes where the repo already tracks them.
- No write-back from the atlas into `plugins/*/knowledge/` or `host-support.json`; a disagreement becomes a `correct` register entry (A §1). The matrix PR is the only knowledge edit, and it is reviewed as its own PR.
- No committed vendor page copies (only URLs, hashes and short quotes); no page that fetches at view time; no unattended refresh routine (M5); no new numbered CI audit gate (A refusal 9; B non-goals).

## Owner decisions in force

The owner was asked T1 and T2 at G4b as multi-option questions and chose against both recommended defaults (`owner-decisions.md`). They override every expert default; the rest of each expert ruling still applies.

| decision | owner's answer | what it commits this plan to |
|---|---|---|
| Decision 1: comparison grain | Named rows on every facet (Plan A's grain), about 840 cells. That figure is A's own estimate and was not re-derived. | Every one of the 22 core facets gets frozen named rows, and every row has a cell in all 8 columns. The real row count is fixed by the P1 draft, and every verification budget is recomputed from it (P1, P4), never carried over from either plan. T1's other rulings stand: both scope-listed areas are core (managed and enterprise controls; usage, cost, limits and observability as one facet); version is core; an `unmapped` bucket U00 catches features that fit no row, and 3 or more U00 records across 2 or more columns become an owner Update item. Because `design_checkins: true`, the row list reaches the owner as Keep/Update/Deny at plan approval (facet list and drafting rule) and again in P2 as a file, before any cell is filled. |
| Decision 2: lever guide for Cursor, Gemini CLI and Grok Bot | Extend the routing files first, in a separate PR. | Sequence: a lever slice of the research first (P5); the routing-matrix extension as its own PR with its own acceptance tests and gates (P6), recommended as its own `/forge` run; the remaining atlas phases (P7 to P10) run in parallel with P6; only the lever-guide phase (P11) waits for the matrix PR, then points at matrix cells for all 8 columns. T2's basis rule, "no such lever" cells and model-keyed levels govern the new matrix rows. If the matrix PR has not merged when the atlas is otherwise ready, the lever guide ships lever locations plus "no recommendation — matrix rows pending" for the three columns and states that the success signal is met for 5 of 8: a flagged fallback, not the owner's preferred end state, with a trigger date recorded at approval and an owner veto. Open design question carried into P6: whether Grok Bot (a general-purpose agent with a vendor-managed model) belongs in coding task-class rankings at all. |

Two posture facts shape every owner gate [obs, grep of `.ravenclaude/comfort-posture.yaml` this session]: line 7 sets `design_checkins: true`, so structural decisions surface to the owner, and line 108 sets `decision_review: binding`, so a single binary yes/no question is auto-decided by the tribunal. Every owner gate in this plan is therefore a question with three or more options (W3, RT10).

## Design

### Facet taxonomy and frozen rows

**Facets (T1 §2).** B's 21 core facets F01 to F21, plus one core facet merged from B's optional O2 and O3 using A's F18 definition, labelled F22 here: 22 core facets. O1 stays optional (`not-researched` allowed). U00 is the unmapped bucket.

| id | facet | what it covers (B §2; F22 from A §2.1) |
|---|---|---|
| F01 | Loop and built-in tools | the agent loop shape and the native tool inventory |
| F02 | Context and memory | window management, compaction, persistent or auto memory |
| F03 | Instruction files | auto-loaded files, import syntax, precedence |
| F04 | Permission engine | allow/deny/ask rule syntax, scopes, precedence, prompt behaviour |
| F05 | Sandbox and network isolation | OS sandbox, container or VM isolation, network allow-lists |
| F06 | Hooks and lifecycle events | event catalog, handler types, contract, blocking semantics |
| F07 | Managed and enterprise controls | org policy, admin settings, data retention, identity |
| F08 | Skills | format, discovery path, invocation, resource loading |
| F09 | Subagents and custom agents | definition format, tool scoping, per-agent model and effort, nesting |
| F10 | Slash and custom commands | built-in and user-defined commands, arguments |
| F11 | Plugins and marketplaces | packaging, source types, versioning, trust |
| F12 | MCP | transports, config location, scoping, auth |
| F13 | Sessions, checkpoints, rewind | resume, fork, undo, transcript location |
| F14 | Worktrees and parallel execution | worktree isolation, concurrency caps, parallel-agent controls |
| F15 | Background, scheduled and cloud-delegated work | background tasks, routines, cloud agents, delegation |
| F16 | Surfaces and programmatic control | CLI, IDE, desktop, web, cloud, headless, SDK, CI |
| F17 | Model selection and routing | picker, flag, setting, auto-router, vendor-managed |
| F18 | Reasoning effort and thinking | controls, allowed values, per-agent override |
| F19 | Modes and autonomy levels | named modes, how each is entered, what each changes |
| F20 | Version, release channel, update path | version at retrieval, cadence, channel, changelog |
| F21 | Relationship to host platform | what the surface runs on and what it shares with siblings |
| F22 | Usage, cost, limits and observability | usage and cost visibility, budgets and caps, rate limits, telemetry and logs |
| O1 | Editor and LSP integration (optional) | diagnostics, selection context, IDE protocol |
| U00 | Unmapped | documented features that fit no frozen row |

**Frozen rows (Decision 1).** Each core facet carries 4 to 8 named sub-feature rows, drafted in P1 by remapping A §2.1's checklists onto these facet boundaries. Two lists are already specified in A §2.1 and are used as drafted. F04: approval-modes, per-tool-rules, path-scoping, command-scoping, trust-prompt, bypass-mode, auto-review, config-scope-precedence. F21: host-platform, shared-account-billing, shared-execution-infrastructure, shared-model-selection, shared-agent-runtime, delegates-to, distinct-harness-features. Parallelism rows sit in F14 (B §2 assembles the parallelism lever across F09, F14 and F15).

**Size (estimate).** A estimated about 105 rows and 840 cells for its own 19 core facets (A §2.1). Over 22 facets at 4 to 8 rows the honest range is about 100 to 130 rows and 800 to 1,040 cells [estimate; basis: A §2.1's per-facet row counts, centred on A's total]. The P1 draft fixes the number and P4 recomputes every budget from it.

**Comparison rule (T1 §2).** A comparison claim ("X has it, Y does not") is made only on a named row; free text never carries a comparison verdict.

**U00 (T1).** A documented feature that fits no row is stored with its quote as a U00 record, listed on the sources pages, and never counted toward "complete". A cluster of 3 or more U00 records across 2 or more columns becomes an owner Update item at the P2 freeze and again after the P8 join, before render.

**F21 for every column (A §2.1).** "Grok Bot runs on Cursor's platform" (row 21) and "not the Cloud Agents setup" (row 22) live as evidence, and the same question is asked of every other column. Grok Bot's `shared-agent-runtime` is `undocumented`, with a sweep record, unless a source states it (row 24).

### Evidence standard

**Tiers.**

| tier | what it is | can make a cell verified? |
|---|---|---|
| E1 docs | raw bytes of a vendor docs page fetched this run, stored with SHA-256 | yes |
| E2 changelog | raw bytes of vendor changelog or release notes; the only tier that supports "since version X" | yes |
| E3 source | vendor source at a commit SHA (raw single file, or an `add_repo` clone) | yes |
| E4 executed | output of a harness binary in this container, version-pinned (A probe: only `claude` is installed here; claim to add) | yes |
| R repo | a statement in this repo: git blob SHA, path:line and quote, script-checked against `git show` (M4; critic SP4) | for register repo claims only, never a vendor cell |
| S secondary | blogs, forums, vendor condensed manuals | no; discovery only |
| U training knowledge | model memory | no; rendered with `[unverified — training knowledge]` |
| banned | any WebFetch or model-summarized text | never evidence (row 15) |

**What "verified" means.** A cell is `verified` only when it carries an E1 to E4 record whose quote a script found in the stored raw bytes, after whitespace normalization and normalization of neutralized tokens on both sides (M4, RT1), and, where T3 samples it, a semantic verifier marked it `supports`. A model saying a quote is present never counts.

**Evidence record.** id; surface; tier; canonical URL after redirects plus `url_effective`; retrieval date; HTTP status; bytes; SHA-256 of the raw page; product version and its source; locator (heading and raw line range); a verbatim quote of at most 300 characters (A §3.2); the 2 raw lines on either side (RT3, so a quote stays checkable after the mirror is gone); `quote_verified`, set only by script; any neutralizer flags touching the span. Install and update command lines are stored as described spans (page, line range, hash of the raw bytes) and never verbatim (W2); a fixture test proves it (P1).

**Cell state (M1).** Support state is one of `supported`, `partial`, `not-exposed`, `not-applicable`, `undocumented`, `not-researched`, with an orthogonal verification field, `verified` or `unverified`.

| state | evidence obligation (enforced by the validator) |
|---|---|
| `supported` | at least one verified E1 to E4 record |
| `partial` | as `supported`, plus a `limitation` field quoting the restriction (A §2.2) |
| `not-exposed` | a vendor statement that no control exists, or a behaviour record plus the vendor's complete reference page for that surface as a positive control (T3; A §2.2) |
| `not-applicable` | a positive quote (T3) |
| `undocumented` | a script sweep over the full raw mirror, excluded pages included, that also hits a positive-control term known to be on that vendor's pages, plus a haiku review of the hits (T3). A worker's search of its own assigned pages never licenses it. |
| `not-researched` | O1 only |

A cell whose quote fails ships `unverified` with a derived marker and per-surface counts on `index.html`; it is never relabelled `undocumented` (T3; scope.md line 38), and a core `unverified` count above zero is reported, not hidden. Where verifier and extractor disagree, an opus adjudicator rules (B W7); an unresolved disagreement stays `unverified` with a marker naming both readings.

**Markers are derived (B §3).** The generator prints `[unverified: <reason>; settles by <probe>]` wherever a load-bearing assertion lacks a verified record; authors cannot omit it, and the validator fails on an unverified assertion with no "settles by" probe.

**Versions and staleness.** Every cell carries its retrieval date and the product version current that day (row 14). Version sources (M3): npm `latest` for the four npm-published CLIs, vendor changelogs otherwise; the Cursor changelog is parsed as HTML or the version is recorded as unavailable (A probe: it returns an HTML body; claim to add); Grok Bot is a hosted service and reads "service; docs as of <date>". A cell says "introduced in X" only on an E2 record. Pages carry only dates; an optional inline script computes age (fresh up to 30 days, ageing up to 90, stale beyond) and the date shows without it.

### Corpus enumeration and source access

**Enumeration (E1; row 3 is falsified by row 29).** Each column is enumerated as the vendor index, plus the vendor sitemap where it lists docs pages, plus a one-hop link closure from fetched pages restricted to that vendor's docs-host allow-list (the critic's SP1 shape, adopted by E1). Link closure never leaves the allow-list.

| column | index | sitemap | link closure and scoping | sources |
|---|---|---|---|---|
| claude-code | `llms.txt`, 231 links | 219 docs URLs, one sitemap-only | 0 of 71 sampled links missing from the index | row 2; row 29; critic probe 6 (claim to add) |
| codex-cli | redirects (308) to the `learn.chatgpt.com` index | none (404) | 1 of 21 missing; A's deterministic ChatGPT-versus-Codex scoping rule plus a residual triage list (E1); the aggregate `codex-manual.md` is excluded from extraction and kept as a cross-check (RT7) | row 2; row 29; critic probes 6 and 7 (claim to add) |
| copilot-cli | docs.github.com Page List API | none (404) | harness filter on the path list, then link closure | row 2; critic probe 6 |
| copilot-vscode | `llms.txt`, 52 URLs under agents, chat or copilot | lists 16 core agent pages the index omits | 10 of 47 sampled links missing | row 30; row 29; critic probe 5 (claim to add) |
| cursor | bare URL list | marketing only, no docs | 133 of 156 sampled links missing, all API reference; distinct pages counted at build start (E1; D17) | row 2; row 29; critic probe 6 |
| gemini-cli | one 959,932 B `llms.txt` | none (404) | split into 97 pages on the page-title lines only, never on the 264 H1 lines; the npm docs bundle is an optional cross-check, not re-run (E1) | row 32 |
| grok-build | xAI `llms.txt`, Grok Build section | matches the index | link closure; 2 of 15 sampled xAI links missing | row 2; row 29; critic probe 6 |
| grok-bot | xAI `llms.txt`, 21 Grok Bot pages | matches the index | Cursor mirror, 13 docs plus 18 help URLs; one canonical host per page pair, xAI (RT7; A §3.1) | rows 19, 21 |

**Fetch rules (one fetch script, run only by the Team Lead).** https only; the docs-host allow-list is checked on every redirect hop; a fixed maximum redirect count; no private, loopback or link-local targets (critic SP3(c)); per-host concurrency of at most 3 with jittered backoff and up to 3 retries (B §4.4); a body under 200 B, or an HTML body for a `.md` target, is rejected, and size is compared with Content-Length (B §4.4); a cross-host landing is flagged and excluded unless adopted by name (B; D16). Outcomes follow the repo's cause taxonomy: 2xx fetched; 404 or 410 negative for that URL only; 429, 5xx, timeout or reset indeterminate (class I), retried, never treated as absent; a 200 whose first heading reads "Page not found" negative. The fetch is never wrapped in command substitution, which the repo's destructive-command guard denies (decisions.md). All fetches finish inside one 24-hour freeze window (A §5.2).

**Raw and neutralized copies (RT1; supersedes M2).** The repo sanitizer `sanitize-webfetch-body.py` deletes text: run over the raw sub-agents page it cut 1,412 lines to 945 (row 36), and over 784 pages it altered 15 and removed about 920K characters, including 47% of Codex's managed-configuration page (red-team RT1 [obs]). Scouts therefore never read its output. Instead:
- raw bytes are stored immutable and hashed;
- an atlas-local neutralizer rewrites each matched tag token in place (for example the leading `<` becomes `‹`) and never deletes a character; flagged raw line numbers go to a per-page flags file;
- lines addressed to agents or shaped like instructions are flagged, not stripped (critic SP3(a): VS Code's approvals page opens with such a line);
- the neutralized line count must equal the raw line count for every page, or the fetch phase fails;
- coverage counting, every absence sweep and the changelog addition scan run on raw lines;
- fixture tests prove that raw lines 1045 and 1064 of the sub-agents page and the Codex managed-configuration "System requirements" section reach scout chunks (P3);
- the sanitizer's strip-to-end-of-file patterns (5 to 9) become an `en-route-defect` register entry.

**Chunking and coverage (E2; row 31).** Pages are chunked at H2 or 12 KB; Gemini splits on its 97 page-title lines (row 32). A whole-file check proves every raw line of every in-scope page landed in a chunk a scout read. No worker relies on a default Read of a page over 2,000 lines (`hooks.md` is 3,880 lines and `settings-reference.md` 6,410; row 31).

**Dedupe before chunking (RT7).** Aggregate pages (`codex-manual.md`, and full-corpus concatenations such as `llms-full.txt`) are excluded from extraction and kept as cross-checks. Per surface, a page at least 90% line-contained in another is marked secondary; the red-team measured 130 of 176 Codex pages at 90% or more containment in the manual and 5 at 0%, so the manual is not a clean superset (claim to add). Evidence cites the canonical per-page URL, and T3 error rates are computed on deduped cells.

**Source trees (rows 4, 5).** GitHub refuses `openai/codex` and `google-gemini/gemini-cli` with a body naming `add_repo`, while single raw files return 200 (row 4). Whether `add_repo` is the route is open (row 5); P0 settles it by trying it, if the owner approves. If it attaches: a shallow clone pinned to a commit SHA, used to answer at most 12 named questions per repo (B §5), never crawled. If it is refused or declined: docs only, and source-dependent cells carry `[unverified — source tree not readable]`.

**Trust boundary (W1, extended by RT2 and RT6).**
- Untrusted vendor text is read only by `scout` (haiku; tools Read, Grep, Glob, Write [obs, this session]). Every Bash-bearing worker reads only neutralized, size-capped snippet files marked as data and returns text or a one-line receipt, never raw pages.
- Quote checking is a script against raw bytes. Network access exists only in the fetch script the Team Lead runs.
- Workers are named roster types: never `general-purpose`, which holds dispatch tools (Gate 289), and never `architect`, which carries WebFetch, WebSearch and Bash.
- The scout's Write tool is closed as a channel (RT2). `_tools/` is committed and its hash pinned before the first scout dispatch. Before every Team Lead script run, `git -C <worktree> diff --exit-code -- <atlas>/_tools` must exit 0 and `git status --porcelain -- <atlas>/_tools` must be empty, or the run aborts. Each scout brief names exactly one output file. After every wave the Team Lead compares before-and-after snapshots of `git status --porcelain` for both the worktree and the primary checkout (which is already dirty, RT4), plus the run-dir listing, against the assigned outputs; any extra path fails the wave and quarantines its records. Scout output is JSON read with `json.load` and schema-validated; no tool imports, evaluates or executes data.
- Judges without Write (`code-reviewer`) return their text in their final message and the Team Lead writes it with the Write tool. No agent writes a prose file by heredoc, tee or printf: the tribunal denied 5 of 8 such heredoc bodies and 0 of 4 Write-tool payloads (red-team RT6 [obs]; claim to add).

### Research fan-out and cost

**Workers and the tools each really has** [obs: `grep ^tools:` over the core agent files, this session; claim to add].

| worker | tier | tools | job | reads | writes |
|---|---|---|---|---|---|
| `scout` | haiku | Read, Grep, Glob, Write | extraction, absence-hit review, residual triage, the P0 gap diff | neutralized chunk files | exactly one assigned path |
| `documentarian` | sonnet | Read, Edit, Write, Grep, Glob and the shell tool | cell assembly, register drafts | verified records and capped snippets | its surface's cells file |
| `tester-qa` | sonnet | Read, Edit, Write, Grep, Glob and the shell tool | semantic verification (T3) | assertion, quote and capped context, as a data file | its verdict file |
| `code-reviewer` | opus | Read, Grep, Glob and the shell tool; no Write | lever-cell checks, adjudication, top-15 ranking, tool review | the same capped inputs | nothing; returns text (RT6) |
| `backend-coder` | sonnet | Read, Edit, Write, Grep, Glob and the shell tool | `_tools/` code | this plan and synthetic fixtures, no vendor text | `_tools/`, before the pin |

Only the Team Lead dispatches; no worker holds `Agent`. Workers run at inherited effort: this session's Agent tool shows no effort parameter (row 7, open, settled by the P0 probe), and the run log records that.

**Shape (X1).** Read-once: page batches of about 80 KB of chunk files; each scout tags records for all facets at once against the frozen row list (at most 3 facet ids plus a row id per record), at most 60 records per batch, with an explicit `no-facts` marker for a page with nothing relevant (B §4.2). A brief is a file path plus one fixed instruction file; a receipt is one line (RT9). B measured that routing by keyword to a single facet still selects 22 to 54% of the Claude corpus (B §4.1), which is why reading per facet would re-read the corpus several times.

**Concurrency.** At most 16 dispatches in flight, keeping 4 of the default 20 slots for retries and verifiers (X1; row 6). A 21st concurrent spawn fails with an error that tells the model not to retry (critic probe 1, same vendor page; claim to add), so 20 is never targeted. The Agent tool is the default. The Workflow tool runs only on the owner's explicit opt-in; it caps a run at 1,000 agents (row 28, vendor-confirmed) and defaults to 16 concurrent agents, fewer on a CPU-limited container (critic probe 3; this container reports 4 CPUs; claim to add), so no wall-clock plan assumes 16.

**Per-dispatch CLAUDE.md load (X1; row 35).** Custom subagents load the CLAUDE.md hierarchy, including AGENTS.md, unless the definition sets `omitClaudeMd: true`, and `scout` does not set it. The two files total 70,401 B, about 17.6K tokens at bytes/4 (critic probe 20; the ratio is `[unverified]`), paid on the first turn of every dispatch. The vendor page contradicts itself on whether the field fully suppresses the load (line 857 against lines 1064 and 1069; row 35), so P4 measures it.

**Pilot (P4; B P2).** Three batches: the largest-chunk Claude batch, a Gemini page batch and the Grok Build corpus. Two arms: `scout` as shipped, and a worktree-local, uncommitted copy of `scout`'s definition that differs only by `omitClaudeMd: true`, deleted after the pilot. Whether the dispatching session loads such a definition is `[unverified]`, so a single-dispatch positive control runs first; if the copy cannot be loaded, the second arm is recorded as not measurable. Measured: processed input tokens per dispatch, record yield, quote-pass rate (gate: at least 95%), malformed rate, wall-clock per wave, and Team Lead tokens per dispatch extrapolated to 50 dispatches (RT9).

**Estimate.** Every figure below is an estimate. It is recomputed in P3 from measured corpus bytes and in P4 from measured tokens, before any extraction wave, and the owner is re-asked if the recomputed total exceeds 1.5 times the approved figure.

| line | calls | input tokens | basis |
|---|---|---|---|
| in-scope corpus | none | 3.3M to 4.3M of text | B measured 17 to 19 MB in scope (B §4.1); minus the 2.9 MB Codex aggregate (RT7); plus sitemap-only and link-closure pages; about 13 to 17 MB at bytes/4 |
| extraction (`scout`) | 180 to 235 | 7M to 24M | about 80 KB batches plus about 10% retries and splits; 40K to 100K processed per call = about 20K text + about 17.6K CLAUDE.md load + brief, times 1 to 2.5 for multi-turn re-sends (unmeasured) |
| semantic verification (`tester-qa`) | 12 to 38 | 0.7M to 3.8M | 460 to 730 checked cells out of 800 to 1,040 (T3 shares; lever rows assumed to be 20 to 30 of the total), about 40 cells per call, doubled as an escalation reserve |
| lever checks and adjudication (`code-reviewer`) | 4 to 22 | 0.5M to 1.5M | 160 to 240 lever cells at about 40 per call, plus at most 16 adjudications (B W7) |
| cell assembly (`documentarian`) | 24 to 48 | 1M to 2.9M | 8 surfaces times 3 to 6 facet groups |
| absence-hit review, pilot, relationship probe, P0 gap diff | 11 to 21 | 0.6M to 1M | B §4.3's small lines plus the P0 probe |
| register | 10 | 0.3M to 0.5M | B W9 |
| tools and tool review | 4 to 6 | 0.2M to 0.5M | B W10 |
| **total** | **about 245 to 380** | **about 10M to 35M input, 1M to 2M output** | mostly haiku; a single Workflow run would fit under the 1,000-agent cap (row 28) |

Not included: the matrix PR's own `/forge` run, priced by that run. Plan A's 185-call figure is not used, because its 1.3 times overlap factor is not derivable from the corpus sizes (X1; critic recompute).

**Run state (RT9).** A disk ledger, `units.jsonl` (unit id, brief path, input hash, status, receipt path, attempt), is the only run state. After any compaction or handoff the Team Lead re-derives the next step from it, never from conversation memory. A unit whose output exists with a matching input hash is skipped on re-run (A §4.5). At every phase close the ledger and the derived records are committed to a `_work/` folder on the forge branch and pushed (RT3); `_work/` is deleted in the landing commit, so the squash merge never carries it. Resume after a container reclaim: check out the pushed branch, rebuild the ledger from `_work/`, re-fetch, and mark `drifted` any cell whose page hash changed (RT3). Whether to quiet the advisory cause-triage, cause-remediation or context-handoff hooks during the build is the owner's call; the agent does not change them (RT9).

### Verification design

T3, scaled to the real cell count fixed in P1.

- **Script quote check** on 100% of evidence records, against raw bytes.
- **Semantic check** by `tester-qa` (sonnet, one tier above the haiku extractor) on 100% of cells that are not `supported`, 100% of lever cells, and a 30% sample of `supported` cells stratified by surface and facet. A surface whose error rate exceeds 5% escalates to 100% of its `supported` cells. Error rates are computed on deduped cells (RT7).
- **Lever cells** are also checked by `code-reviewer` (opus), which adjudicates disagreements between verifier and extractor.
- **Calibration, scaled per wave.** Every verification wave (one per surface, plus the lever-slice waves) carries 5 planted wrong cells, at least 2 of them overreach (a real quote that supports only a narrower claim). The verifier must catch at least 4 of 5, or that wave is re-verified. Across about 800 to 1,040 cells this is about 40 to 50 plants rather than one 5-cell sample (T3 §2, applied per wave).
- **Recall (T3, extended by RT8).** Seeds per (surface, facet class): extension-point seeds from the repo's docs-verified host facts (`host-support.json` components: hooks, skills, slash commands, agents, monitors, instruction files); at least one lever seed per surface (model, effort, mode, permissions or sandbox) from the vendor-verified rows 6, 20, 26 and 31; Grok Build and Grok Bot seeds from rows 19 to 26, because `host-support.json` has no Grok host. The VS Code sitemap-only pages serve as planted-missing pages. The pass bar is at least 80% per surface and per class, checked by script; any (surface, class) pair below it fails.
- **Rubric.** Verifiers check five named failure modes: overreach, cross-surface misattribution, dropped negations, platform or plan scoping, and preview or deprecated features (T3; critic SP7).
- **Judge inputs.** Quotes arrive as files marked as data; a judge's shell use is limited to reading the run dir; judges without Write return text (T3; RT6).

**Budget** [estimate]: 460 to 730 semantic cell checks and 160 to 240 lever cells (see the estimate table), recomputed in P4 from the frozen row count.

**T3's own change test.** The pilot also gives haiku `scout` the 5 planted cells. If it catches at least 4 of 5 overreach plants, the owner is told that T3's sonnet tier could be dropped (T3 §5); the plan never drops it silently.

### Data model and rendering

**Committed under `docs/research/2026-10-04-coding-agent-harness-atlas/`** (all match `docs/**`; rows 8 and 18):

```
README.md                          what this is, how to render, how to re-verify
index.html  matrix.html  levers.html  register.html  method.html
harness/<product>.html   x7        Copilot carries both of its columns
sources/<surface>.html   x8        evidence, manifest summary, coverage table, U00 records
data/snapshot.json                 freeze window, per-column versions and sources, upstream file hashes
data/facets.json                   22 facets, frozen rows, U00, triage rules
data/surfaces.json                 8 columns; Grok Bot parent_product null
data/cells/<surface>.json   x8     one writer per file
data/evidence/<surface>.json x8
data/levers.json                   keyed by (surface, lever, model)
data/register.json
_tools/*.py   _tools/schemas/*.schema.json
```

Per-surface data files follow A §6.2, avoiding the eight parallel writers on one file that gap-delta D20 flagged in B's layout. The raw mirror, neutralized copies, flags, chunks and records stay in the gitignored run dir; `_work/` snapshots live only on the forge branch (RT3).

**Lever records (T2; A §7.2; B §7).** One record per (surface, lever, model). `location_kind` takes one value from a closed set: `cli_flag`, `settings_key`, `config_file_key`, `env_var`, `frontmatter_field`, `per_dispatch_param`, `slash_command`, `ui_picker`, `api_param`, `vendor_managed`, `not_applicable`, `undocumented`. Fields: literal, scope, precedence (only if a source states it), values, default, evidence ids. Where a source says the available levels depend on the model (the sub-agents page, line 316, the source of rows 6 and 27), the record carries `values_by_model{}` and `model_conditional: true` citing that line; any model whose levels were not read is `[unverified]`.

**Rendering.** `render.py` generates every page from `data/` only, and each page opens with a generated-file comment. Determinism (A §6.1; B §6): ordering taken from `facets.json` and `surfaces.json`; no timestamps beyond snapshot dates; no absolute paths; LF, UTF-8, a trailing newline; byte-identical output across two runs and across `TZ`, `LC_ALL` and `PYTHONHASHSEED` variation; `render.py --check` re-renders in memory and diffs against disk. All text passes through `html.escape`; CSS and JS are inline and the pages make no external requests; a CSP meta allows inline script by hash `[unverified — A: meta-CSP honours script hashes; checked in a headless browser in P10 if one is available, otherwise recorded as not run]`; every link is https on a vendor-host allow-list or a relative link whose target is existence-checked (I3). Styling follows `templates/DESIGN.md` (row 11) with system font fallbacks and no remote fonts. Status renders as glyph, word and `aria-label`; tables carry captions and header scopes; wide tables scroll inside their own region at 360 px; reduced motion is honoured (A §6.5; B §6).

**Size ceilings (A §6.6).** Each page at most 1.5 MB, all HTML at most 12 MB, quotes at most 300 characters, each data file at most 2 MB. B's tighter per-page budgets were sized for about 168 cells and do not survive the owner's grain.

**Vendor model ids in data (L3; row 33).** Gate 134 scans tracked `.json` files and its `/docs/` carve-out does not cover top-level `docs/` (row 33). The atlas PR therefore registers the atlas data directory in `CARVE_SUBSTR` in `scripts/check-model-ids.py` (line 53 [obs, grep this session]), the gate's own stated route for a deliberate carve-out. Fallback if the owner declines: vendor model ids stay out of `.json` and appear only in `.html`, which the gate does not govern (row 33).

### HTML pages

B's smaller page set (I1); no drafted prose except the lever guide and the register rationale.

| page | contents |
|---|---|
| `index.html` | snapshot banner with per-column versions and sources; roster; how to read (states, tiers, markers); per-surface counts of verified, unverified and undocumented cells; success-signal status (8 of 8, or the flagged 5 of 8); the top 10 register entries; known gaps |
| `matrix.html` | rows grouped by facet with one anchor per facet, which is the generated facet comparison view; each cell shows glyph, word, a value of at most 60 characters and an evidence count, and links to its harness page; filters are progressive enhancement, and the full table renders without JS |
| `harness/<product>.html` | one section per facet, F21 first; per row: status, value, lever locations, quoted evidence with citation, and the RavenClaude implication linking repo files and register ids |
| `levers.html` | the lever guide (P11) |
| `register.html` | the register, sortable, linked to cells, evidence and repo files |
| `sources/<surface>.html` | every evidence record; manifest summary; redirect list; the per-column coverage table (sitemap-only pages fetched, link-closure pages fetched, residual counts; critic SP1); dedupe decisions; neutralizer flags; U00 records |
| `method.html` | states, tiers, verification rates, planted-error and recall results, the Grok Bot fold ruling and its evidence, and known gaps including the premise-gate holes |
| `README.md` | at most 40 lines; its links are checked |

### Lever guide and the routing-matrix precursor

**Levers (B §7).** Four classes drive the guide: model; reasoning effort or thinking; mode (permission, autonomy, plan); parallelism (subagents, worktrees, background work, concurrency caps). Context controls appear in an "other levers" row. Usage and cost visibility (F22) is the instrument the guide points at, not a lever.

**Two row kinds per column, all 8 columns (T2).**
- *Lever-location rows.* For each lever class, every location (literal in monospace, scope, values, default, citation), each a pointer to a verified `levers.json` cell. These are facts.
- *Task-shape rows.* For the matrix's five task classes (coding-implementation, coding-debugging-design, research-deep, writing-documentation, data-analysis), a pointer to `agent-routing-matrix.json` `task_classes.<class>.recommendations[i]`, rendered with the matrix's own agent, tier, rank and basis, attributed to the matrix and SHA-pinned in `snapshot.json` (A §7.3). Beside each pointer, the concrete lever settings that realise that tier in that harness, taken from `levers.json`.

The atlas never builds a second matrix (A refusal 8). Under Decision 2, Cursor, Gemini CLI and Grok Bot get matrix cells through the precursor PR, so every column renders pointers.

**"No such lever" is a cell (T2).** `vendor_managed` needs a positive vendor quote; `not_applicable` needs a quote showing the lever class does not exist. Grok Bot's model lever is `vendor_managed`, citing row 20 ("There is no customer-facing model picker"); its task-shape rows then name mode and parallelism only, and the model slot reads "not a user choice: vendor-managed". An absence that was not swept is `undocumented`, never `vendor_managed`.

**Model-keyed levels (T2).** A task-shape row that names an effort level names the model it is valid for. Cursor lists per-model pages and a router page (row 16) that nobody has read yet; their level sets stay `[unverified]` until P5 reads them.

**Labels.** Every recommendation carries a basis from the matrix vocabulary (`framework-rule`, `capability-fact`, `cost-heuristic`, `editorial-judgment`), plus `vendor-guidance` if the precursor PR puts it in the enum (RT5). A visible "judgment, not measured" badge sits on everything except `capability-fact`. There is no numeric confidence anywhere (the matrix's own rule). The page heading reads "Lever guide — documented controls, editorial routing"; the "when" of a lever is stated as labelled judgment, and questions that need measurement become `probe` register entries (critic premise attack; SP6).

**Render and check gate (T2).** The validator fails if a task-shape row has neither a matrix pointer nor, in the contingency only, the "no recommendation — matrix rows pending" label; if any row names a lever value with no verified cell; or if any numeric confidence field appears.

**The precursor PR is a schema change (RT5; owner-decisions).** Observed: the matrix maps five agent ids onto four substrate hosts, and the tier map has hosts claude, codex, copilot and grok, with no cursor or gemini host. The Gate 255 checker, `check-agent-routing-matrix.py` in the core plugin's scripts directory (651 lines), rejects an agent id outside a closed set and a host outside the tier map, requires every `model_ref` to resolve by strict key membership, and requires contiguous ranks 1..N in each grounded cell (owner-decisions; red-team RT5 [obs]: `AGENT_IDS` at line 54, `HOST_KEYS` at line 55, `model_ref` required at lines 156 to 181, the tier must exist under its host at lines 304 to 320; claim to add). The precursor's own plan must:
- list every closed set it changes: `AGENT_IDS`, `HOST_KEYS`, `BASIS_VALUES` (gain `vendor-guidance` or map it explicitly), the schema enums, the `HOSTS` lists in the tier-map loader and its JavaScript twin, the route-task self-test, and the must-fail fixtures;
- settle Grok Bot first: either `model_ref` becomes optional under `model_control: vendor_managed`, or Grok Bot stays out of the matrix with a documented "not rankable" note; never an invented tier;
- write new host model entries in display-name form, as the copilot host already does, or update `model-catalog.json` in the same PR, and run Gate 134 from that PR's worktree (an entry using raw vendor ids was flagged UNKNOWN; red-team RT5 [obs]);
- regression-check the tier map's other runtime consumers (the tribunal decision engine, `rc-deep-research`, the dispatch evaluator, the prompt-optimizer scripts and the Grok delegate; red-team RT5 [obs]);
- make substrate edits with the Edit tool only, never by shell mode changes, in-place stream edits or moves on substrate paths (red-team RT5: Edit-tool edits are allowed; the shell forms are denied by the self-disable rule);
- be self-contained: it cannot cite files that exist only on the unmerged forge branch, so P5's verified lever facts travel into it as dated knowledge-file entries, the basis pattern the matrix already uses (owner-decisions);
- bump `ravenclaude-core` and run the version sync and Copilot-package regeneration (see "Landing").

It is recommended as its own `/forge` run, started as soon as P5 is verified (RT5; owner-decisions records this as a recommendation, not a requirement). The trigger date for the 5-of-8 fallback is recorded at approval.

### Enhancement register

**Types (I2).** A's six (`extend`, `improve`, `correct`, `new-lane`, `reconcile`, `en-route-defect`) plus B's `probe`: an entry that rests on an unverified cell becomes a `probe`, never a feature.

**Fields.** id; title; type; surfaces, facets and rows; cells (each verified, or the entry is a `probe`); `repo_files`, each existence-checked or flagged new; `repo_claim` for `correct` and `reconcile` entries (R tier: blob SHA, path:line and quote, script-checked; M4); proposal (at most 120 words); ceiling (linked to a cell and its quote); value, reach, effort and risk (ordinal 1 to 3); basis (observation or inference, and what would falsify it); score; rank; status `proposed`.

**Score.** `score = (value × reach × E) / effort`, where E (0 to 3) is mechanical (B §8): 3 if every supporting cell is verified and its evidence is at most 30 days old at snapshot; 2 if verified but older; 1 if only some supporting cells are verified; 0 if none are. Ties go to `correct` before `extend`, then to more verified evidence, then to id. One-way-door entries rank after two-way ones. `code-reviewer` (opus) reorders the top 15 with a rationale labelled `editorial-judgment`, returned as text for the Team Lead to write.

**Seeds** (each still needs its own evidence record):
- routing-coverage residuals after the matrix PR; no Grok host in `host-support.json` (A §8.3);
- the two `docs/concepts.md` Grok Bot statements and the two `grok-bot-*` plugins (row 25);
- stale review stamps (row 12);
- 10 agents declare `effort: normal`, which is outside the documented set, and 6 declare `high`, which is inside it (row 27); A's seed 4a ("sixteen agents outside the set") was false and is corrected here;
- en-route defects: `premise-gate.py` matches "settled" as a substring (row 17); it counts `falsified` as settled and its blast floor cannot see html, json or md work (row 34); numbered headings parse as phantom phases (decisions.md); the sanitizer's strip-to-end-of-file patterns (row 36); Gate 134's `/docs/` carve-out misses top-level `docs/` (row 33); `forge-receipt.py` drops model, subagent type and effort; `forge-worktree.sh checkpoint` refuses in this repo; the handoff fill defect; cause-triage subject attribution (each in decisions.md); the FORGE effort statement against this Agent tool (row 7); editing a scratch copy of a claims table reads as self-disable (critic probe 19);
- follow-ons the rulings did not adopt here: a shipped-artifact evidence tier (static tarball and binary inspection; critic); a `render.py --check` CI gate (A); a scheduled drift routine (M5); a dedicated extraction agent with `omitClaudeMd: true` (critic SP8).

## Phases

**Order.** P0, then P1, then P2 and P3 in parallel, then P4, then P5; after P5, P6 runs in parallel with P7 to P10; P11 needs both; P12 lands. Details in "Dependency DAG".

**Phase-close checks (every phase).** (a) Print the worktree's toplevel and current branch, and fail on anything other than the forge worktree and `forge/coding-agent-harness-atlas`; an empty branch name is a failure (RT4). (b) Commit derived artifacts on the forge branch with explicit pathspecs, because `forge-worktree.sh checkpoint` refuses in this repo (decisions.md). (c) Push the forge branch, never `main`, and compare the remote head with the local head (RT3). (d) Update the ledger. (e) For any phase that dispatched scouts, run the post-wave diff check of both checkouts and the run dir (RT2). The forge branch is also pushed before every owner question (RT3), and every owner question uses its shape from "Decisions and approvals needed from the owner" (RT10).

### P0 — Approval, durability anchor and pre-flight probes
depends_on_claims: [4, 5, 6, 7, 12, 13]
reversibility: two-way-door

Begins at the FORGE exit. The Team Lead does it, with one haiku `scout` for the row 13 probe.

work:
1. Durability before any question (RT3). Copy `plan.md`, `claims-table.md` and `decisions.md` from the run dir into `docs/plans/2026-10-04-coding-agent-harness-atlas/` in the forge worktree, commit them with explicit pathspecs, and push the forge branch. Then ask the approval questions in their stated shapes, record each answer verbatim in `decisions.md`, copy that file again and push again.
2. Worktree pin (RT4). From the worktree, print the toplevel and the current branch; both must name the forge worktree and branch, and an empty branch name is a failure, not a pass.
3. Row 5 probe, only if the owner approved `add_repo`. Call it read-only for `google-gemini/gemini-cli`, then for `openai/codex`, with no pre-check fetch (the tool's own instruction). Record each result verbatim and rewrite row 5 as settled or falsified. On refusal or decline the corpus runs docs only.
4. Row 7 probe. Read the vendor sub-agents page (row 6) and the vendor tool reference for a per-invocation effort parameter, and compare them with this session's Agent tool schema. Rewrite row 7 with what was observed, stating whether any absence is product-wide or only this build's schema.
5. Row 13 probe. One `scout` reads the repo's per-host customization notes and the host-support map and returns, per host, which of the 22 core facets each note covers, with file and line. Rewrite row 13 with the counts.
6. Every rewritten settling cell starts with "settled", "falsified" or "owner-gated", and never uses the word the premise gate misreads (row 17).

acceptance:
- Rows 5, 7 and 13 each carry a this-session source and a settling cell in that vocabulary.
- `git show origin/forge/coding-agent-harness-atlas:docs/plans/2026-10-04-coding-agent-harness-atlas/plan.md` is byte-identical to the local copy.
- Every approval answer is in `decisions.md` with the option label chosen.
- The worktree pin output is saved in the run dir and names the forge branch.

pre-build gate: the owner approved the plan, and the forge worktree exists on `forge/coding-agent-harness-atlas` (scope.md header).

### P1 — Tools, schemas, neutralizer, ledger and the row-list draft
depends_on_claims: [8, 11, 15, 18, 31, 32, 33, 36]
reversibility: two-way-door

work:
- `backend-coder` (sonnet) writes `_tools/` against synthetic fixtures only, never live vendor text: the canonical JSON writer; the fetch script (rules in Design); the atlas-local neutralizer; the chunker; the raw-line coverage counter; the quote verifier; the absence-sweep script; the containment and dedupe check; the validator; a renderer skeleton that renders every page type from fixtures; `reverify.py` covering quote presence and addition drift (M5); the ledger helper. Every tool asserts at start that its toplevel is the worktree and its branch is the forge branch (RT4).
- The Team Lead drafts the frozen row list (`data/facets.json` plus a readable row-list file for P2, with U00) and the JSON schemas for cell, evidence, lever, register and snapshot records.
- `code-reviewer` (opus) reviews `_tools/` before the pin and returns findings as text; the Team Lead fixes or records each. `_tools/` is then committed and its tree hash recorded in the ledger (RT2). This moves the tool review early (gap-delta §2 point 6).
- Initialise `units.jsonl`.

acceptance:
- Neutralizer parity: on fixtures reproducing both truncation shapes (a tag name mentioned in backticks; a closing code fence followed by a paragraph starting "System"), the neutralized line count equals the raw line count, and a mutant that deletes the flagged span fails the parity test.
- Validator teeth: a non-zero exit on each planted-bad fixture (an uncited core cell; a quote absent from the raw bytes; an unknown status; a `not-exposed` cell with neither a vendor statement nor a reference-page record; a non-https or off-allow-list URL; a `<script>` string in a quote, which must render escaped; a page over budget (A P1); a task-shape row with neither a pointer nor the pending label; a lever value with no verified cell; a numeric confidence field (T2); an install line stored verbatim (W2); an evidence record without its hash or context lines (RT3)), and a zero exit on the good fixture.
- Determinism: renderer output on fixtures is byte-identical across two runs, `TZ=UTC` and `TZ=America/New_York`, `LC_ALL=C` and `en_US.UTF-8`, and two `PYTHONHASHSEED` values.
- Fetch self-test: a redirect to a host off the allow-list is refused; a private or link-local target is refused; a 15-byte body is rejected; a cross-host landing is flagged; a connection reset is retried; a 503 is classified indeterminate.
- Each tool exits non-zero when started from the primary checkout.
- `ruff check` is clean on `_tools/`; the CI layout matcher accepts every new path (row 18); `_tools/schemas/*.schema.json` passes the pinned prettier (critic C21).
- After the pin, `git -C <worktree> diff --exit-code -- <atlas>/_tools` exits 0 and the hash is in the ledger.
- Row list: every row id is unique and every core facet has 4 to 8 rows; total row and cell counts are recorded and the Design budgets recomputed from them.

pre-build gate: P0 complete, with rows 5, 7 and 13 rewritten and every approval answer recorded.

### P2 — Frozen-row check-in (Keep/Update/Deny), before any cell is filled
depends_on_claims: []
reversibility: two-way-door

work: Push the forge branch, then present the row-list file, with the measured row count, the recomputed cell count and verification budget, and the U00 rule, as one question: "Keep as drafted / I edited the file / Deny, rethink" (RT10; Decision 1). "I edited the file" re-runs the validator on the owner's edits; "Deny, rethink" returns to the P1 row draft. Record the answer and freeze the row ids; from then on, rows change only through U00 Update items. Runs in parallel with P3, whose fetching costs no model tokens.

acceptance:
- `decisions.md` records the option chosen and the frozen row count.
- The hash of the frozen facets file is in the ledger.
- The ledger shows no extraction unit dispatched before the answer.

pre-build gate: P1 acceptance passed and the forge branch is pushed.

### P3 — Corpus enumeration, fetch, neutralize, chunk and version snapshot (eight per-surface pipelines)
depends_on_claims: [2, 4, 15, 16, 19, 21, 29, 30, 31, 32, 36]
reversibility: two-way-door

work: For each column independently: enumerate (index, sitemap and one-hop allow-listed link closure; E1); apply the Codex scoping rule and write its residual triage list; split Gemini into its 97 pages; count Cursor's distinct pages; pair each Grok Bot xAI page with its Cursor mirror and record xAI as canonical; fetch under the Design's rules; store raw, neutralized and flags; exclude aggregates and mark pages at least 90% contained in another as secondary; chunk; run raw-line coverage; take the version snapshot; save each index and sitemap URL set as the addition-drift baseline (M5). Then recompute the cost estimate from measured bytes. Small corpora (Grok Build, Gemini, Grok Bot) finish first and do not wait for Claude or Codex.

acceptance:
- Every enumerated URL has a manifest row with status, bytes and SHA-256; no 200 row has an empty body; every non-200 is classified, indeterminate rows were retried, and the remainder are listed.
- Provenance: a script traces every fetched URL to an index, a sitemap or a link on a fetched page; nothing is constructed.
- Positive control for the enumeration reshape: the 16 VS Code sitemap-only core agent pages, `agents/run/approvals` among them, are fetched (critic probe 5).
- The neutralized line count equals the raw line count for 100% of pages (RT1).
- Raw lines 1045 and 1064 of the sub-agents page and the Codex managed-configuration "System requirements" section appear in chunk files (RT1).
- Every raw line of every in-scope page lies in a chunk (E2).
- `codex-manual.md` is excluded from extraction, secondary pages are marked, and every Grok Bot pair has one canonical URL (RT7).
- Gemini yields 97 page units (row 32).
- The per-column coverage table exists for the sources pages.
- The recomputed estimate is in `decisions.md`; if it exceeds 1.5 times the approved figure, the owner answered the re-ask before P4.

pre-build gate: `_tools/` is pinned (P1).

### P4 — Pilot and cost gate
depends_on_claims: [6, 27, 28, 35]
reversibility: two-way-door

work: Run the pilot described under "Research fan-out and cost": three batches, two arms, and the single-dispatch positive control for the `omitClaudeMd` copy. Also give the 5 planted cells to haiku `scout` (T3's change test); probe whether a PreToolUse hook can tell a subagent's Write from the parent's `[unverified]`, and if it can, put a run-scoped deny on subagent writes outside the records folder (RT2); measure wall-clock per wave (critic R14). Recompute the estimate and the verification budget from the frozen row count and the measured tokens.

acceptance:
- Quote-pass rate is at least 95% per pilot corpus, with failures dropped and never repaired; below that, the brief is tightened or that corpus moves to sonnet before P5 (B P2.2).
- Processed input tokens per dispatch are recorded per arm, or the second arm is recorded as not loadable.
- The recomputed total is within the approved envelope, or the owner answered "Proceed at 1.5× / Stop and report / Re-scope".
- Post-wave diffs are clean, and no scout wrote outside its assigned path.
- The `omitClaudeMd` copy is deleted and absent from `git status`.

pre-build gate: P2 answered; P3 complete for claude-code, gemini-cli and grok-build.

### P5 — Lever slice: model, effort, modes, parallelism and relationship rows for all eight columns
depends_on_claims: [6, 16, 19, 20, 21, 22, 23, 24, 26, 27]
reversibility: two-way-door

work:
- The first read-once waves take the batches that carry lever or relationship content (path and heading rules plus the lever term set) for all 8 columns. Records for every facet are kept from these batches, so their pages are never re-read (X1).
- Cursor's per-model pages and router page are read, and levels are keyed by model (row 16; T2).
- "No such lever" cells get their positive quotes; every lever row with no record goes to the raw-mirror absence sweep with its positive control (T3).
- Every lever cell is verified: script check, `tester-qa` at 100%, `code-reviewer` at 100%, and 5 planted cells per wave.
- Grok Bot relationship re-confirmation (G1): term sweeps over the Grok Bot, Cursor Cloud Agents and Grok Build pages, each with a positive-control term; `tester-qa` reads the hits; `code-reviewer` applies the fold rule (both conditions; silence is never evidence; row 26 cited); `shared-agent-runtime` stays `undocumented` unless a source states it.
- Re-verification of the five covered hosts (owner-decisions, sequencing step 1): each lever fact the matrix's cited knowledge files state for claude-code, codex-cli, copilot-cli, copilot-chat and grok-build-cli is checked against the atlas lever cells and marked holds, changed or contradicted; every contradiction becomes a `correct` register seed and a P6 input.
- The lever evidence pack for P6 (verified cell ids, quotes, URLs, dates) is committed on the forge branch.

acceptance:
- Every lever row and F21 row has a cell in all 8 columns with a support state and a verification value.
- 100% of lever cells were checked by both `tester-qa` and `code-reviewer`; at least 4 of 5 plants were caught in every wave.
- Every `vendor_managed` and `not_applicable` lever cell carries a positive quote; Grok Bot's model lever cites row 20.
- Every model-conditional lever has `values_by_model`, with `[unverified]` on unread models.
- The fold ruling is in `decisions.md`, citing the verified cells it compared.
- The five-host re-verification table exists.

pre-build gate: P4 passed, or the owner chose to proceed; P3 complete for all eight columns.

### P6 — Routing-matrix precursor PR (separate PR; recommended as its own FORGE run)
depends_on_claims: [6, 12, 16, 20, 33]
reversibility: one-way-door
rollback: revert the squash commit through a revert PR merged after checks, with a further `ravenclaude-core` version bump; the lever guide then renders the flagged 5-of-8 fallback (P11), which is the kill switch.

work: On its own branch cut from `origin/main`, in its own worktree, never the forge branch. Settle Grok Bot's representation before any code (an owner question if the matrix run defers it). Then make the changes listed under "The precursor PR is a schema change": closed sets, schema, tier-map hosts, agent ids, ranks recomputed contiguously per grounded cell, display-name model entries or a same-PR catalog update, dated knowledge-file entries carrying P5's verified lever facts, and Edit-tool-only substrate edits. Run every gate from that PR's worktree. Bump `ravenclaude-core`, sync the catalog, regenerate the Copilot package and write the CHANGELOG entry. Run `/code-review` before opening the PR. Open the PR, watch checks, and merge with a plain squash once every check passes and the owner has answered the merge question.

acceptance:
- The Gate 255 checker exits 0 from the PR's worktree, and a planted recommendation naming an unknown host, or a tier absent from the tier map, makes it exit non-zero.
- Every grounded cell has contiguous ranks 1..N, and no numeric confidence field exists.
- Gate 134 run from the PR's worktree exits 0 with the new tier-map entries (RT4, RT5).
- Gate 154 is green and the route-task self-test prints N/N.
- Every new recommendation cites a verified P5 lever cell through a dated knowledge-file entry inside the PR.
- Grok Bot has a schema-valid `vendor_managed` entry or a documented not-rankable note, and no invented tier.
- `python3 scripts/sync-plugin-versions.py --check` and the Copilot-package freshness check pass; prettier, ruff and `scripts/audit-gates.sh` pass from the PR's worktree.
- CI is green on the head SHA; the PR merged with a plain squash; after merge the checker passes on `main`.

pre-build gate: P5 acceptance passed; the owner chose the run shape and recorded the contingency trigger date.

### P7 — Remaining extraction waves (eight per-surface pipelines, parallel with P6)
depends_on_claims: [6, 15, 28, 31, 36]
reversibility: two-way-door

work: The rest of the read-once pass, at most 16 in flight, scheduled per surface so that each surface's P8 can start as soon as its own batches finish. One output path per scout, brief files, one-line receipts, ledger updates and post-wave diffs. The quote verifier runs per batch; a batch with more than 10% dropped quotes is re-run once and then split. Record text shaped like an instruction is flagged.

acceptance:
- Every in-scope chunk belongs to a batch marked done, or its page carries an explicit `no-facts` marker.
- Drop rates are reported per surface and per batch.
- Calls used stay within 1.2 times the P4 recomputed extraction figure; beyond that, the Team Lead stops and re-plans.
- Post-wave diffs are clean in every wave.

pre-build gate: P5 complete and the P4 estimate approved.

### P8 — Cell assembly, absence sweeps, verification and recall (per surface, then one join)
depends_on_claims: [6, 15, 23, 27, 29]
reversibility: two-way-door

work: Per surface, as soon as its P7 batches finish: `documentarian` assembles that surface's cells file; every core cell that is not `supported` gets the raw-mirror absence sweep and a haiku review of the hits; `tester-qa` runs the semantic checks with 5 planted cells; `code-reviewer` adjudicates disagreements; U00 records are kept. Then the cross-surface join: recall is scored per surface and per class; each U00 cluster goes to the owner in its stated shape; per-surface counts are published.

acceptance:
- 100% of cells carry a support state and a verification value, and every obligation in the Evidence standard table is met.
- Every `undocumented` cell has a sweep report with a positive-control hit on the same vendor's pages.
- At least 4 of 5 plants were caught in every surface wave; error rates were computed on deduped cells; surfaces above 5% were escalated to 100%.
- Recall is at least 80% per surface and per class (RT8), and the VS Code planted-missing pages produced records.
- The core `unverified` count per surface is published.
- Every U00 cluster was answered.

pre-build gate: that surface's P7 batches are complete and the P5 lever cells are verified.

### P9 — Enhancement register
depends_on_claims: [12, 17, 25, 27, 33, 34, 36]
reversibility: two-way-door

work: A cell-level gap diff against the host-support map, the per-host customization notes, the routing matrix and tier map (as merged by P6, if it has merged) and the `grok-bot-*` plugins. `documentarian` drafts entries per column; every `repo_claim` is script-checked against `git show <blob>:<path>`; scores are computed; `code-reviewer` reorders the top 15 and returns text; the Team Lead writes all register text with the Write tool (RT6). The seeds listed in Design are included.

acceptance:
- Every entry cites at least one cell, and any entry with an unverified supporting cell is a `probe`.
- Every `repo_claim` passes the script check, and every repo path exists or is flagged new.
- Scores recompute identically on a second run; E is derived, never typed.
- Top-15 rationales are labelled `editorial-judgment`.
- The run log shows no register file written through a shell redirect.

pre-build gate: the P8 join is complete.

### P10 — Render, validate and review (every page except the final lever guide)
depends_on_claims: [8, 9, 11, 18, 33]
reversibility: two-way-door

work: Render; run the full validator and the determinism, size, link, anchor, URL allow-list, escaping (planted `<script>`), README link, CSP and accessibility checks, using a headless browser if one exists and otherwise recording "not run"; run the success-signal probe on 30 seeded random (surface, facet, row) triples (A P8); run Gate 134, prettier, ruff and the layout matcher from the worktree.

acceptance:
- Every check passes and `render.py --check` exits 0.
- All 30 probe triples show a status, a value or lever location, a dated quote with a link or the explicit marker, and an implication.
- Gate 134 exits 0 from the worktree, with the carve-out or with vendor ids kept out of JSON.

pre-build gate: P8 and P9 complete.

### P11 — Lever guide (the only phase that waits on the matrix PR)
depends_on_claims: [6, 12, 16, 20, 27]
reversibility: two-way-door

work: Render `levers.html`: lever-location rows for all 8 columns from `levers.json`, and task-shape rows as SHA-pinned pointers to the merged matrix for all 8 columns. If the trigger date passed with the matrix PR unmerged and the owner did not veto the fallback, the three columns show lever locations plus "no recommendation — matrix rows pending", and `index.html` states that the success signal is met for 5 of 8. Re-render `index.html`.

acceptance:
- The T2 render and check gate passes; every pointer resolves to an existing matrix cell at the pinned SHA.
- No numeric confidence appears, and every lever value resolves to a verified cell.
- The pending label is present if and only if the matrix PR is unmerged at render time.
- `render.py --check` exits 0.

pre-build gate: P6 merged, or the trigger date passed without an owner veto; P10 complete.

### P12 — Landing: one atlas PR
depends_on_claims: [8, 9, 10, 18, 33]
reversibility: one-way-door
rollback: revert the squash commit through a revert PR merged after checks; the `.prettierignore`, `.gitattributes` and `CARVE_SUBSTR` lines revert with it, and nothing under `plugins/` changes, so no consumer's plugin update is affected.

work: Run the drift check (quote presence, addition drift against the P3 baselines, and the changelog scan on raw lines; M5) and re-extract or mark every drifted cell. Delete `_work/`. Make the configuration changes listed under "Landing". Commit with explicit pathspecs; run the pre-push checks from the worktree; open the PR (probe `gh` first, otherwise the GitHub MCP tool loaded through ToolSearch); watch checks; merge with a plain squash once every check passes and the owner has answered the merge question; validate on `main`; offer a private Artifact of `index.html` in one line.

acceptance:
- The drift report is attached: zero drifted cells, or each drifted cell re-verified or marked.
- Every local gate exits 0 from the worktree, with its output and the toplevel it ran in quoted.
- A CI run exists for the head SHA and is green.
- After merge, the validator and `render.py --check` pass on `main`.
- The PR body lists the top 10 register entries, the snapshot date, the Grok Bot ruling and the lever-guide status (8 of 8, or the flagged 5 of 8).

pre-build gate: P10 and P11 complete, and the owner answered the merge question.

## Dependency DAG

```
P0 ──> P1 ──┬──> P2  frozen-row check-in (owner) ──────────────┐
            └──> P3  fetch: 8 per-surface pipelines ───────────┤
                                                               v
                                         P4  pilot and cost gate
                                                               v
                                         P5  lever slice, all 8 columns
                          ┌────────────────────────────────────┴───────────────┐
                          v                                                    v
   P6  matrix PR (own branch; own /forge run recommended)        P7 ──> P8  per surface:
                          │                                       claude-code, codex-cli,
                          │                                       copilot-cli, copilot-vscode,
                          │                                       cursor, gemini-cli,
                          │                                       grok-build, grok-bot
                          │                                                    v
                          │                                       JOIN (all 8 surfaces)
                          │                                                    v
                          │                                       P9 register ──> P10 render
                          v                                                    │
                         P11 lever guide <─────────────────────────────────────┘
                          v
                         P12 land the atlas PR
```

**What blocks what.**

| phase | blocked by | why |
|---|---|---|
| P1 | P0 | approvals and the row 5, 7, 13 probes come first |
| P2 | P1 | the row list must exist |
| P3 | P1 | needs the pinned fetch, neutralizer and chunker; not the row freeze, because fetching costs no model tokens |
| P4 | P2; P3 for three pilot corpora | the pilot extracts against frozen rows |
| P5 | P4; P3 for all 8 columns | lever pages of every column are needed |
| P6 | P5 | the matrix rows need verified lever cells |
| P7 | P5 | the lever waves go first; P7 does not wait for P6 |
| P8 (per surface) | that surface's P7 batches | per-surface pipeline |
| P9 | the P8 join | the register compares across columns |
| P10 | P8, P9 | renders verified cells and the register |
| P11 | P6 merged, or the trigger date passed without a veto; P10 | the only phase waiting on the matrix PR (Decision 2) |
| P12 | P10, P11 | one PR, landed once |

**What parallelizes.** P2 with P3. The eight surface pipelines inside P3, P7 and P8: Grok Build (about 94 KB), Gemini and Grok Bot finish early while Claude and Codex continue (gap-delta §2). P6 with all of P7 to P10. Verification waves run as each surface finishes. The tool review runs inside P1 rather than at the end (gap-delta §2 point 6).

**Critical path.** P0, P1, P3, P4, P5, P7, P8, the join, P9, P10, P11, P12. If P6 takes longer than P7 to P10 it joins the critical path; the trigger date bounds that.

**One cross-surface join.** Plan A ran ten stage barriers, with whole-corpus waits between triage, extraction and verification (gap-delta §2). Here the only cross-surface steps are the owner-mandated lever slice (P5) and one join after P8, before the register, render and lever guide. The Grok Bot fold ruling gates nothing but that column's page generation (gap-delta §2 point 3).

## Pre-build gates that do not rely on the premise gate

**Why the plan needs its own gate.** `premise-gate.py` counts `falsified` and `partially-settled` as settled and matches the word "settled" as a substring (rows 17, 34). Its blast floor counts only code-file extensions and a few creation verbs, not html, json or md work (row 34), so it cannot vouch for this plan's heaviest phases (P3, P5, P7 to P11), and a falsified row stops it tripping at all. Both holes are register seeds.

**The manual check, run by the Team Lead before every phase.**
- Re-read every row the phase cites in the live `claims-table.md`.
- A row whose settling cell begins "falsified" voids the phase: stop, reshape, and record the reshape in `decisions.md` before starting.
- A row whose settling cell begins "open" must first be settled by its named probe.
- For a "partially-settled" row, confirm that its residual (below) does not bear on the phase.
- Confirm the phase's other unverified premises (table below) were probed as named.

**Falsified row 3** (the indexes cover the docs completely; falsified by row 29). No phase cites it. Enumeration rests on rows 29 to 32 and is reshaped to index plus sitemap plus link closure in P3 (E1), with the VS Code sitemap-only pages as the positive control in P3's acceptance tests.

**Partially-settled rows.** Row 10's residual (whether pinned-prettier normalization stays stable across prettier versions) is moot, because L2 chose the ignore entry; P12 relies only on its settled half, that a config edit lands through a PR. Row 24's residual (whether Grok Bot's loop is code-shared with Cursor's platform or Grok Build) is recorded as the F21 `shared-agent-runtime` cell, `undocumented` unless a source states it; the roster does not depend on it, and P5 re-checks it.

**Per phase.**

| phase | open rows it needs | settled by | other unverified premises it relies on | probe that settles them |
|---|---|---|---|---|
| P0 | 5, 7, 13 | P0's own probes (work items 3 to 5) | none | none |
| P1 | none | — | the neutralizer never deletes text (RT1) | parity fixtures with a deleting mutant, in P1 |
| P2 | none | — | none | none |
| P3 | none: the docs path does not depend on row 5's answer, and source trees are optional | — | index plus sitemap plus link closure closes the gap row 29 found | the VS Code sitemap-only positive control |
| P4 | none | — | the `omitClaudeMd` copy loads; a hook can tell a subagent Write from the parent's | single-dispatch control; hook probe |
| P5 | none | — | Cursor's per-model pages are unread (row 16) | read in P5 |
| P6 | none | — | Grok Bot is representable in the matrix | settled first, inside P6 or its own FORGE run |
| P7 | none | — | a 21st concurrent spawn fails rather than queues (claim to add) | never more than 16 in flight |
| P8 | none | — | recall seeds exist for every (surface, class) pair | seed build checked before verification starts |
| P9 | none | — | repo claims are current | R-tier script check |
| P10 | none | — | meta-CSP honours script hashes | headless check, or "not run" recorded |
| P11 | none | — | the matrix PR merges by the trigger date | the contingency branch |
| P12 | none | — | the docs have not changed since the freeze | the drift check |

**Rows 7 and 13 have outcome-independent consumers.** Workers run at inherited effort whatever row 7 turns out to say, and the register takes its gap content from P9's cell-level gap diff whatever row 13 turns out to say. So no build phase rests on either inference being true.

**What the premise gate itself will see.** Only P0 cites open rows (5, 7, 13). P0 is a probe phase that writes only markdown records, so by the gate's own rule it is under the blast floor, and the gate should not trip on it. That is the gate behaving as designed for a settling phase, not an assurance to rely on: the manual check above is what holds rows 5, 7 and 13. [obs, this session: the gate's own `run()` over `plan.md`, `plan-A.md` and `plan-B.md` returned exit 0 and no trips; its 65 unwired entries are phantom phases from the two source plans' numbered headings, and all 13 of this plan's phases are wired.] Re-run the gate at the final FORGE gate rather than assuming its result.

## Landing

- **One PR for the atlas (L2).** It carries the atlas directory; the plan copies under `docs/plans/2026-10-04-coding-agent-harness-atlas/`; a `.prettierignore` entry for the atlas's generated `*.html` and `data/**`, preferred over prettier normalization so the committed bytes do not depend on the prettier version (precedent at `.prettierignore` line 33 [obs] and row 9); a `.gitattributes` line pinning LF for the atlas directory; and the `CARVE_SUBSTR` entry for the atlas data directory in `scripts/check-model-ids.py` (L3; fallback: vendor ids out of JSON). Hand-authored `_tools/schemas/*.schema.json` files are formatted by the pinned prettier rather than ignored (critic C21). No `.repo-layout.json` change is needed (rows 8, 18; the red-team confirmed `.gitattributes`, `.prettierignore` and `docs/**` are allowed).
- **Commits.** Explicit pathspecs only, because the FORGE checkpoint script refuses in this repo (decisions.md).
- **Pre-push checks, from the worktree, each logging the toplevel it ran in** (RT4; the Stop-hook definition-of-done gate reads the session's cwd, not the worktree): `scripts/check-checkout-fresh.sh`, `python3 scripts/ci-preflight.py`, `scripts/dod-fast.sh`, the pinned prettier write then check, `ruff check .`, `scripts/audit-gates.sh`, the AGENTS.md layout snippet, and `python3 scripts/check-model-ids.py`.
- **Creating the PR.** Probe the routes first (`command -v gh`, `gh auth status`). If `gh` works, `gh pr create --base main --head forge/coding-agent-harness-atlas --body-file <file>`; otherwise the GitHub MCP `create_pull_request` tool, loaded through ToolSearch (CLAUDE.md, remote-environment PR mechanics).
- **Checks.** `gh pr checks <n> --watch --interval 15`, run in the background; confirm a run exists for the current head (`gh run list --branch forge/coding-agent-harness-atlas`) and re-trigger by `workflow_dispatch` if none does; if runs sit queued with no jobs, run `scripts/check-github-status.sh` (CLAUDE.md).
- **Merge.** Repo auto-merge is off by design, so `--auto` fails. Merge with a plain `gh pr merge <n> --squash`, only after every check reports pass and the owner has answered the merge question (CLAUDE.md, 2026-09-03 correction).
- **Version sync and Copilot package.** The atlas PR changes nothing under `plugins/`, so it bumps no version. If any `ravenclaude-core` file changes (the matrix PR, P6, does): bump `version` in `plugins/ravenclaude-core/.claude-plugin/plugin.json`, run `python3 scripts/sync-plugin-versions.py` (never hand-edit the catalog), then `python3 scripts/generate-copilot-plugin.py`, and update that plugin's CHANGELOG top entry (AGENTS.md, "Modifying an existing plugin").
- **Lever-guide contingency.** If P6 has not merged by the trigger date and the owner did not veto, the atlas lands with the flagged 5-of-8 lever guide (P11), and the PR body and `index.html` say so. A follow-up PR re-renders `levers.html` once the matrix merges; the pointers are SHA-pinned, so `render.py --check` catches the change. If the owner vetoed the fallback, the atlas PR waits for the matrix PR.

## Alternatives considered

| alternative | trade-off in one line | why the chosen route won |
|---|---|---|
| Two-level grain, about 500 cells (T1's default) | about 0.6 times the verification cost, but row-aligned comparison on only 7 facets | the owner chose named rows everywhere (Decision 1) |
| Labelled atlas-local rows for Cursor, Gemini CLI and Grok Bot (T2's default) | leaves the routing files alone, but creates a second, atlas-only source of routing judgment | the owner chose to extend the routing files first (Decision 2) |
| Index-only enumeration with a sampled audit (both plans) | cheapest, but misses real core pages (16 VS Code pages; row 29) | E1: index plus sitemap plus allow-listed link closure |
| Models read the repo sanitizer's copy (M2 as first ruled) | reuses existing code, but deletes text to the end of the file (row 36) | RT1: an atlas-local neutralizer that never deletes |
| Surface-by-facet-group units, about 185 calls (A) | fewer calls on paper, but the count is not derivable and overlapping reads repeat the corpus | X1: B's read-once design with a pilot |
| A separate `.prettierignore` PR, then docs straight to `main` (B) | a smaller first PR, but a code-bearing tree reaches `main` before the whole-tree gates run on it | L2: one PR |
| Same-tier haiku verification at A's 15% sample | cheaper, but extractor and verifier share a tier and blind spots | T3: sonnet and opus verification with a 30% stratified sample; the owner is told if the pilot shows haiku suffices |
| The matrix extension as a phase inside this run | one run, but a closed-set schema change across protected scripts inside an atlas build | RT5: its own FORGE run is recommended; the owner picks the shape |
| A shipped-artifact evidence tier (critic) | could reach undocumented levers, but no ruling adopted it | recorded as a register follow-on |

## Risk matrix

The critic's R1 to R14 and the red-team's RT1 to RT10, merged and deduplicated.

| risk | source ids | probability | impact | mitigation | phase |
|---|---|---|---|---|---|
| Missing vendor pages yield wrong `undocumented` cells | R1 | High (16 VS Code core pages observed missing) | High | index, sitemap and link closure; coverage table; VS Code positive control | P3 |
| The sanitizer deletes vendor text while coverage reads 100% | RT1 | Certain if the repo sanitizer were used (row 36) | High | neutralizer, parity test, raw-line coverage, sweeps and scans on raw lines | P1, P3 |
| Long pages silently truncated by default reads | R5 | High under A's design | High | H2 or 12 KB chunks; raw-line coverage | P1, P3 |
| Injection reaches a shell-, web- or Write-capable worker; the scout's Write used as an execution channel | R3, RT2 | Low to Medium (critic); Low (red-team) | High | W1 boundary; hash-pinned `_tools/`; one output path per scout; both-checkout diffs; JSON-only data | P1, P4, P5, P7, P8 |
| A container reclaim loses run state | RT3 | Medium [inf: CLAUDE.md records that these containers are reclaimed after inactivity] | High | push per phase and before every question; `_work/` snapshots; plan copies; resume procedure | P0 and every phase close |
| Gate 134 fails on vendor model ids in atlas JSON or the tier map | R2 | High if ids are quoted in `.json` (row 33) | High: a required check goes red | `CARVE_SUBSTR` or ids kept in HTML; display-name entries in the matrix PR | P6, P12 |
| Gates validate the wrong tree | RT4 | High when unpinned (reproduced by the red-team) | Medium | worktree assertions in every tool; gates run from the worktree with the toplevel logged | P1, P6, P10, P12 |
| Token overrun from the per-dispatch CLAUDE.md load and re-sends | R4 | High | Medium | explicit cost line; pilot measures both arms; re-ask above 1.5 times | P4 |
| A 21st concurrent spawn fails with a do-not-retry error | R8 | Medium | Low to Medium | at most 16 in flight | P5, P7 |
| An owner gate is auto-decided under `decision_review: binding` | R7, RT10 | Medium | Medium | every gate has 3 or more options; the row list goes as a file plus one 3-option question | P0, P2, P4, P6, P8, P12 |
| The precursor matrix PR stalls or cannot express Grok Bot | RT5 | Medium [inf] | High: lever guide at 5 of 8 | own FORGE run; Grok Bot settled first; trigger date; flagged contingency; owner veto | P6, P11 |
| The lever guide cannot answer "when" for some columns | R12 | High | High | Decision 2 brings matrix pointers for all 8 columns; "when" labelled as judgment; measurement questions become `probe` entries | P6, P9, P11 |
| Judge heredoc writes denied by the tribunal | RT6 | High if heredocs are used (5 of 8 denied) | Medium | judges return text; the Team Lead uses the Write tool | P1, P8, P9 |
| Aggregate pages double-count evidence and skew error rates | RT7 | Certain without dedupe (measured) | Medium | exclude aggregates; containment check; canonical URLs; error rates on deduped cells | P3, P8 |
| The recall control is blind to levers and both Grok columns | RT8 | Certain with host-support seeds alone | Medium | seeds per (surface, class); lever and Grok seeds; per-class pass bar | P8 |
| Team Lead context loses or duplicates units at about 840 cells | RT9 | Medium to High | Medium | disk ledger as the only run state; brief files; one-line receipts; measured in the pilot | P1, P4, P7 |
| False repo-side register claims ship | R6 | High (A's seed 4a was already false) | Medium | R-tier script check against `git show` | P9 |
| Install and update cells lost to tribunal denies on verbatim quotes | R9 | Medium to High | Medium | described spans; fixture test | P1, P5, P7 |
| The atlas goes stale by addition while quote checks say it holds | R10 | High (row 14) | Medium | addition-drift baseline and check; changelog scan on raw lines | P3, P12 |
| False assurance from a clean premise gate | R11 | High (it already happened at G3b) | Medium | the plan's own manual gate; both holes in the register | every phase |
| Effort cells wrong because levels depend on the model | R13 | Medium | Medium | `values_by_model`; unread models marked `[unverified]` | P5 |
| Workflow concurrency below 16 on a 4-CPU container | R14 | Medium | Low | wall-clock measured in the pilot | P4 |

## Tiebreak verdicts

| id | conflicts covered | verdict | lands in |
|---|---|---|---|
| Owner Decision 1 | T1's grain (D2, D7, SP7) | named rows on every core facet; T1's other rulings kept | Design (taxonomy); P1, P2, P8 |
| Owner Decision 2 | T2 (D1, C6, C13) | extend the routing files first in a separate PR; flagged 5-of-8 contingency with trigger date and veto | P5, P6, P11, Landing |
| T1 | D2, D7, SP7 | superseded on grain by Decision 1; both scope areas core, version core (F20), U00, and the Keep/Update/Deny check-in stand | P1, P2, P8 |
| T2 | D1, C6, C13 | superseded on what ships by Decision 2; the basis rule, "no such lever" cells and model-keyed levels govern the matrix rows; the render and check gate stands | P5, P6, P11 |
| T3 | D4, D5, D6, SP7, C10 | as ruled: absence licensing, sonnet and opus verification, 30% stratified sample with escalation, planted control, failed quote ships `unverified`, recall seeds; calibration scaled per wave | P5, P8 |
| E1 | C1, SP1, D8, D9, D16, D17, C15 | index plus sitemap plus allow-listed link closure; Gemini 97-page split (npm bundle an optional cross-check); Codex scoping rule; Cursor distinct pages; redirect and size checks | P3 |
| E2 | D3 | H2 or 12 KB chunks with a whole-file coverage check, on raw lines | P1, P3 |
| L1 | C2, SP2 | the plan's own pre-build gate; no numbered section headings | "Pre-build gates…"; every phase |
| L2 | D12, row 10, C21 | one PR with the `.prettierignore` entry and the `.gitattributes` pin; plain squash after checks; explicit pathspecs | P12 |
| L3 | C3, SP5 | `CARVE_SUBSTR` entry; fallback: vendor ids out of JSON | P12; P6 for tier-map entries |
| W1, extended by RT2 and RT6 | D13, C4, C8, SP3 | only `scout` reads vendor text; capped snippets for shell-bearing workers; named roster types; Write channel closed; judges return text and the Team Lead writes | P1, P4, P5, P7, P8, P9 |
| W2 | C9, SP10 | install and update lines stored as described spans | P1, P5, P7 |
| W3, extended by RT10 | C12 | every owner gate is a multi-option question with its exact shape listed | Decisions; P0, P2, P4, P6, P8, P12 |
| X1 | D14, C7, C11, D24, SP8 | read-once with a 95% quote-pass pilot; at most 16 in flight; CLAUDE.md load as a cost line measured with and without `omitClaudeMd`; 1,000-agent cap vendor-confirmed | P4, P5, P7 |
| X2 | D15, C20 | Keep/Update/Deny at approval and again in P2; cost approval up front | P0, P2 |
| M1 | D18 | six support states plus a verification field | P1 |
| M2 | D11, C18 | superseded by RT1: an atlas-local neutralizer that never deletes | P1, P3 |
| M3 | D10 | npm `latest` plus vendor changelogs; Cursor changelog parsed as HTML or recorded unavailable | P3 |
| M4 | D25, C5, SP4 | whitespace normalization; claim namespaces merged; a repo-observation tier | P1, P9 |
| M5 | C14, D22, SP9 | addition-drift check beside quote presence; no unattended routine | P3 (baseline), P12 |
| I1 | D20 | B's smaller page set; facet views are generated, with no drafted prose | P10 |
| I2 | D21 | A's types and `repo_claim` with B's evidence-strength term; `probe` entries | P9 |
| I3 | D23 | CSP, link allow-list, `html.escape`, planted `<script>` test, README link check | P1, P10 |
| G1 | D19, C17 | full entry; P5 re-confirmation citing row 26; controlled term sweeps; silence is never evidence | P5 |
| Revisions after the red-team | RT3 durability; RT4 worktree pins; RT5 precursor as a schema change; RT7 to RT10 adopted | as listed under "Red-team mitigations" | per that table |
| Record corrections | C16 (row 30), C19 (row 28), the Gate 134 probe (row 33) | the claims table was corrected; nothing to build | none |

Every D1 to D25, C1 to C21 and SP1 to SP10 id appears in the "conflicts covered" column; none is left dangling.

## Red-team mitigations

| RT | severity | concrete mitigation | phase |
|---|---|---|---|
| RT1 | High | Never feed scouts the repo sanitizer's output. An atlas-local neutralizer rewrites matched tag tokens in place and never deletes; flagged raw lines go to a flags file; raw and neutralized line counts must match or the fetch phase fails; coverage, absence sweeps and the changelog scan run on raw lines; the quote check normalizes neutralized tokens on both sides; real-page fixtures prove sub-agents lines 1045 and 1064 and the Codex "System requirements" section reach scout chunks; patterns 5 to 9 become an `en-route-defect` entry. | P1 (built and fixture-proven), P3 (applied to every page), P9 (defect entry) |
| RT2 | High | `_tools/` committed and hash-pinned before the first scout dispatch; before every Team Lead script run, the `_tools` diff must be empty and its status clean, else abort; one output path per scout brief; after every wave, before-and-after status snapshots of both the worktree and the primary checkout plus the run-dir listing are compared with the assigned outputs, and an extra path fails the wave and quarantines its records; scout output is schema-validated JSON and never executed; the pilot probes whether a hook can tell a subagent Write from the parent's and, if so, sets a run-scoped deny. | P1 (pin), P4 (probe), P5, P7, P8 (every wave) |
| RT3 | High | The forge branch is pushed after every phase and before every owner question; at approval, `plan.md`, `claims-table.md` and `decisions.md` are copied to `docs/plans/2026-10-04-coding-agent-harness-atlas/`; every evidence record carries the page SHA-256, the quote and 2 raw context lines; the ledger and records ride in `_work/` on the branch; resume rebuilds the ledger from the pushed branch, re-fetches and marks changed-hash cells `drifted`. | P0, every phase close, P12 |
| RT4 | Medium | Every tool asserts that its toplevel is the worktree and its branch is `forge/coding-agent-harness-atlas` (an empty branch fails); gate scripts run from the worktree with the toplevel logged; the pre-push checklist runs from the worktree, because the Stop-hook gate does not cover it. | P1, P6, P10, P12 |
| RT5 | Medium | The precursor is scoped as a schema change: every closed set listed; Grok Bot's representation settled first, never an invented tier; display-name model entries or a same-PR catalog update; Gate 134 run from that PR's worktree; Edit-tool-only substrate edits; recommended as its own FORGE run started when P5 is verified; the contingency trigger date recorded at approval. | P6, Decisions |
| RT6 | Medium | One route only: a worker or judge without Write returns its text and the Team Lead writes it with the Write tool; no agent writes prose files by heredoc, tee or printf. | P1, P8, P9 |
| RT7 | Medium | Aggregate pages are excluded from extraction and kept as cross-checks; a per-surface line-containment check marks secondary pages; one canonical host per Grok Bot pair; evidence cites canonical URLs; T3 error rates use deduped cells. | P3, P8 |
| RT8 | Medium | Recall seeds per (surface, facet class): extension seeds from `host-support.json`, at least one lever seed per surface from rows 6, 20, 26 and 31, Grok seeds from rows 19 to 26; the 80% bar applies per surface and per class, never pooled. | P8 |
| RT9 | Medium | `units.jsonl` is the only run state, re-read after any compaction or handoff; dispatch prompts are a few lines pointing at brief files and receipts are one line; the pilot measures Team Lead tokens per 50 dispatches; quieting advisory hooks is left to the owner. | P1, P4, P7 |
| RT10 | Medium | Every owner gate is listed with its exact question shape, 3 or more options and labels that are not yes/no; the frozen row list is presented as a file plus one 3-option question. | "Decisions and approvals…"; P0, P2, P4, P6, P8, P12 |

## Open claims and what settles them

**Open rows.**

| row | claim | settled by |
|---|---|---|
| 5 | the 403 is a per-session scope guard and `add_repo` is the route to the source trees | P0 work item 3: try `add_repo` read-only on both repos (if the owner approves); rewrite as settled or falsified |
| 7 | this session's Agent tool has no per-dispatch effort parameter | P0 work item 4: read the vendor sub-agents page and tool reference and compare with the schema |
| 13 | existing repo coverage does not span the full harness | P0 work item 5: a scout gap diff of the per-host notes against the 22 facets, with file and line |

**Falsified and partially-settled rows.** Row 3 is falsified (row 29) and cited by no phase; P3 is the reshape. Row 10's residual is moot under L2. Row 24's residual is the F21 `shared-agent-runtime` cell, re-checked in P5. Details under "Pre-build gates that do not rely on the premise gate".

**Unverified markers carried forward.**

| marker | settled by |
|---|---|
| row 35: the vendor page is internally inconsistent on whether `omitClaudeMd` suppresses the CLAUDE.md load | P4 measures processed tokens with and without it |
| row 16: Cursor's per-model pages and router page are listed but unread | P5 reads them |
| whether a worktree-local agent definition is loaded by the dispatching session | P4 single-dispatch positive control |
| whether a PreToolUse hook can tell a subagent's Write from the parent's (RT2) | P4 probe |
| whether Claude Code applies extra protection to a subagent's edits of `.claude/settings.json` (RT2) | not settled; mitigated by the both-checkout diffs in every wave |
| the bytes-per-token ratio of 4 used in every estimate | P4 measured tokens |
| whether meta-CSP honours script hashes (A) | P10 headless check, or "not run" recorded |
| whether vendor-published settings JSON schemas exist as completeness oracles (critic) | not used by this plan; noted only |

**Claims to add** (facts this plan uses that are not in the 36 rows; the recorder merges them; no id is assigned here).
- claim to add: the VS Code sitemap lists 16 core agent pages under `/docs/agents/` that its `llms.txt` omits, including `agents/run/approvals` (critic probe 5).
- claim to add: sitemaps exist for Claude (219 docs URLs, one sitemap-only), xAI (Grok Build 24 and Grok Bot 21, matching the index) and VS Code; Cursor's sitemap is marketing-only; `learn.chatgpt.com`, `geminicli.com` and `docs.github.com` return 404 (critic probe 6).
- claim to add: the Codex index at `developers.openai.com` answers 308 to `learn.chatgpt.com/docs/llms.txt` (critic probe 7; A proposed claim 102; B proposed claim 201).
- claim to add: npm `latest` versions for the four npm-published CLIs, and the Gemini CLI tarball bundles 95 docs pages (critic probe 11; A proposed claim 103).
- claim to add: `cursor.com/changelog.md` returns an HTML body (A proposed claim 107).
- claim to add: only `claude` resolves on PATH among the harness binaries in this container (A proposed claim 109).
- claim to add: the docs.x.ai Grok Build section lists 24 pages (A proposed claim 108; B proposed claim 213).
- claim to add: a 21st concurrent subagent spawn fails with an error telling the model not to retry (critic probe 1, sub-agents page line 1045).
- claim to add: the Workflow tool defaults to 16 concurrent agents, fewer on CPU-limited containers, and this container reports 4 CPUs (critic probe 3, workflows page line 365).
- claim to add: `CLAUDE.md` plus `AGENTS.md` total 70,401 B (critic probe 20).
- claim to add: the core agent tool grants as tabled under "Research fan-out and cost" (grep of agent frontmatter this session; critic probe 16).
- claim to add: posture line 7 is `design_checkins: true` and line 108 is `decision_review: binding` (grep this session; critic probe 18).
- claim to add: `CARVE_SUBSTR` is defined at line 53 of `scripts/check-model-ids.py` (grep this session).
- claim to add: the Codex aggregate manual is 2,885,197 characters and contains 130 of 176 Codex pages at 90% or more and 5 at 0% (red-team RT7).
- claim to add: the tribunal denied 5 of 8 heredoc-shaped register bodies and 0 of 4 Write-tool payloads (red-team RT6).
- claim to add: the tribunal allows Write and Edit payloads to atlas `_tools/` paths and both `.claude/settings.json` files (red-team RT2).
- claim to add: run from the primary checkout, Gate 134 exits 0 on a worktree-only probe that the worktree's own run fails (red-team RT4).
- claim to add: the routing-matrix checker's closed sets and requirements (`AGENT_IDS` line 54, `HOST_KEYS` line 55, `model_ref` lines 156 to 181, tier existence lines 304 to 320, `BASIS_VALUES` without `vendor-guidance`) and the tier map's other runtime consumers (red-team RT5).
- claim to add: the decision-review hook auto-routes a single, non-multiselect question whose two labels are each yes/no-shaped (red-team RT10, hook lines 89 to 109).

## Decisions and approvals needed from the owner

Every gate is asked after a push of the forge branch (RT3), as a multi-option question in exactly this shape, never a lone yes/no and never a two-label approve/reject (W3, RT10).

| decision | when | question and options | plan default and basis |
|---|---|---|---|
| Frozen row list (Keep/Update/Deny), first pass | at plan approval | "How should the 22-facet list and row-drafting rule stand?" Keep as drafted / Keep with the edits I list / Deny, rethink the taxonomy | Keep (Decision 1; T1) |
| Frozen row list (Keep/Update/Deny), second pass | P2, presented as a file | Keep as drafted / I edited the file / Deny, rethink | none; the owner's file review |
| Cost envelope | at plan approval | Approve up to about 380 calls and 35M input tokens, re-asked above 1.5 times / Approve the pilot only (P0 to P4), then re-ask with measured numbers / Re-scope before any spend | the first option (X2: cost approval up front) |
| Cost re-ask | P3 or P4, only if the recomputed total exceeds 1.5 times | Proceed at 1.5× / Stop and report / Re-scope | none |
| Workflow opt-in | at plan approval | Agent tool only / Workflow for the extraction waves (P5, P7) / Workflow for extraction and verification (P5, P7, P8) | Agent tool only (house rule: Workflow runs only on explicit opt-in) |
| `add_repo` for source reads | at plan approval | Attach both repos read-only / Attach `google-gemini/gemini-cli` only / Docs only, no `add_repo` | none; neither ruling decides (A attached both, B probed one) |
| Matrix PR run shape | at plan approval | Its own `/forge` run, started when P5 is verified / A phase inside this run (P6 as written) / Defer it and accept the flagged 5-of-8 lever guide | its own `/forge` run (RT5; owner-decisions) |
| Veto point on the lever-guide contingency | at plan approval | Allow the flagged 5-of-8 fallback after a date I set / Hold the atlas PR until the matrix PR merges / Allow the fallback as soon as the rest of the atlas is ready | the first option, with the trigger date recorded (RT5) |
| Gate 134 route | at plan approval | `CARVE_SUBSTR` entry in the atlas PR / Keep vendor model ids out of JSON and quote them only in HTML / Decide at PR review | `CARVE_SUBSTR` (L3) |
| Advisory hook noise during the build | at plan approval | Leave every advisory hook as configured / I will quiet cause-triage and cause-remediation for the build / I will quiet those two and the context-handoff nag | none; the owner's call (RT9) |
| Grok Bot in the matrix | P6, before any code, if the matrix run has not settled it | `model_ref` optional under vendor-managed control / Keep Grok Bot out with a not-rankable note / Decide inside the matrix FORGE run | none; open design question (owner-decisions) |
| U00 cluster | P2 and after the P8 join | Put the proposed row into the frozen list / Leave the records in unmapped / Rethink the facet | none |
| Merge, for each PR | P6 and P12, after every check passes | Merge after every check passes / Hold for my review / Close without merging | none |

## Definition of done

- **Acceptance tests.** Every phase's acceptance tests pass, with their outputs in the run dir and the decisions in `decisions.md`.
- **Version bumps.** The atlas PR changes nothing under `plugins/` (`git diff --name-only origin/main...HEAD -- plugins/` is empty), so it bumps no version. The matrix PR bumps `ravenclaude-core`, passes `python3 scripts/sync-plugin-versions.py --check`, regenerates the Copilot package and updates the CHANGELOG top entry.
- **Layout allow-list.** The AGENTS.md layout snippet, run from the worktree, reports that every new file matches `.repo-layout.json`.
- **Prettier.** The pinned prettier write then `--check .` exits 0 over the whole tree.
- **Ruff.** `ruff check .` exits 0.
- **Audit gates.** `scripts/audit-gates.sh` exits 0 from the worktree, with the toplevel logged, for both PRs.
- **Model-governance gate.** Gate 134 (`python3 scripts/check-model-ids.py`) exits 0 from the worktree for both PRs; Gates 255 and 154 are green on the matrix PR.
- **`/code-review`.** Run in the definition of done of every phase that lands as a PR with real code changes: P6 (the checker, schema and tier-map loaders) and P12 (the atlas's `_tools/`). Every finding is fixed or answered before merge.
- **Rendered output.** `render.py --check` exits 0 on `main` after merge, and the success-signal probe passes 30 of 30.
- **Durability.** The plan copies are on `main` after merge, and `_work/` is absent from the merged tree.
- **No count changes.** No skill or agent count changes in this run: neither PR adds a file under any `skills/` or `agents/` directory (the P4 `omitClaudeMd` copy is uncommitted and deleted), and Gates 287 to 289 see no agent change.

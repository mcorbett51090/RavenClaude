# Technical Writing & Docs Plugin — Team Constitution

> Team constitution for the `technical-writing-docs` Claude Code plugin — **3** specialist agents for developer and product documentation done well — the Diataxis framework (tutorial/how-to/reference/explanation), docs-as-code, accurate API reference, and a maintainable docs site — deepening ravenclaude-core's documentarian. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`docs-architect`](agents/docs-architect.md) | Documentation strategy and structure: applying the Diataxis framework, information architecture, the docs-as-code workflow, audience/journey mapping, and what to document (and what not to) | "our docs are a mess", "how should we structure our documentation?", "set up docs-as-code", "what docs do we need?" |
| [`api-reference-writer`](agents/api-reference-writer.md) | Accurate developer reference: spec-driven API reference (from OpenAPI/AsyncAPI), runnable examples, documenting errors/limits/auth, SDK/quickstart guides, READMEs, and changelogs that respect SemVer | "document this API", "write a quickstart", "our examples don't work", "write a good README / changelog" |
| [`docs-site-engineer`](agents/docs-site-engineer.md) | The docs site as software: tooling choice (Docusaurus/Mintlify/MkDocs/Starlight), build + deploy in CI, search, versioning, navigation/IA implementation, link-checking and example-testing in CI, and previews | "set up a docs site", "add versioning to our docs", "our docs search is bad", "check links/examples in CI" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Know which of the four kinds you're writing (Diataxis).** Tutorial (learning), how-to (a task), reference (information), explanation (understanding) serve different needs and must not be mixed. A 'tutorial' full of reference tables teaches nobody.
2. **Docs-as-code, versioned with the product.** Documentation lives in the repo, is reviewed in PRs, CI-checked, and ships with the code it describes. Docs in a separate wiki rot out of sync the day they're written.
3. **Examples must run.** Every code sample is tested (or generated from tested code). A copy-paste example that errors destroys trust faster than a missing one.
4. **Write for the reader's task, not the system's structure.** Organize around what the reader is trying to do, not around your modules. Docs mirroring the codebase's internal structure serve the author, not the user.
5. **Stale docs are worse than no docs.** A confidently-wrong doc sends the reader down a hole. Date volatile content, tie docs to releases, and prune what's no longer true.
6. **Show the unhappy path.** Errors, edge cases, and limits — not just the golden path. The reader hits the docs precisely when something didn't work the easy way.

## 3. Seams (the bridges to neighbouring plugins)

- **The developer portal and SDK/codegen reference for an API you produce** → `api-engineering` (dev portal + SDKs); this team owns the writing craft and reference quality across it.
- **Marketing copy, brand voice, and the visual design of a docs/marketing site** → `web-design`; we own the technical content and IA, they own the brand and look.
- **General prose polish, ADRs, and lightweight per-task documentation** → this plugin **deepens** `ravenclaude-core/documentarian`; the litmus is a one-off doc/polish → core, a docs *system/site/reference* → here.
- **The contract (OpenAPI/AsyncAPI) the reference is generated from** → `api-engineering`; we turn it into great reference, they own the spec.
- **Where the docs site builds/deploys in CI** → `devops-cicd`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks (the dual-bank model)

Two banks back the agents (see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer):
  - [`knowledge/technical-writing-docs-decision-trees.md`](knowledge/technical-writing-docs-decision-trees.md) — the consolidated tree bank (Diátaxis kind, docs tooling, content home, is-it-worth-writing, examples-from-stale, new-page-vs-update, stale-doc handling, API-docs structure) + the dated 2026 capability map.
  - [`knowledge/diataxis-content-type-selection-decision-tree.md`](knowledge/diataxis-content-type-selection-decision-tree.md) — **Mermaid** — the four-kind selector deepened with the **mixed-kind split** logic (the most common Diátaxis failure: one page that is two kinds). Resolves a page against the 2D needs grid.
  - [`knowledge/lint-in-ci-vs-manual-review-decision-tree.md`](knowledge/lint-in-ci-vs-manual-review-decision-tree.md) — **Mermaid** — automate-in-CI/editor vs. keep-it-human: mechanical/objective/high-frequency → prose linter (Vale) in CI **and** as an editor LSP; judgment (accuracy, structure, Diátaxis-kind fit) → human.
  - **Traverse the relevant tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (API-docs drift from code, no-IA findability, tutorial/reference confusion, docs-review bottleneck). Secondary source; never replaces the knowledge bank. The most-likely-to-benefit specialists (`docs-architect`, `api-reference-writer`, `docs-site-engineer`) should check the bank when a situation matches.

## 6. Technical-runtime tier — prose-linter LSP (bundled config, binary installed separately)

Docs-as-code is **markup the writer edits in an editor**, so the runtime tier that fits is a **prose/markdown LSP** — real-time diagnostics as you write, the editor half of the lint-in-CI-vs-manual decision tree. The plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) configuring two real, maintained language servers:

| Surface | Server | `command` | Install (consumer, separate) `[verify-at-use]` |
|---|---|---|---|
| Prose / style | **Vale-LS** (`vale-ls`, errata-ai, MIT, v0.4.0 2025-03-14) | `vale-ls` (stdio) | `cargo install vale-ls` **or** a GitHub release binary on `PATH`; wraps a local Vale install + `.vale.ini`. |
| Markdown structure | **Marksman** (`artempyanykh/marksman`) | `marksman server` (stdio) | release binary on `PATH` (`brew install marksman` / Nix / GitHub release). |

**The plugin ships the *config*, not the *binary*** (same posture as `backend-engineering` §6). If a server's binary isn't on `PATH` it shows `Executable not found in $PATH` in the `/plugin` Errors tab and that one surface degrades — Claude Code and every other tool keep working (**loud-but-non-fatal**). LSP servers start only after the workspace is trusted; `/reload-plugins` picks up a config change mid-session. Vale-LS reviews **prose style** (it needs a `.vale.ini` + `styles/`); Marksman reviews **markdown structure** (links, anchors, completion). They are the editor surface of the same standard CI runs — so editor and CI never disagree.

> The bare-`vale-ls` stdio invocation and the `cargo install vale-ls` path are the conventional Vale-LS editor configs; the `vale-ls` release version (v0.4.0, 2025-03-14, MIT) is verified against the [errata-ai/vale-ls](https://github.com/errata-ai/vale-ls) repo (2026-06-05). Package names + the exact invocation are version-volatile — re-confirm at use. `marksman server` is the documented stdio invocation per the [marksman install docs](https://github.com/artempyanykh/marksman/blob/main/docs/install.md).

## 7. Recommended (not bundled) MCP servers — no docs-MCP clears the bar

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**. The docs-useful servers all fail that bar:

| Server | Why recommend-not-bundle / N-A | Recommended path `[verify-at-use]` |
|---|---|---|
| **Filesystem** (`@modelcontextprotocol/server-filesystem`, MIT, first-party) | Needs a **consumer-specific allowed-directory path** (can't hardcode) and is **write-capable** → both disqualify bundling. A docs writer wants it to read/edit the docs tree. | `claude mcp add fs -- npx -y @modelcontextprotocol/server-filesystem /path/to/docs` — pass only the docs dirs. |
| **Git** (`mcp-server-git`, MIT, first-party) | Needs a **consumer-specific repo path** + exposes **write** verbs → recommend-not-bundle; prefer the read/search subset for "what changed in the docs?" | `claude mcp add git -- uvx mcp-server-git --repository /path/to/repo` |
| A docs-platform's own MCP (e.g. a hosted docs vendor) | **per-tenant / authenticated** (org URL + token = a secret) → never bundle; secret stays a **reference**, gated through `security-reviewer`. | Consumer-configured, secret as an env-var **name**/vault URI, `security-reviewer` sign-off. |

No docs-specific MCP server was found that is simultaneously zero-config, read-only, and broadly-useful — so **none is bundled and none is invented**. The decision table in `bundled-mcp-servers.md` sends every candidate above to *recommend / evaluate-first*. Vale's value reaches the agent through the **LSP** (§6), not an MCP.

## 8. Runnable tooling — `scripts/docs_check.py`

[`scripts/docs_check.py`](scripts/docs_check.py) (stdlib-only, Python 3.8+, `ruff`-clean) is a zero-install **readability + prose-hygiene** triage you can run on any Markdown file or pasted text:

- **`readability`** — public-domain **Flesch Reading Ease** + **Flesch-Kincaid Grade Level** (1948 / 1975 formulas), with markdown/code stripped first so the score reflects prose. Technical docs commonly target grade 9–12 `[verify-at-use against the audience]`. Advisory — never fails a build on its own.
- **`prose`** — flags mechanically-detectable anti-patterns with line numbers: non-descriptive link text (`[click here]`), placeholders (TODO/TBD/lorem), weasel/filler words (`simply`/`just`/`easy`/`obviously`), and banned/inconsistent terminology (`login` vs `log in`, `whitelist`→`allowlist`, …). Exits non-zero on findings (CI-friendly).

It is a **calculator + linter, not a style authority**: syllable counting is estimated (a heuristic), every threshold is a documented overridable default, and the banned-terms map is meant to be edited per house style. It **complements, does not replace, Vale** (§6) — Vale owns the editor/CI style gate; `docs_check.py` is the stdlib-only first pass that needs nothing installed. Owned primarily by `docs-architect` (readability) and `docs-site-engineer` (the CI-prose check). Decision-support only — outputs are a prompt to look, not a verdict.

## 9. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason):

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios (API-docs drift from code, no-IA findability, tutorial/reference confusion, docs-review bottleneck) matching the existing `scenarios/README.md` index + 9-field schema. The README listed them; the files were the net-new gap. |
| 2 | **Decision-tree knowledge (Mermaid)** | **BUILT** — 2 new standalone Mermaid trees: `diataxis-content-type-selection` (mixed-kind split) + `lint-in-ci-vs-manual-review`. They complement the 8 trees PR #315 consolidated into the bank file. Authored with `## The tree` headings (not `## Decision Tree:`) so they render inline without triggering the SVG pre-render gate — the same pattern as `veterinary-practice`'s standalone trees. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §7. No docs-MCP clears the zero-config + read-only bar (filesystem/git need a path + are write-capable; a docs-vendor MCP is per-tenant + secret-handling). Documented the recommended `claude mcp add` paths instead. No invented servers. |
| 4 | **LSP server** | **BUILT** — `.lsp.json` (Vale-LS prose linter + Marksman markdown LSP), wired via `plugin.json` `lspServers`. Genuinely useful for a docs-as-code editing domain (the editor half of the lint decision tree); binaries install separately (§6). Real, maintained tools — not invented. |
| 5 | **Runnable script** | **BUILT** — `scripts/docs_check.py` (Flesch readability + prose hygiene), stdlib-only, ruff-clean. Real non-code value: instant readability + nit triage with nothing installed, complementing (not duplicating) Vale. |
| 6 | **bin/ · monitors · output-styles · settings · themes** | **N-A** — no groundable, broadly-valuable instance. A docs-review output-style was considered but would overlap each agent's Output Contract + the advisory hook; the readability/prose surface is better served by the runnable script. No build/repo daemon to monitor; no docs-specific permission surface beyond core's. |
| 7 | **skills / hooks / commands / templates** | **Coverage sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory anti-pattern hook already cover Diátaxis classification + documentation, API-reference writing, example-testing, and docs-as-code site setup. The new trees + script + LSP extend reach without a new agent (team-growth-as-knowledge house rule). No obvious high-value gap this round. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top entry for this build-out. No `NOTICE.md` (nothing third-party is bundled — the LSP config references external binaries the consumer installs; the script is original stdlib-only; all sources cited inline, not vendored). |

## 10. Milestones

- **v0.2.x** — initial + consolidated knowledge (PR #315 added the decision-tree bank, `best-practices/`, and templates).
- **v0.3.0** — value-add build-out: scenarios bank (4 scenarios) matching the README index, 2 new Mermaid decision trees (Diátaxis content-type selection + lint-in-CI-vs-manual-review), prose-linter LSP tier (`.lsp.json`: Vale-LS + Marksman), `scripts/docs_check.py` (Flesch readability + prose hygiene), CHANGELOG. MCP tier dispositioned recommend-not-bundle with reasons (§7).

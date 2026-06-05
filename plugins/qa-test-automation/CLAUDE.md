# QA & Test Automation Plugin — Team Constitution

> Team constitution for the `qa-test-automation` Claude Code plugin — **3** specialist agents for building a test strategy that catches real defects cheaply — the test pyramid, deterministic E2E automation, test data and environments, coverage that means something, and flake control. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`test-strategy-architect`](agents/test-strategy-architect.md) | The test strategy: which test level catches which defect class, the pyramid shape, what to test vs not, coverage philosophy (mutation over line %), and the risk-based prioritization | "design our test strategy", "what should we unit vs integration vs E2E test", "our tests are slow and don't catch bugs", "how much coverage is enough" |
| [`e2e-automation-engineer`](agents/e2e-automation-engineer.md) | End-to-end and integration test authoring: Playwright/Cypress flows, resilient selectors (roles/test-ids over CSS/XPath), waiting on conditions not sleeps, page-object/fixture structure, and the critical-journey selection | "write E2E tests for checkout", "our Cypress tests are flaky", "set up Playwright", "these selectors keep breaking" |
| [`test-infrastructure-engineer`](agents/test-infrastructure-engineer.md) | Test infrastructure: test data management (factories/seeding), ephemeral environments and service virtualization, flaky-test detection and quarantine, parallelization/sharding, and coverage/mutation reporting in CI | "manage our test data", "spin up ephemeral test environments", "detect and quarantine flaky tests", "speed up the test run" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Respect the pyramid.** Many fast unit tests, fewer integration tests, a few high-value E2E. An ice-cream-cone suite (mostly slow E2E) is slow, flaky, and expensive — invert it.
2. **A flaky test is a broken test.** Quarantine it with an owner and a deadline; never normalize 'just re-run'. Flakiness destroys the suite's signal and trains people to ignore red.
3. **Test behavior, not implementation.** Assert on what the user/consumer observes, not private internals. Tests coupled to implementation break on every refactor and protect nothing.
4. **Determinism or it's not a test.** No fixed `sleep`, no real network/time/randomness without control. Wait on conditions, fake the clock, seed the RNG, stub the boundary.
5. **Coverage % is a floor, not a goal.** 100% line coverage with no assertions tests nothing. Prefer mutation testing to measure whether tests actually catch defects.
6. **The test gate is part of CI's contract.** Tests run in the pipeline, gate the merge, and stay fast — slow suites get sharded or moved post-merge (coordinate with devops-cicd).

## 3. Seams (the bridges to neighbouring plugins)

- **Consumer-driven contract tests between services** → `api-engineering/api-testing-engineer` owns Pact/contract testing; we own the broader pyramid and E2E.
- **Where tests run, sharding, required checks** → `devops-cicd/pipeline-engineer` (we define *what* to test; they wire *where* it runs).
- **The UI being tested (components, accessibility-in-code)** → `frontend-engineering`; selectors and testability are a shared concern.
- **Lightweight per-task QA / acceptance checks** → this plugin **deepens** `ravenclaude-core/tester-qa`; the litmus test is ad-hoc check → core, the test *strategy & automation* → here.
- **Load/performance testing of an API** → `api-engineering` (k6) and `observability-sre` (SLOs); functional E2E is ours.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/qa-test-automation-decision-trees.md`](knowledge/qa-test-automation-decision-trees.md) (test-level selection, flake triage, mock/stub/fake double selection, unit-vs-integration-vs-contract for a seam, blocking-vs-non-blocking merge gate, E2E-fix-vs-quarantine-vs-delete + a dated 2026 capability map) and [`knowledge/qa-selector-and-test-data-decision-trees.md`](knowledge/qa-selector-and-test-data-decision-trees.md) (**selector resilience** — role/text/test-id over CSS/XPath, the brittleness signature; and **test-data strategy** — factory vs fixture vs ephemeral-DB vs namespaced). **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (flaky-quarantine graveyard, ice-cream-cone slow suite, contract-test drift, coverage-gaming with no assertions). Secondary source; never replaces the knowledge bank. The most-likely-to-benefit specialists check the bank when a situation matches.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binary installed separately)

Test automation is a **code** domain — the artifacts under test and the tests themselves are real source (Playwright/Cypress = TS/JS, pytest/unittest = Python). So the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence — go-to-definition, find-references, diagnostics — instead of grep-and-guess when reading or fixing a test file. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section). LSP is enabled by default in Claude Code 2.0.74+ `[verify-at-use]`.

| Language | Server | `command` | Install (consumer, separate) |
|---|---|---|---|
| TypeScript/JS | typescript-language-server | `typescript-language-server --stdio` | `npm install -g typescript-language-server typescript` |
| Python | Pyright | `pyright-langserver --stdio` | `pip install pyright` **or** `npm install -g pyright` |

**The plugin ships the *config*, not the *binary*.** Per the plugins reference: "LSP plugins configure how Claude Code connects to a language server, but they don't include the server itself." If a server's binary isn't on `PATH`, it shows `Executable not found in $PATH` in the `/plugin` Errors tab and that one language degrades — Claude Code and all other tools keep working (the same **loud-but-non-fatal** posture as a missing MCP prerequisite). LSP servers start only after the workspace is trusted, and `/reload-plugins` is needed to pick up a config change mid-session. The two servers cover the plugin's example languages; a Go/Java/etc. test codebase would add the matching server (the `backend-engineering` `.lsp.json` carries a `gopls` example).

> Package names + the `--stdio` invocations are verified against the official LSP-plugin table in the plugins reference (`typescript-lsp`, `pyright-lsp`, 2026-06-05). Re-confirm the 2.0.74 LSP-support version at use — version-volatile.

## 7. Recommended (not bundled) MCP servers — Playwright MCP & the browser-launching class

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a write-capable, browser-launching, or per-consumer-configured server is **recommend-not-bundle**. The single most-requested QA server — **Playwright MCP** — fails the bar decisively, so we document the recommended `claude mcp add …` path with a `security-reviewer` gate instead of shipping an `mcpServers` entry.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Playwright MCP** ([`@playwright/mcp`](https://github.com/microsoft/playwright-mcp), Apache-2.0, **first-party Microsoft**) | **Launches a real browser** (headed by default; `--headless` flag) and drives navigation/clicks/typing/screenshots against arbitrary URLs — a live, content-fetching subprocess whose **tool results are untrusted page content flowing into agent context**. Upstream states plainly: *"Playwright MCP is not a security boundary"* (`[verify-at-use]` — retrieved 2026-06-05). That makes it a deliberate, opt-in, `security-reviewer`-gated adoption — never a bundled auto-start. | `claude mcp add playwright -- npx -y @playwright/mcp@<pinned-version>` (the version is volatile — `0.0.x` series as of 2026-06; pin it, don't float `@latest`). Gate through `ravenclaude-core/security-reviewer` before adoption; prefer `--headless` and the upstream `allowUnrestrictedFileAccess`-off default. |

**Why not bundled (the load-bearing reasoning):** a browser-launching server is the textbook "evaluate-first, never default" row of the doctrine table — it auto-starts when the plugin is enabled, runs outside every model-layer guard, fetches arbitrary web content as untrusted input, and is explicitly *not* a security boundary upstream. Bundling it would put an un-contained browser subprocess on every consumer's machine on `/plugin marketplace update`. The owning agent is `e2e-automation-engineer`; the security gate is mandatory. **No MCP server was invented** — Playwright MCP is the one verified, broadly-relevant QA server, and it lands in the gated row.

> Verified 2026-06-05 via web research: `@playwright/mcp` is the first-party Microsoft package (Apache-2.0), invoked `npx @playwright/mcp@latest`, launches headed Chromium by default, and the docs state "Playwright MCP is not a security boundary." Package name + license confirmed; the exact version is volatile — re-confirm and pin at use.

## 8. Scenarios bank & runnable tooling (added v0.3.0)

- **Scenarios bank** — [`scenarios/`](scenarios/) holds dated, scope-tagged, unverified field notes (the marketplace scenarios pattern). Surface a matching scenario only as a *secondary* source, behind the mandatory unverified-scenario preamble, never overriding the cited knowledge bank.
- **Runnable analyzer** — [`scripts/qa_suite_metrics.py`](scripts/qa_suite_metrics.py) (stdlib only, Python 3.9+; ruff-clean) is the runtime complement to two scenarios: `flake_rate` computes a per-test flake rate from a JSONL run log (a pass-on-retry counts as a **flake event, not a pass**) and ranks the flakiest; `pyramid_ratio` reports the unit:integration:e2e shape from supplied counts or by auto-counting a test directory, and flags an inverted **ice-cream cone**. It is an **analyzer, not a test runner or data source** — the user supplies the inputs; output is decision-support, owned primarily by `test-infrastructure-engineer` (flake_rate) and `test-strategy-architect` (pyramid_ratio).

## Value-add completeness (build-out 2026-06-05)

PR #315 had already shipped the consolidated knowledge decision-trees, `best-practices/`, and `templates/`. This build-out fills the net-new gaps and dispositions **every** value-add menu item honestly below (built vs. recorded N-A with reason).

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — `scenarios/README.md` index + 9-field schema and **4** dated field notes: flaky-quarantine-graveyard (pre-existing), ice-cream-cone-slow-suite (pyramid inversion), contract-test-drift (provider-side verification), coverage-gaming-no-assertions (mutation testing exposes it). |
| 2 | **New decision-tree knowledge (complement #315)** | **BUILT** — `knowledge/qa-selector-and-test-data-decision-trees.md`: two Mermaid trees the #315 file lacked — **selector resilience** (role/text/test-id over CSS/positional-XPath; the E2E-brittleness signature) and **test-data strategy** (factory vs shared-fixture vs ephemeral-DB vs namespaced). Chosen because the existing tree file already covers test-level / flake-triage / double-selection / seam / blocking-gate / E2E-fix — selectors and test-data were the authoring-time gaps. |
| 3 | **Bundled MCP server** | **N-A (evaluate-first / recommend-not-bundle)** — §7. **Playwright MCP** (`@playwright/mcp`, first-party MS, Apache-2.0) is the one verified broadly-relevant QA server, but it **launches a real browser** (headed by default), fetches arbitrary URLs as untrusted input, and upstream states it is *"not a security boundary"* — the textbook browser-launching, `security-reviewer`-gated, opt-in row. Documented the recommended `claude mcp add` path (pinned, headless, gated) instead of an `mcpServers` entry. No server invented. |
| 4 | **LSP server** | **BUILT** — `.lsp.json` (typescript-language-server + Pyright), wired via `plugin.json` `lspServers`. Genuinely useful: tests and the code under test are real source (TS/JS for Playwright/Cypress, Python for pytest). Binaries install separately (§6). |
| 5 | **Runnable script (`scripts/`)** | **BUILT** — `qa_suite_metrics.py` (`flake_rate` + `pyramid_ratio`), the runtime tier with real value: it operationalizes the two scenarios' "measure first" lesson (flake rate before touching retries; pyramid ratio before re-platforming). Stdlib-only, ruff-clean, executable. |
| 6 | **bin/ executables / monitors / output-styles / settings / themes** | **N-A** — covered by the single stdlib analyzer + the advisory hook; no compiled binary, long-running watcher, or vertical-specific tool-permission / styling surface beyond `ravenclaude-core`. Deliverables are reports + test code, governed by the agents' Output Contract. |
| 7 | **skills / hooks / commands / templates** | **SUFFICIENT** — 5 skills (test-strategy-design, e2e-automation, test-infrastructure, flaky-test-triage, test-pyramid-audit), 1 advisory anti-pattern hook, 4 commands, 4 templates already cover the surface. The new selector + test-data trees and the analyzer extend reach without a 5th agent (team-growth-as-knowledge house rule). No high-value gap this round. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top `0.3.0` entry. No `NOTICE.md` — nothing third-party is bundled (the script is original stdlib-only; Playwright MCP is *referenced*, not vendored). |

## Milestones

- **v0.2.x** — 3-agent QA team (test-strategy-architect, e2e-automation-engineer, test-infrastructure-engineer); 5 skills, the consolidated decision-tree knowledge bank + best-practices + templates (PR #315), 4 commands, 1 advisory hook, 1 seed scenario.
- **v0.3.0** — value-add build-out: scenarios bank (4 field notes + index), `qa-selector-and-test-data-decision-trees.md` (selector-resilience + test-data-strategy Mermaid trees), `scripts/qa_suite_metrics.py` (flake-rate + pyramid-ratio analyzer, ruff-clean), `.lsp.json` (TS/JS + Python LSP config wired via `lspServers`), CLAUDE.md §5–§8 + the value-add completeness table, CHANGELOG. Bundled-MCP tier dispositioned recommend-not-bundle (Playwright MCP, security-gated) with reasons (§7).

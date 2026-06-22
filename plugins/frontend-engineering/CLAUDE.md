# Frontend Engineering Plugin — Team Constitution

> Team constitution for the `frontend-engineering` Claude Code plugin — **4** specialist agents for app-grade frontend engineering — component architecture, rendering strategy (SSR/SSG/RSC/CSR), state and server-data management, performance and bundle discipline, and accessibility-in-code — distinct from web-design's brand/marketing-site craft. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`frontend-architect`](agents/frontend-architect.md) | Frontend architecture: framework/rendering strategy (CSR/SSR/SSG/ISR/RSC) per route, project structure, component boundaries, the TypeScript posture, and the build/tooling shape | "Next.js or a SPA?", "which rendering strategy?", "how should we structure this frontend?", "set up our React app properly" |
| [`react-implementation-engineer`](agents/react-implementation-engineer.md) | Component implementation: composable React components, hooks correctly (deps, no stale closures, custom hooks), controlled forms, accessibility-in-code (semantic HTML, ARIA, keyboard, focus), and testable markup | "build this component", "this useEffect is buggy", "make this accessible", "refactor this god-component" |
| [`frontend-state-and-data-engineer`](agents/frontend-state-and-data-engineer.md) | State and data architecture: separating server-cache from client state, server-data libraries (TanStack Query / RSC data), choosing client state (local/context/store), caching/invalidation/optimistic updates, and data-fetching patterns | "where should this state live?", "do we need Redux?", "set up data fetching", "add optimistic updates" |
| [`frontend-performance-engineer`](agents/frontend-performance-engineer.md) | Frontend performance: Core Web Vitals (LCP/INP/CLS), JavaScript bundle analysis and code-splitting, lazy-loading, image/font optimization, hydration cost, and the perf budget — the in-code engineering complement to web-design's CWV tuning | "our app is slow / big bundle", "fix our Core Web Vitals", "reduce JavaScript", "why is hydration slow?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Server state is not client state.** Data from the API is a cache, not app state — manage it with a server-cache library (TanStack Query / RSC), not by stuffing it into a global store. Conflating the two is the root of most React state bugs.
2. **Choose the rendering strategy per route, by need.** Static marketing page → SSG; personalized dashboard → SSR/RSC; highly interactive app shell → CSR. One global rendering mode for everything is a mismatch somewhere.
3. **TypeScript strict, and type the boundaries.** `strict` on, no `any` at API/props boundaries. Types are the cheapest test you'll ever write; `any` is a hole you'll fall through in production.
4. **Accessibility is implementation, not decoration.** Semantic HTML first, ARIA only to fill gaps, keyboard operable, focus managed. An inaccessible app is a broken app for real users — and the design-side WCAG audit is web-design's.
5. **The bundle is a budget.** Code-split by route, lazy-load the heavy and the below-the-fold, watch what you ship. A 2MB JS bundle is a slow first load and a Core-Web-Vitals failure you chose.
6. **Composition over configuration.** Small, composable components with clear props beat a mega-component with thirty boolean flags. Prop-drilling and god-components are refactors waiting to happen.

## 3. Seams (the bridges to neighbouring plugins)

- **Brand, visual design, UX/wireflows, the WCAG *audit*, and marketing-site builds** → `web-design`; this team engineers the *app*, that team owns design/brand and the accessibility audit (we implement accessibly, they verify).
- **Login/signup UX and session handling on the client** → `auth-identity` (we render it; they own the auth flow and token discipline).
- **The API the frontend consumes (contract, pagination, errors)** → `api-engineering`; we consume it, they design it.
- **Native iOS/Android (and React Native/Flutter)** → `mobile-engineering`; shared web patterns are ours.
- **E2E test authoring and testability (data-testids)** → `qa-test-automation` (a shared concern — we add the hooks).

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/frontend-engineering-decision-trees.md`](knowledge/frontend-engineering-decision-trees.md) (rendering-strategy per route, where-state-lives, server-vs-client component, data-fetching, optimistic-update, which-global-store, slow-render triage, form library) and [`knowledge/styling-and-bundle-decision-trees.md`](knowledge/styling-and-bundle-decision-trees.md) (styling-approach selection, bundle-size-regression triage). **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol. Capability-map rows are `[verify-at-use]` — re-check against the vendor before quoting.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (hydration mismatch from an unpinned locale/timezone, CLS+LCP perf-budget regression, server-state-in-Redux refactor, accessibility modal-focus remediation). Secondary source; never replaces the knowledge bank or the `web-design` WCAG audit.
- **Cross-plugin (render loop)** [`../ravenclaude-core/knowledge/visual-feedback-loop.md`](../ravenclaude-core/knowledge/visual-feedback-loop.md) — the render→see→critique→iterate discipline behind `react-implementation-engineer`'s and `frontend-performance-engineer`'s **Visual feedback loop** sections: screenshot via `chrome-devtools-mcp` (the model's eyes), the objective stopping signals (Lighthouse perf/a11y, zero console errors), and the referee that merges them into one pass/fail verdict. Conditional on the optional MCP; degrades to the structural read, never stalls.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binary installed separately)

Frontend engineering is a **code** domain, so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence — go-to-definition, find-references, diagnostics — instead of grep-and-guess. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section, 2026-06-05); LSP support landed in Claude Code 2.0.74 `[verify-at-use]`.

It configures three language servers covering this plugin's stack (TypeScript/JS, ESLint, CSS/SCSS/LESS):

| Surface | Server | `command` | Install (consumer, separate) |
|---|---|---|---|
| TypeScript/JS | typescript-language-server | `typescript-language-server --stdio` | `npm install -g typescript-language-server typescript` |
| ESLint | vscode-eslint-language-server | `vscode-eslint-language-server --stdio` | `npm install -g vscode-langservers-extracted` |
| CSS / SCSS / LESS | vscode-css-language-server | `vscode-css-language-server --stdio` | `npm install -g vscode-langservers-extracted` |

**The plugin ships the *config*, not the *binary*.** Per the plugins reference: "LSP plugins configure how Claude Code connects to a language server, but they don't include the server itself." If a server's binary isn't on `PATH`, it shows `Executable not found in $PATH` in the `/plugin` Errors tab and that one surface degrades — Claude Code and all other tools keep working (the same **loud-but-non-fatal** posture as a missing MCP prerequisite). LSP servers start only after the workspace is trusted, and `/reload-plugins` is needed to pick up a config change mid-session.

> The `vscode-eslint-language-server` and `vscode-css-language-server` binaries both ship in the **`vscode-langservers-extracted`** npm package (the HTML/CSS/JSON/ESLint servers extracted from VS Code) — verified 2026-06-05 against its [npm listing](https://www.npmjs.com/package/vscode-langservers-extracted) and [repo](https://github.com/hrsh7th/vscode-langservers-extracted). `typescript-language-server` is its own package (with `typescript` as a peer). Package names + the 2.0.74 LSP-support version are version-volatile — re-confirm at use. (The original `vscode-langservers-extracted` is community-maintained with active forks; vet the package's maintenance status at adoption.)

## 7. Recommended (not bundled) MCP servers — browser/DevTools context

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a server that launches a browser, drives a live page, or needs per-consumer setup is **recommend-not-bundle**. Both genuinely-useful frontend MCP servers below launch and drive a real browser (a stateful, side-effecting subprocess) and so fail the zero-config-read-only bar — documented as recommend-not-bundle.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Playwright MCP** ([`@playwright/mcp`](https://www.npmjs.com/package/@playwright/mcp), Microsoft, [repo](https://github.com/microsoft/playwright-mcp), Apache-2.0) | First-party from the vendor (the rule's "first-party from the vendor → recommend, don't bundle" row) **and** it **launches and drives a browser** (navigates, clicks, types, runs scripts) — write-capable/side-effecting by nature, not zero-config-read-only. | `claude mcp add playwright -- npx -y @playwright/mcp@latest` — review the toolset; the `browser_run_code_unsafe`-class tools execute arbitrary page scripts, so gate adoption through `ravenclaude-core/security-reviewer`. |
| **Chrome DevTools MCP** ([`chrome-devtools-mcp`](https://www.npmjs.com/package/chrome-devtools-mcp), Google / ChromeDevTools, [repo](https://github.com/ChromeDevTools/chrome-devtools-mcp), Apache-2.0) | First-party from the vendor; **controls a live Chrome** (record perf traces, inspect network/console, automate actions) — stateful + side-effecting, not zero-config-read-only. Also ships **usage telemetry on by default** (opt out with `--no-usage-statistics`). | `claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest --no-usage-statistics` — strong for in-the-loop CWV/perf-trace work (the perf engineer's lane); `security-reviewer` gate before adoption. |

**Why none are bundled (the load-bearing reasoning):** both are real, first-party, Apache-2.0 servers — but each is **first-party-from-the-vendor** *and* **launches/drives a browser** (a side-effecting subprocess, not read-only), which the rule's decision table routes to **recommend, don't bundle** (and the browser-automation tools warrant a `security-reviewer` gate before any consumer adopts them). No invented servers. If a genuinely zero-config, read-only, broadly-useful frontend server appears, revisit with the doctrine block in [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 4.

> Verified 2026-06-05: `@playwright/mcp` is Microsoft's official Playwright MCP server ([npm](https://www.npmjs.com/package/@playwright/mcp) / [github](https://github.com/microsoft/playwright-mcp)); `chrome-devtools-mcp` is Google's official Chrome DevTools MCP server ([npm](https://www.npmjs.com/package/chrome-devtools-mcp) / [github](https://github.com/ChromeDevTools/chrome-devtools-mcp), ~v0.21.0 as of April 2026, weekly cadence, telemetry-on-by-default). Versions, tool surfaces, and telemetry defaults are volatile — re-confirm at use.

## 8. Runnable tooling

[`scripts/perf_budget.py`](scripts/perf_budget.py) (stdlib only, Python 3.8+) makes two perf checks mechanical and CI-gateable: `bundle` (measured per-route JS transfer sizes vs. a per-route KB budget, exits non-zero on any overage) and `vitals` (75th-percentile field LCP/INP/CLS vs. Google's published "good" thresholds — LCP < 2.5s, INP < 200ms, CLS < 0.1 `[verify-at-use]`). It is a **checker, not a measurement tool** — the user supplies the measured numbers (from the bundler's analyze output and RUM/CrUX field data); a passing budget is necessary, not sufficient (measure field data, not just lab). Owned primarily by `frontend-performance-engineer`.

## 9. Value-add completeness (build-out 2026-06-05)

PR #315 already added the consolidated `knowledge/frontend-engineering-decision-trees.md`, `best-practices/`, and `templates/`. This build-out adds the net-new gap (scenarios bank + the runtime tier) and dispositions every value-add menu item below (built or recorded N-A with reason):

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios (hydration mismatch from unpinned locale/timezone, CLS+LCP perf-budget regression, server-state-in-Redux refactor, accessibility modal-focus remediation) matching the existing `scenarios/README.md` index + 9-field schema. |
| 2 | **Decision-tree knowledge** | **BUILT** — `knowledge/styling-and-bundle-decision-trees.md`: styling-approach selection (RSC-aware, zero-runtime-default) + bundle-size-regression triage. Chosen to **complement** #315's tree file (rendering/state/component/fetch/optimistic/store/slow-render/form), not duplicate it — styling and bundle-triage were the gaps. |
| 3 | **LSP server** | **BUILT (pre-existing, kept)** — `.lsp.json` (typescript-language-server / vscode-eslint-language-server / vscode-css-language-server), wired via `plugin.json` `lspServers`. Genuinely useful for a code domain; binaries install separately via `typescript-language-server` + `vscode-langservers-extracted` (§6). |
| 4 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §7. The two real, first-party frontend MCP servers (Microsoft Playwright MCP, Google Chrome DevTools MCP) each launch/drive a live browser → side-effecting + first-party-from-vendor → the doctrine routes both to recommend-not-bundle, with a `security-reviewer` gate. Documented the `claude mcp add` paths instead. No invented servers. |
| 5 | **Runnable script** | **BUILT** — `scripts/perf_budget.py` (`bundle` + `vitals` modes), stdlib-only, ruff-clean. Real value: turns the perf budget into a CI-gateable check (the recurring lesson from the CLS/LCP scenario). |
| 6 | **bin/ / monitors / output-styles / settings / themes** | **N-A** — no `rc-*` binary clears the "namespace + prefer Bash-tool skills" bar better than the existing advisory hook + the new `scripts/` tool; nothing to monitor (no long-running process); an output-style/theme would overlap the agents' Output Contract and `web-design`'s visual lane; no plugin-specific permission surface beyond `ravenclaude-core`. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory hook already cover architecture, component craft, state/data, rendering strategy, performance, and accessibility. The new decision trees + script extend reach without a 5th agent (team-growth-as-knowledge house rule). |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top entry for this build-out. No `NOTICE.md` (nothing third-party is bundled; the script is original stdlib-only; MCP/LSP packages are referenced + attributed inline, not vendored). |

## 10. Milestones

- **v0.2.2 (and earlier)** — 4-agent frontend-engineering team; 5 skills, 4 commands, 4 templates, 1 advisory hook, 12 best-practices; `.lsp.json` (TS/ESLint/CSS) wired via `plugin.json`. PR #315 added the consolidated decision-tree knowledge bank, best-practices, and templates.
- **this build-out (2026-06-05)** — value-add completeness: scenarios bank (4 field notes), a complementary `styling-and-bundle-decision-trees.md` (2 Mermaid trees), `scripts/perf_budget.py` (bundle + vitals checks), and CLAUDE.md §5–§10 (knowledge/scenario banks, LSP tier, recommended-not-bundle MCP, runnable tooling, value-add disposition). Bundled-MCP tier dispositioned recommend-not-bundle with reasons (§7).

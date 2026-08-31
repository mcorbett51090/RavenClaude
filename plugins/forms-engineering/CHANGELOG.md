# Changelog — forms-engineering

All notable changes to this plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the plugin uses [semantic versioning](https://semver.org/).

## [0.1.0] — 2026-08-17

Initial release. A **seam** between three existing owners rather than a new owner: `web-design` keeps form construction, accessibility and conversion diagnosis; `process-improvement` keeps control charts and control plans; `ravenclaude-core` keeps upload hardening, challenge-widget mechanics and every binding security verdict.

### Added

- **Skills** — `form-intake-and-triage-design` (request taxonomy, fields derived from the routing decision, routing rules as data, per-type response clocks, abandonment as a defect stream), `form-telemetry-and-control` (the measurement contract and the SPC hand-off), `harden-a-form-submission` (the server half `web-design` routes out by rule), `wire-form-substrate` (the RavenPower layer).
- **Knowledge** — form telemetry and the SPC seam; the anti-abuse ladder, honeypot failure modes and the named WCAG conflict; the seven durable form-platform axes; and the RavenPower substrate description, every changeable claim carrying its own re-verification command.
- **Best practices** — one rule per file, opening with an **inherited-rules table** that names the owner of everything deliberately not re-ruled here.
- **Templates** — form spec, telemetry plan, platform evaluation matrix.
- **Scenarios** — the honeypot that flagged real customers; the field removal that fell over a denominator change; the upload endpoint that stored nothing.
- **`scripts/form_metrics.py`** — session metrics with the denominator printed and per-field drop-off carrying its proxy label; `--emit-imr` emits a numbers-only individuals series for `process-improvement`'s `lss_calc.py imr`, and refuses below 20 individual observations.
- **`commands/design-form-intake.md`** and an advisory anti-pattern hook scoped strictly to rules this plugin owns.

⛔ The SPC hand-off this release introduces is labelled at every surface that makes it, including the script's own stderr:

> [NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not established practice. We found no published work joining web-form telemetry to SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that method and is not proof of universal absence.]

Upload handling and challenge-widget mechanics are cited, never restated — see [`../ravenclaude-core/rules/security.md`](../ravenclaude-core/rules/security.md) and [`../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md).

### Enforcement

- **Gate 219** — substrate separation and cite-don't-restate. A vendor token outside the two allowlisted substrate files must sit on a line that links into `ravenclaude-core`; the constitution's distinctive phrases may not be restated; any file discussing uploads or a challenge widget must carry a **resolving** link home; each cited upstream file must still contain the anchor text it is cited for. ⛔ The literal-match sub-checks cannot fail on a paraphrase — that limitation is stated in the checker's own header and a paraphrase fixture is committed to keep it visible.
- **Gate 220** — runs `form_metrics.py` against a committed fixture with hand-computed expectations, asserts the numbers-only stream contract as a **count** of violating lines, proves the marker reaches stderr, and **executes** the round-trip into `lss_calc.py imr`.
- **Gate 221** — the novel-synthesis marker on every documentation surface that makes the join, the WCAG conformance conflict as a named conflict only, and no vendor pricing in prose.
- **Gate 30** — a fire/silent fixture pair for the advisory hook, shipped in the same change as the hook.

### Deliberately not shipped

- **No agents.** See `CLAUDE.md` §4 for the ruling and what would reopen it.
- **No restatement** of `ravenclaude-core`'s upload or challenge-widget rules, or of `web-design`'s existing form rules.
- **No re-implementation of control charts** — `lss_calc.py` is fed, not duplicated.
- **No vendor pricing, no feature matrix, no `substrate/` directory.**

[0.1.0]: https://github.com/mcorbett51090/RavenClaude

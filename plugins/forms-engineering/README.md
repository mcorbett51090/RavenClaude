# forms-engineering

**A form is the entry point of a process.** This plugin owns the part nobody else in this marketplace does: the **intake** behind the form, the **measurement contract** in front of it, and the **trust boundary** underneath it.

It is a **seam**, not a new owner. `web-design` keeps form construction, form accessibility and conversion diagnosis. `process-improvement` keeps control charts and control plans. `ravenclaude-core` keeps upload hardening, challenge-widget mechanics and every binding security verdict. This plugin links to all of them and restates none of them — enforced by a CI gate, not by intention.

## Install

```sh
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install forms-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Start here

```
/forms-engineering:design-form-intake  a contact form whose submissions become support tickets
```

## What's inside

| Surface | What it is for |
| --- | --- |
| [`skills/form-intake-and-triage-design/`](skills/form-intake-and-triage-design/SKILL.md) | Request taxonomy, fields derived from the routing decision, routing rules as data, per-type response clocks, self-serve-vs-escalate bright lines, abandonment read as a defect stream |
| [`skills/form-telemetry-and-control/`](skills/form-telemetry-and-control/SKILL.md) | The measurement contract: which events, which denominator, what a defect is, how per-field drop-off lies, and the hand-off to statistical process control |
| [`skills/harden-a-form-submission/`](skills/harden-a-form-submission/SKILL.md) | The server half `web-design` routes out by rule: validation parity, the anti-abuse ladder, honeypot design, duplicate guards, webhook verification, PII minimisation |
| `skills/wire-form-substrate/` | The RavenPower stack layer — one of exactly two vendor-specific files here. Deliberately **not linked** from this table: the dependency is one-way, so deleting the substrate layer leaves nothing dangling |
| [`knowledge/`](knowledge/) | Dated fact banks: form telemetry and the SPC seam, the anti-abuse ladder, the seven platform-selection axes |
| [`best-practices/`](best-practices/) | Named, citable rules — **and an inherited-rules table** that points at the owner of everything this plugin deliberately does not re-rule |
| [`templates/`](templates/) | The form spec, the telemetry plan, the platform evaluation matrix |
| [`scenarios/`](scenarios/) | Dated, unverified engagement narratives |
| [`scripts/form_metrics.py`](scripts/form_metrics.py) | Session metrics with the denominator printed; `--emit-imr` feeds `process-improvement`'s I-MR calculator |
| [`hooks/`](hooks/) | An advisory anti-pattern hook, scoped strictly to rules this plugin owns |

**No `agents/` directory, deliberately** — see [`CLAUDE.md`](CLAUDE.md) §4. Reachability comes from reciprocal priors in the agents that would otherwise miss this work, plus the command.

## The measurement seam, end to end

```sh
python3 plugins/forms-engineering/scripts/form_metrics.py sessions.csv

python3 plugins/process-improvement/scripts/lss_calc.py imr \
  --values "$(python3 plugins/forms-engineering/scripts/form_metrics.py --emit-imr sessions.csv)"
```

Command substitution, not a pipe — `lss_calc.py imr` requires `--values` and reads no stdin. `--emit-imr` writes numbers only to stdout for exactly that reason, and refuses below **20 individual observations**.

## ⛔ Two honesty constraints, both enforced by permanent CI gates

1. **Applying statistical process control to form telemetry is our synthesis, not established practice.** Two targeted open-web searches (2026-08-17) found no published work joining the two. Every surface that makes the join carries a verbatim marker, and `form_metrics.py` prints it on stderr in every mode.
2. **The challenge widget's WCAG conformance level is disputed by its own vendor's documentation.** No surface here states either level unqualified; it ships only as a named conflict.


> [NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not established practice. We found no published work joining web-form telemetry to SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that method and is not proof of universal absence.]

And one negative constraint: **no vendor pricing and no feature matrix anywhere.** Both go stale within a quarter.

## Boundaries

Read [`CLAUDE.md`](CLAUDE.md) §1 and §7 before adding anything. The short version: if another plugin already rules on it, link — do not re-rule. The binding security verdict is always [`../ravenclaude-core/agents/security-reviewer.md`](../ravenclaude-core/agents/security-reviewer.md)'s, zero-exception.

## License

MIT — see [`../../LICENSE`](../../LICENSE).

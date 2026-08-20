# P4 — Path-keyed harness: what it found, and two corrections to the plan

**Phase 4 of** [`plan.md`](plan.md). `depends_on_claims: [5, 12, 14]`

The harness runs across **308 artifacts with zero inventory entries authored** —
that decoupling is the phase's whole point. This document records what the first
runs actually returned, including the findings I **withdrew** after checking them.

---

## 1. ⛔ GT13 does not reproduce. The plan's P4 acceptance #1 is not satisfiable as written.

Plan §6.6 acceptance #1: *"The skill-reference resolver reproduces GT13's two real
findings and its negative control."* GT13 recorded two dangling `SKILL.md`
references. **Neither is dangling today**, and the reasons differ:

| GT13 claim | Measured 2026-08-19 | Verdict |
|---|---|---|
| `webfetch-hardening` → a knowledge file that does not exist | The link target is `docs/research/2026-06-02-data-viz-agent/webfetch-injection-memo.md`. `ls` → **the file exists.** The `../../../../` prefix resolves to the repo root correctly. | **Not dangling.** |
| `cross-platform-determinism` → `scripts/generate-repo-guide.py`, absent | The file is genuinely absent, but the mention is not a link. `SKILL.md:14` reads: *"the **since-removed** `scripts/generate-repo-guide.py`; its successor is `scripts/generate-index-dashboard.py`"* — a backticked prose reference to a deliberately removed file, with its replacement named in the same sentence. | **Not a defect.** Flagging it is the recorded *"a grep is satisfied by the thing being described"* class. |

**What this changes.** GT13 was the plan's decisive datum for shipping the harness
first (*"a 10-line resolver found 2 real dangling refs… that check should run
tomorrow, not in month 4"*). The **sequencing argument survives** — a path-keyed
harness still runs on day 1 across 308 artifacts, and it still found a real
coverage hole (§3) plus a real side-effect hazard (§4) in its first two runs. What
does not survive is the specific evidence: **the resolver reproduces 0 of GT13's 2
findings**, and building it to produce two would have meant tuning a detector to
hit a predetermined number.

⛔ Recorded rather than quietly dropped, because the acceptance criterion is now
unmeetable and a future reader would otherwise assume it passed.

---

## 2. Four findings I withdrew, and why

The first sweep reported **20 artifact-level findings**. Fifteen were **my
detector's** defects, not the repo's. Each is recorded because the reasoning is
the reusable part.

| Reported | Count | Verdict | Why |
|---|---|---|---|
| `unregistered` hooks | 11 | **withdrawn** | 7 are `_`-prefixed **shared helpers** (`_advise.sh`, `_scrub.sh`, `_emit-event.sh`…) reached through their *caller*, never through an event registration. 4 are **other-host adapters** (`codex`/`copilot`/`cursor`/`gemini`) wired into `.codex/hooks.json` and `.github/hooks`, not Claude Code's `hooks.json`. A reachability probe that models only one of three reachability routes is measuring its own ignorance. |
| `missing-name` skills | 6 | **withdrawn** | Those 6 SKILL.md files carry `description:` and `allowed-tools:` but no `name:`. The host **derives the name from the directory**, so they load fine. This is a convention inconsistency, not unreachability. `description:` **is** gated — it is the only field a model reads when deciding whether to load a skill at all. |
| `dangling-reference` | 2 | **withdrawn** | The targets were `../skills/<pattern-name>.md` (a named placeholder) and `...` (an ellipsis in an example). Both are **authoring templates**. Fenced code is now stripped and placeholder-shaped targets skipped. |
| `orphan` script | 1 | **withdrawn** | `_model_catalog.py` is a Python module. Nothing imports it *by filename* — imports name the **module**. It is also named in `plugins/ravenclaude-core/CLAUDE.md`. ⚠ Honest caveat: a doc mention is a weaker reachability signal than a call site, and the plan's own class definition lists workflows, `bin/rc` verbs, hooks, SKILL.md and scripts — **not** CLAUDE.md. Widening the haystack to include it is a judgment call, recorded here rather than buried. |

**Two false findings in a first run is how a new detector gets switched off in
week two.** Every withdrawal is now encoded as a comment at the detector, so the
reasoning cannot be lost and re-litigated.

---

## 3. ✅ The R8 assertion found a real coverage hole on its first run

First run: `independent census = 308`, `artifacts enumerated = 299`. A divergence
of exactly **9** — the `commands/` population, which the census counted and **no
probe class covered**.

That is the sweep-of-the-sweep doing precisely what it exists for: it detected a
gap in the harness itself, from a source (`git ls-files`) the harness does not
write. A registry-derived denominator would have shrunk alongside the enumeration
and reported green.

`command-static` was added; the count is now 308 == 308.

---

## 4. ✅ A real side-effect hazard, caught by its own consequence

`script-selftest` originally **executed** all 183 scripts with
`--must-fail-convention` to discover which implemented it. Two problems:

1. It took **5m24s**, unacceptable for a PR gate.
2. ⛔ **A script that does not parse arguments simply RUNS.** The probe left a
   stray 10,678-byte file literally named `--must-fail-convention` in the repo
   root — a copy of `forge-route.py`. A probe must not have side effects on the
   thing it is probing.

Fixed by **reading before executing**: the declaration is a literal string in the
file, so the source is grepped and only declaring tools are run. Runtime dropped
to **33s** and the side effect is gone.

Separately, `hook-benign-passthrough` originally ran all 47 real shipping guards
against the **live repo** — violating this file's own security overlay. It now runs
in a `mktemp` project root with `HOME` and `CLAUDE_PROJECT_DIR` redirected, and is
deferred to `--tier T1`, matching plan §7.4's nightly tier.

---

## 5. What the harness reports today

```
CLASS                      TIER          STRENGTH      VERDICTS
hook-registration          reachability  static        pass=47
skill-static               reachability  static        pass=54
agent-static               reachability  static        pass=15
command-static             reachability  static        pass=9
script-callgraph           reachability  static        pass=183
script-selftest            effect        executed      pass=3  skip=180
hook-benign-passthrough    effect        executed      pass=47   (T1)
canary-permanently-red     effect        executed      pass=1

independent census   : 308
artifacts enumerated : 308  ✓
probes registered    : 8
probes executed      : 7    ✓  (hook-benign-passthrough deferred to T1, NAMED)
classes never invoked: none ✓
permanently-red canary: RED (correct)
```

⛔ **A zero-finding sweep is only meaningful because its controls are proven.**
`--capping-table` shows all 7 non-canary class controls **firing**; `--must-fail`
proves the label scrubber constrains its vocabulary and the canary is red. Without
those, "nothing is broken" and "the sweep is blind" would be the same output.

⛔ **`skip=180` is not `pass=180`.** 180 scripts declare no self-test convention.
That is an honest absence, rendered as `skip`, and it is what `verify.strength`
will surface to a reader in P5/P6.

---

## 6. Claim 14 — capped, per the plan's exit condition

Plan §17 row 14 exit condition: *"any class whose control does not fire is demoted
to `tier: none` with a written rationale. A probe with no working control does not
ship."*

**All 7 non-canary controls fire**, so no class is demoted. Three classes are
`tier: reachability, strength: static` **up front** — they check findability and
reference integrity, never execution — and P5's `verify.strength` badge is what
renders that cap to a reader rather than letting it hide behind a checkmark.

`hook-benign-passthrough` carries an honest scope note at its definition: it proves
a hook does **not** deny an unrelated benign call (the deny-everything failure
mode, which is real and which a one-sided probe cannot see). It does **not** prove
the hook denies what it should — that needs per-hook trigger knowledge this generic
runner does not have.

---

## 7. Claim 5 / GT16 settled early

`inventory-census.py --explain` states the counting rule. Measured: **47 hooks**,
not 48 — `hooks/*.sh` at depth 1, excluding `hooks/tests/**` and `hooks.json`,
**including** `_`-prefixed helpers (they ship, execute, and can break). 54 skills,
15 agents, 9 commands, 45 plugin scripts, 138 root scripts. **Total 308.**

The rule is written into the script, so it cannot drift again — which was the
actual deliverable, the number being downstream of it.

---
target_path: plugins/ravenclaude-core/skills/probe-kit/SKILL.md
description: Run a ready-made CONTROL probe alongside any negative result — http/dns/file/cmd. A negative is not a diagnosis until a positive control on the same subsystem has been observed. Makes the right action one line instead of an idea you have to have.
allowed-tools: Bash, Read
audience: [coder, architect, reviewer, tester, any agent diagnosing a reported defect]
counters_failure_modes:
  [
    unfalsified premise promoted to repo fact,
    inferential distance (true observation -> false inference),
    silent fail-open (a check that reports clean because it could not see),
  ]
sources:
  - docs/plans/2026-08-08-premise-gate/incidents.md §Incident 1 (the measured cost asymmetry)
  - docs/plans/2026-08-08-premise-gate/plan.md §2.4 (control != kill_shot), §6 Alternative 1
  - plugins/ravenclaude-core/knowledge/verification-discipline.md Rule 6
---

# probe-kit

> **A negative result is not a diagnosis until a positive control on the same subsystem has been
> observed.**

A 404, an NXDOMAIN, a missing file, a `command not found` tells you what did **not** happen in **one
probe**. It never tells you *why*, and it never tells you the blast radius. Those are separate
measurements — and the one that closes the gap is a **control**: a second, differently-shaped probe on
the same subsystem that is *expected to succeed*. If the control succeeds, your negative is real. If
the control **also** fails, you have learned about your instrument and **nothing** about the subject.

```shell
rc probe http https://host/some/path    # + a control on the same host
rc probe dns  api.example.com           # + the parent zone
rc probe file /some/path                # + the containing directory
rc probe cmd  timeout                   # + a command that must exist
rc probe --explain [http|dns|file|cmd]  # what a negative does NOT license
rc probe --self-test                    # prove the instrument first
```

One line, no setup, no config, no state. It prints both probes side by side, a verdict, and a
copy-pasteable one-liner for the control it ran.

## The worked example — why this exists

`[measured 2026-08-07 / 08; replayed live 2026-08-08]`

```
GET https://www.ravenpower.net/cdn-cgi/l/email-protection   ->  404
```

That became *"the decoder is broken, therefore every visitor sees a mangled address. P1."* On that
premise, before anyone tested it: an **85-line component**, **10 call sites** converted, **15**
`<!--email_off-->` marker pairs across **5 files**, a header comment asserting the cause as fact
("measured 2026-08-07"), a go-live checklist item **pushed to `main`**, and **two turns** of
owner-facing architectural advice.

All of it wrong. The controls, none of which was run:

```
GET /cdn-cgi/l/email-protection  -> 404   EXPECTED — a PLACEHOLDER href. Nothing fetches it.
GET /cdn-cgi/trace               -> 200   the edge is healthy.
GET .../email-decode.min.js      -> 200   the decoder is being served.

a real browser against the "broken" production site, none of the fix deployed:
  span.__cf_email__ remaining ... 0
  href ......................... mailto:matt@ravenpower.net
  "[email protected]" in body ... false
```

**No user had ever seen the reported bug.** Worse: the "fix" opted 15 addresses out of the
anti-scraping protection that was the only thing the feature was doing.

**The cost asymmetry is the whole point.** The disconfirming probe cost **~10 seconds**. The
construction cost hours and touched **16 files**. The observation (`404`) was **true**; the inference
(`the decoder is broken`) was **false**. Nothing checks that gap for you.

**The control was cheap and nobody ran it, because running it required thinking of it.** This kit is
the thinking-of-it part, pre-done. Replayed today it is one command:

```
$ rc probe http https://www.ravenpower.net/cdn-cgi/l/email-protection
  SUBJECT  GET .../cdn-cgi/l/email-protection  ->  HTTP 404   [NEGATIVE]
  CONTROL  GET .../cdn-cgi/trace               ->  HTTP 200   [POSITIVE]
  VERDICT  negative result CONFIRMED by control
           ...It still does NOT license a diagnosis of the subsystem or of user impact.
```

## What a negative does and does NOT license

| Probe | A negative licenses **only** | It does **NOT** license |
|---|---|---|
| `http` | "this URL returned this status, now, from this client" | "the host is down" · "the feature is broken" · "every visitor is affected" — some URLs are **supposed** to 404 |
| `dns` | "this resolver returned no record for this name, now" | "the domain doesn't exist" — split-horizon, VPN, captive portal, propagation delay |
| `file` | "this process, this uid, this cwd could not stat this path" | "it was never created" — wrong cwd/base path, or a permission-denied traverse, reads identically |
| `cmd` | "this name is not on **this** PATH in **this** process" | "the tool isn't installed" · "this host can't do X" — that is the capability-grounding error |

Run `--explain <type>` for the full version with the in-repo worked cases (the `cmd` one is this
repo's own macOS door 2: stock macOS has no GNU `timeout`, so `127` read as an empty result and
silently disarmed the decision-review tribunal on every session).

## Verdicts and the exit-code contract

| Exit | Verdict | Meaning |
|---|---|---|
| `0` | POSITIVE | The subject succeeded. Nothing negative to diagnose. |
| `1` | **CONFIRMED** | Subject negative, control positive — the negative is about the **target**. |
| `2` | **⛔ SUSPECT** | The control **also failed**. Your probe target may be wrong, not the subject. Fix the control first. |
| `3` | ⛔ INCONCLUSIVE | The control could not run (no network/resolver/permission), **or** the control was the same probe as the subject. Evidence about your instrument only. |
| `64` | usage | — |

**`1` is not "done".** CONFIRMED means the instrument works. It still does not license a claim about
the subsystem or about user impact — for that, measure what the user experiences (verification
discipline Rule 7), not the nearest proxy.

## Two invariants worth knowing

**A re-run is not a control.** The control must be a *different* probe (plan §2.4: `control` must
differ from `kill_shot`). A repeat of the same request moves in lockstep with the subject under every
hypothesis, so it distinguishes nothing. The kit refuses it: `/cdn-cgi/trace` derives the site root
as its control (not itself), and an explicit `--control` equal to the subject returns `3` with
"NOT A CONTROL", never a verdict.

**Prove the instrument before believing it.** `--self-test` runs 27 offline-capable fixtures
(loopback HTTP server, temp trees, a deliberately broken `PATH`) and includes a **teeth** subtest
asserting the four verdicts are mutually distinct — a constant-verdict stub fails 11 subtests. A
skip is printed as `LOUD SKIP (NOT A PASS)`, never counted as a pass.

## When to reach for it

- **Before writing the first line** justified by a defect diagnosis. That is the moment Incident 1
  was lost.
- The instant you're about to write *"X is broken"*, *"every user…"*, *"the decoder/API/DNS is…"*
  into a **durable artifact** — a header comment, a knowledge file, a checklist, a PR body.
- When a probe returns nothing and you're about to conclude absence.
- When a check reports **clean** and you have not shown it *can* report dirty.

## Honest limits

- **This is not a gate.** It blocks nothing and enforces nothing. It fires only if you reach for it —
  and Incident 1's author felt no need to reach. It ships as the deliberately
  **claim-#11-independent** alternative (plan §6, Alternative 1): it asks nobody to believe that
  gates beat prose, because it changes a **cost**, not a rule. If the fail-closed gate is disabled or
  its premise is wrong, this still works.
- **It bounds inference, not correctness.** A CONFIRMED negative is still not a user-visible
  measurement. For "is anyone actually affected?", load the real thing in a real browser.
- **Four subsystems only** — HTTP, DNS, filesystem, PATH. Anything else, apply the rule by hand: name
  the control *before* you run the probe, and predict its result under both hypotheses. If your
  predictions are identical, it is not a control.

## References

- Engine: [`bin/probe-kit.sh`](../../bin/probe-kit.sh) (bash 3.2 / stock-macOS safe;
  no GNU `timeout`, `grep -P` or `sed -i`; every probe carries its own ceiling so nothing hangs)
- The rule in context: [`knowledge/verification-discipline.md`](../../knowledge/verification-discipline.md) Rule 6
- Evidence base: [`docs/plans/2026-08-08-premise-gate/incidents.md`](../../../../docs/plans/2026-08-08-premise-gate/incidents.md)
- Where it sits in the plan: [`docs/plans/2026-08-08-premise-gate/plan.md`](../../../../docs/plans/2026-08-08-premise-gate/plan.md) §6

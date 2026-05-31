---
description: "Write up a statistical result for a non-statistician — lead with a plain-language bottom line tied to the decision, attach the effect size and CI, surface assumptions and caveats in the open, and date any volatile claim."
argument-hint: "[the result to communicate, e.g. 'the A/B test outcome for the leadership readout']"
---

# Communicate results with uncertainty

You are running `/applied-statistics:communicate-results-with-uncertainty`. Turn the user's result (`$ARGUMENTS`) into a deliverable a decision-maker can act on — the interval not the point, the caveat in the open not buried — the communication discipline the `applied-statistician` agent owns.

## When to use this

You have a finished analysis and need to communicate it to a stakeholder (a written report, a go/no-go memo, a dashboard annotation). NOT for the analysis itself — run the test, check assumptions, and correct for multiplicity first.

## Steps

1. **Open with a one-sentence plain-language bottom line tied to the decision** (`report-communicate-uncertainty-to-non-statisticians.md`): what the stakeholder should *do*, tied to their threshold — the deliverable is the decision, not the test output.
2. **Put the effect size + 95% CI right behind the bottom line, p-value secondary** (`effect-size-and-ci-not-bare-p.md`): translate the magnitude into the stakeholder's units ("+4 conversions per 100 visitors", not just "d = 0.18"). On large n, a trivially small effect can be "highly significant" — check whether it clears the decision threshold.
3. **Handle a non-significant result honestly** (`effect-size-and-ci-not-bare-p.md`): never call it "no effect" — give the CI and the minimum detectable effect (MDE) the design could catch; absence of evidence is not evidence of absence.
4. **Surface assumptions and pitfalls in the open** (`report-communicate-uncertainty-to-non-statisticians.md`): state which assumption checks ran (or the fallback taken), which pitfalls are in play, and what could change the conclusion.
5. **Guard the causal language** (`report-communicate-uncertainty-to-non-statisticians.md`): don't let "drives / causes / impact" into the bottom line unless a causal design backs it — downgrade to "associated with" otherwise.
6. **Date anything volatile** (`report-communicate-uncertainty-to-non-statisticians.md`): tooling versions and vendor A/B-method claims get a retrieval date. Shape the deliverable per the plugin's `templates/statistical-report.md`; for a dashboard metric, emit the CI / uncertainty annotation.

## Guardrails

- Never hand over a bare p-value, a naked point estimate, or a forecast point line with no interval.
- A buried caveat is an undisclosed risk — assumptions and pitfalls go in the open, not a footnote.
- "Cleared by a hair" vs "cleared with room" changes how much to trust a go/no-go call — the CI rides along even when only a verdict was asked for.

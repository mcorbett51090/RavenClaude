---
name: author-quickstart-and-sample-app
description: Author a copy-paste-runnable quickstart and/or a minimal golden-path sample app that minimizes time-to-first-hello-world (TTFHW), with every code block language-tagged, an explicit "you should see …" success check, and the friction logged back to PM/eng. Reach for this when the user asks to write a quickstart, build a sample app, or shrink TTFHW. Used by `developer-advocate` (primary).
---

# Skill: author-quickstart-and-sample-app

> **Invoked by:** `developer-advocate` (primary). Co-driven with `devrel-strategist` when the motion calls for golden-path content.
>
> **When to invoke:** "write a quickstart"; "build a sample app for <use case>"; "our getting-started takes too long — shrink it"; building the golden path.
>
> **Output:** a quickstart and/or sample app that runs unmodified, names its success criterion, reports its TTFHW, and routes friction to PM/eng. Use [`../../templates/quickstart-tutorial.md`](../../templates/quickstart-tutorial.md).

## Procedure

1. **Define first hello-world for this product.** What is the smallest *real* result the developer can produce — a returned API response, a rendered widget, a passing call? That is the activation event; everything before it is overhead to cut.
2. **Map and minimize the path to it.** List every step from zero to first hello-world. Cut or defer every dependency, account step, and config that doesn't gate the result. The metric you are optimizing is **TTFHW** (see [`../../knowledge/devrel-metrics.md`](../../knowledge/devrel-metrics.md)).
3. **Write the golden path, one happy path only.** Use the template's structure: prerequisites → install → minimal runnable example → success check → next step.
4. **Tag every code block with a runnable language** (```bash, ```python, ```js, ```go …) — never a bare ``` fence. Each block must run unmodified (no `<placeholder>` the developer can't resolve from the page).
5. **Add the explicit success check.** "You should see `Hello, world` in the response." The developer must know, unambiguously, that they succeeded.
6. **Run it (if you can).** With `Bash`, actually execute the path and confirm the success check fires. If you can't run it, say so — don't claim "runs unmodified" untested.
7. **Log the friction to PM/eng.** Every awkward step, missing default, or confusing error you hit is product feedback — record it (the loop in [`../../best-practices/close-the-product-feedback-loop.md`](../../best-practices/close-the-product-feedback-loop.md)).
8. **Report the TTFHW** — measured (you timed it) or estimated, and what you cut to shrink it.

## Worked example

> User: "Write a quickstart for our REST API."

- First hello-world = a successful authenticated `GET` returning real data.
- Path audit: signup → API key → install client → make call. The API-key step is the TTFHW bottleneck → ship a pre-provisioned sandbox key so the developer reaches first call in one command.

```bash
# install + first call — runs unmodified against the public sandbox
pip install acme-sdk
export ACME_KEY="sandbox-demo-key"          # pre-provisioned; no signup to first call
python -c "import acme; print(acme.ping())"  # you should see: {'status': 'ok'}
```

- Success check: `{'status': 'ok'}`. TTFHW (measured): ~90 seconds on a clean machine, down from ~12 minutes once the signup step is deferred past first hello-world.
- Friction logged to PM: the production flow forces an API key *before* any call — recommend a sandbox/demo key so TTFHW isn't gated on account creation.

## Guardrails
- Never ship a code block with a bare ``` fence or an unresolved `<placeholder>` — it can't be copy-paste-run (the advisory hook flags bare fences).
- Never claim "runs unmodified" you didn't verify — run it with `Bash` or mark it untested.
- A quickstart is one happy path, not a reference — exhaustive options/edge cases belong to `technical-writing-docs`.
- Always name the success criterion and report TTFHW (see [`../../best-practices/optimize-time-to-first-hello-world.md`](../../best-practices/optimize-time-to-first-hello-world.md) and [`../../best-practices/sample-apps-must-run-unmodified.md`](../../best-practices/sample-apps-must-run-unmodified.md)).

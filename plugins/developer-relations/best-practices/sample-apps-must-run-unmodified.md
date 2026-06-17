# Sample apps and quickstarts must run unmodified

**Status:** Absolute rule
**Domain:** Developer experience / content quality
**Applies to:** `developer-relations`

---

## Why this exists

A sample that doesn't run is worse than no sample — it spends the developer's trust and rarely gets it back. The whole value of a quickstart or sample app is that the developer can copy-paste-run it and reach first hello-world; the moment a step fails, an `<placeholder>` can't be resolved, or a code block has no language tag to copy cleanly, the golden path is broken and the developer concludes the *product* is broken. "Runs unmodified" is not a nicety — it is the contract that makes the activation event ([`./optimize-time-to-first-hello-world.md`](./optimize-time-to-first-hello-world.md)) possible.

## How to apply

Every code block carries a runnable language tag, and the author actually runs the path before shipping it:

````
Good:
```bash
pip install acme-sdk && python -c "import acme; print(acme.ping())"
```
You should see: {'status': 'ok'}

Bad:
```
install the sdk, then run ping() with <your-api-key>      # bare fence, unresolved placeholder
```
````

**Do:**
- Tag every fenced block with its language (```bash, ```python, ```js, ```go …) — never a bare ``` fence.
- Run the full path on a clean machine before publishing; if you have `Bash`, execute it.
- Resolve every placeholder the reader can't ("use a pre-provisioned sandbox key", not `<your-api-key>` with no way to get one on the page).
- Name the explicit "you should see …" success check.

**Don't:**
- Ship a code block you haven't run, or claim "runs unmodified" untested.
- Leave a bare ``` fence (the advisory hook [`../hooks/flag-devrel-smells.sh`](../hooks/flag-devrel-smells.sh) flags it).
- Pad a quickstart into a reference manual — one happy path; exhaustive options belong to `technical-writing-docs`.

## Edge cases / when the rule does NOT apply

- **Illustrative pseudocode** clearly labeled as such (not a copy-paste path) may omit a runnable tag — but never inside the quickstart's golden path.
- **Output blocks** showing expected results are fenced for formatting, not execution — that's correct; the *input* blocks are what must be runnable.

## See also

- [`./optimize-time-to-first-hello-world.md`](./optimize-time-to-first-hello-world.md) — the activation rule this enables.
- [`../templates/quickstart-tutorial.md`](../templates/quickstart-tutorial.md) — the template with the runnable-block author checklist.
- [`../skills/author-quickstart-and-sample-app/SKILL.md`](../skills/author-quickstart-and-sample-app/SKILL.md) — the run-it-before-you-ship-it procedure.

## Provenance

Codifies house opinion "a sample that doesn't run is worse than no sample" in [`../CLAUDE.md`](../CLAUDE.md) §3/§4. The advisory hook [`../hooks/flag-devrel-smells.sh`](../hooks/flag-devrel-smells.sh) flags bare code fences and missing success criteria (last reviewed 2026-06-17).

---

_Last reviewed: 2026-06-17 by `claude`_

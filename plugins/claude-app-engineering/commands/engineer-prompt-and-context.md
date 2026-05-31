---
description: "Engineer a Claude prompt and its context window — climb the leverage ladder (clear+direct+examples first, multi-agent last), curate the right tokens and compact stale history, force structured output via a tool, and keep thinking config stable and dated."
argument-hint: "[the prompt problem, e.g. 'the model keeps missing edge cases in extraction']"
---

# Engineer the prompt and context

You are running `/claude-app-engineering:engineer-prompt-and-context`. Fix or build the prompt the user described (`$ARGUMENTS`) by climbing the leverage ladder and curating the context window — the work the `prompt-and-context-engineer` agent owns. Most "the model won't do what I want" tickets are an underspecified prompt, not a model limitation.

## When to use this

The model's output is wrong, inconsistent, or unstructured and you want to improve it without changing the architecture. NOT for the build-surface/model decision (that is `/claude-app-engineering:design-claude-app-architecture`).

## Steps

1. **Climb the prompt leverage ladder one rung at a time** (`prompt-climb-the-leverage-ladder.md`): clear+direct instruction first, then examples, then structure — stop at the first rung that works against an eval. Reaching for chain-of-thought, a fine-tune-equivalent, or a multi-agent orchestration before exhausting clear+direct+examples is the anti-pattern; newer Claude models can *regress* when over-prompted.
2. **Curate the right set of tokens, in the right order** (`context-budget-the-1m-window.md`): ask at each step what *should* be in the window and what should be compacted — irrelevant or stale context measurably degrades output (context rot) and costs money on every uncached request; a 1M window is not a license to dump everything in.
3. **For a long-running agent, actively shrink stale history** (`context-budget-the-1m-window.md`): prune superseded tool-results rather than treating the window as append-only.
4. **Force structured output via a tool, not a regex over prose** (`output-structured-via-forced-tool.md`): when the app needs machine-readable output, define a tool whose `input_schema` is the target shape and force it with `tool_choice` — asking for "JSON only" and parsing free text throws in production.
5. **Keep the thinking config stable and dated** (`context-keep-thinking-config-stable-and-dated.md`): pin and date the extended-thinking settings so a config drift isn't mistaken for a prompt regression.
6. **Validate every change against the eval harness** (`evals-before-vibes.md`): each rung of the ladder is justified by a delta on the golden set — run `/claude-app-engineering:build-eval-harness` so the prompt change ships on a number, not vibes. Keep the static prefix cache-stable as you edit (`cache-the-static-prefix.md`).

## Guardrails

- Jumping to multi-agent or chain-of-thought before clear+direct+examples costs latency, tokens, and debuggability for a problem a clear instruction would have solved.
- Over-prompting a capable model on a trivial task can hurt — don't add "think step by step" reflexively.
- Parsing JSON out of prose works until a stray sentence or markdown fence breaks the parse in prod — force the tool instead.

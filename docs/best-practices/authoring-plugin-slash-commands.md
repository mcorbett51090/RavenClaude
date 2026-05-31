# Authoring plugin slash commands

**Status:** Pattern · **Applies to:** every plugin under `plugins/`

How to write the `plugins/<plugin>/commands/*.md` slash commands that ship to consumers and surface on the dashboard's **Commands** tab. Grounded in a 2026-05 fact-check of Claude Code's command/skill model (see the "How commands actually run" section — it changes what you can promise the user).

## How commands actually run (the load-bearing facts)

- **A command is a prompt that runs *inside* the user's Claude Code session** — not a shell script the OS executes. When the user types the command, Claude reads the markdown body as its instructions and does the work with its tools and judgment.
- **It is invoked NAMESPACED: `/<plugin>:<command>`** (e.g. `/salesforce:scaffold-apex-trigger`). Plugin commands are always namespaced, so two plugins can ship the same command name without colliding. Author the body so it reads correctly under that invocation.
- **A web page / the dashboard CANNOT run a command for the user.** There is no browser→session bridge. The dashboard's honest, working UX is **Copy → paste into Claude Code**. Never write a command (or a dashboard affordance) that implies a button on a web page will execute domain work. (The only press-to-run buttons are the fixed, non-destructive `/__run` ops — install/update/status — which are not domain commands.)
- **Commands are designed for multi-step playbooks.** A command body legitimately says "do step 1, then 2, then 3, verify, report." That's the intended use — ship rich procedures, not one-liners.

## Required frontmatter

```yaml
---
description: One sentence, action-first, ≤ ~200 chars. This is what the dashboard
  Commands tab shows and what Claude uses to decide when to auto-invoke. Quote it
  if it contains a colon-space (the strict-YAML gate rejects an unquoted `foo: bar`).
argument-hint: "[object-name] [--flag]"   # optional but recommended: shows in autocomplete
---
```

- **`description` is mandatory** and gated (`scripts/check-frontmatter.py` now scans `commands/*.md`; a missing/blank description fails CI).
- **`argument-hint`** is real and worth adding — it shows the user what to type after the command in the `/` autocomplete.
- Use **`$ARGUMENTS`** (all args) or **`$1`, `$2`** (positional) in the body where the command takes input.

## Body shape (the template)

```markdown
# <Command title>

You are running `/<plugin>:<command-name>`. <One-line restatement of the goal.>

## When to use this
<1-2 sentences: the situation this command is for, and when NOT to use it.>

## Inputs
- `$1` / `$ARGUMENTS` — <what the user passes>; if absent, ask once via AskUserQuestion.

## Steps
1. <First concrete step — read X, gather Y.>
2. <Do the domain work, using the plugin's knowledge files / decision trees.>
3. <Verify — run the relevant check / show the diff for approval.>
4. <Report: what changed, what's left for the human (deep-link / one action).>

## Guardrails
- <Domain-specific cautions: what to never do, what needs confirmation.>
- Inherit the core protocols (Capability Grounding, Last-Mile, Structured Output)
  — don't restate them; cite them.
```

## House rules for command authoring

1. **Be genuinely useful, not filler.** Each command earns its place by encoding real domain craft (a pattern, a checklist, a gotcha) the plugin's knowledge files back up — not a thin wrapper around one tool call.
2. **Ground it in the plugin.** Reference the plugin's own knowledge/best-practices/decision-trees; a command is a *playbook entry point* into that material.
3. **Match the domain's depth.** 5+ per plugin is the floor; broad domains (Salesforce, Power Platform, Azure) carry more because they have more distinct high-value workflows. Don't pad a narrow domain to hit a number.
4. **Surface the human-only residue** per the Last-Mile protocol — the command does everything automatable and tees up the rest as a confirm/click with a deep link.
5. **Never imply browser execution.** Bodies and descriptions describe what happens *in the Claude session*. The dashboard copy-button is the only "run" affordance for domain commands.

## What the dashboard does with your command

The Commands tab auto-discovers every `commands/*.md`, shows the `description`, the namespaced `/<plugin>:<command>` string, a **Copy** button, and a 5th-grade tooltip ("copy it, paste it into Claude Code, it runs the whole job there"). You don't wire anything — authoring the file is enough.

---
name: tui-design
description: "Decide whether a full-screen TUI is warranted (vs a scriptable CLI), pick the framework (Ink / Bubble Tea / Textual / ratatui), and design the render-loop + non-TTY fallback. Use for interactive terminal dashboards, pickers, and wizards."
---

# TUI Design

## First: is a TUI even warranted?

A full-screen TUI is right for **sustained, stateful interaction** — dashboards, file/log explorers, multi-step wizards. For a one-shot job a **scriptable CLI** wins (it pipes, automates, composes). If you take the screen, you owe a **non-TTY fallback**.

## Framework by language + model

| Language | Framework | Model |
|---|---|---|
| TS/JS | **Ink** | React-style components |
| Go | **Bubble Tea** (+ Lip Gloss) | Elm-style model/update/view |
| Python | **Textual** | CSS-like, async |
| Rust | **ratatui** | Immediate-mode, you own the loop |

## The render loop

Keep a **model → update → view** cycle: input arrives as messages, the model updates, the view re-renders. **Diff, don't repaint** the whole screen each tick. Never block the render thread — push slow work to a task and feed results back as messages.

## Survive reality

- **Resize** is a first-class event: re-lay-out, don't corrupt the buffer.
- **Restore the terminal** (exit alt-screen, show cursor, leave raw mode) on every exit path — including panics and signals.
- **Non-TTY**: when stdout/stdin isn't a terminal, fall back to plain line output (or refuse with a clear message) — never emit alt-screen/escape codes into a pipe.
- **Accessibility**: keyboard-first navigation; keep output screen-reader-tolerant.

See the CLI-vs-TUI branch of the command-surface tree in [`../../knowledge/cli-tooling-decision-trees.md`](../../knowledge/cli-tooling-decision-trees.md).

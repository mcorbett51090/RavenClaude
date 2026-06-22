# TUI decision

**Tool/feature:** <name>

## Is a full-screen TUI warranted?

| Question | Answer |
|---|---|
| Is the interaction sustained + stateful? | <yes / no> |
| Would a scriptable CLI + `--json` serve it better? | <yes / no> |
| Can we provide a non-TTY fallback? | <yes / no> |

**Verdict:** <full-screen TUI / scriptable CLI / GUI instead>  **Trade accepted:** <…>

## If TUI

| Decision | Choice |
|---|---|
| Framework | <Ink / Bubble Tea / Textual / ratatui> |
| Loop model | model → update → view (input as messages) |
| Redraw | diff, not full repaint |
| Slow work | off the render thread → message back |

## Survive reality (checklist)

- [ ] Resize re-lays-out (no buffer corruption)
- [ ] Terminal restored on every exit path (incl. panic/signal)
- [ ] Non-TTY → plain output or clear refusal
- [ ] Keyboard-first, screen-reader-tolerant

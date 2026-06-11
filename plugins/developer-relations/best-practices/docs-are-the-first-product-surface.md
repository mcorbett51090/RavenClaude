# Docs are the first product surface

**Status:** Pattern.

**Rule:** Most developers meet a product through its docs before they meet a human. A broken
quickstart costs more activations than any talk wins. Treat docs and onboarding as a DX-engineering
problem with a measurable funnel, not a content afterthought.

## Why

Search, an LLM answer, or a shared link drops a developer into the docs first. If the getting-started
path has hidden steps, undeclared versions, or fragile happy-path-only examples, the developer
leaves before any advocacy reaches them. Onboarding is the highest-leverage, lowest-glamour surface
DevRel owns.

## What it looks like in practice

- The quickstart is instrumented as a funnel (sign-up → credential → first call → first success) and
  the steepest drop gets the next fix.
- Prerequisites and versions are declared up front; commands are real and copy-paste runnable; the
  path ends with a verification step.
- Error messages are treated as a product surface — clear and actionable, or they send developers to
  support instead of success.

## Anti-pattern

Investing in conference talks and swag while the quickstart silently fails for a third of sign-ups.
Defer docs *information architecture* and reference craft to `technical-writing-docs`; own the
activation funnel here.

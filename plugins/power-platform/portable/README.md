# Using the Power Platform Plugin with Copilot, Cursor & Other Tools

This folder contains a portable version of the most important instructions from the power-platform plugin.

## Why this exists

The full plugin is designed for Claude Code marketplace installation. However, many developers now use GitHub Copilot, Cursor, Continue.dev, or other tools that support Claude-style project instructions via CLAUDE.md.

This portable package lets you bring the key standards (especially the anti-hallucination Capability Grounding Protocol) into any project, regardless of which model you're using.

## Recommended Usage

### Option 1: Simple (Recommended)
1. Copy portable/CLAUDE.md to the root of your project and name it CLAUDE.md
2. (Optional) Merge it into an existing CLAUDE.md

This gives Copilot, Cursor, and similar tools the core Power Platform principles + the grounding protocol.

### Option 2: Stronger
Also copy useful skills from plugins/power-platform/skills/ (especially grounding-protocol/ and maintainability-review/) into a .claude/skills/ folder in your project.

### Option 3: GitHub Copilot Specific
Create .github/copilot-instructions.md and paste key sections from portable/CLAUDE.md.

## What you get
- Strong Power Platform house rules
- The Capability Grounding Protocol (reduces confident but incorrect "I can't do that" responses)
- Partial progress mindset
- Clear output expectations

## Limitations
You won't get the full specialist agent dispatch system unless you're using Claude Code with the plugin installed. However, the core behavioral guardrails travel well.
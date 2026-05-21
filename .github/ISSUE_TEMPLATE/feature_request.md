---
name: Feature request
about: Propose a new agent, skill, hook, template, or plugin.
title: "[feat] "
labels: enhancement
assignees: mcorbett51090
---

## What kind of feature?

- [ ] New specialist agent (in which plugin?)
- [ ] New skill / playbook (in which plugin?)
- [ ] New hook (advisory or blocking?)
- [ ] New template
- [ ] New plugin (which domain?)
- [ ] Change to an existing agent / skill / hook
- [ ] Marketplace / CI / docs tooling
- [ ] Other:

## What problem does this solve?

Lead with the **outcome you want**, not the implementation. Example: "When I ask Claude to design a Dataverse schema, no specialist owns the question of column data-type trade-offs — it gets answered superficially."

## What's the smallest version that would help?

Describe the minimum viable shape. We bias toward small, focused additions rather than large new subsystems.

## Who would use this?

- [ ] Me, in my consumer projects
- [ ] Other RavenClaude collaborators
- [ ] Future engagements where we'd install the plugin from scratch
- [ ] All of the above

## Does this belong in a specific plugin, or is it cross-domain?

If cross-domain, it likely belongs in `ravenclaude-core`. If only useful in one vertical, it belongs in (or starts) that vertical's plugin. If you're not sure, ask in this issue — the routing decision matters for whether it'll be accepted.

## Alternatives considered?

What else could solve the same problem? (Existing agent reused differently, a doc instead of a hook, a manual procedure, etc.)

## Anything that would block this?

License concerns on imported content, dependency on a feature not in Claude Code yet, requires changes to multiple plugins at once, etc.

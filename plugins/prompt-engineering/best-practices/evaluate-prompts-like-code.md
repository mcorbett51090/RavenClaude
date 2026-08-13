# Evaluate prompts like code

A prompt change is a code change. "It looked better on the one example I tried" is
not evidence — single-example iteration is how a tweak fixes one case and silently
breaks five others.

**Do:** keep prompts in version control; back every prompt with a regression set
(hard cases + every past failure); score with a method fit to the task; pin the
model + version so results reproduce; and gate changes in CI so a regression fails
the build.

**Don't:** grade with an LLM judge you haven't validated against human labels, or
let a model grade its own output unaudited — judges have position, verbosity, and
self-preference biases.

**Flag:** a prompt shipping with no eval, a "passing" eval against an unpinned
model, or a green gate over a suspiciously thin set. State coverage honestly.

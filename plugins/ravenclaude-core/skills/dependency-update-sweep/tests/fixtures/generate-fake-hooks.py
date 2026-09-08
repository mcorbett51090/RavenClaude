# SYNTHETIC FIXTURE — mimics generate-copilot-hooks.py's _SKIP dict shape for
# dependency-sweep.py's scan/classify self-tests. Not a real generator.

_SKIP = {
    "agent-dispatch-evaluator.sh": "Copilot CLI has no SubagentStart-equivalent event below 1.0.70",
}

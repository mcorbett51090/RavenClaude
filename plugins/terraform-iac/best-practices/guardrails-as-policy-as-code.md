# Encode guardrails as policy-as-code on the plan

Translate 'no public buckets, no wildcard IAM, tags required, encryption on' into OPA/Conftest/Sentinel checks that evaluate the plan JSON and fail the pipeline before apply. Preventive guardrails stop the misconfiguration from ever existing; a post-hoc audit only finds it after it's exposed. Route the security verdict to security-engineering.
